#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from math import sin, cos, atan2, dist
from upemtk import *
from time import time, sleep
from random import randrange,choice
from re import sub
from sys import argv
import os.path

###########################################################################
# Gestion de l'affichage
###########################################################################

def affichage_tour(numTour,nbTours): 
    efface('rounds')
    texte(17*l/20,h/32,f'Round {(numTour//2)+1}/{nbTours//2+nbTours%2}','white','center',taille=taille,tag='rounds')

def affichage_timer(temps,couleur):
    efface('timer')
    texte(19*l/20,h/32,f'{temps:.1f}s',couleur,'center',taille=taille,tag='timer')

def affichage_tour_joueur(typeJoueur):
    efface('tour')
    if typeJoueur == 'vert':
        couleur = '#64C850'
    else:
        couleur = '#ef271b'
    texte(l/2,h/32,f'Tour du joueur {typeJoueur}',couleur,'center',taille=5*taille//4,tag='tour')

def affichage_gagnant_partie(gagnant):
    efface('terminaison')
    efface('timer')
    efface('tour')

    mise_a_jour()
    sleep(0.5)
    rectangle(l/4,h/4,l*3/4,h*3/4,'black','#1c1c1c')
    texte(l/2,h/2,'Et le gagnant est .','white','center',tag='suspens')
    mise_a_jour()
    sleep(0.3)
    efface('suspens')

    texte(l/2,h/2,'Et le gagnant est ..','white','center',tag='suspens')
    mise_a_jour()
    sleep(0.5)
    efface('suspens')

    texte(l/2,h/2,'Et le gagnant est ...','white','center',tag='suspens')
    mise_a_jour()
    sleep(0.5)
    efface('suspens')
    

    if gagnant == 'vert':
        texte(l/2,h/2,'Le joueur Vert','#64C850',taille=2*taille,ancrage='center')
    elif gagnant == 'rouge':
        texte(l/2,h/2,'Le joueur Rouge','#C92519',taille=2*taille,ancrage='center')
    else:
        texte(l/2,h/2,'Egalité','white',taille=2*taille,ancrage='center')
    mise_a_jour()
    sleep(3)

def affichage_aire(aires):
    efface('score')
    texte(l/2 - l/16,h/16,f'{int(aires[0])}','#64C850','ne',taille=taille,tag='score')
    texte(l/2 + l/16,h/16,f'{int(aires[1])}','#ff2323',ancrage='nw',taille=taille,tag='score') 

def affichage_prix(prix,couleur):
    efface('prix')
    if prix == '':
        prix = 0
    texte(l/7,h/32,prix,couleur,'center',taille=taille,tag='prix')

def affichage_epargne(epargnes):
    efface('epargnes')
    texte(l/5,h/32,epargnes['vert'],'#64C850','center',taille=taille,tag='epargnes')
    texte(l/4,h/32,epargnes['rouge'],'#C92519','center',taille=taille,tag='epargnes')

def afficher_variante(texteV,variante,CouleurTexte):
    """
    Permet l'affichage un texte de variante sans dépasser son cadre
    """
    efface('variante')
    texteFinal = f' {variante} :\n\n'
    longueur = 0
    for mot in texteV.split():
        if longueur + longueur_texte(mot) > 3*l/8 : #La phrase saute à la ligne si elle dépasse
            texteFinal = f'{texteFinal}\n {mot}'
            longueur = longueur_texte(mot)
        else:
            texteFinal = f'{texteFinal} {mot}'
            longueur += longueur_texte(mot)

    texte(25*l/48,7*h/12,texteFinal,CouleurTexte,'center',taille=taille,tag='variante')

############################################################################
# Gestion des coordonnés
############################################################################

def coordonnes_point3(point1,point2,distance):
    """
    Permet d'obtenir les coordonnées d'un point P3 à partir de
    deux points P1 et P2 et de la distance P1-P3
    Fonctionne tant que les coordonnées sont stockés dans PointN de 
    cette manière : (xn,yn,...) dans un itérable
    
    :param tuple point1: (x1,y1)
    :param tuple point2: (x2,y2)
    :param distance: Distance entre le point 1 et le point 3
    :return: (x3, y3)
    """
    x1,y1 = point1[0],point1[1]
    x2,y2 = point2[0],point2[1]

    angle = atan2(y2-y1,x2-x1) #ANGLE P1-P2, donc du centre initial et du clic
    x3 = x1 + distance * cos(angle)
    y3 = y1 + distance * sin(angle)
    return x3, y3

############################################################################
# Gestion des cercles
############################################################################

def verifier_placement(x,y,rayon,cerclesEnnemis,obstacles,cercleDetecte=None,rayonCercleDetecte=None):
    """
    Vérifie la validité d'un cercle à tracer
    """
    if cercleDetecte: #SI IL YA AU MOINS AU CERCLE 
        if rayonCercleDetecte < cercleDetecte[2]: #SI LE CLIC EST INCLUS DANS LE CERCLE ENNEMI ON AUTORISE LES CLICS PRES DES BORDS
            return True 

    if obstacles:
        for xObstacle,yObstacle,rayonObstacle in obstacles:
            if dist((xObstacle,yObstacle),(x,y)) < rayon+rayonObstacle:
                return False
        
    for xEnnemi,yEnnemi,rayonEnnemi,idEnnemi in cerclesEnnemis:
        if dist((x,y),(xEnnemi,yEnnemi)) < rayon + rayonEnnemi:
            return False
    if x < rayon or y - rayon < l/32 +2 : #SI LE CERCLE TOUCHE LE BORD DU HAUT OU A GAUCHE
        return False
    elif l - x < rayon or h - y < rayon : #SI LE CERCLE TOUCHE LES BORD DU BAS OU A DROITE
        return False 
    return True

def cercle_ennemi_plus_proche(x,y,cerclesEnnemis):
    """
    Permet d'avoir le cercle ennemi le plus proche du clic 

    :param float x: Coordonnée x du clic
    :param float y: Coordonnée y du clic
    :param list cerclesEnnemis: Liste des cercles ennemis
    """
    if cerclesEnnemis == [] :
        return None,None
    cercleLePlusPres = None
    distanceMini = dist((x,y),(cerclesEnnemis[0][0],cerclesEnnemis[0][1]))

    for cercleEnnemi in cerclesEnnemis:
        xc, yc = cercleEnnemi[0],cercleEnnemi[1]
        distance = dist((x,y),(xc,yc))

        if distance <= distanceMini:
            distanceMini = distance
            cercleLePlusPres = cercleEnnemi
    return cercleLePlusPres, distanceMini

def tracer_cercle(x,y,rayon,cercles,numTour,obstacles): 
    """
    Trace le(s) cercle(s) en fonction du clic du joueur et de sa position
    relative avec le cercle ennemi le plus proche
    
    :param float x: Coordonnée x du clic
    :param float y: Coordonnée y du clic
    :param float rayon: Rayon du cercle a tracer
    :param list cercles: Liste des cercles
    :param int numTour: Numéro du tour
    """
    efface('score')
    if x == None: #SI LE JOUEUR N'A PAS CLIQUE (sablier activé)
        return

    cerclesEnnemis = cercles[not numTour%2]
    joueur_actif, autre_joueur = joueur_du_tour(numTour)
    cercleProche,distanceClicCentre = cercle_ennemi_plus_proche(x,y,cerclesEnnemis) #ON PREND LE CERCLE LE PLUS PROCHE
    if not verifier_placement(x,y,rayon,cerclesEnnemis,obstacles,cercleProche,distanceClicCentre):
        return

    if cercleProche is None: #SI IL N'Y A PAS DE CERCLE ENNEMI
        idC = cercle(x,y,rayon,'black',joueur_actif[1])
        cercles[numTour%2].append((x,y,rayon,idC))
        return
    
    if distanceClicCentre < cercleProche[2] : #LE CLIC EST INCLUS DANS LE CERCLE ENNEMI -> DIVISION DU CERCLE
        rayon = cercleProche[2]
        NouveauRayonClic = rayon-distanceClicCentre #RAYON DU NOUVEAU CERCLE AVEC POUR CENTRE LE CLIC
        idC1 = cercle(x,y,NouveauRayonClic,'black',autre_joueur[1])
        cercles[not numTour%2].append((x,y,NouveauRayonClic,idC1))

        x3, y3 = coordonnes_point3((x,y),(cercleProche),rayon) #CALCUL DU CENTRE DE L'AUTRE CERCLE FORME
        idC2 = cercle(x3,y3,(rayon-NouveauRayonClic),'black',autre_joueur[1])
        cercles[not numTour%2].append((x3,y3,rayon-NouveauRayonClic,idC2))

        cercles[not numTour%2].pop(cercles[not numTour%2].index(cercleProche))
        efface(cercleProche[3])
        return True
        
    elif not (cercleProche[2] < distanceClicCentre < rayon + cercleProche[2]) and rayon: 
        
        idC = cercle(x,y,rayon,'black',joueur_actif[1])
        cercles[numTour%2].append((x,y,rayon,idC))

def incrementation_cercles(cercles,obstacles):
    """
    Incrémentation des cercles
    à chaque fin de tour
    """
    for numJoueur in (0,1):
        i = 0
        visites = set()
        while i < len(cercles[numJoueur]):
            x, y, rayon, id = cercles[numJoueur][i]
            if id in visites or not verifier_placement(x,y,rayon*1.05,cercles[not numJoueur],obstacles):
                i += 1
                continue
            efface(id)
            cercles[numJoueur].pop(i)
            
            idIncrementation = cercle(x,y,rayon*1.05,'black',('#6DC267','#E74545')[numJoueur])
            cercles[numJoueur].append((x,y,rayon*1.05,idIncrementation))
            visites.add(idIncrementation)

def determiner_gagnant(cercles):
    """
    Compte l'aire totale de chaque joueur et attribut le gagnant
    """
    aireVerte = ensemble_points(cercles[0])
    aireRouge = ensemble_points(cercles[1])
    if aireVerte > aireRouge:
        return 'vert', aireVerte, aireRouge 
    elif aireRouge > aireVerte:
        return 'rouge', aireVerte, aireRouge 
    else:
        return None, aireVerte, aireRouge

def ensemble_points(cercles):
    """
    Compte chaque pixel situé dans une liste de cercles
    """
    return len({(i,j) for x,y,rayon,id in cercles for i in range(int(x-rayon),int(x+rayon)+1) for j in range(int(y-rayon),int(y+rayon)+1)
    if dist((x,y),(i,j)) <= rayon})

############################################################################
# Gestion du jeu
############################################################################

def generer_obstacles(nbObstacles,obstaclesCharges):
    obstacles = set()
    couleurs = ('#9d8ca1','#a7abdd','#9993b2','#b4d4ee')
    for _ in range(nbObstacles):
        x = randrange(20,l-10)
        y = randrange(h//16+33,h-20)
        rayon = randrange(10,40)

        obstacles.add((x,y,rayon))
        cercle(x,y,rayon,'black',choice(couleurs))

    for x, y, rayon in obstaclesCharges:
        x,y,rayon = int(x),int(y),int(rayon)
        obstacles.add((x,y,rayon))
        cercle(x,y,rayon,'black',choice(couleurs))

    return obstacles

def verifier_prix(prix,epargnes,joueur):
    if epargnes[joueur] == 0 or prix == '':
        return True
    prix = int(prix)
    if prix > epargnes[joueur] :
        return False
    elif prix < 5:
        return False
    return True

def joueur_du_tour(numTour):
    """
    Permet de déterminer la couleur des boules du joueur du tour et celles de l'ennemi 
    Si le numéro du tour est impair, alors c'est au vert de jouer, sinon, c'est au tour
    du joueur rouge
    """
    if numTour%2: 
        return (('rouge','#E74545'),('vert','#6DC267')) #SI numTour EST IMPAIR
    return (('vert','#6DC267'),('rouge','#E74545'))    

def gestion_evenement(ev,typeEv,joueur,scores,cercles,scoreTour,tempsAffichageScore,terminaison,economie, prix=None,epargnes=None):
    """
    S'occupe de la gestion des évenements des joueurs
    """
    if economie:
        if typeEv == 'Touche':
            valeurEv = touche(ev)
            if scores and scoreTour:
                if touche(ev) == 's' or touche(ev) == 'S':
                    scoreTour = False
                    a = determiner_gagnant(cercles)[1:]
                    affichage_aire(a)
                    tempsAffichageScore = time() + 2

            if valeurEv in '0123456789': #TOUCHES NUMERIQUES
                prix += valeurEv
            elif valeurEv[:-1] == 'KP_': #TOUCHES NUMERIQUES SUR LINUX
                prix += valeurEv[-1]
            elif valeurEv == 'BackSpace': #EFFACER 
                prix = prix[:-1]
            if len(prix) > 3: #SI LA VALEUR ENTRE EST TROP GRANDE
                prix = ''
            affichage_prix(prix,joueur[1])

        elif typeEv == 'ClicGauche': #LE JOUEUR CLIQUE
            x, y = clic_x(ev), clic_y(ev)
            if terminaison:
                if dist((x, y), (3*l/4.3,h/32)) < 18:
                    return {'prix':0,'epargnes':epargnes,'scoreTour':True,'tempsAffichageScore':tempsAffichageScore,'termine':True}
            if verifier_prix(prix,epargnes,joueur[0]):
                if epargnes[joueur[0]] == 0:
                    return {'x':x,'y':y,'prix':0,'epargnes':epargnes}
                if prix == '': 
                    prix = rayonInitial if epargnes[joueur[0]] >= rayonInitial else epargnes[joueur[0]] #SI L'EPARGNE A MOINS DE 40 POINTS, ON PREND TOUT
                epargnes[joueur[0]] -= int(prix) #ON DECREMENTE L'EPARGNE DU JOUEUR 
                efface('prix')
                affichage_epargne(epargnes)
                return {'x':x,'y':y,'prix':int(prix),'epargnes':epargnes}
            else:
                efface('prix')
                texte(l/10,h/32,'Prix invalide','white','center',taille=taille,tag='prix')
                prix = ''
                
        if tempsAffichageScore and time() >= tempsAffichageScore: 
            efface('score')
        return {'prix':prix,'epargnes':epargnes,'scoreTour':scoreTour,'tempsAffichageScore':tempsAffichageScore}

    else: #SI LE MODE DE JEU ECONOMIE N'EST PAS ACTIVE
        if typeEv == 'ClicGauche': #LE JOUEUR CLIQUE
            x,y = clic_x(ev),clic_y(ev)
            if terminaison:
                if dist((x, y), (3*l/4.3,h/32)) <= taille:
                    return {'termine':True}
            return {'x':x,'y':y}
        elif scores and scoreTour and typeEv == 'Touche':
            if touche(ev) == 's' or touche(ev) == 'S':
                scoreTour = False
                a = determiner_gagnant(cercles)[1:]
                affichage_aire(a)
                tempsAffichageScore = time() + 2
        if tempsAffichageScore and time() >= tempsAffichageScore: 
            efface('score')
        return {}
   
def action_joueur(cercles,joueur,sablier,scores,terminaison,epargnes,economie,tempsSablier):
    """
    Boucle principale qui permet de gérer les actions des joueurs
    """
    tempsAffichageScore = None
    scoreTour = scores
    prix = ''        
    tempsMax = time() + tempsSablier if sablier else None
    if economie :
        affichage_epargne(epargnes)
        while tempsMax is None or time() < tempsMax:
            ev = donne_evenement()
            typeEv = type_evenement(ev)
            resultats = gestion_evenement(ev,typeEv,joueur,scores,cercles,scoreTour,tempsAffichageScore,terminaison,economie,prix,epargnes)
            prix = resultats['prix']
            if 'termine' in resultats:
                return resultats
            if 'x' in resultats:
                return resultats
            if sablier:
                affichage_timer(tempsMax-time(),joueur[1])
            mise_a_jour()
        return {'epargnes':epargnes,'prix':0} #TEMPS PASSE

    else: #MODE ECONOMIE DESACTIVE
        while tempsMax is None or time() < tempsMax:
            ev = donne_evenement()
            typeEv = type_evenement(ev)
            resultats = gestion_evenement(ev,typeEv,joueur,scores,cercles,scoreTour,tempsAffichageScore,terminaison,economie=False)
            if 'termine' in resultats:
                return resultats
            if 'x' in resultats:
                return resultats
            if sablier:
                affichage_timer(tempsMax-time(),joueur[1])
            mise_a_jour()
        return {}

def menu_initial(options):
    """
    Affiche le menu initial permettant de choisir les modes de jeu
    et de lancer la partie
    """

    BoutonVert="#46A040"
    BoutonRouge="#2e2e2e"
    CouleurFondFenetre="#2e2e2e"
    TexteEntete="#5F7DBE"
    BordureModes="#68217A"
    BordureJouer="#5F7BDE"
    _E74545="#E74545"
    CouleurBordureParametres="#5d5396"
    _22222="#222222"
    CouleurTexte="#FFFFFF"

    couleurBoutons = (BoutonVert,BoutonRouge) #VERT, ROUGE
    rectangle(0, 0, l, h, CouleurFondFenetre, CouleurFondFenetre, 2) #FOND DE LA FENETRE

    rectangle(1,1, l-1, h/6, TexteEntete, _22222,3, 'menu') #ENTETE DU MENU
    texte(l/2, h/12, 'Bataille de Boules', TexteEntete, 'center', taille=taille*2, tag='menu') #TEXTE DE L'ENTETE DU MENU

    rectangle(2, h/6+4, (l/8)+l/6 , h-3, BordureModes, _22222, 3, 'menu') #ZONE DES MODES DE JEU

    boutonJouer = (3*l/4, 3*h/4) #COORDONNEES DU BOUTON JOUER
    rectangle(3*l/4,3*h/4,l-1,h-1,BordureJouer,_22222,3,'menu') #BOUTON JOUER
    texte(7*l/8,7*h/8 ,'JOUER',TexteEntete,'center',taille=taille*2,tag='menu') #TEXTE 'JOUER'

    boutonQuitter = (3*l/4,h/6+3,h/3) #COORDONNEES DU BOUTON QUITTER
    rectangle(3*l/4,h/6+3,l,h/3,_E74545,_22222,3,'menu') #BOUTON QUITTER
    texte(7*l/8, 3*h/12,'Quitter',_E74545,'center',taille=taille*2,tag='menu') #TEXTE QUITTER
    
    rectangle(3*l/4,h/3+2,l,3*h/4-2,CouleurBordureParametres,_22222,2,tag='menu') #ZONE DES PARAMETRES
    texte(3*l/4-10,h/3+3 + (3*h/4-3-h/3+3)/2,f'\
    {"Nombre Obstacles":<20}\n\
    {"Largeur Fenêtre":<20}\n\
    {"Hauteur Fenêtre":<20}\n\
    {"Épargne Rouge":<20}\n\
    {"Durée Sablier":<20}\n\
    {"Nombre Rounds":<20}\n\
    {"Épargne Vert":<20}\n\
    {"Rayon Initial":<20}\
    ', CouleurTexte,'w',"Arial",taille=taille-4,tag='menu')

    texte(l,h/3+3 + (3*h/4-3-h/3+3)/2,f'\
    => {options["nombreObstacles"]:<5}\n\
    => {options["largeurFenetre"]:<5}\n\
    => {options["hauteurFenetre"]:<5}\n\
    => {options["epargneRouge"]:<5}\n\
    => {options["tempsSablier"]:<5}\n\
    => {options["nombreDeRounds"]:<5}\n\
    => {options["epargneVert"]:<5}\n\
    => {options["rayon"]:<5}',CouleurTexte,'e',taille=taille-4,tag='menu')

    sablier,scores,economie,dynamique,terminaison,obstacles = False,False,False,False,False,False #AU LANCEMENT, LES MODES DE JEU SONT INACTIFS
    modes    = [ sablier,  scores,   economie,  dynamique,  terminaison,  obstacles]
    nomModes = ['Sablier','Scores', 'Économie','Dynamique','Terminaison','Obstacles']
    listeProprietesModes = [] # (x,y) du coin en haut à gauche ; (x,y) du coin en bas à droite ; identifiant du mode
    textesVariantes = {
    'Sablier':f'Chaque joueur a {options["tempsSablier"]} secondes pour jouer, après le temps passé, il perd son tour.',
    'Scores':f'Un joueur peut appuyer sur la touche \'S\' pour voir les scores de chaque joueur, Disponible une seule fois par tour.',
    'Économie':f'Chaque joueur possède un budget initial, on peut tracer une boule plus ou moins grande selon la valeur demandée par le joueur,\
    On entre la taille voulue en appuyant sur les touches numériques, si la valeur n\'est pas valide, le programme l\'indique et il doit réiterer.\
    Si le joueur appuye avec un prix nul, une boule avec la taille initiale est posée.',
    'Dynamique':f'Chaque boule voit sa taille augmenter à la fin de chaque tour. Elles s\'arrêtent de grandir si elles touchent un obstacle ou une boule ennemie.',
    'Terminaison':f'Une fois par partie, un joueur peut décider que le jeu se finit en 5 rounds. Il faut appuyer sur le bouton bleu pour l\'activer ',
    'Obstacles':f'Des obstacles sont générés sur le terrain de jeu, une boule ne peut pas intersecter un obstacle, sur le fichier des obstacles sont décidés\
    le nombre d\'obstacles aléatoires et la répartition de ceux chargés. Pour charger une zone de jeu, il faut indiquer dans la ligne de commande le nom du fichier après le nom du fichier du jeu.\
    Le fichier actuellement chargé est : {options["nomFichierObstacles"]}'}

    for i in range(6): #CREATION DE CHAQUE RECTANGLE CORRESPOND A UN MODE DE JEU
        xCoinHautGauche,yCoinHautGauche = (l/16),((i+2)*(h/8.45))
        xCoinBasDroite,yCoinBasDroite = ((l/16)+l/6),(((i+2)*h/8.45)+h/11) 
        rectangle(xCoinHautGauche,yCoinHautGauche,xCoinBasDroite,yCoinBasDroite,couleurBoutons[1],couleurBoutons[1],1,'menu')                                 

        listeProprietesModes.append((xCoinHautGauche,yCoinHautGauche,xCoinBasDroite,yCoinBasDroite,i))
        texte((xCoinBasDroite + xCoinHautGauche) / 2, (yCoinBasDroite + yCoinHautGauche) / 2, nomModes[i],
        'white','center',taille=taille,tag='menu') #NOM DES MODES DE JEU

    clicx,clicy,typeEvent = attente_clic()
    while not (clicx >= boutonJouer[0] and clicy >= boutonJouer[1]): #TANT QUE LE CLIC NEST PAS DANS LA BOITE JOUEUR 
        if (clicx >= boutonQuitter[0] and clicy >= boutonQuitter[1] and clicy <= boutonQuitter[2]):
            ferme_fenetre()
            exit()
        for xCoinHautGauche,yCoinHautGauche,xCoinBasDroite,yCoinBasDroite,id in listeProprietesModes:
            if (clicx <= xCoinBasDroite and clicx >= xCoinHautGauche and clicy <= yCoinBasDroite and clicy >= yCoinHautGauche): 
                modes[id] = not modes[id] #SI LE CLIC EST INCLUS DANS UNE ZONES DES MODES DE JEU, ON INVERSE LA VALEUR DU MODE
                rectangle(xCoinHautGauche,yCoinHautGauche,xCoinBasDroite,yCoinBasDroite,couleurBoutons[not modes[id]],couleurBoutons[not modes[id]],1,'menu')
                texte((xCoinBasDroite + xCoinHautGauche) / 2, (yCoinBasDroite + yCoinHautGauche) / 2,nomModes[id],'white','center',taille=taille,tag='menu')
                if modes[id]:
                    afficher_variante(textesVariantes[nomModes[id]], nomModes[id],CouleurTexte)
                break
        clicx,clicy,typeEvent = attente_clic()
    efface('menu')
    efface('variante')
    return modes

def recup_donnees(donnees):
    """
    Renvoie tous les paramètres dans un dictionnaire
    """
    with open(donnees) as options:
        options = options.readlines()
        dico = dict()
        for ligne in options:
            ligne = sub(r'[\n ]','',ligne)
            if ligne == '' or ligne[0] == '#':
                continue
            option, valeur = ligne.split('=')
            dico[option] = int(valeur)
        return dico

def recup_obstacles(fichierObstacles):
    """
    Renvoie la liste des obstacles chargés, et le nombre d'obstacles aléatoires
    """
    with open(fichierObstacles) as obstacles:
        obstacles = obstacles.readlines()
        nbObstacles = 0
        obstaclesCharges = []
        for ligne in obstacles:
            ligne = sub(r'[\n ]','',ligne)
            if ligne == '' or ligne[0] == '#': #Si la ligne est un commentaire ou est vide
                continue
            elif ligne[0] == '*':
                nbObstacles = int(ligne[1:])
                continue
            o = tuple(ligne.split(';'))   
            obstaclesCharges.append(o)
    return obstaclesCharges, nbObstacles

def main():
    if len(argv) > 1 and os.path.exists(argv[1]): #on charge le fichier d'obstacles indiqué 
        fichierObstacles = argv[1]
    else:
        fichierObstacles = 'obstacles.txt'

    options = recup_donnees('settings.txt')
    obstaclesCharges, nbObstacles = recup_obstacles(fichierObstacles)

    global l, h #MIEUX VAUT UTILISER DES VARIABLES GLOBALES PLUTOT QUE DE LES METTRE EN PARAMETRE A QUASI CHAQUE FONCTION
    l, h = options['largeurFenetre'], options['hauteurFenetre']
    global taille #Taille du texte responsive par rapport aux dimensions de la fenêtre
    taille = int((l+h)*(0.010667))

    options['nombreObstacles'] = nbObstacles + len(obstaclesCharges)
    global rayonInitial 
    rayonInitial = options['rayon']
    nbTours = options['nombreDeRounds']
    tempsSablier = options['tempsSablier']
    options['nomFichierObstacles'] = fichierObstacles
    cree_fenetre(l, h)

    while 1:
        epargnes = {'vert':options['epargneVert'],'rouge':options['epargneRouge']}
        sablier,  scores,  economie,  dynamique,  terminaison,  obstacles = menu_initial(options)
        cercles = [[],[]] #La première liste correspond aux cercles verts, la deuxième aux cercles rouges
        rectangle(0,0,l,h/16,'black','#1c1c1c',2) #SEPARATION ENTETE ET TERRAIN DE JEU
        uniqueTerminaison = terminaison 

        listeObstacles = generer_obstacles(nbObstacles,obstaclesCharges) if obstacles else None
        if terminaison:
            cercle(3*l/4.3,h/32,taille,'black','#2986cc',tag='terminaison')
            texte(3*l/4.3,h/32,'T','white',taille=taille,ancrage='center', tag='terminaison')
        if economie:
            rectangle(l/32,0,l/6,h/16,'white','#222222')

        numTour = 0
        finJeu = nbTours*2 #Chaque joueur joue chacun nbTours
        while numTour < finJeu: #VERT = PAIR, ROUGE = IMPAIR
            joueur = joueur_du_tour(numTour)[0] #Attribution du joueur
            affichage_tour_joueur(joueur[0])
            affichage_tour(numTour,finJeu)

            resultats = action_joueur(cercles,joueur,sablier,scores,terminaison,epargnes,economie,tempsSablier)
            
            if 'termine' in resultats and uniqueTerminaison:
                finJeu = numTour + 10 #On termine le jeu dans 10 tours
                uniqueTerminaison = False #Terminaison ne peut être activé qu'une fois dans une partie
                efface('terminaison')
                continue
                
            if economie:
                rayon = resultats['prix']
                epargnes = resultats['epargnes']
                affichage_epargne(epargnes)
            else:
                rayon = rayonInitial

            if 'x' in resultats:
                x = resultats['x']
                y = resultats['y']
                if tracer_cercle(x,y,rayon,cercles,numTour,listeObstacles) and economie: #On réalise l'action du joueur
                    epargnes[joueur[0]] += rayon #On rembourse si une division a eu lieu
            
            if dynamique:
                incrementation_cercles(cercles,listeObstacles)
            numTour +=1

        gagnant = determiner_gagnant(cercles)
        affichage_gagnant_partie(gagnant[0])

        clic()
        efface_tout()
    ferme_fenetre()

#########################
if __name__ == '__main__':
    main()
