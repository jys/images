#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2022 LATEJCON"

import sys
from os import path
import codecs
import re
import subprocess
import pickle
import NindFile
from NindLexiconindex import NindLexiconindex
from NindTermindex import NindTermindex
#from NindLocalindex import NindLocalindex

def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print (f"""© l'ATEJCON.
Programme de test de la classe ViRecherche.

usage   : {script} <racine fichiers> <texte recherché> 
usage   : {script} ressources/RV "Gustave Flaubert"
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
    vignettes = viRecherche.rechercheVignettes(texte)
    print(vignettes)
    viRecherche.close()
    
LIMIT = 100
################################################################
class ViRecherche:
    def __init__(self, racine):
        # ouvre les 2 classes
        self.nindLexiconindex = NindLexiconindex(f'{racine}.nindlexiconindex')
        self.nindTermindex = NindTermindex(f'{racine}.nindtermindex')
        # vejrifie l'apairage des fichiers
        ident1 = self.nindLexiconindex.donneIdentificationFichier()
        ident2 = self.nindTermindex.donneIdentificationFichier()
        if ident1 != ident2: raise Exception('FICHIERS NON APAIRÉS')
        with open(f'{racine}-Urls.csv.pick', 'rb') as pick:
            self.idsUrls = pickle.load(pick)
        
    ################################
    def close(self):
        self.nindLexiconindex.close()
        self.nindTermindex.close()
        
    ###############################
    # ah partir d'un texte, trouve une liste de vignettes
    def rechercheUrlsParTexte(self, texte):
        idsDocs = self.__rechercheParTexte(texte)
        return self.rechercheUrlsParIds(idsDocs)
    
    ###############################
    # ah partir d'une liste d'ids, trouve une liste de vignettes
    def rechercheUrlsParIds(self, idsDocs):
        idsDocs.sort()
        lesUrls = []
        for idDoc in idsDocs[:LIMIT]:
            # 109400141;1608/10940-141.jpg
            lesUrls.append(f'{idDoc};{self.idsUrls[idDoc]}')
        return lesUrls, len(idsDocs)>LIMIT
        
    ###############################
    # ah partir d'un texte, trouve une liste de documents
    def __rechercheParTexte(self, texte):
        mots = texte.split()
        etOk = False
        for mot in mots:
            idsDocsMot = self.__rechercheParMot(mot)
            if len(idsDocsMot) == 0: continue
            if etOk : idsDocs &= idsDocsMot
            else: idsDocs = idsDocsMot
            etOk = True
        if not etOk: idsDocs = []
        # recherche avec tous les mots concatejnejs
        idsDocs |= self.__rechercheParMot('_'.join(mots))
        return list(idsDocs)
            
    ###############################
    # ah partir d'un mot simple, trouve une liste de documents
    def __rechercheParMot(self, mot):
        idsDocs = set()
        idsDocs |= self.__rechercheUnitaire(mot)
        idsDocs |= self.__rechercheUnitaire('§_Person.PERSON_' + mot)
        idsDocs |= self.__rechercheUnitaire('§_Location.LOCATION_' + mot)
        idsDocs |= self.__rechercheUnitaire('§_Miscellaneous.MISCELLANEOUS_' + mot)
        return idsDocs
    
    ###############################        
    # ah partir d'un mot, trouve une liste de documents
    def __rechercheUnitaire(self, mots):
        idsDocs = set()
        motsSimples = mots.split('_')
        motId = self.nindLexiconindex.donneIdentifiant(motsSimples)
        # si mot inconnu, aucun document
        if motId == 0: return idsDocs
        # sinon sort la liste des documents concernejs
        listeDocs = []
        termesCGList = self.nindTermindex.donneListeTermesCG(motId)
        for (categorie, frequenceTerme, docs) in termesCGList:
            for (noDoc, frequenceDoc) in docs: idsDocs.add(noDoc)
        return idsDocs
        
        
if __name__ == '__main__':
    main()

