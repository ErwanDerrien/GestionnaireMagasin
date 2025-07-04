#!/bin/bash

cd "$(dirname "$0")/.."

# Fonction d'aide
show_help() {
  echo "Usage: $0 [--resume CONFIG_INSTANCES]"
  echo ""
  echo "Options:"
  echo "  --resume CONFIG_INSTANCES   Reprendre à partir d'une configuration spécifique"
  echo "                              Format: CONFIG_INSTANCES (ex: hash_15)"
  echo ""
  echo "Configurations disponibles:"
  echo "  rr_1, rr_5, rr_10, rr_15"
  echo "  lc_1, lc_5, lc_10, lc_15"
  echo "  hash_1, hash_5, hash_10, hash_15"
  echo "  w_1, w_5, w_10, w_15"
  echo ""
  echo "Exemple:"
  echo "  $0 --resume hash_15"
  exit 0
}

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

# Parse des arguments
RESUME_FROM=""
while [[ $# -gt 0 ]]; do
  case $1 in
  --resume)
    RESUME_FROM="$2"
    shift 2
    ;;
  -h | --help)
    show_help
    ;;
  *)
    echo "Argument inconnu: $1"
    show_help
    ;;
  esac
done

# Configuration des tests
CONFIGS=("rr" "lc" "hash" "w")
INSTANCES_LIST=(1 5 10 15)
VUS_LIST=(1 10 50)
DURATIONS=(1)
REPO="load_tests"

# Variable pour marquer si on a atteint le point de reprise
RESUME_REACHED=false

# Fonction pour vérifier si on doit reprendre à partir d'une config
should_skip() {
  local current_config="$1"
  local current_instances="$2"
  local current_key="${current_config}_${current_instances}"

  if [[ -z "$RESUME_FROM" ]]; then
    return 1 # Ne pas ignorer, exécuter
  fi

  if [[ "$current_key" == "$RESUME_FROM" ]]; then
    log "🎯 Reprise détectée à partir de: $current_key"
    RESUME_REACHED=true
    return 1 # Ne pas ignorer cette config
  fi

  if [[ "$RESUME_REACHED" == false ]]; then
    log "⏭️  Ignoré: $current_key (reprise prévue à: $RESUME_FROM)"
    return 0 # Ignorer cette config
  fi

  return 1 # Ne pas ignorer
}

# Affichage du plan d'exécution
log "📋 Plan d'exécution:"
TEMP_RESUME_REACHED=false
for CONFIG in "${CONFIGS[@]}"; do
  for INSTANCES in "${INSTANCES_LIST[@]}"; do
    CONFIG_NAME="${CONFIG}_${INSTANCES}_instances"
    CONFIG_KEY="${CONFIG}_${INSTANCES}"

    if [[ -n "$RESUME_FROM" && "$CONFIG_KEY" == "$RESUME_FROM" ]]; then
      TEMP_RESUME_REACHED=true
    fi

    if [[ -z "$RESUME_FROM" || "$TEMP_RESUME_REACHED" == true ]]; then
      echo "  ✅ $CONFIG_KEY"
    else
      echo "  ⏭️  $CONFIG_KEY (ignoré - reprise prévue)"
    fi
  done
done

if [[ -n "$RESUME_FROM" ]]; then
  log "🎯 Reprise configurée à partir de: $RESUME_FROM"
fi

# Execution principale
for CONFIG in "${CONFIGS[@]}"; do
  for INSTANCES in "${INSTANCES_LIST[@]}"; do
    CONFIG_NAME="${CONFIG}_${INSTANCES}_instances"
    CONFIG_KEY="${CONFIG}_${INSTANCES}"

    # Vérifier si on doit ignorer cette configuration
    if [[ -n "$RESUME_FROM" && "$RESUME_REACHED" == false ]]; then
      if [[ "$CONFIG_KEY" == "$RESUME_FROM" ]]; then
        log "🎯 Reprise détectée à partir de: $CONFIG_KEY"
        RESUME_REACHED=true
      else
        log "⏭️  Ignoré: $CONFIG_KEY (reprise prévue à: $RESUME_FROM)"
        continue
      fi
    fi

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
