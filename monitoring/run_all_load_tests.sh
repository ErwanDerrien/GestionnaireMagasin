#!/bin/bash

cd "$(dirname "$0")/.."

# Définition de la fonction countdown avant toute utilisation
countdown() {
  local seconds=$1
  local message=$2

  if [[ -n "$message" ]]; then
    log "$message"
  fi

  for ((i=seconds; i>0; i--)); do
    printf "\r⏳ Pause en cours... %d secondes restantes" "$i"
    sleep 1
  done
  printf "\r✅ Pause terminée!                              \n"
}

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

CONFIGS=("rr" "lc" "hash" "w")
INSTANCES_LIST=(1 5 25)
VUS_LIST=(1)
DURATIONS=(1) # minutes
REPO="load_tests"
NOW=$(date +"%Y%m%d_%H%M%S")

for CONFIG in "${CONFIGS[@]}"; do
  for INSTANCES in "${INSTANCES_LIST[@]}"; do
    CONFIG_NAME="${CONFIG}_${INSTANCES}_instances"
    
    log "🚀 Déploiement: config=$CONFIG, instances=$INSTANCES"
    ./docker/deploy.sh --instances "$INSTANCES" --config "$CONFIG"

    countdown 30 "⏸️  Pause de 30 sec avant les tests"

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

    log "🧹 Nettoyage containers"
    docker compose down
    sleep 5
  done
done

log "✅ Tous les tests sont terminés!"
