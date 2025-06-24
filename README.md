# Lab4_LOG430

## Backend de l'application de gestion de magasins v4

## Documentation

- Rapport disponible en version `.md` dans `./documentation`

# Étapes complètes pour tester démarrer le docker container

- avec le fichier .zip fraichement décompressé (faire `cd ./Lab4`)
- avec git (faire `git clone https://github.com/ErwanDerrien/GestionnaireMagasin.git` puis faire `git checkout Lab4`)
- à partir de la machine virtuelle (faire `cd ./Lab4`)

## Lancer le serveur Flask pour le backend (Docker doit être installé)

- `cd ./docker; docker compose down && docker compose build --no-cache && docker compose up`

## Lire la documentation de l'API (une fois le serveur démarré)

- Aller sur un navigateur à `http://localhost:8080/apidocs/`

## Intéragir avec l'API avec Postman

- Ouvrir Postman
- Importer `StoreManager.postman_collection.json`
- Exécuter `Dev>ResetDatabase` si c'est la première fois que le projet est roulé sur la machine
- Vous pouvez toujours tester la sécurité des endpoints si le login n'est pas fait.
- Exécutez `Dev>Login Success Employee` (ou Manager) pour avoir le jwt nécessaire sauvegardé dans les variables globales de postman.
- Une fois le login fait, les autres endpoints doivent être disponibles

## Exécuter localement les tests de services

- Si ce projet roule à partir du fichier `.zip` ou d'un `git clone` soyez sur d'avoir les dépendences, installez au besoin avec `npm install pytest`. Vous pouvez l'enlever après avec `npm uninstall pytest`
- `pytest tests/`

## Générer le rapport en pdf


`./monitoring/automate_load_tests.sh --repo "after_round_robin_least_con" --filename "round_robin_least_con"`
`./monitoring/automate_load_tests.sh --repo "after_round_robin_least_con" --filename "round_robin_least_con" --skip-tests`
`pandoc ./documentation/RapportArc42.md -o ./ErwanDerrien-RapportArc42.pdf \ 
--resource-path=.:./out \
--pdf-engine=xelatex \
--listings \
-V urlcolor=blue \
-V geometry:margin=2cm \
-V fontsize=12pt`

## Monitoring

Visualiser sur Prometheus :

Mode durée relative :
`python ./monitoring/generate_prometheus_graphs.py \
  --repo "after_round_robin" \
  --filename "round_robin" \
  --duration 40`

Mode plage absolue :
`python ./monitoring/generate_prometheus_graphs.py \
  --repo "prod" \
  --filename "incident_analysis" \
  --start "2024-06-24T13:25:00" \
  --end "2024-06-25T13:45:00"`

Avec dimensions customisées :
`python ./monitoring/generate_prometheus_graphs.py \
  --repo "large_report" \
  --filename "wide_format" \
  --duration 120 \
  --width 20 --height 10`

Pour requests per seconds
- `sum by(path) (
  rate(flask_http_request_duration_seconds_count{instance=~"store_manager.*"}[1m])
)`
Pour mémoire
- `sum by(instance) (process_resident_memory_bytes / 1024 / 1024)`
Pour CPU
- `sum by(instance) (rate(process_cpu_seconds_total[15m]) * 100)`