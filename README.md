# Lab3_LOG430

## Backend de l'application de gestion de magasins v3

## Documentation
- Rapport disponible en version `.md` dans `./documentation`

# Étapes complètes pour tester démarrer le docker container
- avec le fichier .zip fraichement décompressé (faire `cd ./Lab3`)
- avec git (faire `git clone https://github.com/ErwanDerrien/GestionnaireMagasin.git` puis faire `git checkout Lab3`)
- à partir de la machine virtuelle (faire `cd ./Lab3`) 

## Lancer le serveur Flask pour le backend ?
- `cd ./docker; docker compose down && docker compose build --no-cache && docker compose up`

## Exécuter localement les tests de services
- Si ce projet roule à partir du fichier `.zip` ou d'un `git clone` soyez sur d'avoir les dépendences, installez au besoin avec `npm install pytest`. Vous pouvez l'enlever après avec `npm uninstall pytest`
- `pytest tests/`
