# Lab0_LOG430

## Instructions

### Compilation, Exécution et Utilisation
#### Du programme seulement
- Ouvrir la console à la racine du projet.
- Activer l'environnement de développement local python avec `source env/bin/activate`
- Exécuter le projet avec la commande `python3 -m src.Controller.store_manager`

#### À l'aide du docker-compose
- Ouvrir la console à la racine du projet.
- Activer l'environnement de développement local python avec `source env/bin/activate`
- Accéder au dossier Docker `cd ./Docker`
- Rouler la commande `docker compose run --rm --service-ports store_manager`
- (Ré)initialiser la BD locale `y`
- Faire les manipulations voulues selon les instructions dans la console.
  

###### Pour ouvrir une autre console qui manipule les mêmes données :
- Ouvrir une nouvelle console à la racine du projet.
- Activer l'environnement de développement local python avec `source env/bin/activate`
- Accéder au dossier Docker `cd ./Docker`
- Rouler la commande `docker ps`
- Copier l'id du de l'image "docker-store_manager"
- Exécuter la commande `docker exec -it <id du container docker-store_manager> bash`
- Ne pas réinitialiser la BD locale `n`
- Faire les manipulations voulues selon les instructions dans la console.

### Compilation

### Test
- Ouvrir la console à la racine du projet.
- Activer l'environnement de développement local python avec `source env/bin/activate`
- Exécuter `python3 -m pytest ./tests/`

## Choix technologiques

### Langage

Python a été choisi pour développer l'application. Comme les exigences sont relativement simples, Python va me permettre de me concentrer sur les autres parties du projet avec lesquelles je suis moins familier.

### Persistance

Pour la persistance j'ai choisi d'utiliser SQLite, car c'est ce qui était recommandé dans l'éconcé. Je tiens à dire que je regrette un peu d'avoir utilisé ça, car c'est une BD qui fonctionne seulement comme un fichier en local. Si j'avais à refaire ce projet, je le referais en prenant dès le départ une BD qui me permet d'avoir un port avec lequel communiquer lorsque mon conteneur Docker est en marche.
