# Lab3_LOG430

## Backend de l'application de gestion de magasins v3

## Documentation
- Rapport disponible en version `.md` dans `./documentation`

# Étapes complètes pour tester démarrer le docker container
- avec le fichier .zip fraichement décompressé (faire `cd ./Lab3`)
- avec git (faire `git clone https://github.com/ErwanDerrien/GestionnaireMagasin.git` puis faire `git checkout Lab3`)
- à partir de la machine virtuelle (faire `cd ./Lab3`) 

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
`pandoc ./documentation/RapportArc42.md -o ./ErwanDerrien-RapportArc42.pdf \ 
--resource-path=.:./out \
--pdf-engine=xelatex \
--listings \
-V urlcolor=blue \
-V geometry:margin=2cm \
-V fontsize=12pt`