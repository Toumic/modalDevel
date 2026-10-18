# ModalDevel

ModalDevel est un petit programme Python dédié à la recherche de gammes et de formes modales. Il repose sur une représentation numérique des degrés et sur des tables de signatures pour retrouver des gammes cohérentes à partir d'une tonique et d'un type de recherche.

## Objectif

Le programme permet de :

- choisir une tonique parmi C, D, E, F, G, A, B ;
- appliquer une altération à la tonique ;
- sélectionner un mode de recherche ;
- retrouver une gamme ou une forme modale compatible.

## Principe de fonctionnement

La gamme naturelle de référence est :

- C, D, E, F, G, A, B

Sa formule numérique est :

- 102034050607

Un chiffre représente un degré. Un zéro correspond à une position libre. En mode graphique, la recherche par formule exacte utilise une grille de douze cases initialisée avec la forme majeure ; les cases majeures sont indiquées au-dessus. Cliquer sur une case ajoute ou retire une note, et les degrés sont renumérotés dans l'ordre.

L'option « Maintenir une gamme de 7 notes » est cochée par défaut. Si vous confirmez l'ajout d'une autre position, la grille peut temporairement dépasser sept notes. Pour plus de sept notes, la recherche teste toutes les inhibitions nécessaires et les rotations. Pour moins de sept notes, elle teste les rotations des formes cataloguées qui contiennent les positions choisies ; les degrés catalogués situés dans les cases vides sont proposés comme compléments chromatiques, selon l'orthographe majeure/dièse et enharmonique/bémol. Dans les deux cas, les correspondances `classic` et `physic` sont conservées, avec la septième majeure prioritaire, puis le poids modal absolu le plus faible. Le poids suit une règle uniforme : chaque degré naturel fournit sa tare (la gamme naturelle complète pèse 28) ; une altération remplace cette tare, par exemple `#4 = +5` et `b3 = -4`.

Les modes de recherche disponibles sont :

- 0 = formule exacte ;
- 1 = recherche stricte ;
- 2 = recherche déductive.

## Lancement

Depuis le dossier du projet, avec le venv :

```powershell
.\venv\Scripts\python.exe .\modalDevel.py
```

Exécution rapide de la démonstration :

```powershell
.\venv\Scripts\python.exe .\modalDevel.py --demo
```

Mode guidé :

```powershell
.\venv\Scripts\python.exe .\modalDevel.py --pro
```

Interface graphique TTK (également lancée par défaut depuis VS Code) :

```powershell
.\venv\Scripts\python.exe .\modalDevel.py --gui
```

L'interface graphique utilise `tkinter.ttk`, inclus dans la bibliothèque standard de Python. Elle permet de relancer plusieurs recherches sans redémarrer le programme.

Pour une recherche stricte ou déductive, la gamme se construit expression par expression : choisissez d'abord un degré, puis un signe compatible, cliquez sur `Ajouter`, puis répétez l'opération. Par exemple, le degré `2` avec le signe `-`, puis le degré `5` avec le signe `+`, construit `-2+5`. Une expression peut être retirée avant de lancer la recherche. Les choix tiennent compte des chaînes d'altéractivité et une confirmation apparaît lorsqu'un nouveau choix rend une sélection précédente incohérente.

Pour conserver le menu interactif dans le terminal :

```powershell
.\venv\Scripts\python.exe .\modalDevel.py --cli
```

Pour lancer les tests des règles modales :

```powershell
python -m unittest discover -s tests -v
```

## Fichiers du projet

- `modalDevel.py` : interface, moteur de recherche et reconstruction analogique ;
- `modal_data.py` : tables partagées des signes, positions chromatiques et chaînes d'altéractivité ;
- `modal_catalog.py` : formes de référence `classic` et `physic` ;
- `modal_names.py` : `MODE_NAMES`, les 462 noms modaux (formule → nom) tirés du rapport exhaustif `modalDevel_modesExhaustifs.txt` de GlobalApplis, puis corrigés selon les règles de nommage ;
- `globdicTcoup.txt` : base de données de formes modales ;
- `content_mode.txt` : historique de session ;
- `MANUEL_UTILISATEUR.md` : guide d'utilisation détaillé ;
- `README.md` : documentation du projet.
- `tests/test_modal_rules.py` : tests des règles de sélection et de propagation.

## Fonctionnement interne

Le fichier principal contient plusieurs fonctions clés :

