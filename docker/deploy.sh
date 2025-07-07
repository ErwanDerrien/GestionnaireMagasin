#!/bin/bash

set -e

INSTANCES=3
NO_CACHE=""
DOCKER_COMPOSE_FILE="docker-compose.yml"
PROMETHEUS_CONFIG="./prometheus.yml"
NGINX_CONFIG="./nginx.conf"
NGINX_UPSTREAM_CONFIG="least_conn"
REDIS_PASSWORD=""

while [[ $# -gt 0 ]]; do
  case $1 in
  --instances)
    INSTANCES="$2"
    shift 2
    ;;
  --no-cache)
    NO_CACHE="--no-cache"
    shift
    ;;
  --redis-password)
    REDIS_PASSWORD="$2"
    shift 2
    ;;
  --config)
    case $2 in
    round_robin | rr)
      NGINX_UPSTREAM_CONFIG="round_robin"
      ;;
    least_conn | lc)
      NGINX_UPSTREAM_CONFIG="least_conn"
      ;;
    ip_hash | hash)
      NGINX_UPSTREAM_CONFIG="ip_hash"
      ;;
    weighted | w)
      NGINX_UPSTREAM_CONFIG="weighted"
      ;;
    *)
      echo "Erreur: Configuration nginx invalide. Options: round_robin|rr, least_conn|lc, ip_hash|hash, weighted|w"
      exit 1
      ;;
    esac
    shift 2
    ;;
  -h | --help)
    echo "Usage: $0 [--instances N] [--no-cache] [--config CONFIG] [--redis-password PASSWORD]"
    echo ""
    echo "Options:"
    echo "  --instances N         Nombre d'instances (défaut: 3)"
    echo "  --no-cache           Build sans cache Docker"
    echo "  --redis-password PWD Mot de passe Redis (optionnel)"
    echo "  --config CONFIG      Configuration nginx:"
    echo "                         round_robin|rr    - Round Robin"
    echo "                         least_conn|lc     - Least Connections (défaut)"
    echo "                         ip_hash|hash      - IP Hash"
    echo "                         weighted|w        - Weighted Round Robin"
    exit 0
    ;;
  *)
    echo "Argument inconnu: $1"
    exit 1
    ;;
  esac
done

if ! [[ "$INSTANCES" =~ ^[1-9][0-9]*$ ]]; then
  echo "Erreur: Le nombre d'instances doit être un entier positif"
  exit 1
fi

log_message() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log_message "🚀 Déploiement avec $INSTANCES instance(s) store_manager (config: $NGINX_UPSTREAM_CONFIG)"

# Nettoyage complet au début
log_message "🧹 Nettoyage complet des conteneurs existants"
docker compose down --volumes --remove-orphans 2>/dev/null || true

# Nettoyer TOUS les conteneurs liés à Redis
log_message "🧹 Nettoyage des conteneurs Redis"
docker rm -f $(docker ps -aq --filter "name=redis") 2>/dev/null || true
docker rm -f $(docker ps -aq --filter "ancestor=redis") 2>/dev/null || true

# Attendre un peu pour que les ports se libèrent
log_message "⏳ Attente de la libération des ports..."
sleep 3

# Forcer la libération du port 6379 si nécessaire
log_message "🔧 Vérification et libération du port 6379"
if lsof -i :6379 &>/dev/null; then
  log_message "🔧 Libération forcée du port 6379"
  # Tuer tous les processus utilisant le port 6379
  sudo lsof -ti :6379 | xargs -r sudo kill -9 2>/dev/null || true
  sleep 2
fi

log_message "📝 Génération du nginx.conf"

generate_nginx_config() {
  local file="$1"
  local instances="$2"
  local config_type="$3"

  cat >"$file" <<'EOF'
# Configuration générée automatiquement par deploy.sh
# Ne pas modifier manuellement

EOF

  # Générer les différentes configurations upstream
  case $config_type in
  "round_robin")
    cat >>"$file" <<EOF
# Configuration Round Robin (par défaut)
upstream store_manager {
EOF
    for i in $(seq 1 $instances); do
      echo "    server store_manager_$i:8080;" >>"$file"
    done
    echo "}" >>"$file"
    ;;
  "least_conn")
    cat >>"$file" <<EOF
