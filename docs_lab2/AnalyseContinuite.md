# Analuse et Continuité

## Solutions développées aux labs 0 et 1

## Éléments à ...

### Conserver

Je veux conserver la séparation actuelle du traitement de l'info (MVC + services)

### Modifier

Je veux modifier la structure dont l'information est sauvegardée sur la base de donnée pour permettre l'expension du scope.
Je veux changer la manière dont la base de donnée est accédée. Actuellement, la BD est 

### Refactorer

Je veux changer l'inerface pour permettre à un nouvel utilisateur de : 
- Démarrer l'application
- Choisir un magasin ou la maison mère

## Nouveau/elles

### Exigences

- La personne qui va configurer les caisses peut sélectionner dans quel magasin il est, mais il ne peut pas indiquer qu'il est dans la maison mère.
- Les employés qui vont utiliser le programme ne peuvent que utiliser la caisse, ils n'ont pas accès
- Les administrateurs peuvent utiliser le programme soit pour se connecter à un des trois magasins, et a aussi les accès pour démarrer l'interface de la maison mère


### Défis architecturaux

- L'architecture des données sauvegardées dans la base de donnée doit être accomodante avec les différents magasins

# Réplexion basée sur les principes du Domain-Driven Design


## Sous-domaines fonctionnels

1. Ventes en magasin
- Responsabilité : Commandes locales, gestion du stock en temps réel
- Concepts clés : 
- - Entités: `Product`, `Order`
- - Événements : `OrderSubmitted`, `CancelOrder`
- Language ubiquitaire : "Produit", "Commande", "Succursale"

2. Gestion logistique
- Responsabilité : Réapprovisionner les stocks des magasins
- Concepts clés : 
- - Agrégats: `RestockDemand`, `GlobalStock`
- - Événements : `ReplenishStoreStock`
- - Services : `RestockService`
- Language ubiquitaire : "Seuil critique", "Transfert de stock"

3. Supervision par la maison mère
- Responsabilité : Réapprovisionner les stocks des magasins
- Concepts clés : 
- - Agrégats: `RestockDemand`, `GlobalStock`
- - Événements : `ReplenishStoreStock`
- - Services : `RestockService`
- Language ubiquitaire : "Seuil critique", "Transfert de stock"
