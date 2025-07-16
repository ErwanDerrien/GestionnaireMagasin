#!/bin/bash

# Script d'automatisation des tests de charge K6 avec génération de rapport
# Usage: ./automate_load_tests.sh --repo "nom_repo" --filename "nom_fichier" [--vus nombre_users] [--duration minutes]

# Valeurs par défaut
VUS=10
REPO=""
FILENAME=""
SKIP_TESTS=false
DURATION=1 # Durée en minutes par défaut

# Parser les arguments
while [[ $# -gt 0 ]]; do
    case $1 in
    --repo)
        REPO="$2"
        shift 2
        ;;
    --filename)
        FILENAME="$2"
        shift 2
        ;;
    --vus)
        VUS="$2"
        shift 2
        ;;
    --skip-tests)
        SKIP_TESTS=true
        shift
        ;;
    --duration)
        DURATION="$2"
        shift 2
        ;;
    -h | --help)
        echo "Usage: $0 --repo REPO_NAME --filename FILENAME [--vus VUS_COUNT] [--duration MINUTES] [--skip-tests]"
        exit 0
        ;;
    *)
        echo "Argument inconnu: $1"
        exit 1
        ;;
    esac
done

if [[ -z "$REPO" || -z "$FILENAME" ]]; then
    echo "Erreur: --repo et --filename sont requis"
    exit 1
fi

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

countdown() {
    local seconds=$1
    local message=$2
    log_message "$message"
    for ((i = seconds; i > 0; i--)); do
        printf "\r⏳ Pause en cours... %d secondes restantes" $i
        sleep 1
    done
    printf "\r✅ Pause terminée!                              \n"
}

# Définir les timestamps
if [ "$SKIP_TESTS" = true ]; then
    END_TIME=$(date +"%Y-%m-%dT%H:%M:%S")
    if [[ "$OSTYPE" == "darwin"* ]]; then
        START_TIME=$(date -v-${DURATION}M +"%Y-%m-%dT%H:%M:%S")
    else
        START_TIME=$(date -d "${DURATION} minutes ago" +"%Y-%m-%dT%H:%M:%S")
    fi
    log_message "⏭️  Mode skip-tests activé"
    log_message "📊 Génération du rapport pour les $DURATION dernières minutes"
    log_message "⏰ Période analysée: $START_TIME à $END_TIME (heure locale)"
else
    START_TIME=$(date +"%Y-%m-%dT%H:%M:%S")
    log_message "🚀 Début des tests de charge automatisés"
    log_message "📊 Configuration: $VUS utilisateurs virtuels pendant ${DURATION}min"
    log_message "⏰ Heure de début: $START_TIME"
fi

log_message "📁 Rapport: $REPO/$FILENAME"
echo ""

if [ "$SKIP_TESTS" = false ]; then
    countdown 30 "⏸️  Pause de 30 sec avant"
    echo ""
    log_message "🔥 Lancement du test (${DURATION} minute(s))"
    if ! k6 run --vus "$VUS" --duration "${DURATION}m" monitoring/load_test.js; then
        log_message "⚠️  Erreur durant le test K6, mais le script continue"
    fi
    log_message "✅ Test terminé"
    countdown 30 "⏸️  Pause de 30 sec après"
    echo ""
    END_TIME=$(date +"%Y-%m-%dT%H:%M:%S")
fi

log_message "📈 Génération du rapport Prometheus..."
log_message "⏰ Période: $START_TIME à $END_TIME"

PYTHON_CMD=""
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    log_message "❌ Python non trouvé"
    exit 1
fi

TEMP_VENV="temp_report_env"
log_message "🐍 Création venv temporaire..."
$PYTHON_CMD -m venv $TEMP_VENV

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    source $TEMP_VENV/Scripts/activate
else
    source $TEMP_VENV/bin/activate
fi

log_message "📦 Installation des dépendances Python..."
pip install --quiet matplotlib python-dateutil requests

log_message "📊 Exécution du script de génération de rapport..."
$PYTHON_CMD ./monitoring/generate_prometheus_graphs.py \
    --repo "$REPO" \
    --filename "$FILENAME" \
    --start "$START_TIME" \
    --end "$END_TIME" \
    --width 14 \
    --height 16

deactivate
rm -rf $TEMP_VENV

PDF_PATH="documentation/monitoring/$REPO/$FILENAME.pdf"
if [[ -f "$PDF_PATH" ]]; then
    log_message "✅ PDF généré avec succès: $PDF_PATH"
else
    log_message "⚠️  PDF non trouvé à l'emplacement attendu: $PDF_PATH"
fi

log_message "🎉 Script terminé avec succès"
echo ""
echo "📋 Résumé:"
if [ "$SKIP_TESTS" = true ]; then
    echo "   • Mode: Rapport des $DURATION dernières minutes (tests non exécutés)"
else
    echo "   • Tests effectués: 1 (${DURATION}min)"
    echo "   • Utilisateurs virtuels: $VUS"
    echo "   • Durée totale: ~${DURATION} minute(s)"
fi
echo "   • Rapport: $PDF_PATH"
echo "   • Période: $START_TIME → $END_TIME"
