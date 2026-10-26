# Guitar Fret Trainer

Application Windows pour apprendre la position des notes et les formes d'accords avec fondamentale sur les cordes de Mi grave et de La.

## Origine du projet

Cette application est full vibecodée : elle a été conçue et développée avec l'aide de GitHub Copilot, à partir des spécifications et retours musicaux du créateur du projet.

## Fonctionnalités

- Exercices de notes ou d'accords.
- Sélection de la corde de fondamentale : Mi grave, La, ou les deux alternées.
- Notes naturelles seules ou notes incluant les altérations, affichées alternativement en dièse ou bémol lorsque cela est possible.
- Manche vertical de six cordes, avec 15 frettes visibles.
- Repères de frettes configurables : numéros ou points à gauche du manche.
- Deux rythmes : révélation après un délai ou à l'appui d'une touche.
- Auto-évaluation après la révélation : `Juste` ou `Faux`.
- Résultats conservés localement et tirage plus fréquent des notes ou accords souvent ratés.
- Prévention des doublons consécutifs.

## Accords

Les formes proposées sont : majeur, septième, mineur, mineur septième et quatrième (`4`).

Les formes ouvertes sont utilisées pour Mi sur la corde de Mi grave et La sur la corde de La. Les autres fondamentales utilisent un barré bleu sur la frette de la fondamentale, puis la forme transposée. Le manche affiche jusqu'à la quinzième frette afin de montrer les doigts des accords dont le barré est à la douzième frette.

## Utilisation

1. Choisir le type d'exercice, la ou les cordes et les autres réglages.
2. Cliquer sur `Commencer la session`.
3. Retrouver mentalement la position demandée sur le manche.
4. Attendre la révélation ou appuyer sur une touche en mode manuel.
5. Indiquer `Juste` ou `Faux` après la révélation.

### Raccourcis

- `V` : marquer la réponse comme juste.
- `F` : marquer la réponse comme fausse.
- En mode sans délai, n'importe quelle touche, y compris `Espace`, révèle la réponse ou passe à l'étape suivante.
- `Quitter` : revenir à l'écran de configuration.

## Installation pour le développement

Prérequis : Python 3.13 ou une version récente de Python 3.

```powershell
git clone <url-du-depot>
Set-Location Guitar-Fret-Trainer
python -m pip install -r requirements.txt
python app.py
```

## Données locales

Au premier résultat enregistré, l'application crée `results.sqlite3` à côté de `app.py`.

Ce fichier contient l'historique des réponses et sert à pondérer les prochains tirages. Il est ignoré par Git. Pour repartir de zéro, fermer l'application puis supprimer ce fichier.

## Créer un exécutable Windows

Installer PyInstaller, puis lancer :

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --windowed --name "GuitarFretTrainer" app.py
```

Le livrable est placé dans `dist/GuitarFretTrainer/`. Pour partager l'application, envoyer le dossier entier, de préférence archivé en `.zip`. La personne qui le reçoit décompresse le dossier et lance `GuitarFretTrainer.exe` ; Python n'est pas nécessaire.

## Structure du projet

- `app.py` : interface PySide6, modèle musical, cycle d'exercice et stockage SQLite.
- `requirements.txt` : dépendance Python de l'interface graphique.
- `SPECIFICATIONS.md` : spécification fonctionnelle initiale et décisions de conception.
- `README.md` : ce guide.
- `.gitignore` : exclusions des caches, résultats et fichiers générés.

## Technologies

- Python
- PySide6 pour l'interface graphique
- SQLite pour les résultats locaux
- PyInstaller pour l'empaquetage Windows
