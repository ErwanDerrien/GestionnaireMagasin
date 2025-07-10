#!/bin/bash
set -e
source ../config/variables.sh

# Fichier de configuration par défaut
if [[ ! -f "../config/variables.sh" ]]; then
  echo "⚠️  Fichier de configuration '../config/variables.sh' non trouvé"
  echo "Création d'un fichier de configuration par défaut..."
  mkdir -p ../config
  cat >../config/variables.sh <<EOF
#!/bin/bash
export DATABASE_URL="postgresql://kong:kong@postgres:5432/kong"
export REDIS_URL="redis://redis-store:6379"
EOF
fi

source ../config/variables.sh

# Valeurs par défaut
AUTH_INSTANCES=1
PRODUCT_INSTANCES=1
ORDER_INSTANCES=1
OTHER_INSTANCES=1
AUTH_MODE=""
PRODUCT_MODE=""
ORDER_MODE=""
OTHER_MODE=""
NO_CACHE=""
DOCKER_COMPOSE_FILE="docker-compose.yml"

log_message() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

show_help() {
  cat <<EOF
Usage: $0 [OPTIONS]

Options:
  --auth N MODE        Nombre d'instances du service auth + mode (hash, lc, rr, w)
  --products N MODE    Nombre d'instances du service product + mode
  --orders N MODE      Nombre d'instances du service order + mode
  --others N MODE      Nombre d'instances du service other + mode
  --no-cache           Construire sans cache Docker
  -h, --help           Afficher cette aide

Exemples:
  $0 --auth 2 hash --products 3 lc --orders 5 rr --others 2 w
EOF
}

# Parsing des arguments
while [[ $# -gt 0 ]]; do
  case $1 in
  --auth)
    AUTH_INSTANCES="$2"
    AUTH_MODE="$3"
    shift 3
    ;;
  --products)
    PRODUCT_INSTANCES="$2"
    PRODUCT_MODE="$3"
    shift 3
    ;;
  --orders)
    ORDER_INSTANCES="$2"
    ORDER_MODE="$3"
    shift 3
    ;;
  --others)
    OTHER_INSTANCES="$2"
    OTHER_MODE="$3"
    shift 3
    ;;
  --no-cache)
    NO_CACHE="--no-cache"
    shift
    ;;
  -h | --help)
    show_help
    exit 0
    ;;
  *)
    echo "❌ Argument inconnu: $1"
    exit 1
    ;;
  esac
done

check_prerequisites() {
  for cmd in docker curl jq; do
    if ! command -v $cmd &>/dev/null; then
      echo "❌ $cmd est requis"
      exit 1
    fi
  done
}

wait_for_service() {
  local name=$1
  local url=$2
  for i in {1..30}; do
    if curl -s -f "$url" &>/dev/null; then
      log_message "✅ $name est prêt"
      return
    fi
    sleep 2
  done
  echo "❌ $name ne répond pas"
  exit 1
}

# Fonction pour configurer Kong avec gestion d'erreur
configure_kong_service() {
  local service=$1
  local path=$2
  local port=$3
  local mode=$4
  local count_var_name="${service^^}_INSTANCES"
  local count="${!count_var_name}"

  # Mapper les modes à ceux de Kong
  case "$mode" in
    rr) algorithm="round-robin" ;;
    lc) algorithm="least-connections" ;;
    hash) algorithm="consistent-hashing" ;;
    *) algorithm="round-robin"; log_message "⚠️ Mode $mode non supporté. Utilisation de round-robin." ;;
  esac

  log_message "🔧 Config Kong: $service ($mode -> $algorithm)"

  # Créer l'upstream
  curl -s -X POST http://localhost:8001/upstreams \
    -d "name=${service}-upstream" \
    -d "algorithm=${algorithm}" >/dev/null

  # Ajouter les targets
  for i in $(seq 1 $count); do
    curl -s -X POST http://localhost:8001/upstreams/${service}-upstream/targets \
      -d "target=${service}_instance_$i:${port}" \
      -d "weight=100" >/dev/null
  done

  # Créer le service
  curl -s -X POST http://localhost:8001/services \
    -d "name=${service}-service" \
    -d "host=${service}-upstream" \
    -d "port=${port}" \
    -d "protocol=http" >/dev/null

  # Créer la route
  curl -s -X POST http://localhost:8001/services/${service}-service/routes \
    -d "paths[]=${path}" >/dev/null

  # Authentification
  curl -s -X POST http://localhost:8001/services/${service}-service/plugins \
    -d "name=key-auth" \
    -d "config.key_names[]=x-api-key" >/dev/null

  log_message "✅ $service configuré avec stratégie $algorithm"
}

