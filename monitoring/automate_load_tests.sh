#!/bin/bash

# Script d'automatisation des tests de charge K6 avec génération de rapport
# Usage: ./automate_load_tests.sh --repo "nom_repo" --filename "nom_fichier" [--vus nombre_users]

set -e  # Arrêter le script en cas d'erreur

# Valeurs par défaut
VUS=10
REPO=""
FILENAME=""
SKIP_TESTS=false

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
        -h|--help)
            echo "Usage: $0 --repo REPO_NAME --filename FILENAME [--vus VUS_COUNT] [--skip-tests]"
            echo ""
            echo "Options:"
            echo "  --repo         Nom du repository pour le rapport (obligatoire)"
            echo "  --filename     Nom du fichier pour le rapport (obligatoire)"
            echo "  --vus          Nombre d'utilisateurs virtuels (défaut: 10)"
            echo "  --skip-tests   Skip les tests et génère un rapport des 30 dernières minutes"
            echo "  -h, --help     Afficher cette aide"
            echo ""
            echo "Exemples:"
            echo "  $0 --repo \"after_round_robin\" --filename \"round_robin\" --vus 15"
            echo "  $0 --repo \"current_data\" --filename \"last_30min\" --skip-tests"
            exit 0
            ;;
        *)
            echo "Argument inconnu: $1"
            echo "Utilisez -h ou --help pour voir l'aide"
            exit 1
            ;;
    esac
done

# Vérifier que les paramètres obligatoires sont fournis
if [[ -z "$REPO" || -z "$FILENAME" ]]; then
    echo "Erreur: Les paramètres --repo et --filename sont obligatoires"
    echo "Utilisez -h ou --help pour voir l'aide"
    exit 1
fi

# Fonction pour afficher un message avec timestamp
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Fonction pour attendre avec compte à rebours
countdown() {
    local seconds=$1
    local message=$2
    
    log_message "$message"
    for ((i=seconds; i>0; i--)); do
        printf "\r⏳ Pause en cours... %d secondes restantes" $i
        sleep 1
    done
    printf "\r✅ Pause terminée!                              \n"
}

# Stocker l'heure de début
if [ "$SKIP_TESTS" = true ]; then
    # Calculer les 30 dernières minutes en heure locale
    END_TIME=$(date +"%Y-%m-%dT%H:%M:%S")
    
    # Détecter l'OS pour utiliser la bonne syntaxe de date
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - heure locale
        START_TIME=$(date -v-30M +"%Y-%m-%dT%H:%M:%S")
    else
        # Linux - heure locale
        START_TIME=$(date -d '30 minutes ago' +"%Y-%m-%dT%H:%M:%S")
    fi
    
    log_message "⏭️  Mode skip-tests activé"
    log_message "📊 Génération du rapport pour les 30 dernières minutes"
    log_message "⏰ Période analysée: $START_TIME à $END_TIME (heure locale)"
else
    START_TIME=$(date +"%Y-%m-%dT%H:%M:%S")
    
    log_message "🚀 Début des tests de charge automatisés"
    log_message "📊 Configuration: $VUS utilisateurs virtuels"
    log_message "⏰ Heure de début: $START_TIME (heure locale)"
fi

log_message "📁 Rapport: $REPO/$FILENAME"
echo ""

if [ "$SKIP_TESTS" = false ]; then
    # TODO config de gestion de param
    # # Test 1: 5 minutes
    # log_message "🔥 Lancement du test 1/3 (5 minutes)"
    # k6 run --vus $VUS --duration 5m monitoring/load_test.js
    # log_message "✅ Test 1/3 terminé"
    # echo ""

    # # Pause 1 minute
    # countdown 60 "⏸️  Pause de 1 minute avant le test 2/3"
    # echo ""

    # Test 2: 3 minutes
    log_message "🔥 Lancement du test 2/3 (3 minutes)"
    k6 run --vus $VUS --duration 3m monitoring/load_test.js
    log_message "✅ Test 2/3 terminé"
    echo ""

    # Pause 1 minute
    countdown 60 "⏸️  Pause de 1 minute avant le test 3/3"
    echo ""

    # Test 3: 1 minute
    log_message "🔥 Lancement du test 3/3 (1 minute)"
    k6 run --vus $VUS --duration 1m monitoring/load_test.js
    log_message "✅ Test 3/3 terminé"
    echo ""

    # Stocker l'heure de fin pour les tests
    END_TIME=$(date +"%Y-%m-%dT%H:%M:%S")
fi

log_message "📈 Génération du rapport Prometheus..."
if [ "$SKIP_TESTS" = false ]; then
    log_message "⏰ Période analysée: $START_TIME à $END_TIME (heure locale)"
fi

# Détecter la commande Python disponible
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    log_message "❌ Erreur: Ni 'python' ni 'python3' n'ont été trouvés"
    log_message "📋 Veuillez installer Python ou vérifier votre PATH"
    exit 1
fi

# Créer un environnement virtuel temporaire
TEMP_VENV="temp_report_env"
log_message "🐍 Création de l'environnement Python temporaire..."

$PYTHON_CMD -m venv $TEMP_VENV

# Activer l'environnement virtuel
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source $TEMP_VENV/Scripts/activate
else
    # Linux/macOS
    source $TEMP_VENV/bin/activate
fi

# Installer les dépendances
log_message "📦 Installation des dépendances Python..."
pip install --quiet matplotlib python-dateutil requests

# Générer le rapport
log_message "📊 Exécution du script de génération de rapport..."
python ./monitoring/generate_prometheus_graphs.py \
    --repo "$REPO" \
    --filename "$FILENAME" \
    --start "$START_TIME" \
    --end "$END_TIME"

# Désactiver l'environnement virtuel
deactivate

# Supprimer l'environnement virtuel temporaire
log_message "🗑️  Suppression de l'environnement temporaire..."
rm -rf $TEMP_VENV

# Vérifier si le PDF a été généré
PDF_PATH="documentation/monitoring/$REPO/$FILENAME.pdf"
if [[ -f "$PDF_PATH" ]]; then
    log_message "✅ PDF généré avec succès: $PDF_PATH"
else
    log_message "⚠️  Attention: Le PDF n'a pas été trouvé à l'emplacement attendu: $PDF_PATH"
fi

log_message "🎉 Automatisation terminée avec succès!"
echo ""
if [ "$SKIP_TESTS" = true ]; then
    echo "📋 Résumé:"
    echo "   • Mode: Rapport des 30 dernières minutes (tests skippés)"
    echo "   • Période analysée: $START_TIME → $END_TIME (heure locale)"
    echo "   • Rapport: $PDF_PATH"
else
    echo "📋 Résumé:"
    echo "   • Tests effectués: 3 (5min + 3min + 1min)"
    echo "   • Utilisateurs virtuels: $VUS"
    echo "   • Durée totale: ~11 minutes (tests + pauses)"
    echo "   • Rapport: $PDF_PATH"
    echo "   • Période: $START_TIME → $END_TIME (heure locale)"
fi