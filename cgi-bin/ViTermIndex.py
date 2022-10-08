#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2022 LATEJCON"

import sys
from os import path
import time
from QcIndex import QcIndex
from QcFichier import DEJBUT, FIN

def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print (f"""© l'ATEJCON.
Analyse le fichier plat des index de termes système Vi.

usage   : {script} <fichier Vi> 
exemple : {script} Latejcon.vitermindex
""")
    
def main():
    try:
        if len(sys.argv) < 2 : raise Exception()
        nomFichierVi = path.abspath(sys.argv[1])
        action = 'analyse' 
        analyse(nomFichierVi, action)
    except Exception as exc:
        if len(exc.args) == 0: usage()
        else:
            print ("******************************")
            print (exc.args[0])
            print ("******************************")
            raise
        sys.exit()

def analyse(nomFichierVi, action):
    viTermIndex = ViTermIndex(nomFichierVi)
    if action.startswith('ana'):
        viTermIndex.afficheFichierViTermIndex()
    viTermIndex.close()
    
######################################################################################
# <donnejesIndexejes>     ::= { <dejfinition> }
# <blocEnVrac>            ::= { <donnejesTerme> }
# <dejfinition>           ::= <flagDejfinition=17> <identifiantTerme>
#                             <nombreImages> <adresseDonnejes>
# <flagDejfinition=17>    ::= <Entier1>
# <identifiantTerme>      ::= <Entier3>
# <nombreImages>          ::= <Entier3>
# <adresseDonnejes>       ::= <Entier4>
# <donnejesTerme>         ::= <flagDonnejes=63> { <identDocRelatif> }
# <flagDonnejes=63>       ::= <Entier1>
# <identDocRelatif>       ::= <EntierULat>
######################################################################################
TAILLE_ENTREJE = 11
FLAG_DEJFINITION = 17
FLAG_DONNEJES = 63
#############################################################
class ViTermIndex(QcIndex):
    def __init__(self, nomViFichier, enEjcriture = False, nombreIdentifiants = 0):
        self.nomViFichier = nomViFichier
        # init la couche d'en-dessous
        # nombreIdentifiants +1 parce que le premier identifiant est 1
        QcIndex.__init__(self, self.nomViFichier, enEjcriture, TAILLE_ENTREJE, nombreIdentifiants +1) 
        if self.tailleEntreje != TAILLE_ENTREJE:
            raise Exception('{} : TAILLE_ENTREJE incompatibles'.format(self.nomViFichier))
        
    ################################
    # ajoute une description de terme 
    def ajouteTerme(self, identifiantTerme, description):
        # ejcrit ah la fin du fichier dans le bloc en vrac
        self.seek(0, FIN)
        adresseDonnejes = self.tell()
        # <flagDonnejes=63>(1) { <identDocRelatif> }
        self.ejcritNombre1(FLAG_DONNEJES)
        identifiantPrejcejdent = 0
        for identifiantImage in description:
            identifiantRelatif = identifiantImage - identifiantPrejcejdent
            self.ejcritNombreULat(identifiantRelatif)
            identifiantPrejcejdent = identifiantImage
        # ejcrit dans le bloc indexej
        adresseIndex = self.donneAdresseIndex(identifiantTerme)
        self.seek(adresseIndex, DEJBUT)
        # <flagDejfinition=17>(1) <identifiantTerme>(3) <nombreImages>(3) <adresseDonnejes>(4)
        self.ejcritNombre1(FLAG_DEJFINITION)
        self.ejcritNombre3(identifiantTerme)
        self.ejcritNombre3(len(description))
        self.ejcritNombre4(adresseDonnejes)
        
    ################################
    # retourne l'ensemble des donnejes d'un terme (la liste des identifiants d'images)
    def trouveDonnejes(self, identifiantTerme):
        adresseIndex = self.donneAdresseIndex(identifiantTerme)
        self.seek(adresseIndex, DEJBUT)
        # <flagDejfinition=17>(1) <identifiantTerme>(3) <nombreImages>(3) <adresseDonnejes>(4)
        flag = self.litNombre1()
        # entreje inutiliseje = bizarre mais bon...
        if flag == 0: return []
        if flag != FLAG_DEJFINITION: 
            raise Exception('{} : pas FLAG_DEJFINITION à {:08X}'.format(self.nomViFichier, self.tell() -1))
        if self.litNombre3() != identifiantTerme:
            raise Exception('{} : incohérence à {:08X}'.format(self.nomViFichier, self.tell() -3))
        nombreImages = self.litNombre3()
        adresseDonnejes = self.litNombre4()
        # construit le rejsultat
        self.seek(adresseDonnejes, DEJBUT)
        flag = self.litNombre1()
        if flag != FLAG_DONNEJES: 
            raise Exception('{} : pas FLAG_DONNEJES à {:08X}'.format(self.nomViFichier, self.tell() -1))
        rejsultat = []
        identifiantPrejcejdent = 0
        for ii in range(nombreImages):
            identifiantRelatif = self.litNombreULat()
            identifiantImage = identifiantPrejcejdent + identifiantRelatif
            identifiantPrejcejdent = identifiantImage
            rejsultat.append(identifiantImage)
        return rejsultat
        
    ################################
    # affiche les dejtails du fichier
    def afficheFichierViTermIndex(self):
        self.afficheFichierIndex()
        longueurs = {}
        total = 0
        vides = []
        for identifiantTerme in range(1, self.nombreEntrejes):
            longueur = len(self.trouveDonnejes(identifiantTerme))
            if longueur == 0: vides.append(identifiantTerme)
            if longueur not in longueurs: longueurs[longueur] = 0
            longueurs[longueur] +=1
            total += longueur
        print ("=============")
        print('NOMBRE DE FORMES           : ', self.nombreEntrejes -1)
        print("NOMBRE DE DONNÉES          : ", total)
        longueursListe = list(longueurs.items())
        longueursListe.sort()
        for (longueur, nombre) in longueursListe:
            print(f'{longueur} : {nombre}')
        print ("=============")
        print(vides)
        
            
if __name__ == '__main__':
    main()
        
        
        
        
