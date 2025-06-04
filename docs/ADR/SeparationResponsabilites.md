# ADR Séparation des responsabilitées

## Statut
Implémenté

## Contexte
Le code source de ce projet est séparé selon la sctructure classique MVP, en plus d'avoir le dossier "Services". Je prends cette décision car c'est une architecture avec laquelle je suis habitué de travailler. C'est une application relativement simple pour le moment, mais en pensant à des futurs améliorations l'implémentation de cette structure facilite sont extensibilité.

## Décision
Cette décision affecte les accès aux données selon les responsabilités attribués. La gestion des fichiers est plus facile. Le changement d'interface plus tard est facilité en isolant la partie de communication avec la vue.

## Conséquences
Il faut maintenant respecter la structure MVP et restructurer les fichiers actuels.