#!/bin/bash
source ../config/variables.sh

# Valeurs par défaut
AUTH_INSTANCES=1
PRODUCT_INSTANCES=1
ORDER_INSTANCES=1
OTHER_INSTANCES=1
AUTH_LB="least_conn" # Default
PRODUCT_LB="least_conn"
ORDER_LB="least_conn"
OTHER_LB="least_conn"
NO_CACHE=""
DOCKER_COMPOSE_FILE="docker-compose.yml"
PROMETHEUS_CONFIG="prometheus.yml"
NGINX_CONFIG="nginx.conf"
NGINX_UPSTREAM_CONFIG="least_conn"
REDIS_PASSWORD=""

while [[ $# -gt 0 ]]; do
  case $1 in
  --auth)
    AUTH_INSTANCES="$2"
    if [[ "$3" == "rr" || "$3" == "least_conn" ]]; then
      AUTH_LB="$3"
      shift 1
    fi
    shift 2
    ;;
  --products)
    PRODUCT_INSTANCES="$2"
    if [[ "$3" == "rr" || "$3" == "least_conn" ]]; then
      PRODUCT_LB="$3"
      shift 1
    fi
    shift 2
    ;;
  --orders)
    ORDER_INSTANCES="$2"
    if [[ "$3" == "rr" || "$3" == "least_conn" ]]; then
      ORDER_LB="$3"
      shift 1
    fi
    shift 2
    ;;
  --others)
    OTHER_INSTANCES="$2"
    if [[ "$3" == "rr" || "$3" == "least_conn" ]]; then
      OTHER_LB="$3"
      shift 1
    fi
    shift 2
    ;;
  --no-cache)
    NO_CACHE="--no-cache"
    shift
    ;;
  -h | --help)
    echo "Usage: $0 [--auth N [rr|least_conn]] [--products N [rr|least_conn]] [--orders N [rr|least_conn]] [--others N [rr|least_conn]] [--no-cache]"
    exit 0
    ;;
  *)
    echo "Argument inconnu: $1"
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

# 2. Génération du docker-compose.yml dynamique
log_message "📝 Génération du fichier docker-compose.yml"
cat >$DOCKER_COMPOSE_FILE <<EOF
version: '3'

services:
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

# Génération des instances auth
for i in $(seq 1 $AUTH_INSTANCES); do
  PORT=$((8080 + i))
  cat >>$DOCKER_COMPOSE_FILE <<EOF

  auth_instance_$i:
    build:
      context: ../
      dockerfile: ./docker/Dockerfile
    command: python -m src.app --service=auth
    volumes:
      - ../:/app
    environment:
      - INSTANCE_NUM=$i
      - SERVICE_TYPE=auth
      - PROMETHEUS_METRICS_PORT=8080
      - REDIS_HOST=redis-store
      - REDIS_PORT=6379
    ports:
      - "$PORT:8080"
    networks:
      - monitoring_net
    container_name: auth_instance_$i
    depends_on:
      - redis
    restart: unless-stopped
EOF
done

# Génération des instances product
for i in $(seq 1 $PRODUCT_INSTANCES); do
  PORT=$((8090 + i))
  cat >>$DOCKER_COMPOSE_FILE <<EOF

  product_instance_$i:
    build:
      context: ../
      dockerfile: ./docker/Dockerfile
    command: python -m src.app --service=product
    volumes:
      - ../:/app
    environment:
      - INSTANCE_NUM=$i
      - SERVICE_TYPE=product
      - PROMETHEUS_METRICS_PORT=8080
      - REDIS_HOST=redis-store
      - REDIS_PORT=6379
    ports:
      - "$PORT:8080"
    networks:
      - monitoring_net
    container_name: product_instance_$i
    depends_on:
      - redis
    restart: unless-stopped
EOF
done

# Génération des instances order
for i in $(seq 1 $ORDER_INSTANCES); do
  PORT=$((8100 + i))
  cat >>$DOCKER_COMPOSE_FILE <<EOF

  order_instance_$i:
    build:
      context: ../
      dockerfile: ./docker/Dockerfile
    command: python -m src.app --service=order
    volumes:
      - ../:/app
    environment:
      - INSTANCE_NUM=$i
      - SERVICE_TYPE=order
      - PROMETHEUS_METRICS_PORT=8080
      - REDIS_HOST=redis-store
      - REDIS_PORT=6379
    ports:
      - "$PORT:8080"
    networks:
      - monitoring_net
    container_name: order_instance_$i
    depends_on:
      - redis
    restart: unless-stopped
EOF
done

# Génération des autres instances
for i in $(seq 1 $OTHER_INSTANCES); do
  PORT=$((8110 + i))
  cat >>$DOCKER_COMPOSE_FILE <<EOF

  other_instance_$i:
    build:
      context: ../
      dockerfile: ./docker/Dockerfile
    command: python -m src.app --service=other
    volumes:
      - ../:/app
    environment:
      - INSTANCE_NUM=$i
      - SERVICE_TYPE=other
      - PROMETHEUS_METRICS_PORT=8080
      - REDIS_HOST=redis-store
      - REDIS_PORT=6379
    ports:
      - "$PORT:8080"
    networks:
      - monitoring_net
    container_name: other_instance_$i
    depends_on:
      - redis
    restart: unless-stopped
