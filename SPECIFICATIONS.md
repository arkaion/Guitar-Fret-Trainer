# Guitar Fret Trainer - Specifications

## Objectif

Application de bureau pedagogique permettant d'apprendre a localiser les notes et les formes d'accords sur les cordes de Mi grave et de La d'une guitare. L'interface privilegie le contraste blanc sur fond noir pour limiter la fatigue visuelle.

## Perimetre initial

- Application locale de bureau, dans un projet distinct de StockMaster.
- Deux modes d'exercice : notes seules et accords.
- Cordes de travail : Mi grave, La, ou les deux alternees aleatoirement.
- Les six cordes restent visibles sur le manche afin de situer les formes d'accords.
- Les cordes sont affichees verticalement.
- Notation alternee entre diese (`#`) et bemol (`b`) lorsque les deux denominations sont possibles, afin d'entrainer leur reconnaissance.

## Ecran de configuration

Le premier ecran permet de choisir puis de lancer une session :

1. Type de contenu : `Notes` ou `Accords`.
2. Corde de travail : `Mi grave`, `La`, ou `Mi grave et La`.
3. Rythme de revelation :
   - `Avec delai` : la reponse est revelee automatiquement apres le temps configure.
   - `A l'appui d'une touche` : la reponse est revelee a l'appui d'une touche.
4. Duree du delai, lorsque ce mode est choisi.
5. Filtres :
   - notes naturelles uniquement ou notes incluant dieses/bemols ;
   - familles d'accords a inclure.

Le choix de la duree doit rester visible mais desactive lorsque le mode a l'appui d'une touche est selectionne.

## Ecran d'entrainement

L'ecran comporte :

- une zone de question indiquant la note ou l'accord a retrouver ;
- pour chaque question, la corde concernee (`Mi grave` ou `La`) ;
- un chronometre decompte lorsque le mode avec delai est actif ;
- un manche vertical affichant les six cordes, leurs notes a vide `E A D G B E` au-dessus, et les numeros de frettes sur la gauche ;
- des marqueurs de doigts et de barre lorsque la reponse est revelee ;
- une zone d'auto-evaluation visible apres la revelation, avec les boutons `Juste` vert et `Faux` rouge ;
- un fond noir, avec texte, cordes, frettes et marqueurs blancs ou gris tres clairs.

## Cycle d'une question

1. Une note ou un accord compatible avec les filtres est tire aleatoirement.
2. La question et la corde demandee sont affichees ; le manche ne montre pas encore la reponse.
3. Selon le rythme choisi :
   - le chronometre attend l'expiration du delai ;
   - ou l'application attend un appui sur une touche.
4. La bonne position est revelee sur le manche.
5. L'utilisateur auto-evalue sa reponse :
   - `V` ou le bouton vert `Juste` enregistre une reponse correcte ;
   - `F` ou le bouton rouge `Faux` enregistre une reponse incorrecte.
6. Le resultat est stocke et une nouvelle question est generee immediatement.

Une commande explicite permettra de quitter la session et de revenir a la configuration.

## Resultats et repetition adaptee

- Chaque auto-evaluation est enregistree avec l'element demande (note ou accord), la corde de fondamentale lorsqu'elle existe, le resultat et la date.
- Les statistiques sont conservees entre les sessions sur l'ordinateur local.
- Le tirage evite de proposer deux fois consecutivement le meme exercice.
- Un element dont le taux de reponses fausses est plus eleve obtient une probabilite plus forte d'etre tire lors des questions suivantes.
- Cette ponderation s'applique aux notes et aux accords selon le mode de session ; elle n'empeche pas les autres elements d'apparaitre.
- Une vue de statistiques detaillee n'est pas necessaire pour la premiere version, mais les donnees devront permettre de l'ajouter sans migration.

## Reponses pour les notes

- La reponse d'une note est une position sur la corde selectionnee.
- Pour une corde a vide, la corde entiere s'illumine au lieu d'afficher un point sur une frette.
- Les notes des deux cordes doivent provenir du schema de reference fourni :
  - Mi grave : `E, F, F#/Gb, G, G#/Ab, A, A#/Bb, B, C, C#/Db, D, D#/Eb, E, ...`
  - La : `A, A#/Bb, B, C, C#/Db, D, D#/Eb, E, F, F#/Gb, G, G#/Ab, A, ...`
- L'intervalle de frettes initial sera precise avant implementation ; le schema illustre les positions necessaires pour les exercices prevus.

## Reponses pour les accords

Les formes a travailler sont celles dessinees dans les references :

- Fondamentale sur Mi grave : majeur, septieme, mineur, mineur septieme et quatrieme.
- Fondamentale sur La : majeur, septieme, mineur, mineur septieme et quatrieme.
- Pour `E` avec une fondamentale sur Mi grave et `A` avec une fondamentale sur La, les formes ouvertes sont utilisees telles quelles.
- Pour les autres fondamentales, l'index realise un barre sur la frette de la fondamentale et les autres doigts reprennent la forme correspondante plus bas sur le manche.
- La revelation indique les doigts utilises par les numeros `1` a `4`, ainsi que le barre lorsqu'il existe.

Les enchainements ecrits sous les schemas ne font pas partie du perimetre initial.

## Donnees a confirmer avant l'implementation

1. Nombre exact de frettes a afficher et a inclure dans les tirages. -> le manche affiche 15 frettes pour voir les formes transposes jusqu'a la quinzieme ; les fondamentales peuvent aller jusqu'a la douzieme.
2. Tableau precise des positions de chaque doigt pour les dix formes d'accords, notamment les cordes qui ne doivent pas sonner. -> je t'ai donné deux images avec les formes de chaque accord pour la corde de mi et de la. Tu a juste à mettre une note avec un accord, et sur la réponse à metttre un barré sur la note et transposer la forme de l'accord juste en dessous
3. Touches de commande : une touche unique pour reveler/passer, ou des touches distinctes. -> quand c'est juste une touche pour passer à l'étape suivante, n'importe quelle touche doit fonctionner.
4. Comportement des doublons : eviter ou non deux questions consecutives identiques. -> oui
5. Plateforme cible de l'application de bureau (Windows uniquement ou multiplateforme). -> windows uniquement

## Proposition technique a valider

L'application est realisee en Python avec PySide6 pour l'interface de bureau, SQLite pour les resultats locaux et PyInstaller pour produire ultérieurement un executable Windows. Le modele musical reste separe du rendu du manche afin de pouvoir enrichir les positions sans modifier l'interface.

## Decoupage de realisation

1. Initialiser le projet independant et poser le theme noir/blanc.
2. Construire l'ecran de configuration avec ses filtres.
3. Afficher le manche vertical statique avec six cordes et frettes.
4. Implementer le cycle des notes, y compris les deux modes de rythme.
5. Ajouter les formes d'accords et leurs marqueurs de doigts.
6. Ajouter l'auto-evaluation, la persistance des resultats et le tirage pondere par les erreurs.
7. Ajouter les controles de session et tester les parcours principaux.