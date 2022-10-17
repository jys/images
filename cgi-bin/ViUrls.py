#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2022 LATEJCON"

import sys
from os import path
import pickle

def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print (f"""© l'ATEJCON.
Programme de test de la classe ViUrls.

usage   : {script} <racine> <liste d'idents> 
usage   : {script} VI "39895045, 39895046, 36651018"
""")

def main():
    try:
        if len(sys.argv) < 3 : raise Exception()
        racine = sys.argv[1]
        listeIdents = sys.argv[2]
        rechercheUrls(racine, listeIdents)
    except Exception as exc:
        if len(exc.args) == 0: usage()
        else:
            print ("******************************")
            print (exc.args[0])
            print ("******************************")
            raise
        sys.exit()

def rechercheUrls(racine, listeIdents):
    idents = listeIdents.split(',')
    idsDocs = []
    for ident in idents:
        ident = ident.strip()
        idsDocs.append(int(ident))
    viUrls = ViUrls(racine)
    urls = viUrls.rechercheUrls(idsDocs)
    print(urls)
    
################################################################
class ViUrls:
    def __init__(self, racine):
        with open(f'{racine}-Urls.pickle', 'rb') as pick:
            self.idsUrls = pickle.load(pick)
        
    ###############################
    # ah partir d'une liste d'ids, trouve une liste de vignettes
    def rechercheUrls(self, idsDocs):
        lesUrls = []
        for idDoc in idsDocs:
            # 109400141;1608/10940-141.jpg
            if idDoc in self.idsUrls:
                lesUrls.append(f'{idDoc};{self.idsUrls[idDoc]}')
            else:
                lesUrls.append(f'{idDoc};IDENT INCONNU')
        return lesUrls
        
        
        
if __name__ == '__main__':
    main()