EOF
done

# Ajout des services communs
cat >>$DOCKER_COMPOSE_FILE <<EOF

  nginx:
    image: nginx:alpine
    ports:
      - '80:80'
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
EOF

# Dépendances Nginx
for i in $(seq 1 $AUTH_INSTANCES); do
  echo "      - auth_instance_$i" >>$DOCKER_COMPOSE_FILE
done
for i in $(seq 1 $PRODUCT_INSTANCES); do
  echo "      - product_instance_$i" >>$DOCKER_COMPOSE_FILE
done
for i in $(seq 1 $ORDER_INSTANCES); do
  echo "      - order_instance_$i" >>$DOCKER_COMPOSE_FILE
done
for i in $(seq 1 $OTHER_INSTANCES); do
  echo "      - other_instance_$i" >>$DOCKER_COMPOSE_FILE
done

cat >>$DOCKER_COMPOSE_FILE <<EOF
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

# Dépendances Prometheus
for i in $(seq 1 $AUTH_INSTANCES); do
  echo "      - auth_instance_$i" >>$DOCKER_COMPOSE_FILE
done
for i in $(seq 1 $PRODUCT_INSTANCES); do
  echo "      - product_instance_$i" >>$DOCKER_COMPOSE_FILE
done
for i in $(seq 1 $ORDER_INSTANCES); do
  echo "      - order_instance_$i" >>$DOCKER_COMPOSE_FILE
done
for i in $(seq 1 $OTHER_INSTANCES); do
  echo "      - other_instance_$i" >>$DOCKER_COMPOSE_FILE
done

cat >>$DOCKER_COMPOSE_FILE <<EOF

  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: redis-exporter
    ports:
      - "9121:9121"
    environment:
      - REDIS_ADDR=redis://redis-store:6379
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

# 3. Génération de la configuration Nginx
generate_upstream() {
  local service=$1
  local instances=$2
  local lb_method=$3

  echo "upstream ${service}_servers {"
  if [[ "$lb_method" == "rr" ]]; then
    echo "    # Round Robin"
  else
    echo "    least_conn;"
  fi

  for i in $(seq 1 $instances); do
    echo "    server ${service}_instance_$i:8080;"
  done
  echo "}"
}

cat >nginx.conf <<EOF
$(generate_upstream auth $AUTH_INSTANCES $AUTH_LB)

$(generate_upstream product $PRODUCT_INSTANCES $PRODUCT_LB)

$(generate_upstream order $ORDER_INSTANCES $ORDER_LB)

$(generate_upstream other $OTHER_INSTANCES $OTHER_LB)

server {
    listen 80;
    
    location /auth {
        proxy_pass http://auth_servers;
        proxy_set_header Host \$host;
    }

    location /product {
        proxy_pass http://product_servers;
        proxy_set_header Host \$host;
    }

    location /order {
        proxy_pass http://order_servers;
        proxy_set_header Host \$host;
    }

    location / {
        proxy_pass http://other_servers;
        proxy_set_header Host \$host;
    }
}
EOF

# 4. Génération de la configuration Prometheus
log_message "📝 Génération de la configuration Prometheus"
cat >prometheus.yml <<EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'auth_instances'
    static_configs:
      - targets:
EOF
for i in $(seq 1 $AUTH_INSTANCES); do
  echo "          - 'auth_instance_$i:8080'" >>prometheus.yml
done

cat >>prometheus.yml <<EOF

  - job_name: 'product_instances'
    static_configs:
      - targets:
EOF
for i in $(seq 1 $PRODUCT_INSTANCES); do
  echo "          - 'product_instance_$i:8080'" >>prometheus.yml
done

cat >>prometheus.yml <<EOF

  - job_name: 'order_instances'
    static_configs:
      - targets:
EOF
for i in $(seq 1 $ORDER_INSTANCES); do
  echo "          - 'order_instance_$i:8080'" >>prometheus.yml
done

cat >>prometheus.yml <<EOF

  - job_name: 'other_instances'
    static_configs:
      - targets:
EOF
for i in $(seq 1 $OTHER_INSTANCES); do
  echo "          - 'other_instance_$i:8080'" >>prometheus.yml
done

cat >>prometheus.yml <<EOF

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
EOF

# 5. Démarrage des services
log_message "🚀 Démarrage des services"
docker compose up -d $NO_CACHE

# 6. Vérification de Prometheus
log_message "⏳ Vérification du démarrage de Prometheus..."
until curl -s http://localhost:9091/-/ready >/dev/null; do
  sleep 1
done

log_message "🔁 Rechargement de la configuration Prometheus"
curl -X POST http://localhost:9091/-/reload

log_message "✅ Déploiement terminé!"
echo ""
echo "🌐 Accès:"
echo "  - Application: http://localhost"
echo "  - Auth: http://localhost/auth (Instances: $AUTH_INSTANCES)"
echo "  - Products: http://localhost/product (Instances: $PRODUCT_INSTANCES)"
echo "  - Orders: http://localhost/order (Instances: $ORDER_INSTANCES)"
echo "  - Prometheus: http://localhost:9091/targets"
echo "  - Redis Exporter: http://localhost:9121"
