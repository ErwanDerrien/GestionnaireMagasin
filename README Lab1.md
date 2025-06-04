# Lab1_LOG430

## Instuctions d'exécution

- Ouvrir la console à la racine du projet.
- Activer l'environnement de développement local python avec `source env/bin/activate`
- Accéder au dossier Docker `cd ./Docker`
- Rouler la commande `docker compose run --rm --service-ports store_manager`
- (Ré)initialiser la BD locale `y`
- Faire les manipulations voulues selon les instructions dans la console.
  
Pour ouvrir une autre console qui manipule les mêmes données :
- Ouvrir une nouvelle console à la racine du projet.
- Activer l'environnement de développement local python avec `source env/bin/activate`
- Accéder au dossier Docker `cd ./Docker`
- Rouler la commande `docker ps`
- Copier l'id du de l'image "docker-store_manager"
- Exécuter la commande `docker exec -it <id du container docker-store_manager> bash`
- Ne pas réinitialiser la BD locale `n`
- Faire les manipulations voulues selon les instructions dans la console.

## Instructions de tests

- Ouvrir la console à la racine du projet.
- Activer l'environnement de développement local python avec `source env/bin/activate`
- Exécuter `python3 -m pytest ./tests/`