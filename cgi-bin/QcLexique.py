#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2021 LATEJCON"

import sys
from os import path
import time
import QcFichier
from QcIndex import QcIndex
from QcFichier import DEJBUT, FIN


def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print (f"""© l'ATEJCON.
Analyse le fichier plat du lexique du système Qc.
Donne l'identifiant d'un mot.

usage   : {script} <fichier Qc> [ "analyse" | "ident" <mot> ]
exemple : {script} Latejcon.qclexique
exemple : {script} Latejcon.qclexique id désoccultation
""")
    
def main():
    try:
        if len(sys.argv) < 2 : raise Exception()
        nomFichierQc = path.abspath(sys.argv[1])
        action = 'analyse' 
        if len(sys.argv) > 2 : action = sys.argv[2]
        mot = ''
        if len(sys.argv) > 3 : mot = sys.argv[3]
        analyse(nomFichierQc, action, mot)
    except Exception as exc:
        if len(exc.args) == 0: usage()
        else:
            print ("******************************")
            print (exc.args[0])
            print ("******************************")
            raise
        sys.exit()

def analyse(nomFichierQc, action, mot):
    qcLexique = QcLexique(nomFichierQc)
    if action.startswith('ana'):
        qcLexique.afficheFichierLexique()
    elif action.startswith('id'):
        identifiant = qcLexique.trouveIdentifiant(mot)
        print(f'identifiant : {identifiant}')
    qcLexique.close()
        
       
       
