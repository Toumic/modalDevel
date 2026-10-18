# Manuel utilisateur de ModalDevel

## 1. Présentation

ModalDevel est un outil de recherche et de construction de gammes musicales. Il travaille à partir de :

- l'ordre diatonique `C D E F G A B` ;
- une note tonique ;
- la hauteur éventuelle de cette tonique ;
- des degrés modulés par des signes d'altération ;
- des règles de continuité entre degrés voisins ;
- des formes modales de référence `classic` et `physic`.

Le programme peut reconnaître une forme existante ou conserver une construction nouvelle lorsqu'elle n'est pas présente dans les catalogues de référence.

## 2. Prérequis

Le projet utilise Python et la bibliothèque standard. Aucun paquet externe n'est nécessaire.

Depuis PowerShell, placer le terminal dans le dossier du projet :

```powershell
cd C:\Users\Vincent\Documents\GitHub\modalDevel
```

Le lancement recommandé utilise l'environnement virtuel :

```powershell
.\venv\Scripts\python.exe .\modalDevel.py
```

## 3. Modes de lancement

### Interface graphique

```powershell
.\venv\Scripts\python.exe .\modalDevel.py --gui
```

Sans option `--cli`, `--pro` ou `--demo`, le programme lance également l'interface graphique par défaut.

### Mode Pro

```powershell
.\venv\Scripts\python.exe .\modalDevel.py --pro
```

Le mode Pro guide la saisie dans le terminal et affiche les étapes du calcul.

### Menu CLI

```powershell
.\venv\Scripts\python.exe .\modalDevel.py --cli
```

Le menu CLI propose une recherche, le mode Pro, la démonstration et la sortie du programme.

### Démonstration

```powershell
.\venv\Scripts\python.exe .\modalDevel.py --demo
```

La démonstration exécute automatiquement une recherche simple en do majeur.

## 4. Paramètres d'une recherche

Une recherche utilise quatre informations :

1. la note tonique ;
2. la hauteur de la tonique ;
3. le type de recherche ;
4. la gamme ou les degrés modulés demandés.

### Note tonique

Les notes disponibles sont :

```text
C, D, E, F, G, A, B
```

La tonique constitue le point de référence de la gamme. Elle n'est pas un degré modal ordinaire.

### Hauteur de la tonique

Dans la GUI, la hauteur est choisie dans la liste `Altération`. Les équivalences sont affichées directement :

```text
+ = #
x = ##
^ = ###
- = b
o = bb
* = bbb
```

Les signes composés sont également disponibles. Par exemple :

```text
+^ = ####
^^^^ = 12 dièses
******** = 24 bémols
```

La hauteur de la tonique s'applique à la gamme majeure de référence. Elle est distincte d'une modulation comme `+3`, qui agit sur le troisième degré.

### Types de recherche

- `0 - Formule exacte` : recherche à partir d'une formule numérique complète ;
- `1 - Recherche stricte` : construction contrôlée à partir des degrés signés ;
- `2 - Recherche déductive` : recherche de formules compatibles dans la base des formes modales.

Dans l'interface, chaque mode affiche uniquement ses réglages : la grille de formule en mode 0, ou les contrôles de construction de gamme en modes 1 et 2.

## 5. Construire une gamme dans la GUI

La sélection des degrés et des signes suit obligatoirement cet ordre :

1. choisir un degré ;
2. consulter les signes proposés pour ce degré ;
3. choisir un signe ;
4. cliquer sur `Ajouter`.

Le degré `1` n'est pas proposé dans cette liste, car il correspond à la tonique et se règle séparément.

Exemple :

```text
Degré : 3
Signe : +
Choix ajouté : +3
```

Une expression peut être supprimée avec `Retirer`. `Effacer la gamme` supprime tous les degrés sélectionnés.

## 6. Signes disponibles par degré

Les possibilités sont limitées par la position du degré dans l'octave et par les règles d'altéractivité.

Exemples de possibilités initiales :

```text
2 : -2, 2, +2, x2, ^2, +^2
3 : o3, -3, 3, +3, x3, ^3
4 : o4, -4, 4, +4, x4, ^4
5 : *5, o5, -5, 5, +5, x5
6 : -*6, *6, o6, -6, 6, +6
7 : o*7, -*7, *7, o7, -7, 7
```

Les listes sont ensuite recalculées après chaque sélection. Elles ne représentent donc pas toujours les mêmes choix : elles reflètent la continuité altéractive déjà engagée.

## 7. Continuité altéractive

Une altération peut entraîner les degrés voisins. Les chaînes utilisent le symbole `>` pour exprimer cette continuité.

### Propagation ascendante

```text
+3 > +4
x3 > x4 > +5
^3 > ^4 > x5 > +6
```

Après `+3`, le degré 4 peut conserver une force ascendante. Les signes proposés pour 4 peuvent donc être :

```text
+4, x4, ^4
```

Les signes descendants de 4 ne sont plus proposés dans cette continuité.

### Propagation descendante

```text
o*7 > -*6 > *5 > o4 > o3 > -2
```

Après `o*7`, la propagation atteint le degré 2 et celui-ci est limité à `-2`.

### Exemple de degré entraîné

Après le choix `-4` :

- le degré 3 reste disponible mais son signe est entraîné vers `-3` ;
- le degré 2 est limité par la continuité descendante ;
- les autres degrés sont recalculés selon les chaînes concernées.

## 8. Fenêtre de remise en cohérence

Un nouveau choix peut modifier la continuité d'un choix déjà effectué. Par exemple, l'utilisateur peut choisir d'abord `+4`, puis sélectionner `^3`.

