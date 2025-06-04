# Analyse des besoins

## Besoins fonctionnels

- Gérer les commandes prise en compte par la structure
  - Rechercher un produit
  - Créer une vente
    - Avec un ou plusieurs produits
    - Calcul du montant total
    - Enregristrement de la vente
  - Gérer les retours
  - Consulter l'état du stock des produits
- Gérer les commandes inconnues

## Besoins non fonctionnels

- Persistance locale des données avec base de données (ex : SQLite)
- Fiabilité via gestion transactionnelle (ventes et retours atomiques)
- Interface console simple, réactive et tolérante aux erreurs
- Couverture de test automatisée (tests unitaires)
- Linting automatique du code
- CI/CD :
  - Tests et lint à chaque commit/push
  - Build et publication Docker sur Docker Hub
- Portabilité multiplateforme via conteneur Docker