# Fonction pour générer les instances de services
generate_instances() {
  local service=$1
  local count=$2
  local base_port=$3

  for i in $(seq 1 $count); do
    port=$((base_port + i))
    cat >>"$DOCKER_COMPOSE_FILE" <<EOF

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
      - REDIS_HOST=redis-store
      - REDIS_PORT=6379
    ports:
      - "${port}:8080"
    networks: [monitoring_net]
    depends_on: 
      - redis
      - postgres
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
EOF
  done
}

# Vérification des prérequis
check_prerequisites

log_message "🧹 Nettoyage des conteneurs existants"
docker compose down --volumes --remove-orphans 2>/dev/null || true

# Nettoyer les anciens fichiers
rm -f "$DOCKER_COMPOSE_FILE"
rm -rf prometheus.yml # Supprimer le répertoire ou fichier prometheus.yml

log_message "📝 Génération du docker-compose.yml avec Kong"
cat >"$DOCKER_COMPOSE_FILE" <<EOF
services:
  postgres:
    image: postgres:13
    container_name: postgres-db
    environment:
      POSTGRES_USER: kong
      POSTGRES_PASSWORD: kong
      POSTGRES_DB: kong
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks: [monitoring_net]
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U kong"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: redis-store
    ports: ["6379:6379"]
    volumes: [redis_data:/data]
    networks: [monitoring_net]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  kong-migrations:
    image: kong:latest
    container_name: kong-migrations
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: postgres
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: kong
      KONG_PG_DATABASE: kong
    command: kong migrations bootstrap
    networks: [monitoring_net]
    restart: "no"

  kong:
    image: kong:latest
    container_name: kong-gateway
    depends_on:
      - kong-migrations
      - postgres
      - redis
    ports:
      - "80:8000"
      - "8001:8001"
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: postgres
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: kong
      KONG_PG_DATABASE: kong
      KONG_PROXY_ACCESS_LOG: /dev/stdout
      KONG_ADMIN_ACCESS_LOG: /dev/stdout
      KONG_PROXY_ERROR_LOG: /dev/stderr
      KONG_ADMIN_ERROR_LOG: /dev/stderr
      KONG_ADMIN_LISTEN: 0.0.0.0:8001
    networks: [monitoring_net]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "kong", "health"]
      interval: 30s
      timeout: 10s
      retries: 3

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports: ["9091:9090"]
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    networks: [monitoring_net]
    restart: unless-stopped
    depends_on: [redis]

  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: redis-exporter
    ports: ["9121:9121"]
    environment:
      - REDIS_ADDR=redis://redis-store:6379
    networks: [monitoring_net]
    depends_on: 
      redis:
        condition: service_healthy
    restart: unless-stopped
EOF

# Générer les instances des services
generate_instances auth $AUTH_INSTANCES 8080
generate_instances product $PRODUCT_INSTANCES 8090
generate_instances order $ORDER_INSTANCES 8100
generate_instances other $OTHER_INSTANCES 8110

# Ajouter les réseaux et volumes
cat >>"$DOCKER_COMPOSE_FILE" <<EOF

networks:
  monitoring_net:
    driver: bridge

volumes:
  redis_data:
  prometheus_data:
  postgres_data:
EOF

log_message "📝 Génération de la configuration Prometheus"
cat >prometheus.yml <<EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
EOF

