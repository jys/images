#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2022 LATEJCON"

import sys
from os import path
import codecs
import re
from QcLexique import QcLexique
from ViTermIndex import ViTermIndex

def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print (f"""© l'ATEJCON.
Programme de test de la classe ViRecherche.

usage   : {script} <racine fichiers> <texte recherché> 
usage   : {script} ressources/Latejcon "Gustave Flaubert"
""")

def main():
    try:
        if len(sys.argv) < 3 : raise Exception()
        racine = sys.argv[1]
        texte = sys.argv[2]
        rechercheDocs(racine, texte)
    except Exception as exc:
        if len(exc.args) == 0: usage()
        else:
            print ("******************************")
            print (exc.args[0])
            print ("******************************")
            raise
        sys.exit()

def rechercheDocs(racine, texte):
    viRecherche = ViRecherche(racine)
    idents = viRecherche.rechercheIdentsParTexte(texte)
    print(f'{len(idents)} identifiants trouvés')
    print(idents)
    viRecherche.close()
    
################################################################
class ViRecherche:
    def __init__(self, racine):
        # ouvre les 2 classes
        self.viLexique = QcLexique(f'{racine}.vilexique')
        self.viTermIndex = ViTermIndex(f'{racine}.vitermindex')
        # vejrifie l'apairage des fichiers
        ident1 = self.viLexique.donneIdentificationFichier()
        ident2 = self.viTermIndex.donneIdentificationFichier()
        if ident1 != ident2: raise Exception('FICHIERS NON APAIRÉS')
        
    ################################
    def close(self):
        self.viLexique.close()
        self.viTermIndex.close()
                
    ###############################
    # ah partir d'un texte, trouve une liste d'identifiants d'images 
    # si le texte a des ·, le traite comme des mots clefs 
    def rechercheIdentsParTexte(self, texte):
        if '·' in texte: mots = texte.split('·')
        else: mots = texte.split()
        etOk = False
        for mot in mots:
            mot = mot.strip()
            if mot == '': continue
            mot = mot.replace(' ', '_')
            idsDocsMot = self.__rechercheParMot(mot)
            if len(idsDocsMot) == 0: continue
            if etOk : idsDocs &= idsDocsMot
            else: idsDocs = idsDocsMot
            etOk = True
        if not etOk: idsDocs = set()
        # recherche avec tous les mots concatejnejs
        if '·' in texte: idsDocs |= self.__rechercheParMot('_'.join(mots))
        return sorted(list(idsDocs))
            
    ###############################
    # ah partir d'un mot simple, trouve une liste de documents
    def __rechercheParMot(self, mot):
        # 1) mot tel quel
        idsDocs = self.__rechercheUnitaire(mot)
        # 2) mot en majuscules
        idsDocs |= self.__rechercheUnitaire(mot.upper())
        # 3) mot en minuscules
        idsDocs |= self.__rechercheUnitaire(mot.lower())
        # 4) avec les premiehres lettres en majuscules
        sousmots = mot.split('_')
        for ii in range(len(sousmots)): sousmots[ii] = sousmots[ii].title()
        idsDocs |= self.__rechercheUnitaire('_'.join(sousmots))
        return idsDocs
    
    ###############################        
    # ah partir d'un mot, trouve une liste de documents
    def __rechercheUnitaire(self, mot):
        identMot = self.viLexique.trouveIdentifiant(mot)
        # si mot inconnu, aucun document
        if identMot == 0: return set()
        # sinon sort la liste des documents concernejs
        return set(self.viTermIndex.trouveDonnejes(identMot))
       
        
if __name__ == '__main__':
    main()

