# Analuse et Continuité

## Solutions développées aux labs 0 et 1

## Éléments à ...

### Conserver

Je veux conserver la séparation actuelle du traitement de l'info (MVC + services)

### Modifier

Je veux modifier la structure dont l'information est sauvegardée sur la base de donnée pour permettre l'expension du scope.
Je veux changer la manière dont la base de donnée est accédée. Actuellement l'interaction avec les services se fait à partir du terminal, je veux modifier ça pour que ce soit à partir d'une api reste que on peut accéder aux données.

### Refactorer

Je veux changer l'inerface pour permettre à un nouvel utilisateur de :

- Démarrer l'application
- Se connecter
- En tant qu'employé
  - Rechercher des produits
  - Enregistrer des commandes
  - Réapprovisionner son magasin
- En tant que gestionnaire
  - Consulter les statistiques
  - Voir toutes les informations de tous les magasins

## Nouveau/elles

### Exigences

- La personne qui va configurer les caisses peut sélectionner dans quel magasin il est, mais il ne peut pas indiquer qu'il est dans la maison mère.
- Les employés qui vont utiliser le programme ne peuvent que utiliser la caisse, ils n'ont pas accès
- Les administrateurs peuvent utiliser le programme soit pour se connecter à un des trois magasins, et a aussi les accès pour démarrer l'interface de la maison mère

### Défis architecturaux

- L'architecture des données sauvegardées dans la base de donnée doit être accomodante avec les différents magasins

# Réflexion basée sur les principes du Domain-Driven Design

1. **Gestion des produits**

   - **Responsabilité** : Gestion du stock, recherche de produits, réapprovisionnement
   - **Concepts clés** :
     - Entités : `Product`
     - Services : `restock_store_products`, `search_product_service`, `stock_status`
   - **Langage ubiquitaire** : "Produit", "Stock", "Réapprovisionnement", "Magasin"

2. **Gestion des commandes et ventes**

   - **Responsabilité** : Enregistrement, suivi, annulation des commandes
   - **Concepts clés** :
     - Entités : `Order`
     - Services : `save_order`, `return_order`, `orders_status`
     - Événements : `OrderSubmitted`, `OrderCancelled`
   - **Langage ubiquitaire** : "Commande", "Vente", "Statut", "Magasin"

3. **Authentification et sécurité**

   - **Responsabilité** : Gestion des accès, connexion utilisateur
   - **Concepts clés** :
     - Services : `login`
   - **Langage ubiquitaire** : "Utilisateur", "Session", "Authentification"

4. **Supervision et rapports**

   - **Responsabilité** : Génération des rapports d’activité, suivi global
   - **Concepts clés** :
     - Services : `generate_orders_report`
   - **Langage ubiquitaire** : "Rapport", "Revenu", "Stock restant", "Commande"

5. **Gestion de la persistance**

   - **Responsabilité** : Réinitialisation et gestion de la base de données
   - **Concepts clés** :
     - Services : `reset_database`
   - **Langage ubiquitaire** : "Base de données", "Migration", "Initialisation"