# Configuration Least Connections
upstream store_manager {
    least_conn;
EOF
    for i in $(seq 1 $instances); do
      echo "    server store_manager_$i:8080;" >>"$file"
    done
    echo "}" >>"$file"
    ;;
  "ip_hash")
    cat >>"$file" <<EOF
# Configuration IP Hash
upstream store_manager {
    ip_hash;
EOF
    for i in $(seq 1 $instances); do
      echo "    server store_manager_$i:8080;" >>"$file"
    done
    echo "}" >>"$file"
    ;;
  "weighted")
    cat >>"$file" <<EOF
# Configuration Weighted Round Robin
upstream store_manager {
EOF
    for i in $(seq 1 $instances); do
      # Poids décroissant : premier serveur poids le plus élevé
      local weight=$((instances - i + 1))
      echo "    server store_manager_$i:8080 weight=$weight;" >>"$file"
    done
    echo "}" >>"$file"
    ;;
  esac

  cat >>"$file" <<'EOF'

server {
    listen 80;
    
    location / {
        proxy_pass http://store_manager;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        proxy_buffering off;
    }

    # Endpoint de health check pour toutes les instances
    location /health {
        proxy_pass http://store_manager;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Métriques Prometheus depuis store_manager_1 seulement
    location /metrics {
        proxy_pass http://store_manager_1:8080/metrics;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Endpoint pour vérifier le cache Redis
    location /cache-status {
        proxy_pass http://store_manager_1:8080/cache-status;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF
}

generate_nginx_config "$NGINX_CONFIG" "$INSTANCES" "$NGINX_UPSTREAM_CONFIG"

log_message "📝 Génération du docker-compose.yml"

generate_docker_compose() {
  local file="$1"
  local instances="$2"
  local redis_password="$3"

  cat >"$file" <<EOF
version: '3.8'

services:
  # Service Redis pour le cache partagé
  redis:
    image: redis:7-alpine
    container_name: redis-store
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - monitoring_net
    restart: unless-stopped
    command: >
      redis-server
      --appendonly yes
      --appendfsync everysec
      --maxmemory 256mb
      --maxmemory-policy allkeys-lru
EOF

  if [ -n "$redis_password" ]; then
    echo "      --requirepass $redis_password" >>"$file"
  fi

  echo "" >>"$file"

  # Générer les services store_manager
  for i in $(seq 1 $instances); do
    cat >>"$file" <<EOF
  store_manager_$i:
    build:
      context: ../
      dockerfile: ./docker/Dockerfile
    command: python -m src.app
    volumes:
      - ../:/app
    environment:
      - INSTANCE_NUM=$i
      - PROMETHEUS_METRICS_PORT=8080
      - REDIS_HOST=redis-store
      - REDIS_PORT=6379
      - REDIS_DB=0
      - JWT_EXPIRATION_DELTA=45
EOF
    if [ -n "$redis_password" ]; then
      echo "      - REDIS_PASSWORD=$redis_password" >>"$file"
    fi
    cat >>"$file" <<EOF
    ports:
      - "$((8080 + i)):8080"
    networks:
      - monitoring_net
    container_name: store_manager_$i
    depends_on:
      - redis
    restart: unless-stopped

EOF
  done

  cat >>"$file" <<EOF
  nginx:
    image: nginx:alpine
    ports:
      - '80:80'
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
EOF

  for i in $(seq 1 $instances); do
    echo "      - store_manager_$i" >>"$file"
  done

  cat >>"$file" <<'EOF'
    networks:
      - monitoring_net
    container_name: nginx
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - '9091:9090'
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
    networks:
      - monitoring_net
    container_name: prometheus
    restart: unless-stopped
    depends_on:
EOF

  for i in $(seq 1 $instances); do
    echo "      - store_manager_$i" >>"$file"
  done

  cat >>"$file" <<'EOF'

  # Service pour monitoring Redis (optionnel)
  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: redis-exporter
    ports:
      - "9121:9121"
    environment:
      - REDIS_ADDR=redis://redis-store:6379
EOF
  if [ -n "$redis_password" ]; then
    echo "      - REDIS_PASSWORD=$redis_password" >>"$file"
  fi
  cat >>"$file" <<'EOF'
    networks:
      - monitoring_net
    depends_on:
      - redis
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
}

generate_docker_compose "$DOCKER_COMPOSE_FILE" "$INSTANCES" "$REDIS_PASSWORD"

log_message "📝 Génération du prometheus.yml"

# Vérifier si prometheus.yml existe comme dossier et le supprimer
if [ -d "$PROMETHEUS_CONFIG" ]; then
  log_message "⚠️  prometheus.yml existe comme dossier, suppression..."
  rm -rf "$PROMETHEUS_CONFIG"
fi

PROMETHEUS_TARGETS=""
for i in $(seq 1 $INSTANCES); do
  if [ "$i" -eq 1 ]; then
    PROMETHEUS_TARGETS="'store_manager_$i:8080'"
  else
    PROMETHEUS_TARGETS="$PROMETHEUS_TARGETS, 'store_manager_$i:8080'"
  fi
done

cat >"$PROMETHEUS_CONFIG" <<EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'store_managers'
    static_configs:
      - targets: [$PROMETHEUS_TARGETS]
    scrape_interval: 15s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
    scrape_interval: 15s
EOF

log_message "✅ Fichiers de configuration générés"

log_message "🔍 Validation du docker-compose.yml"
if command -v docker-compose &>/dev/null; then
  docker-compose -f "$DOCKER_COMPOSE_FILE" config >/dev/null &&
    log_message "✅ docker-compose.yml valide" ||
    {
      log_message "❌ Erreur dans docker-compose.yml:"
      docker-compose -f "$DOCKER_COMPOSE_FILE" config
      exit 1
    }
elif command -v docker &>/dev/null && docker compose version &>/dev/null; then
  docker compose -f "$DOCKER_COMPOSE_FILE" config >/dev/null &&
    log_message "✅ docker-compose.yml valide" ||
    {
      log_message "❌ Erreur dans docker-compose.yml:"
      docker compose -f "$DOCKER_COMPOSE_FILE" config
      exit 1
    }
else
  log_message "⚠️  Impossible de valider le YAML (docker-compose non trouvé)"
fi

if [ -n "$NO_CACHE" ]; then
  log_message "🔨 Build des images (sans cache)"
  docker compose build --no-cache
else
  log_message "🔨 Build des images"
  docker compose build
fi

log_message "🚀 Démarrage des services"
docker compose up -d

log_message "⏳ Vérification du démarrage des services..."
sleep 10

log_message "📊 État des conteneurs:"
docker compose ps

# Vérifier la connectivité Redis
log_message "🔍 Test de connectivité Redis"
if docker exec redis-store redis-cli ping >/dev/null 2>&1; then
  log_message "✅ Redis est accessible"
else
  log_message "❌ Erreur de connectivité Redis"
  log_message "📋 Logs Redis:"
  docker logs redis-store --tail 10
fi

# Vérifier les logs pour les erreurs Redis
log_message "🔍 Vérification des logs d'erreur Redis"
for i in $(seq 1 $INSTANCES); do
  if docker logs "store_manager_$i" 2>&1 | grep -q "redis\|Redis\|cache" | head -3; then
    log_message "📋 Logs Redis pour store_manager_$i:"
    docker logs "store_manager_$i" 2>&1 | grep -i "redis\|cache" | head -3
  fi
done

log_message "✅ Déploiement terminé!"
echo ""
echo "🌐 Services disponibles:"
echo "   • Application (Load Balancer): http://localhost"
echo "   • Prometheus: http://localhost:9091"
echo "   • Redis: localhost:6379"
echo "   • Redis Exporter: http://localhost:9121"
echo ""
echo "🔧 Instances store_manager:"
for i in $(seq 1 $INSTANCES); do
  echo "   • store_manager_$i: http://localhost:$((8080 + i))"
done
echo ""
echo "📊 Monitoring:"
echo "   • Métriques Redis: http://localhost:9121/metrics"
echo "   • État cache: http://localhost/cache-status"
echo ""
echo "🔧 Commandes utiles:"
echo "   • Logs Redis: docker logs redis-store"
echo "   • CLI Redis: docker exec -it redis-store redis-cli"
echo "   • Statut cache: docker exec redis-store redis-cli info memory"