- `print_hi` : collecte et validation des informations utilisateur ;
- `mode` : transforme la formule numérique en structure exploitable ;
- `signal` : gère les altérations et les signatures ;
- `gamme` : reconstruit la gamme analogique sous forme de notes.

Les données modales sont séparées en plusieurs niveaux :

- `DEGREE_SIGNATURES` décrit les signes disponibles pour chaque degré dans une octave ;
- `CHROMATIC_SIGNATURES` associe les positions chromatiques aux écritures possibles ;
- `ALT_ACTIVITY` décrit la continuité et la propagation des forces altéractives ;
- `pre_classic` et `pre_physic` servent à reconnaître les formes de référence, sans limiter la création de nouvelles gammes.

Nom affiché d'un mode : les noms `classic` / `physic` restent prioritaires ; à défaut, le nom de `MODE_NAMES` sert de repli (notamment pour les modes non toniques).

Règles de nommage modal :

- diminution (`-`, `o`, `*`) : degrés descendants ; augmentation (`+`, `x`, `^`) : degrés ascendants ;
- forme entière : un signe pour un à six degrés (`-65`, `x23`) ou deux signes pour deux degrés (`-34+`, `SDDS`, limite de la forme entière) ; un signe n'est jamais répété (`x23`, pas `x23x`) ;
- deux signes de sens opposé : degrés en ordre croissant, chaque signe restant attaché à son degré ;
- forme décimale (`+6.-42`) : seulement si aucune forme entière ne peut nommer le mode ; chaque partie suit les mêmes règles que la partie entière ;
- le nom entier retenu est la forme la plus courte.

Chaque signe d'un nom s'additionne au degré déjà présent (`-6` puis `o6` donne `*6`), puis sa chaîne d'altéractivité fixe les degrés suivants.

La hauteur de la tonique est indépendante des modulations de degrés. Les tables `tab_sup` et `tab_inf` permettent d'exprimer jusqu'à 24 unités d'altération de la tonique. Une modulation comme `+3` agit ensuite sur le troisième degré majeur de cette référence.

Une altération ascendante ou descendante peut entraîner les degrés voisins. La GUI recalcule donc les degrés et signes disponibles après chaque choix. Les cas qui dépassent le cadre classique de l'octave sont conservés comme cas exceptionnels à traiter séparément.

Le moteur classe également la gamme reconstruite selon sa cardinalité (`pentatonique`, `hexatonique`, `heptatonique`, etc.). Les chaînes d'altéractivité disposent d'un score normalisé qui pourra servir à classer les propositions probabilistes.

Le programme traite la saisie de l'utilisateur et tente de reconstruire des familles de gammes cohérentes à partir des règles modales de référence.

## Stabilisation

Plusieurs problèmes de logique ont été corrigés au fil du développement :

- gestion de l'ordre des saisies ;
- cohérence des altérations ;
- prise en charge des tonicités altérées ;
- traitement des conflits entre degrés et formules.

## Dépendances

Le projet n'utilise pas de dépendances externes. Il fonctionne avec la bibliothèque standard de Python.

## Utilisation recommandée

1. Lancer le programme.
2. Choisir la tonique et sa hauteur.
3. Choisir le type de recherche.
4. Choisir un degré, puis un signe compatible.
5. Consulter le résultat et son origine (`classic` ou `physic`).

Le mode `--pro` est le plus guidé et le plus lisible pour une utilisation en ligne de commande.
Le fichier principal contient plusieurs fonctions essentielles :

- `print_hi` : construction de la saisie utilisateur et préparation des degrés altérés
- `mode` : conversion de la formule numérique en structure exploitable
- `signal` : gestion des altérations et des signatures
- `gamme` : reconstruction de la gamme analogique sous forme de notes

Le programme traite la saisie de l’utilisateur et tente de reconstruire des familles de gammes cohérentes à partir des règles modales de référence.

## Stabilisation

Plusieurs problèmes de logique ont été corrigés au fil du développement :

- gestion de l’ordre des saisies utilisateur,
- cohérence des altérations,
- prise en charge des tonicités altérées,
- traitement des conflits entre degrés et formules.

## Dépendances

Le projet n’utilise pas de dépendances externes. Il fonctionne avec Python standard.

## Utilisation recommandée

1. Lancer le programme.
2. Choisir la tonique.
3. Définir l’altération.
4. Choisir le type de recherche.
5. Consulter le résultat.

Le mode `--pro` est le plus guidé et le plus approprié pour une utilisation en ligne de commande plus claire.
