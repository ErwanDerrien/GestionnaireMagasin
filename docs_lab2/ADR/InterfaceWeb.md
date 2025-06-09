# ADR Changement de BD

## Statut
En cours d'implémentation

## Contexte
Durant le lab 1, c'est avec SQLite que la persitence a été assurée. Dans le contexte du lab 2, les exigences sont beaucoup plus nombreuses et le setup actuel ne permet pas 

## Décision
Je décide de changer de DB, je ne vais plus utiliser SQLite, je vais plutôt utiliser MySQL pour avoir la BD qui opère en standalone.

## Conséquences
Le logiciel ne vas plus rouler sur le même docker container que la BD. Cela veut dire qu'il y pourra y avoir un grand nombre de docker containers qui communiquent tous avec la même BD.