Dans ce cas, ModalDevel ouvre une fenêtre de confirmation indiquant les choix concernés.

- `OK` confirme la remise en cohérence et retire les choix devenus incompatibles ;
- `Cancel` conserve la sélection précédente et annule le nouveau choix.

Cette fenêtre évite de modifier silencieusement la construction de l'utilisateur.

## 9. Formules numériques

La formule majeure naturelle de référence est :

```text
102034050607
```

Les chiffres représentent les degrés et les zéros représentent les positions intermédiaires entre les degrés.

Exemple :

```text
100203405067
```

Une formule exacte doit respecter l'ordre des degrés. Dans la GUI, le type de recherche `0` affiche une grille de douze cases, avec les degrés de la forme majeure indiqués au-dessus. Les cases majeures contiennent les chiffres initiaux ; les positions libres affichent `0`. Un clic sur une case ajoute ou retire une note et renumérote les degrés actifs dans l'ordre croissant.

L'option `Maintenir une gamme de 7 notes` est cochée par défaut. Si vous confirmez l'ajout d'une autre position, la grille peut temporairement dépasser sept notes. Pour plus de sept notes, la recherche teste toutes les suppressions nécessaires pour revenir à sept, puis toutes les rotations. Pour moins de sept notes, elle inhibe les degrés de chaque forme cataloguée et teste ses rotations ; aucune note chromatique n'est ajoutée automatiquement. Toutes les correspondances `classic` et `physic`, ainsi que les orthographes cataloguées des mêmes positions chromatiques, sont conservées. Les correspondances avec une septième majeure sont classées en premier, puis les résultats sont ordonnés par poids modal absolu croissant. Le poids compte uniformément les degrés naturels et altérés : chaque degré naturel fournit sa tare (la gamme naturelle complète vaut 28) ; une altération remplace cette tare, par exemple `#4 = +5` et `b3 = -4`.

## 10. Lecture des résultats

Le résultat présente notamment :

```text
Tonique : B
Formule : 100203405067
Gamme : B | xC | xD | +E | xF | xG | +A
Type : heptatonique
```

Le type indique la cardinalité de la gamme :

- 5 notes : pentatonique ;
- 6 notes : hexatonique ;
- 7 notes : heptatonique ;
- autre cardinalité : catégorie correspondante.

Les lignes modales indiquent aussi :

- la ligne analogique ;
- la forme énumérée ;
- le mode tonique ou non tonique ;
- le nom de la forme lorsque le dictionnaire la reconnaît ;
- le dictionnaire d'origine : `classic`, `physic` ou `construction`.

## 11. Classic, physic et construction

Les catalogues `classic` et `physic` sont deux sources de référence distinctes. Même si elles produisent la même ligne de notes, elles peuvent fournir des noms ou des formules différentes. Les deux résultats sont donc conservés et identifiés séparément.

Pour nommer les modes non toniques, le programme utilise aussi `modal_names.py` (462 noms issus du rapport exhaustif `modalDevel_modesExhaustifs.txt`, corrigés). Priorité : le nom `classic` / `physic` d'abord, le nom du rapport en repli.

Règles de nommage : diminution (`-`, `o`, `*`) = degrés descendants, augmentation (`+`, `x`, `^`) = degrés ascendants ; forme entière avec un signe pour un à six degrés (`-65`, `x23`) ou deux signes pour deux degrés (`-34+`), sans répéter un même signe ; deux signes de sens opposé = degrés croissants ; forme décimale (`+6.-42`) seulement si aucune forme entière n'est possible, avec les mêmes règles pour chaque partie.

Une construction qui n'est pas dans ces catalogues n'est pas supprimée. Elle peut être affichée avec :

```text
Dictionnaire : construction
Mode tonique : non référencé
```

Cela permet de conserver des gammes nouvelles, notamment hexatoniques ou appartenant à une autre famille.

## 12. Exemple complet

Pour construire une gamme avec la tonique `B` et les degrés `+2`, `+3`, `+4`, `+5`, `+6` :

1. choisir `B` comme tonique ;
2. laisser la tonique sans altération ;
3. choisir la recherche stricte ou déductive ;
4. ajouter successivement `+2`, `+3`, `+4`, `+5`, `+6` ;
5. lancer la recherche.

La gamme construite est de la forme :

```text
B | +C | +D | E | +F | +G | +A
```

Le résultat conserve cette construction comme ligne tonique, même si elle n'est pas identifiée par un nom dans les catalogues.

## 13. Problèmes courants

### La liste des signes est vide

Vérifier qu'un degré est sélectionné avant de choisir le signe. Le degré 1 est réservé à la tonique et ne possède pas de liste de modulation.

### Un signe attendu n'apparaît plus

Un choix précédent peut avoir réduit la marge disponible. Retirer le choix précédent ou utiliser `Effacer la gamme`, puis sélectionner à nouveau le degré.

### Une fenêtre de confirmation apparaît

Cela signifie que le nouveau choix modifie la continuité d'un choix antérieur. Lire la liste proposée avant de confirmer avec `OK`.

### Le résultat est non référencé

La gamme a bien été construite, mais sa formule ne correspond pas aux catalogues `classic` ou `physic`. Elle reste néanmoins disponible comme construction nouvelle.

## 14. Tests

Depuis le dossier du projet :

```powershell
python -m unittest discover -s tests -v
```

Les tests vérifient notamment :

- les signes composés comme `+^2` ;
- la propagation `+3` vers le degré 4 ;
- la propagation `o*7` jusqu'au degré 2 ;
- la frontière du degré 7 après une montée ;
- la remise en cohérence des choix ;
- la classification hexatonique et heptatonique ;
- le chargement des tables partagées.
