#!/bin/bash

# Fonction pour charger les variables depuis le fichier JSON
load_variables() {
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local json_file="$script_dir/universal_variables.json"
    
    if [[ ! -f "$json_file" ]]; then
        echo "Erreur: Fichier universal_variables.json non trouvé" >&2
        return 1
    fi
    
    # Utiliser jq pour parser le JSON (installer avec: apt install jq ou brew install jq)
    if command -v jq &> /dev/null; then
        export HOST=$(jq -r '.host' "$json_file")
        export APP_PORT=$(jq -r '.app_port' "$json_file")
        export API_MASK=$(jq -r '.api_mask' "$json_file")
        export VERSION=$(jq -r '.version' "$json_file")
        export PROMETHEUS_PORT=$(jq -r '.prometheus_port' "$json_file")
        export REDIS_PORT=$(jq -r '.redis_port' "$json_file")
        export REDIS_EXPORTER_PORT=$(jq -r '.redis_exporter_port' "$json_file")
        export AUTH_SERVICE=$(jq -r '.auth_service' "$json_file")
        export PRODUCTS_SERVICE=$(jq -r '.products_service' "$json_file")
        export ORDERS_SERVICE=$(jq -r '.orders_service' "$json_file")
    else
        # Fallback sans jq (parsing basique)
        export HOST=$(grep -o '"host"[[:space:]]*:[[:space:]]*"[^"]*"' "$json_file" | cut -d'"' -f4)
        export APP_PORT=$(grep -o '"app_port"[[:space:]]*:[[:space:]]*"[^"]*"' "$json_file" | cut -d'"' -f4)
        export API_MASK=$(grep -o '"api_mask"[[:space:]]*:[[:space:]]*"[^"]*"' "$json_file" | cut -d'"' -f4)
        export VERSION=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' "$json_file" | cut -d'"' -f4)
        export PROMETHEUS_PORT=$(grep -o '"prometheus_port"[[:space:]]*:[[:space:]]*"[^"]*"' "$json_file" | cut -d'"' -f4)
        export REDIS_PORT=$(grep -o '"redis_port"[[:space:]]*:[[:space:]]*"[^"]*"' "$json_file" | cut -d'"' -f4)
        export REDIS_EXPORTER_PORT=$(grep -o '"redis_exporter_port"[[:space:]]*:[[:space:]]*"[^"]*"' "$json_file" | cut -d'"' -f4)
        export AUTH_SERVICE=$(grep -o '"auth_service"[[:space:]]*:[[:space:]]*"[^"]*"' "$json_file" | cut -d'"' -f4)
        export PRODUCTS_SERVICE=$(grep -o '"products_service"[[:space:]]*:[[:space:]]*"[^"]*"' "$json_file" | cut -d'"' -f4)
        export ORDERS_SERVICE=$(grep -o '"orders_service"[[:space:]]*:[[:space:]]*"[^"]*"' "$json_file" | cut -d'"' -f4)
    fi
}

# Charger les variables automatiquement
load_variables

# Usage:
# source ./variables.sh
# echo $HOST  # "localhost"
# echo $APP_PORT  # "8080"
# echo $API_MASK  # "api"
# echo $VERSION  # "v2"
# echo $PROMETHEUS_PORT  # "9091"
# echo $REDIS_PORT  # "6379"
# echo $REDIS_EXPORTER_PORT  # "9121"
# echo $AUTH_SERVICE  # "auth/a"
# echo $PRODUCTS_SERVICE  # "products"
# echo $ORDERS_SERVICE  # "orders"
