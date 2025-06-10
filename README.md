# Lab2_LOG430

## Backend de l'application de gestion de magasins

## Rapport disponible
- En version `.md` dans `./Lab2_LOG430/docs_lab2`

# Étapes complètes pour tester le logiciel sur un navigateur à partir du fichier .zip fraichement décompressé

- Ouvrir un teminal
## Lancer le serveur Flask pour le backend ?
- `cd ./Lab2_LOG430/Docker`
- `docker compose down && docker compose build --no-cache && docker compose up`

- Ouvrir nouveau teminal
## Exécuter les tests
- `cd ./Lab2_LOG430`
- `pytest tests/`