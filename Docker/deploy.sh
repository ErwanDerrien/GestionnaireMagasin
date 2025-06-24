#!/bin/bash

set -e

INSTANCES=3
NO_CACHE=""
DOCKER_COMPOSE_FILE="docker-compose.yml"
PROMETHEUS_CONFIG="./prometheus.yml"

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
        -h|--help)
            echo "Usage: $0 [--instances N] [--no-cache]"
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

log_message "🚀 Déploiement avec $INSTANCES instance(s) store_manager"
log_message "📝 Génération du docker-compose.yml"

generate_docker_compose() {
    local file="$1"
    local instances="$2"

    cat > "$file" << EOF
version: '3.8'

services:
EOF

    for i in $(seq 1 $instances); do
        cat >> "$file" << EOF
  store_manager_$i:
    build:
      context: ../
      dockerfile: ./docker/Dockerfile
    command: python -m src.controller.app
    volumes:
      - ../:/app
    environment:
      - INSTANCE_NUM=$i
      - PROMETHEUS_METRICS_PORT=8080
    ports:
      - "$((8080 + i)):8080"
    networks:
      - monitoring_net
    container_name: store_manager_$i

EOF
    done

    cat >> "$file" << EOF
  nginx:
    image: nginx:alpine
    ports:
      - '80:8080'
    command: >
      /bin/sh -c "echo -e \"
        upstream store_manager {
          least_conn;
EOF

    for i in $(seq 1 $instances); do
        echo "          server store_manager_$i:8080 max_fails=3 fail_timeout=30s;" >> "$file"
    done

    cat >> "$file" << 'EOF'
        }
        server {
          listen 80;
          location / {
            proxy_pass http://store_manager_lc;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
            proxy_buffering off;
          }
          location /health {
            proxy_pass http://store_manager_lc;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
          }
          location /metrics {
            proxy_pass http://store_manager_lc_1:8080/metrics;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
          }
        }\" > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"
    depends_on:
EOF

    for i in $(seq 1 $instances); do
        echo "      - store_manager_$i" >> "$file"
    done

    cat >> "$file" << 'EOF'
    networks:
      - monitoring_net
    container_name: nginx

  prometheus:
    image: prom/prometheus:latest
    ports:
      - '9091:9090'
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--log.level=debug'
    networks:
      - monitoring_net
    container_name: prometheus
    depends_on:
EOF

    for i in $(seq 1 $instances); do
        echo "      - store_manager_$i" >> "$file"
    done

    cat >> "$file" << 'EOF'

networks:
  monitoring_net:
    driver: bridge

volumes:
  grafana_data:
EOF
}

generate_docker_compose "$DOCKER_COMPOSE_FILE" "$INSTANCES"

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

cat > "$PROMETHEUS_CONFIG" << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'store_managers'
    static_configs:
      - targets: [$PROMETHEUS_TARGETS]
EOF

log_message "✅ Fichiers de configuration générés"

log_message "🔍 Validation du docker-compose.yml"
if command -v docker-compose &> /dev/null; then
    docker-compose -f "$DOCKER_COMPOSE_FILE" config > /dev/null && \
    log_message "✅ docker-compose.yml valide" || \
    { log_message "❌ Erreur dans docker-compose.yml:"; docker-compose -f "$DOCKER_COMPOSE_FILE" config; exit 1; }
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    docker compose -f "$DOCKER_COMPOSE_FILE" config > /dev/null && \
    log_message "✅ docker-compose.yml valide" || \
    { log_message "❌ Erreur dans docker-compose.yml:"; docker compose -f "$DOCKER_COMPOSE_FILE" config; exit 1; }
else
    log_message "⚠️  Impossible de valider le YAML (docker-compose non trouvé)"
fi

log_message "🛑 Arrêt des conteneurs existants"
docker compose down || true

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
sleep 5

log_message "📊 État des conteneurs:"
docker compose ps

log_message "✅ Déploiement terminé!"
echo ""
echo "🌐 Services disponibles:"
echo "   • Application (Load Balancer): http://localhost"
echo "   • Prometheus: http://localhost:9091"
echo ""
echo "🔧 Instances store_manager:"
for i in $(seq 1 $INSTANCES); do
    echo "   • store_manager_$i: http://localhost:$((8080 + i))"
done