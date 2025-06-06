# 1. Introduction et buts

Le but de ce laboratoire est de concevoir un système de gestion de magasin.

Durant le laboratoire 1, une interface graphique simple a été conçu pour permettre l'utilisation des fonctionnalitées minimales implémentées. Le but du laboratoire 2 précisément est d'améliorer ce qui a été fait dans le laboratoire un, en plus d'implémenter de nouveaux requis.

L'architecture monolithique 2-tiers de ce projet doit être amélioré vers un système distribué et scalable.

Les objectifs clés incluent :

- La cohérence des donnéess entre les entités
- Génération de rapports centralisés pour le siège social
- Évolutivité vers une interface web

## 1.1 Aperçu des exigences

### Priorisation MoSCoW

#### Must

- UC1 – Générer un rapport consolidée des ventes
- UC2 – Consulter le stock central et déeclencher un réapprovisionnement
- UC3 – Visualiser les performances des magasins dans un tableau de bord

### Should

- UC4 – Mettre à jour les produits depuis la maison mère
- UC6 – Approvisionner un magasin depuis le centre logistique

### Could

- UC7 – Alerter automatiquement la maison mère en cas de rupture critique
- UC8 – Offrir une interface web minimale pour les gestionnaires

## 1.2 Objectifs de Qualité

### Top 3 Qualités

1. **Cohérence des données** :

   - Synchronisation des données au travers de la chaine. de magasins
   - Mécanisme de résolution de conflits

2. **Évolutivité** :

   - Ajout d'un magasin en <1 jour ouvré
   - Support pour extensions futures

3. **Transférabilité** :
   - Les interfaces ne doivent pas pas dépendre du système d'exploitation pour être mises en marche

## 1.3 Parties Prenantes

| Rôle                | Préoccupations Majeures            |
| ------------------- | ---------------------------------- |
| Hauts dirigeants    | Exactitude des rapports financiers |
| Employés de magasin | Simplicité d'interface             |
| Équipe DevOps       | Facilité de déploiement            |
| Gestionnaires       | Utilité du centre logistique       |

### Attentes Techniques

- Documentation ADR complète
- Tests automatisés >80% de couverture
- CI/CD avec validation

# 2. Contraintes Architecturales

- **VM imposée** : L'infrastructure doit fonctionner sur la machine virtuelle fournie
- **Docker obligatoire** : Conteneurisation requise pour tous les composants
- **Modèle 4+1 UML** : Production des vues architecturales exigée
- **ADR requis** : Documentation des décisions architecturales obligatoire
- **CI/CD imposée** : Pipeline GitLab existante à utiliser
- **Budget limité** : Solutions open-source uniquement, pas de services cloud payants
- **Conventions de code** :
  - Français pour le domaine métier
  - Anglais pour le code technique
  - JavaDoc obligatoire

# 3. Contexte et Périmètre

## 3.1 Contexte Métier

**Système Central**:

- Gestion des stocks multi-magasins
- Génération de rapports consolidés
- Tableaux de bord de performance

**Partenaires Métier**:

| Acteur              | Interactions                    | Format/Protocole         |
| ------------------- | ------------------------------- | ------------------------ |
| Magasins (5)        | Mise à jour des stocks          | API REST (JSON)          |
| Centre Logistique   | Demandes de réapprovisionnement | Messagerie (RabbitMQ)    |
| Siège Social        | Consultation des rapports       | Web (HTTPS/JSON)         |
| Employés de magasin | Saisie des ventes               | Interface graphique Java |

![Contexte métier](/out/docs_lab2/UML/ContexteMétier/ContexteMétier.png)

## 3.2 Contexte Technique

**Stock**:

- Synchronisation via WebSockets
- Base de données MySQL centrale

**Contraintes d'Intégration**:

- Doit coexister avec l'infrastructure CI/CD implémentée durant le lab 1
- Doit le système doit rouler sur un docker container

![Contexte métier](/out/docs_lab2/UML/ContexteTechnique/ContexteTechnique.png)

# 4. Stratégie de Solution

## Décisions Fondamentales

**1. Architecture MVC + Services + DAO**

- _Pourquoi_ : Découple les différents éléments du système pour les rendre indépendents des un des autres et donc facile à refactorer
- _Implémentation_ :

**2. Synchronisation par Événements**

- _Pourquoi_ : Atteindre la cohérence des données entre magasins
- _Avantage_ : Nécessite seuelement de mettre à jour les informations sur la BD, pas d'avertir les autres éléments du système.

**3. Découpage Microservices**

- _Services_ :
  - Gestion-Stock (Spring Boot)
  - Reporting (Quarkus pour performance)
- _Avantage_ : Évolutivité indépendante

## Qualités Clés Adressées

| Qualité         | Scénario                         | Solution                                            |
| --------------- | -------------------------------- | --------------------------------------------------- |
| **Cohérence**   | Sync stocks instantané           | Toutes transactions refletées directement sur la BD |
| **Évolutivité** | Ajout magasin en moins d'un jour | API versionnée + contrat Swagger                    |

## Choix Technologiques

- **Backend** :

  - Python
  - Base de données : MySQL

- **Frontend** :

  - Vue.js (découplée)

- **DevOps** :
  - CI/CD : GitLab Pipelines

# 5. Vue des Blocs de Construction

## 5.1 Vue Niveau 1 (Système Global)

![Diagramme Niveau 1](/out/docs_lab2/UML/BlockViewLevel1/Niveau1.png)

**Composants principaux** :

| Bloc                  | Responsabilités                            | Interfaces              |
| --------------------- | ------------------------------------------ | ----------------------- |
| Gestion des Stocks    | Gestion centralisée des stocks             | API REST, WebSockets    |
| Génération Rapports   | Production des rapports consolidés         | API REST                |
| Interface Utilisateur | Point d'accès unique pour tous les acteurs | GraphQL, JavaFX, Vue.js |

**Relations** :

- Tous les composants accèdent à la base MySQL centrale
- L'interface orchestre les interactions utilisateur

## 5.2 Vue Niveau 2 (Détail Gestion des Stocks)

![Diagramme Niveau 2](/out/docs_lab2/UML/BlockViewLevel2/Niveau2.png)

**Structure interne** :

1. **Service Stock** :

   - Expose la logique métier (`checkStock`, `updateInventory`)
   - Implémente les règles de gestion
   - Contrôle les transactions

2. **DAO MySQL** :
   - Abstraction de l'accès aux données
   - Implémente le pattern Repository
   - Gère le mapping objet-relationnel

**Principe clé** :  
Séparation stricte entre logique métier (Service) et persistance (DAO) via l'injection de dépendances.

# 6. Vue de runtime

## UC1 – Générer un rapport consolidée des ventes

![UC1](/out/docs_lab2/UML/RuntimeViewUC1/UC1%20-%20Génération%20et%20consultation%20de%20rapport.png)

## UC2 – Consulter le stock central et déclencher un réapprovisionnement

![UC2](/out/docs_lab2/UML/RuntimeViewUC2/UC2%20-%20Consulter%20le%20stock%20et%20réapprovisionnement.png)

## UC3 – Visualiser les performances des magasins dans un tableau de bord

![UC2](/out/docs_lab2/UML/RuntimeViewUC3/UC3%20-%20Visualiser%20les%20performances%20des%20magasins%20dans%20un%20tableau%20de%20bord.png)

## 7. Vue de déploiement

## 8. Crosscutting concepts

## 9. Décision d'architecture

## 10. Quality requirements

## 11. Risques et dette technique

## 12. Glossaire