# Fonction pour générer les targets d'un service
generate_targets() {
  local service=$1
  local count=$2
  local targets=""

  for i in $(seq 1 $count); do
    if [[ $i -eq 1 ]]; then
      targets="'${service}_instance_$i:8080'"
    else
      targets="$targets, '${service}_instance_$i:8080'"
    fi
  done

  echo "  - job_name: '${service}_instances'"
  echo "    static_configs:"
  echo "      - targets: [$targets]"
}

# Ajouter les targets pour chaque service
for svc in auth product order other; do
  case $svc in
  auth) count=$AUTH_INSTANCES ;;
  product) count=$PRODUCT_INSTANCES ;;
  order) count=$ORDER_INSTANCES ;;
  other) count=$OTHER_INSTANCES ;;
  esac

  for i in $(seq 1 $count); do
    cat >>prometheus.yml <<EOF
  - job_name: '${svc}_instance_$i'
    static_configs:
      - targets: ['${svc}_instance_$i:8080']
    metrics_path: /metrics
    scrape_interval: 15s
EOF
  done
done

cat >>prometheus.yml <<EOF
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
    scrape_interval: 15s

  - job_name: 'kong'
    static_configs:
      - targets: ['kong:8001']
    metrics_path: /metrics
    scrape_interval: 15s
EOF

# Corriger les permissions du fichier prometheus.yml
chmod 644 prometheus.yml

log_message "🚀 Démarrage des services avec Kong"
if [[ -n "$NO_CACHE" ]]; then
  docker compose build $NO_CACHE
fi

docker compose up -d

# Attendre que Kong soit prêt
if ! wait_for_service "Kong Admin" "http://localhost:8001"; then
  log_message "❌ Impossible de démarrer Kong"
  exit 1
fi

# Configuration des services Kong
configure_kong_service "auth" "/$API_MASK/$VERSION/auth" "8080" "$AUTH_MODE"
configure_kong_service "product" "/$API_MASK/$VERSION/products" "8080" "$PRODUCT_MODE"
configure_kong_service "order" "/$API_MASK/$VERSION/orders" "8080" "$ORDER_MODE"
configure_kong_service "other" "/$API_MASK/$VERSION/" "8080" "$OTHER_MODE"

log_message "🔑 Génération d'une clé API"
if ! curl -s -X POST http://localhost:8001/consumers \
  -d "username=default-user" >/dev/null; then
  log_message "❌ Erreur lors de la création du consumer"
  exit 1
fi

KEY=$(curl -s -X POST http://localhost:8001/consumers/default-user/key-auth | jq -r '.key')

if [[ "$KEY" == "null" ]] || [[ -z "$KEY" ]]; then
  log_message "❌ Erreur lors de la génération de la clé API"
  exit 1
fi

# Redémarrer Prometheus pour charger la nouvelle configuration
log_message "🔄 Redémarrage de Prometheus avec la nouvelle configuration"
docker compose restart prometheus

log_message "✅ Déploiement terminé avec succès"
cat <<EOF

🌐 Services disponibles:
  - API Gateway (Kong): http://localhost
  - Kong Admin: http://localhost:8001
  - Prometheus: http://localhost:9091
  - Redis Exporter: http://localhost:9121
  
🔑 Clé API générée: $KEY

📊 Instances déployées:
  - Auth: $AUTH_INSTANCES instance(s)
  - Product: $PRODUCT_INSTANCES instance(s)
  - Order: $ORDER_INSTANCES instance(s)
  - Other: $OTHER_INSTANCES instance(s)

📮 Exemple d'utilisation:
  curl -H "apikey: $KEY" http://localhost/$API_MASK/$VERSION/auth
  curl -H "apikey: $KEY" http://localhost/$API_MASK/$VERSION/product
  curl -H "apikey: $KEY" http://localhost/$API_MASK/$VERSION/order

🐳 Status des conteneurs:
EOF

docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

log_message "📋 Vérification des services Kong"
echo "Services Kong configurés:"
curl -s http://localhost:8001/services | jq -r '.data[].name' 2>/dev/null || echo "Erreur lors de la récupération des services"
