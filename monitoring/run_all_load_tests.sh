#!/bin/bash

cd "$(dirname "$0")/.."

# Fonctions utilitaires
countdown() {
  local seconds=$1
  local message=$2
  [[ -n "$message" ]] && log "$message"
  for ((i = seconds; i > 0; i--)); do
    printf "\r⏳ Pause en cours... %d secondes restantes" "$i"
    sleep 1
  done
  printf "\r✅ Pause terminée! %-20s\n" ""
}

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

force_cleanup() {
  log "🧹 Nettoyage agressif des containers"

  # 1. Arrêt des services avec compose
  docker compose down --volumes --remove-orphans --timeout 2 >/dev/null 2>&1 || true

  # 2. Suppression forcée des containers résiduels
  docker rm -f $(docker ps -aq --filter "name=store_manager") 2>/dev/null || true
  docker rm -f $(docker ps -aq --filter "name=nginx") 2>/dev/null || true
  docker rm -f $(docker ps -aq --filter "name=prometheus") 2>/dev/null || true

  # 3. Nettoyage réseau
  docker network prune -f >/dev/null 2>&1

  # 4. Suppression des fichiers
  rm -f ./docker-compose.yml ./nginx.conf ./prometheus.yml

  sleep 3
}

# Configuration des tests
CONFIGS=("rr" "lc" "hash" "w")
INSTANCES_LIST=(1 5 10 15)
VUS_LIST=(1 10 50)
DURATIONS=(1)
REPO="load_tests"

# Execution principale
for CONFIG in "${CONFIGS[@]}"; do
  for INSTANCES in "${INSTANCES_LIST[@]}"; do
    CONFIG_NAME="${CONFIG}_${INSTANCES}_instances"

    force_cleanup

    log "🚀 Déploiement: config=$CONFIG, instances=$INSTANCES"
    (
      cd ./docker
      ./deploy.sh --instances "$INSTANCES" --config "$CONFIG"
    )
    countdown 10 "⏸️  Pause de 10 sec avant les tests pour laisser les images se stabiliser"

    for VUS in "${VUS_LIST[@]}"; do
      for MIN in "${DURATIONS[@]}"; do
        FILE_BASENAME="${CONFIG_NAME}-${VUS}vus-${MIN}min"
        log "🔥 Test: $FILE_BASENAME"
        ./monitoring/automate_load_tests.sh \
          --repo "$REPO/$CONFIG_NAME" \
          --filename "$FILE_BASENAME" \
          --vus "$VUS" \
          --duration "$MIN"
      done
    done

    force_cleanup
  done
done

log "✅ Tous les tests sont terminés!"
