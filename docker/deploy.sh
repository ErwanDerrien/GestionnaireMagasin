#!/bin/bash
set -e

# Vérifier si le fichier de configuration existe
if [[ ! -f "../config/variables.sh" ]]; then
  echo "⚠️  Fichier de configuration '../config/variables.sh' non trouvé"
  echo "Création d'un fichier de configuration par défaut..."
  mkdir -p ../config
  cat >../config/variables.sh <<EOF
#!/bin/bash
# Configuration par défaut
export DATABASE_URL="postgresql://kong:kong@postgres:5432/kong"
export REDIS_URL="redis://redis-store:6379"
EOF
fi

source ../config/variables.sh

# Variables par défaut
AUTH_INSTANCES=1
PRODUCT_INSTANCES=1
ORDER_INSTANCES=1
OTHER_INSTANCES=1
NO_CACHE=""
DOCKER_COMPOSE_FILE="docker-compose.yml"

log_message() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Fonction d'aide
show_help() {
  cat <<EOF
Usage: $0 [OPTIONS]

Options:
  --auth N        Nombre d'instances du service auth (défaut: 1)
  --products N    Nombre d'instances du service product (défaut: 1)
  --orders N      Nombre d'instances du service order (défaut: 1)
  --others N      Nombre d'instances du service other (défaut: 1)
  --no-cache      Construire sans cache Docker
  -h, --help      Afficher cette aide

Exemples:
  $0                           # Déploiement par défaut
  $0 --auth 2 --products 3     # 2 instances auth, 3 instances product
  $0 --no-cache                # Reconstruction sans cache
EOF
}

# Traitement des arguments
while [[ $# -gt 0 ]]; do
  case $1 in
  --auth)
    if [[ -z "$2" ]] || [[ "$2" =~ ^- ]]; then
      echo "❌ Erreur: --auth nécessite un nombre"
      exit 1
    fi
    if ! [[ "$2" =~ ^[0-9]+$ ]] || [[ "$2" -lt 1 ]]; then
      echo "❌ Erreur: --auth doit être un nombre positif"
      exit 1
    fi
    AUTH_INSTANCES="$2"
    shift 2
    ;;
  --products)
    if [[ -z "$2" ]] || [[ "$2" =~ ^- ]]; then
      echo "❌ Erreur: --products nécessite un nombre"
      exit 1
    fi
    if ! [[ "$2" =~ ^[0-9]+$ ]] || [[ "$2" -lt 1 ]]; then
      echo "❌ Erreur: --products doit être un nombre positif"
      exit 1
    fi
    PRODUCT_INSTANCES="$2"
    shift 2
    ;;
  --orders)
    if [[ -z "$2" ]] || [[ "$2" =~ ^- ]]; then
      echo "❌ Erreur: --orders nécessite un nombre"
      exit 1
    fi
    if ! [[ "$2" =~ ^[0-9]+$ ]] || [[ "$2" -lt 1 ]]; then
      echo "❌ Erreur: --orders doit être un nombre positif"
      exit 1
    fi
    ORDER_INSTANCES="$2"
    shift 2
    ;;
  --others)
    if [[ -z "$2" ]] || [[ "$2" =~ ^- ]]; then
      echo "❌ Erreur: --others nécessite un nombre"
      exit 1
    fi
    if ! [[ "$2" =~ ^[0-9]+$ ]] || [[ "$2" -lt 1 ]]; then
      echo "❌ Erreur: --others doit être un nombre positif"
      exit 1
    fi
    OTHER_INSTANCES="$2"
    shift 2
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
    echo "Utilisez --help pour voir les options disponibles"
    exit 1
    ;;
  esac
done

# Vérifier les prérequis
check_prerequisites() {
  local missing_tools=()

  if ! command -v docker &>/dev/null; then
    missing_tools+=("docker")
  fi

  if ! command -v docker-compose &>/dev/null && ! docker compose version &>/dev/null; then
    missing_tools+=("docker-compose")
  fi

  if ! command -v curl &>/dev/null; then
    missing_tools+=("curl")
  fi

  if ! command -v jq &>/dev/null; then
    missing_tools+=("jq")
  fi

  if [[ ${#missing_tools[@]} -gt 0 ]]; then
    echo "❌ Outils manquants: ${missing_tools[*]}"
    echo "Veuillez installer ces outils avant de continuer."
    exit 1
  fi
}

# Fonction pour attendre qu'un service soit prêt
wait_for_service() {
  local service_name=$1
  local url=$2
  local max_attempts=30
  local attempt=1

  log_message "⏳ Attente du service $service_name..."

  while [[ $attempt -le $max_attempts ]]; do
    if curl -s -f "$url" >/dev/null 2>&1; then
      log_message "✅ Service $service_name prêt"
      return 0
    fi

    echo -n "."
    sleep 2
    ((attempt++))
  done

  echo
  log_message "❌ Timeout: Service $service_name non disponible après $((max_attempts * 2))s"
  return 1
}

# Fonction pour configurer Kong avec gestion d'erreur
configure_kong_service() {
  local service=$1
  local path=$2
  local port=$3

  log_message "🔧 Configuration du service Kong: $service"

  # Créer le service
  if ! curl -s -X POST http://localhost:8001/services \
    -d "name=${service}-service" \
    -d "url=http://${service}_instance_1:${port}" >/dev/null; then
    log_message "❌ Erreur lors de la création du service $service"
    return 1
  fi

  # Créer la route
  if ! curl -s -X POST http://localhost:8001/services/${service}-service/routes \
    -d "paths[]=${path}" >/dev/null; then
    log_message "❌ Erreur lors de la création de la route pour $service"
    return 1
  fi

  # Ajouter l'authentification
  if ! curl -s -X POST http://localhost:8001/services/${service}-service/plugins \
    -d "name=key-auth" >/dev/null; then
    log_message "❌ Erreur lors de l'ajout de l'authentification pour $service"
    return 1
  fi

  log_message "✅ Service $service configuré"
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
configure_kong_service "auth" "/auth" "8080"
configure_kong_service "product" "/product" "8080"
configure_kong_service "order" "/order" "8080"
configure_kong_service "other" "/" "8080"

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
  curl -H "apikey: $KEY" http://localhost/api/v2/auth
  curl -H "apikey: $KEY" http://localhost/api/v2/product
  curl -H "apikey: $KEY" http://localhost/api/v2/order

🐳 Status des conteneurs:
EOF

docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

log_message "📋 Vérification des services Kong"
echo "Services Kong configurés:"
curl -s http://localhost:8001/services | jq -r '.data[].name' 2>/dev/null || echo "Erreur lors de la récupération des services"
