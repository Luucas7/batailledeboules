# Bataille de boules
Bataille de boules est un jeu où le but est d'occuper la plus grande aire possible en plaçant des boules,
chaque joueur joue en cliquant sur la fenêtre pour poser une boule ou pour interagir avec les variantes proposées,
les joueurs contrôlent la souris chacun à leur tour.



# Structure du tour à tour
La structure de ce programme se repose sur un système de jeu tour à tour, pour cela, le programme utilise la parité 
d'un itérateur numTour dans une boucle "while" pour attribuer le joueur du tour, ce qui permet une alternance peu importe les valeurs,
le joueur vert joue quand numTour est pair, le joueur rouge joue quand numTour est impair.
La boucle est initiée à 0, donc le joueur vert commence, et va jusqu'à (nombre de tours * 2), puisqu'un joueur joue quand
la parité de numTour lui correspond, on a besoin d'un total de (nombre de tours * 2) tours pour que chaque joueur joue (nombre de tours) fois
vu qu'il n'y a que 2 joueurs.



# Gestion des cercles
Les données des cercles (x centre , y centre , rayon , identifiant du cercle) sont stockés dans une liste qui comporte séparement
les cercles verts et les rouges dans 2 listes : [ [cercles verts], [cercles rouges] ].
Pour ajouter un cercle il suffit d'utiliser la méthode .append() avec les données du cercle dès qu'un cercle est tracé.
Pour pouvoir accéder à la liste des cercles correspondants à l'action du joueur, il faut vérifier la parité de numTour,
d'où l'utilisation de modulo : 

    EXEMPLE (VERT) : Le joueur vert clique dans un cercle rouge, donc le programme doit interagir uniquement avec les cercles rouges :
    (numTour % 2) renvoie le reste de (numTour / 2) donc 0 (car numTour est pair, vert qui joue)
    cercles[not numTour % 2] = cercles[1] permet bien d'accéder aux cercles rouges,
    L'opérateur not, qui inverse la valeur booléene, permet d'accéder aux cercles ennemis.
    Si on a besoin de tracer un cercle vert en étant vert : cercles[numTour % 2] = cercles[0]



# Gestion des interactions au clic
Pour les interactions avec les autres cercles, le programme parcourt la liste des cercles ennemis, puis calcule la distance 
euclidienne entre le clic du joueur et le centre de chaque cercle. 
Ensuite, il enregistre la distance minimale trouvée, et l'interaction est choisie en fonction de la distance
minimale trouvée, si elle est inférieure au rayon proche : Le clic est inclus est dans le cercle, alors on divise le cercle en deux,
sinon, si il est inférieur à (rayon du cercle à tracer + rayon du cercle proche), alors il y a une intersection et aucun cercle ne 
doit être tracé, sinon si il n'y a aucune interaction, le cercle est tracé.
Si le cercle est trop près des bords ou d'un cercle ennemi, le cercle n'est pas dessiné et le tour du joueur est passé.



# Gestion du choix du gagnant
Quand un joueur demande d'afficher l'aire via la variante Scores ou que la partie se termine, on parcourt chaque cercle et on prend
chaque point qui se trouve dans un cercle dans un ensemble pour chaque joueur, comme les ensembles ne peuvent pas avoir de doublons,
les pixels qui se retrouvent dans plusieurs cercles ne sont comptés qu'une seule fois, 
la longueur de ces deux ensembles correspond aux aires totales de chaque joueur.



# Gestion du menu
Pour le menu initial, à gauche se trouvent les zones qui correspondent aux modes de jeu, qu'on peut activer et désactiver en cliquant
sur ces zones, une zone est verte quand le mode de jeu est actif, sinon il est rouge. Pour lancer le jeu, il suffit d'appuyer sur la
zone verte qui se situe en bas à droite, tout objet du menu est supprimé et le jeu commence.
Cliquer sur une zone de mode de jeu verte la rend rouge et transforme la valeur booléenne de la variable attribuée au mode de jeu.
Tout en haut de la fenêtre se trouve l'entête de la page, avec le titre, un peu en bas à droite se trouve le bouton pour quitter le jeu.
à gauche se trouve la description des options du jeu, modifiables via le fichier settings.txt

    EXEMPLE : Cliquer sur la zone Sablier fait (sablier = not sablier), sablier qui est stocké dans une liste 'modes' avec les autres variables 
    des modes de jeu qui sont donc toutes des variables booléennes



# Variantes
    -Sablier : On demande à l'utilisateur de cliquer pendant un certain nombre de secondes, si il ne clique pas le tour est passé.
    -Scores : Affiche l'aire totale des cercles des joueurs pendant 2 secondes en appuyant sur la touche S, disponible qu'une seule fois par tour.
    -Économie (ou Taille de Boules) : Les deux joueurs commencent avec une certaine somme et ils doivent entrer la valeur du rayon avant de cliquer,
    une valeur initiale du rayon est prévue au cas ou le joueur ne rentre pas de valeur. Un joueur peut diviser les boules adverses avec une épargne vide.
    -Version dynamique : A chaque fin de tour, chaque cercle s'incrémente si possible.
    -Terminaison : Disponible qu'une seule fois par partie, permet de rajouter 5 rounds.
    -Obstacles : Des cercles sont générés aléatoirement sur le terrain, les cercles ne peuvent pas s'intersecter avec ces obstacles, on peut aussi
    charger un nombre d'obstacles aléatoires et des obstacles chargés via le fichier passé en argument dans la ligne de commande,
    qui est par défaut obstacles.txt 