######################################################################################
# <donnejesIndexejes>     ::= <dejfinitionHash>
# <blocEnVrac>            ::= <donnejesHash>
# <dejfinitionHash>       ::= <flagIdHash=13> <identifiantHash> 
#                             <longueurDonnejes> <adresseDonnejes>
# <flagIdHash=13>         ::= <Entier1>
# <identifiantHash>       ::= <Entier3>
# <longueurDonnejes>      ::= <Entier3>
# <adresseDonnejes>       ::= <Entier4>
# <donnejesHash>          ::= { <mot> <identifiant> }
# <mot>                   ::= <MotUtf8>
# <identifiant>           ::= <EntierULat>
######################################################################################
# <flagIdHash=13>(1) <identifiantHash>(3) <longueurDonnejes>(3) <adresseDonnejes>(4) = 11
TAILLE_ENTREJE = 11
FLAG_IDHASH = 13
#############################################################
class QcLexique(QcIndex):
    def __init__(self, nomQcFichier, enEjcriture = False, nombreHash = 0):
        self.nomQcFichier = nomQcFichier
        # init la couche d'en-dessous
        QcIndex.__init__(self, self.nomQcFichier, enEjcriture, TAILLE_ENTREJE, nombreHash) 
        if enEjcriture: self.prejparation = {}
        if self.tailleEntreje != TAILLE_ENTREJE:
            raise Exception('{} : TAILLE_ENTREJE incompatibles'.format(self.nomQcFichier))

    ################################
    # prejpare l'ajout d'un mot
    def ajouteMot(self, mot):
        clefB = QcFichier.clefB(mot)
        index = clefB % self.nombreEntrejes
        if index not in self.prejparation: self.prejparation[index] = []
        self.prejparation[index].append(mot)
         
    ################################
    # fin de la prejparation, ejcriture sur le fichier
    def valideMots(self):
        identifiant = 0
        for (index, mots) in self.prejparation.items():
            listeMots = list(set(mots))
            # ejcrit ah la fin du fichier dans le bloc en vrac
            self.seek(0, FIN)
            adresseDonnejes = self.tell()
            for mot in mots:
                identifiant +=1
                self.ejcritMotUtf8(mot)
                self.ejcritNombreULat(identifiant)
            longueurDonnejes = self.tell() - adresseDonnejes
            # ejcrit dans le bloc indexej
            adresseIndex = self.donneAdresseIndex(index)
            self.seek(adresseIndex, DEJBUT)
            # <flagIdHash=13>(1) <identifiantHash>(3) <longueurDonnejes>(3) <adresseDonnejes>(5)
            self.ejcritNombre1(FLAG_IDHASH)
            self.ejcritNombre3(index)
            self.ejcritNombre3(longueurDonnejes)
            self.ejcritNombre4(adresseDonnejes)
        # ejcrit le bloc identification
        self.ejcritIdentificationFichier(identifiant, int(time.time()))

    ################################
    # retourne l'adresse et la longueur des donnejes d'une entreje de lexique
    def _trouveDonnejes(self, index):
        adresseIndex = self.donneAdresseIndex(index)
        self.seek(adresseIndex, DEJBUT)
        # <flagIdHash=13>(1) <identifiantHash>(3) <longueurDonnejes>(3) <adresseDonnejes>(4)
        flag = self.litNombre1()
        # entreje inutiliseje = graphie inconnue
        if flag == 0: return (0, 0)
        if flag != FLAG_IDHASH: 
            raise Exception('{} : pas FLAG_IDHASH à {:08X}'.format(self.nomQcFichier, self.tell() -1))
        if self.litNombre3() != index:
            raise Exception('{} : incohérence à {:08X}'.format(self.nomQcFichier, self.tell() -3))
        longueurDonnejes = self.litNombre3()
        adresseDonnejes = self.litNombre4()
        return (adresseDonnejes, longueurDonnejes)
        
    ################################
    # donne l'identifiant d'une graphie, 0 si pas trouveje
    def trouveIdentifiant(self, graphie):
        clefB = QcFichier.clefB(graphie)
        index = clefB % self.nombreEntrejes
        (adresseDonnejes, longueurDonnejes) = self._trouveDonnejes(index)
        # entreje inutiliseje = graphie inconnue
        if adresseDonnejes == 0: return 0
        adresseFinDonnejes = adresseDonnejes + longueurDonnejes
        self.seek(adresseDonnejes, DEJBUT)
        # { <mot> <identifiant> }
        while self.tell() < adresseFinDonnejes:
            mot = self.litMotUtf8()
            identifiant = self.litNombreULat()
            if mot == graphie: return identifiant
        return 0
        
    ################################
    # vidage complet du lexique sous forme d'une liste 
    def vidage(self):
        motsIdentifiants = []
        for index in range(self.nombreEntrejes):
            (adresseDonnejes, longueurDonnejes) = self._trouveDonnejes(index)
            # entreje inutiliseje 
            if adresseDonnejes == 0: continue
            adresseFinDonnejes = adresseDonnejes + longueurDonnejes
            self.seek(adresseDonnejes, DEJBUT)
            # { <mot> <identifiant> }
            while self.tell() < adresseFinDonnejes:
                mot = self.litMotUtf8()
                identifiant = self.litNombreULat()
                motsIdentifiants.append((identifiant, mot))
        motsIdentifiants.sort()
        return motsIdentifiants
        
    ################################
    # affiche les dejtails du fichier
    def afficheFichierLexique(self):
        self.afficheFichierIndex()
        longueurs = {}
        total = 0
        for index in range(self.nombreEntrejes):
            (adresseDonnejes, longueurDonnejes) = self._trouveDonnejes(index)
            longueur = 0
            if adresseDonnejes != 0: 
                adresseFinDonnejes = adresseDonnejes + longueurDonnejes
                self.seek(adresseDonnejes, DEJBUT)
                # { <mot> <identifiant> }
                while self.tell() < adresseFinDonnejes:
                    self.litMotUtf8()
                    self.litNombreULat()
                    longueur +=1
            if longueur not in longueurs: longueurs[longueur] = 0
            longueurs[longueur] +=1
            total += longueur
        print ("=============")
        print("NOMBRE D'INDEX             : ", self.nombreEntrejes)
        print("NOMBRE DE DONNÉES          : ", total)
        longueursListe = list(longueurs.items())
        longueursListe.sort()
        for (longueur, nombre) in longueursListe:
            print(f'{longueur} : {nombre}')
        print ("=============")
            
       
if __name__ == '__main__':
    main()

       
        
        

