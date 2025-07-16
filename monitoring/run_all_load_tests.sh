#!/bin/bash

cd "$(dirname "$0")/.."

# Fonction d'aide
show_help() {
  echo "Usage: $0 [--resume CONFIG_NAME]"
  echo ""
  echo "Options:"
  echo "  --resume CONFIG_NAME   Reprendre à partir d'une configuration spécifique"
  echo ""
  echo "Configurations disponibles:"
  echo "  uniform_rr, uniform_lc, uniform_hash, uniform_w"
  echo "  mixed_balanced, mixed_performance, mixed_resilient, mixed_high_availability"
  echo "  auth_focused, products_focused, orders_focused, others_focused"
  echo "  all_rr_high, all_lc_high, all_hash_high, all_w_high"
  echo ""
  echo "Exemple:"
  echo "  $0 --resume mixed_performance"
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

  docker compose down --volumes --remove-orphans --timeout 2 >/dev/null 2>&1 || true
  docker rm -f $(docker ps -aq --filter "name=store_manager") 2>/dev/null || true
  docker rm -f $(docker ps -aq --filter "name=nginx") 2>/dev/null || true
  docker rm -f $(docker ps -aq --filter "name=prometheus") 2>/dev/null || true
  docker network prune -f >/dev/null 2>&1
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

# Configurations de test
TEST_CONFIGS=(
  "uniform_rr=--auth 2 rr --products 2 rr --orders 2 rr --others 2 rr"
  "uniform_lc=--auth 2 lc --products 2 lc --orders 2 lc --others 2 lc"
  "uniform_hash=--auth 2 hash --products 2 hash --orders 2 hash --others 2 hash"
  "uniform_w=--auth 2 w --products 2 w --orders 2 w --others 2 w"
  "mixed_balanced=--auth 2 hash --products 3 lc --orders 5 rr --others 2 w"
  "mixed_performance=--auth 3 hash --products 3 hash --orders 3 lc --others 1 rr"
  "mixed_resilient=--auth 2 lc --products 2 lc --orders 3 w --others 3 hash"
  "mixed_high_availability=--auth 4 rr --products 2 hash --orders 4 rr --others 2 lc"
  "auth_focused=--auth 4 hash --products 1 rr --orders 1 rr --others 1 rr"
  "products_focused=--auth 1 rr --products 4 lc --orders 1 rr --others 1 rr"
  "orders_focused=--auth 1 rr --products 1 rr --orders 4 w --others 1 rr"
  "others_focused=--auth 1 rr --products 1 rr --orders 1 rr --others 4 hash"
  "all_rr_high=--auth 5 rr --products 5 rr --orders 5 rr --others 5 rr"
  "all_lc_high=--auth 5 lc --products 5 lc --orders 5 lc --others 5 lc"
  "all_hash_high=--auth 5 hash --products 5 hash --orders 5 hash --others 5 hash"
  "all_w_high=--auth 5 w --products 5 w --orders 5 w --others 5 w"
)

# Paramètres
VUS_LIST=(1 10 50)
DURATION=1
REPO="load_tests"
RESUME_REACHED=false

# Affichage du plan d'exécution
log "📋 Plan d'exécution:"
for entry in "${TEST_CONFIGS[@]}"; do
  CONFIG_NAME="${entry%%=*}"

  if [[ -n "$RESUME_FROM" && "$RESUME_REACHED" == false ]]; then
    if [[ "$CONFIG_NAME" == "$RESUME_FROM" ]]; then
      RESUME_REACHED=true
      echo "  ✅ $CONFIG_NAME (point de reprise)"
    else
      echo "  ⏭️  $CONFIG_NAME (ignoré - reprise prévue)"
    fi
  else
    echo "  ✅ $CONFIG_NAME"
  fi
done

if [[ -n "$RESUME_FROM" ]]; then
  log "🎯 Reprise configurée à partir de: $RESUME_FROM"
fi

# Reset le flag pour la vraie exécution
RESUME_REACHED=false

# Exécution principale
for entry in "${TEST_CONFIGS[@]}"; do
  CONFIG_NAME="${entry%%=*}"
  CONFIG_ARGS="${entry#*=}"

  if [[ -n "$RESUME_FROM" && "$RESUME_REACHED" == false ]]; then
    if [[ "$CONFIG_NAME" == "$RESUME_FROM" ]]; then
      log "🎯 Reprise détectée à partir de: $CONFIG_NAME"
      RESUME_REACHED=true
    else
      log "⏭️  Ignoré: $CONFIG_NAME (reprise prévue à: $RESUME_FROM)"
      continue
    fi
  fi

  force_cleanup

  log "🚀 Déploiement: $CONFIG_NAME avec args: $CONFIG_ARGS"
  (
    cd ./docker
    ./deploy.sh $CONFIG_ARGS
  )
  countdown 10 "⏸️  Pause de 10 sec avant les tests pour laisser les images se stabiliser"

  for VUS in "${VUS_LIST[@]}"; do
    FILE_BASENAME="${CONFIG_NAME}-${VUS}vus-${DURATION}min"
    log "🔥 Test: $FILE_BASENAME"
    ./monitoring/automate_load_tests.sh \
      --repo "$REPO/$CONFIG_NAME" \
      --filename "$FILE_BASENAME" \
      --vus "$VUS" \
      --duration "$DURATION"
  done

  force_cleanup
done

log "✅ Tous les tests sont terminés!"
