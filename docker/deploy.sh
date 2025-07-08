#!/bin/bash
source ../config/variables.sh

# Valeurs par défaut
AUTH_INSTANCES=1
PRODUCT_INSTANCES=1
ORDER_INSTANCES=1
OTHER_INSTANCES=1
AUTH_LB="lc"  # Default: least_conn
PRODUCT_LB="lc"
ORDER_LB="lc"
OTHER_LB="lc"
NO_CACHE=""
DOCKER_COMPOSE_FILE="docker-compose.yml"
PROMETHEUS_CONFIG="prometheus.yml"
NGINX_CONFIG="nginx.conf"

# Fonction pour afficher l'aide
show_help() {
  echo "Usage: $0 [options]"
  echo "Options:"
  echo "  --auth N [lc|rr|hash|w]    Nombre d'instances auth + méthode LB"
  echo "  --products N [lc|rr|hash|w] Nombre d'instances products + méthode LB"
  echo "  --orders N [lc|rr|hash|w]   Nombre d'instances orders + méthode LB"
  echo "  --others N [lc|rr|hash|w]   Nombre d'instances others + méthode LB"
  echo "  --no-cache                 Rebuild sans cache Docker"
  echo "Méthodes LB:"
  echo "  lc    - Least Connections (défaut)"
  echo "  rr    - Round Robin"
  echo "  hash  - IP Hash"
  echo "  w     - Weighted Round Robin"
  exit 0
}

# Parsing des arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --auth)
      AUTH_INSTANCES="$2"
      if [[ "$3" =~ ^(lc|rr|hash|w)$ ]]; then
        AUTH_LB="$3"
        shift
      fi
      shift 2
      ;;
    --products)
      PRODUCT_INSTANCES="$2"
      if [[ "$3" =~ ^(lc|rr|hash|w)$ ]]; then
        PRODUCT_LB="$3"
        shift
      fi
      shift 2
      ;;
    --orders)
      ORDER_INSTANCES="$2"
      if [[ "$3" =~ ^(lc|rr|hash|w)$ ]]; then
        ORDER_LB="$3"
        shift
      fi
      shift 2
      ;;
    --others)
      OTHER_INSTANCES="$2"
      if [[ "$3" =~ ^(lc|rr|hash|w)$ ]]; then
        OTHER_LB="$3"
        shift
      fi
      shift 2
      ;;
    --no-cache)
      NO_CACHE="--no-cache"
      shift
      ;;
    -h|--help)
      show_help
      ;;
    *)
      echo "Erreur: Argument inconnu $1"
      show_help
      exit 1
      ;;
  esac
done

log_message() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 1. Nettoyage
log_message "🧹 Nettoyage des conteneurs existants"
docker compose down --volumes --remove-orphans 2>/dev/null || true

# 2. Génération du docker-compose.yml
log_message "📝 Génération du docker-compose.yml"
cat > "$DOCKER_COMPOSE_FILE" <<EOF
services:
  redis:
    image: redis:7-alpine
    container_name: redis-store
    ports: ["6379:6379"]
    volumes: [redis_data:/data]
    networks: [monitoring_net]
    restart: unless-stopped
    command: >
      redis-server
      --appendonly yes
      --appendfsync everysec
      --maxmemory 256mb
      --maxmemory-policy allkeys-lru
EOF

# Fonction pour générer les instances
generate_instances() {
  local service=$1
  local instances=$2
  local start_port=$3

  for i in $(seq 1 $instances); do
    port=$((start_port + i))
    cat >> "$DOCKER_COMPOSE_FILE" <<EOF

  ${service}_instance_$i:
    build:
      context: ../
      dockerfile: ./docker/Dockerfile
    command: python -m src.app --service=$service
    volumes:
      - ../:/app
    environment:
      - INSTANCE_NUM=$i
      - SERVICE_TYPE=$service
      - PROMETHEUS_METRICS_PORT=8080
      - REDIS_HOST=redis-store
      - REDIS_PORT=6379
    ports:
      - "$port:8080"
    networks: [monitoring_net]
    container_name: ${service}_instance_$i
    depends_on: [redis]
    restart: unless-stopped
EOF
  done
}

generate_instances auth $AUTH_INSTANCES 8080
generate_instances product $PRODUCT_INSTANCES 8090
generate_instances order $ORDER_INSTANCES 8100
generate_instances other $OTHER_INSTANCES 8110

# Section Nginx
cat >> "$DOCKER_COMPOSE_FILE" <<EOF

  nginx:
    image: nginx:alpine
    ports: ["80:80"]
    volumes: [./nginx.conf:/etc/nginx/conf.d/default.conf:ro]
    depends_on:
      - redis
EOF

# Fonction pour générer les dépendances
generate_depends_on() {
  local service=$1
  local instances=$2
  for i in $(seq 1 $instances); do
    echo "      - ${service}_instance_$i"
  done
}

# Ajout des dépendances
generate_depends_on auth $AUTH_INSTANCES >> "$DOCKER_COMPOSE_FILE"
generate_depends_on product $PRODUCT_INSTANCES >> "$DOCKER_COMPOSE_FILE"
generate_depends_on order $ORDER_INSTANCES >> "$DOCKER_COMPOSE_FILE"
generate_depends_on other $OTHER_INSTANCES >> "$DOCKER_COMPOSE_FILE"

