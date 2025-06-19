# ADR Choix de Flask pour l'API

## Statut  
En cours d'implémentation

## Contexte  
Lors du laboratoire 1, la communication entre l'interface utilisateur et la base de données était limitée et directe, avec peu de logique métier côté serveur. Avec l'évolution vers le laboratoire 2, le système doit gérer davantage de règles métier, de validations et d’interactions complexes entre les entités (commandes, produits, magasins, utilisateurs).  
Il fallait un moyen simple, flexible et rapide à mettre en œuvre pour exposer ces fonctionnalités sous forme d’API REST, tout en gardant la maintenance facile et la possibilité d’évolution.

## Décision  
Nous avons décidé d’utiliser Flask comme framework backend pour l’API. Flask est léger, simple à prendre en main, compatible avec SQLAlchemy (notre ORM), et permet de construire des routes REST rapidement et efficacement.  
Cela nous offre un contrôle granulaire sur les requêtes, les réponses, la gestion des erreurs et la sécurité, tout en gardant la possibilité d’étendre ou d’ajouter des fonctionnalités facilement.

## Conséquences  
- L’API est découplée de la couche frontend, facilitant les développements parallèles et la maintenance.  
- Le backend peut évoluer indépendamment, par exemple en ajoutant des authentifications, middlewares, ou en intégrant d’autres services.  
- Flask, grâce à sa simplicité, réduit la complexité de mise en place initiale, ce qui accélère le développement.  
- Le choix impose de gérer manuellement certains aspects (gestion des erreurs, sécurité) mais offre aussi plus de flexibilité.  
- Le projet nécessite un serveur dédié pour héberger cette API, ce qui est pris en compte dans le déploiement via Docker.
