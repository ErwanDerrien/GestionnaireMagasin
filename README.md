# Lab5_LOG430

## Backend de l'application de gestion de magasins v4

Documentation technique pour cette version du laboratoire disponible dans ce README.md. Cette documentation est en partie pour des personnes voulant utiliser et tester cette application. Il y a des commandes qui sont utiles pour le développement de l'application et servent de référence durant l'avancement du projet.

Le rapport de l'étape 2 se trouve à la racine.

La documentation de load tests est disponible dans le répertoire `documentation/monitoring` sous forme de pdfs.

## Installation et démarrage

### Méthodes d'installation

1. Via fichier ZIP :
```bash
cd ./Lab5
```

2. Via Git :
```bash
git clone https://github.com/ErwanDerrien/GestionnaireMagasin.git
cd GestionnaireMagasin
git checkout Lab5
```

### Lancement du serveur Flask avec Docker

Prérequis : Docker doit être installé

Configuration du load balancing :
```bash
cd ./docker
colima start
./deploy.sh --instances 5 --config least_conn
```

Seulement une instance
```bash
cd ./docker
docker compose down && docker compose build --no-cache && docker compose up
```

## Documentation et tests API

### Documentation interactive

Accéder à la documentation Swagger :
```
http://localhost:8080/apidocs/
```

### Tests avec Postman

1. Importer la collection : `StoreManager.postman_collection.json`
2. Exécuter dans l'ordre :
   - `Dev > ResetDatabase` (pour l'initialisation)
   - `Dev > Login Success Employee` (ou Manager) pour obtenir le JWT
3. Les autres endpoints deviennent accessibles après authentification

### Tests unitaires locaux

Pour les installations manuelles (ZIP ou git clone) :

```bash
npm install pytest  # Si nécessaire
pytest tests/
npm uninstall pytest  # Optionnel après utilisation
```

## Génération de rapports

### Commandes pour les tests de charge

Aide sur les options :
```bash
./monitoring/automate_load_tests.sh --help
```

Exemples d'utilisation :
```bash
./monitoring/run_all_load_tests.sh

./monitoring/automate_load_tests.sh --repo "after_round_robin_least_con" --filename "round_robin_least_con" --vus 15
./monitoring/automate_load_tests.sh --repo "after_round_robin_least_con" --filename "round_robin_least_con" --vus 50
./monitoring/automate_load_tests.sh --repo "after_round_robin_least_con" --filename "round_robin_least_con" --vus 500
./monitoring/automate_load_tests.sh --repo "after_round_robin_least_con" --filename "round_robin_least_con" --skip-tests
```

### Génération de PDF

Rapport Arc42 :
```bash
pandoc ./documentation/RapportArc42.md -o ./ErwanDerrien-RapportArc42.pdf \
--resource-path=.:./out \
--pdf-engine=xelatex \
--listings \
-V urlcolor=blue \
-V geometry:margin=2cm \
-V fontsize=12pt
```

Rapport d'étude de cas :
```bash
(cd ./Rapport && pandoc "RapportEtudeDeCas.md" -o "../ErwanDerrien-RapportEtudeDeCas.pdf" \
--resource-path=".:../out")
```

## Monitoring

### Tests de charge avec k6

```bash
k6 run --vus 10 --duration 1m monitoring/load_test.js
```

### Visualisation avec Prometheus

Mode durée relative :
```bash
python ./monitoring/generate_prometheus_graphs.py \
  --repo "after_round_robin" \
  --filename "round_robin" \
  --duration 40
```

Mode plage absolue :
```bash
python ./monitoring/generate_prometheus_graphs.py \
  --repo "prod" \
  --filename "incident_analysis" \
  --start "2024-06-24T13:25:00" \
  --end "2024-06-25T13:45:00"
```

Dimensions personnalisées :
```bash
python ./monitoring/generate_prometheus_graphs.py \
  --repo "large_report" \
  --filename "wide_format" \
  --duration 120 \
  --width 20 --height 10
```

### Requêtes Prometheus utiles

Requêtes par seconde :
```promql
sum by(path) (
  rate(flask_http_request_duration_seconds_count{instance=~"store_manager.*"}[1m])
)
```

Utilisation mémoire :
```promql
sum by(instance) (process_resident_memory_bytes / 1024 / 1024)
```

Utilisation CPU :
```promql
sum by(instance) (rate(process_cpu_seconds_total[15m]) * 100)
```

### Mettre à jour les variables globales
1. Mettre une nouvelle entrée dans universal_variables.json
2. Exécuter `python ./config/update_variables.py` à partir de la racine