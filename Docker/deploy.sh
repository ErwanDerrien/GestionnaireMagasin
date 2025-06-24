#!/bin/bash

set -e

INSTANCES=3
NO_CACHE=""
DOCKER_COMPOSE_FILE="docker-compose.yml"
PROMETHEUS_CONFIG="./prometheus.yml"
NGINX_CONFIG="./nginx.conf"
NGINX_UPSTREAM_CONFIG="least_conn"

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
        --config)
            case $2 in
                round_robin|rr)
                    NGINX_UPSTREAM_CONFIG="round_robin"
                    ;;
                least_conn|lc)
                    NGINX_UPSTREAM_CONFIG="least_conn"
                    ;;
                ip_hash|hash)
                    NGINX_UPSTREAM_CONFIG="ip_hash"
                    ;;
                weighted|w)
                    NGINX_UPSTREAM_CONFIG="weighted"
                    ;;
                *)
                    echo "Erreur: Configuration nginx invalide. Options: round_robin|rr, least_conn|lc, ip_hash|hash, weighted|w"
                    exit 1
                    ;;
            esac
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--instances N] [--no-cache] [--config CONFIG]"
            echo ""
            echo "Options:"
            echo "  --instances N     Nombre d'instances (défaut: 3)"
            echo "  --no-cache        Build sans cache Docker"
            echo "  --config CONFIG   Configuration nginx:"
            echo "                      round_robin|rr    - Round Robin (défaut)"
            echo "                      least_conn|lc     - Least Connections"
            echo "                      ip_hash|hash      - IP Hash"
            echo "                      weighted|w        - Weighted Round Robin"
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
log_message "📝 Génération du nginx.conf"

generate_nginx_config() {
    local file="$1"
    local instances="$2"
    local config_type="$3"

    cat > "$file" << 'EOF'
# Configuration générée automatiquement par deploy.sh
# Ne pas modifier manuellement

EOF

    # Générer les différentes configurations upstream
    case $config_type in
        "round_robin")
            cat >> "$file" << EOF
# Configuration Round Robin (par défaut)
upstream store_manager {
EOF
            for i in $(seq 1 $instances); do
                echo "    server store_manager_$i:8080;" >> "$file"
            done
            echo "}" >> "$file"
            ;;
        "least_conn")
            cat >> "$file" << EOF
# Configuration Least Connections
upstream store_manager {
    least_conn;
EOF
            for i in $(seq 1 $instances); do
                echo "    server store_manager_$i:8080;" >> "$file"
            done
            echo "}" >> "$file"
            ;;
        "ip_hash")
            cat >> "$file" << EOF
# Configuration IP Hash
upstream store_manager {
    ip_hash;
EOF
            for i in $(seq 1 $instances); do
                echo "    server store_manager_$i:8080;" >> "$file"
            done
            echo "}" >> "$file"
            ;;
        "weighted")
            cat >> "$file" << EOF
# Configuration Weighted Round Robin
upstream store_manager {
EOF
            for i in $(seq 1 $instances); do
                # Poids décroissant : premier serveur poids le plus élevé
                local weight=$((instances - i + 1))
                echo "    server store_manager_$i:8080 weight=$weight;" >> "$file"
            done
            echo "}" >> "$file"
            ;;
    esac

    cat >> "$file" << 'EOF'

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
}
EOF
}

generate_nginx_config "$NGINX_CONFIG" "$INSTANCES" "$NGINX_UPSTREAM_CONFIG"

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
      - '80:80'
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
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