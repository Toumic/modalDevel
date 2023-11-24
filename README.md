# Anthologie utilisateur et les gammes
Comporte un dictionnaire qui a comme clef une forme modale numérique, et comme valeur les sept formes modales.<br>
La gamme naturelle analogique `[C, D, E, F, G, A, B]` donne cette formule numérique (`102034050607`).<br>
Seule la recherche par formule exacte nécessite une forme énumérée (exemple : `102034050607`), vous devez connaitre 
la formule avant de la proposer comme une recherche de la gamme heptatonique. Il n'y a rien de difficile, un chiffre
égale un degré et un zéro correspond à un intervalle vide d'un demi-ton (soit un ton = 00). Pour les autres types de 
recherche, veuillez vous référer au menu **(Le programme pose quatre questions :)**<br>

Le programme pose quatre questions :<br>
... 1 : Le choix d'une note tonique est nécessaire, **en DO par défaut**.<br>
... 2 : Quelle altération supporte la tonique, **non signée par défaut**.<br>
... 3 : Quelle forme de résultat est souhaitée, **vaût "1" par défaut**.<br>
... ... : 0 = Recherche par une formule, exemple (`102034500607`).<br>
... ... ... : _Les chiffres sont absolus et les zéros sont les intervalles vides._<br>
... ... ... : _Exemples choisis (`102304050607`= b3. `102304500607`= b3, b5...)._<br>
... ... : 1 = Recherche stricte, le résultat selon la saisie utilisateur.<br>
... ... ... : _Si l'utilisateur choisit "-2+5", le résultat passera par (`120034005607`)._<br>
... ... ... : _`En saisissant "+++" celà équivaudra à "###". "++" = "x ou ##".`_<br>
... ... ... : _Vous pouvez voir les valeurs des altérations sur cette série : `+, x, ^, -, o, *`._<br>
... ... : 2 = Recherche déductive, propose un choix guidé par la saisie utilisateur.<br>
... ... ... : _Le résultat propose un nombre de gammes ayant les mêmes degrés signés._<br>
... ... ... : _Les modes résultants et les modes toniques, sont dans des dictionnaires différents._<br>
<br>
Cette application traite le choix de l'utilisateur, et à chaque fois, il répond avec précision.<br>
Pour celà, il est nécessaire de préparer des fichiers[Listes et dictionnaires], se trouvant déjà dans 
les premières lignes du programme avec leurs commentaires.<br>

#### Les fonctions et leurs utilités :
`def print_hi` = Mise en forme des renseignements donnés par l'utilisateur, ce qui permettra la mise en situation 
des degrés altérés dans une première liste dédiée aux choix de l'utilisateur. Les conditions de cette "fabrication" 
réunissent les choix parmi les degrés dits "naturels", pendant cette évolution se testent les concordances
événementielles telles que certaines demandes qui créeraient des collisions entre les degrés.<br>
Dans cette partie, le choix du type de recherche est traité selon qu'il est (une formule exacte, 
une formule créée selon le choix déterminé au début ou bien, le choix initial se trouvant parmi les modulations
étant dans le fichier "globdicTcoup.txt")

`def mode` = Cette fonction scripte la formule numéraire en une formule binaire, celle-ci est plus facile à
développer diatoniquement. Donnant un résultat numéraire reflétant les valeurs formées des degrés diatoniques pour
chaque gamme demandée.

`def signal` = L'unique but est d'apporter soit un index du signe d'altération dans les tables[tab_sup et tab_inf],<br>
soit un signe altératif, cette fonction est appelée par la fonction **gamme**.

`def gamme` = Elle dessine au final la ou les gammes avec leurs notes (`CDEFGAB`), altérées ou non. Cette fonction, 
dessine au final la ou les gammes avec leurs notes (`CDEFGAB`), altérées ou non.
<br><br>

### le fichier content_mode.txt
Il va se remplir avec des nouvelles gammes, au fur et à mesure de la recherche. Pour le moment, il n'est pas utilisé.<br>

#### Éléments entrainants des erreurs
~~+36+ : Créer une solution pour remettre en ordre les entrées utilisateur (quand c'est possible)~~ `réglé`<br>
~~o1 : Produit -2 qui n'est pas une clé de dic_120~~ `réglé`<br>