# Suite de la configuration
cat >> "$DOCKER_COMPOSE_FILE" <<EOF
    networks: [monitoring_net]
    container_name: nginx
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports: ["9091:9090"]
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--log.level=info'
      - '--web.enable-lifecycle'
    networks: [monitoring_net]
    container_name: prometheus
    restart: unless-stopped
    depends_on:
EOF

# Dépendances Prometheus
generate_depends_on auth $AUTH_INSTANCES >> "$DOCKER_COMPOSE_FILE"
generate_depends_on product $PRODUCT_INSTANCES >> "$DOCKER_COMPOSE_FILE"
generate_depends_on order $ORDER_INSTANCES >> "$DOCKER_COMPOSE_FILE"
generate_depends_on other $OTHER_INSTANCES >> "$DOCKER_COMPOSE_FILE"

# Finalisation
cat >> "$DOCKER_COMPOSE_FILE" <<EOF

  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: redis-exporter
    ports: ["9121:9121"]
    environment:
      - REDIS_ADDR=redis://redis-store:6379
    networks: [monitoring_net]
    depends_on: [redis]
    restart: unless-stopped

networks:
  monitoring_net:
    driver: bridge

volumes:
  redis_data:
    driver: local
  prometheus_data:
    driver: local
EOF

# 3. Génération de la configuration Nginx
generate_upstream() {
  local service=$1
  local instances=$2
  local lb_method=$3

  echo "upstream ${service}_servers {"
  case "$lb_method" in
    "rr")
      echo "    # Round Robin"
      ;;
    "hash")
      echo "    ip_hash;"
      ;;
    "w")
      echo "    # Weighted Round Robin"
      for i in $(seq 1 $instances); do
        weight=$((instances - i + 2))  # Poids décroissant
        echo "    server ${service}_instance_$i:8080 weight=$weight;"
      done
      echo "}"
      return
      ;;
    *)
      echo "    least_conn;"
      ;;
  esac

  for i in $(seq 1 $instances); do
    echo "    server ${service}_instance_$i:8080;"
  done
  echo "}"
}

log_message "📝 Génération de la configuration Nginx"
cat > "$NGINX_CONFIG" <<EOF
$(generate_upstream auth $AUTH_INSTANCES $AUTH_LB)

$(generate_upstream product $PRODUCT_INSTANCES $PRODUCT_LB)

$(generate_upstream order $ORDER_INSTANCES $ORDER_LB)

$(generate_upstream other $OTHER_INSTANCES $OTHER_LB)

server {
    listen 80;
    
    location /auth {
        proxy_pass http://auth_servers;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location /product {
        proxy_pass http://product_servers;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location /order {
        proxy_pass http://order_servers;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location / {
        proxy_pass http://other_servers;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location /metrics {
        proxy_pass http://auth_instance_1:8080/metrics;
    }
}
EOF

# 4. Génération de la configuration Prometheus
generate_prometheus_targets() {
  local service=$1
  local instances=$2
  local targets=""
  
  for i in $(seq 1 $instances); do
    targets+="'${service}_instance_${i}:8080', "
  done
  
  # Retire la dernière virgule
  targets=${targets%, }
  
  cat <<EOF
  - job_name: '${service}_instances'
    static_configs:
      - targets: [${targets}]
EOF
}

log_message "📝 Génération de la configuration Prometheus"
cat > "$PROMETHEUS_CONFIG" <<EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
$(generate_prometheus_targets auth $AUTH_INSTANCES)
$(generate_prometheus_targets product $PRODUCT_INSTANCES)
$(generate_prometheus_targets order $ORDER_INSTANCES)
$(generate_prometheus_targets other $OTHER_INSTANCES)
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
EOF

# 5. Démarrage des services
log_message "🚀 Démarrage des services"
if ! docker compose up -d $NO_CACHE; then
  log_message "❌ Erreur lors du démarrage des services"
  docker compose logs --tail=20
  exit 1
fi

# 6. Vérification du démarrage
log_message "⏳ Vérification du démarrage des services (timeout: 60s)..."

# Vérification simplifiée avec timeout
timeout=60
elapsed=0
while ! curl -s http://localhost:9091/-/ready >/dev/null; do
  if [ $elapsed -ge $timeout ]; then
    log_message "⚠️ Prometheus ne répond pas après $timeout secondes (peut être lent au premier démarrage)"
    log_message "ℹ️ Les autres services peuvent être fonctionnels même si Prometheus est lent"
    break
  fi
  sleep 5
  elapsed=$((elapsed + 5))
  log_message "⏳ Attente de Prometheus... (${elapsed}s/${timeout}s)"
done

# Tentative de rechargement (silencieuse)
curl -s -X POST http://localhost:9091/-/reload >/dev/null || true

# Message final
log_message "✅ Déploiement terminé!"
cat <<EOF

🌐 Accès aux services:
  - Application:       http://localhost
  - Prometheus:        http://localhost:9091/targets
  - Redis Exporter:    http://localhost:9121

Configuration Load Balancing:
  - Auth:    $AUTH_INSTANCES instances (méthode: $AUTH_LB)
  - Products: $PRODUCT_INSTANCES instances (méthode: $PRODUCT_LB)
  - Orders:  $ORDER_INSTANCES instances (méthode: $ORDER_LB)
  - Others:  $OTHER_INSTANCES instances (méthode: $OTHER_LB)

Pour consulter les logs:
  docker compose logs -f
EOF

# Vérification finale des services
sleep 2  # Laisse un peu de temps pour le démarrage complet
log_message "🔍 État des containers:"
docker compose ps