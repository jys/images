#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2021 LATEJCON"

import sys
from os import path

def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print (f"""© l'ATEJCON.
Programme de test de la classe QcFichier.
Cette classe permet l'accès aux fichiers binaires avec codages Latejcon.
Ce script écrit dans le fichier spécifié la taille des données sur un 
entier 3 bits puis un nombre N sous 4 formes : 
1) N en non signé, 2) N en signé, 3) -N en signé, 4) -N en non signé.
Le programme relit ce fichier et donne les 4 nombres
latecon sous 2 interprétations : 1) non signée, 2) signée"

usage   : {script} <fichier codage latecon> <nombre>
exemple : {script} /tmp/Nind_testLateconNumber.lat 314159
""")
    
DEJBUT = 0
COURANT = 1
FIN = 2

def main():
    try:
        if len(sys.argv) < 3 : raise Exception()
        nomFichierTest = path.abspath(sys.argv[1])
        nombre = int(sys.argv[2])
        test(nomFichierTest, nombre)
    except Exception as exc:
        if len(exc.args) == 0: usage()
        else:
            print ("******************************")
            print (exc.args[0])
            print ("******************************")
            raise
        sys.exit()

def test(nomFichierTest, nombre):
    #1) ejcrit le fichier
    latFile = QcFichier(nomFichierTest, True)
    # mejmorise position
    latFile.ejcritNombre3(0)
    posDejb = latFile.tell()
    latFile.ejcritNombreULat(nombre)
    latFile.ejcritNombreSLat(nombre)
    latFile.ejcritNombreULat(-nombre)
    latFile.ejcritNombreSLat(-nombre)
    taille = latFile.tell() - posDejb
    latFile.seek(0, DEJBUT)
    latFile.ejcritNombre3(taille)
    latFile.seek(0, FIN)
    latFile.ejcritMotUtf8('coucou les échevelés !')
    latFile.close()
    
    # 2) relit le fichier
    latFile = QcFichier(nomFichierTest)
    #taille du fichier
    latFile.seek(0, FIN)
    taille = latFile.tell()
    print ("taille du fichier : %d"%(taille))
    #lit la taille
    latFile.seek(0, DEJBUT)
    taille = latFile.litNombre3()
    print ("taille=%d"%(taille))
    nonSignes = []
    signes = []
    #lit les nombres en non signé 
    for i in range(4): nonSignes.append(latFile.litNombreULat())
    #lit les nombres en non signé 
    latFile.seek(3, DEJBUT)
    for i in range(4): signes.append(latFile.litNombreSLat())
    #affiche
    for i in range(4): print (f"U: {nonSignes[i]} S: {signes[i]}")
    message = latFile.litMotUtf8()
    print(message)
    



######################################################################################
# <fichier>               ::= { <Entier1> | <Entier2> | <Entier3> | <Entier4> | <Entier5> |
#                               <EntierULat> | <EntierULat> | <MotUtf8> | <Utf8> | <Octet> }
# <MotUtf8>               ::= <longueur> <Utf8>
# <longueur>              ::= <Entier1>
# <Utf8>                  ::= { <Octet> }
# <Entier1>               ::= <Octet>
# <Entier2>               ::= <Octet> <Octet>
# <Entier3>               ::= <Octet> <Octet> <Octet>
# <Entier4>               ::= <Octet> <Octet> <Octet> <Octet>
# <Entier5>               ::= <Octet> <Octet> <Octet> <Octet> <Octet>
# <EntierULat>            ::= { <Octet> }
# <EntierSLat>            ::= { <Octet> }
######################################################################################
class QcFichier:
    def __init__(self, nomQcFichier, enEjcriture = False):
        if not enEjcriture:
            #ouvre le fichier en lecture
            self.latFile = open(nomQcFichier, 'rb')
            self.latFile.seek(0, DEJBUT)
        else:
            #ejcrit le fichier completement
            self.latFile = open(nomQcFichier, 'wb')
        
    def seek(self, offset, from_what):
        self.latFile.seek(offset, from_what)
        
    def tell(self):
        return self.latFile.tell()
    
    def close(self):
        self.latFile.close()
        
    def litNombre1(self):
        return ord(self.latFile.read(1))

    def litNombre2(self):
        #gros-boutiste
        ba = bytes(self.latFile.read(2))
        return ba[0]*0x100 + ba[1]
        #return (ba[0] <<8) + ba[1]

    def litNombre3(self):
        #petit-boutiste
        ba = bytes(self.latFile.read(3))
        return (ba[2]*0x100 + ba[1])*0x100 + ba[0]
        #return (((ba[2] <<8) + ba[1]) <<8) + ba[0]
        #return (ba[2] <<16) + (ba[1] <<8) + ba[0]

    def litNombreS3(self):
        #petit-boutiste
        ba = bytes(self.latFile.read(3))
        res = (ba[2]*0x100 + ba[1])*0x100 + ba[0]
        #res = (((ba[2] <<8) + ba[1]) <<8) + ba[0]
        #res = (ba[2] <<16) + (ba[1] <<8) + ba[0]
        if res < 0x800000: return res 
        return res - 0x1000000

    def litNombre4(self):
        #petit-boutiste
        ba = bytes(self.latFile.read(4))
        return ((ba[3]*0x100 + ba[2])*0x100 + ba[1])*0x100 + ba[0]
        #return (((((ba[3] <<8) + ba[2]) <<8) + ba[1]) <<8) + ba[0]
        #return (ba[3] <<24) + (ba[2] <<16) + (ba[1] <<8) + ba[0]

    def litNombreS4(self):
        #petit-boutiste
        ba = bytes(self.latFile.read(4))
        res = ((ba[3]*0x100 + ba[2])*0x100 + ba[1])*0x100 + ba[0]
        if res < 0x80000000: return res 
        return res - 0x100000000

    def litNombre5(self):
        #gros-boutiste
        ba = bytes(self.latFile.read(5))
        return (((ba[0]*0x100 + ba[1])*0x100 + ba[2])*0x100 + ba[3])*0x100 + ba[4]
        #return (((((((ba[0] <<8) + ba[1]) <<8) + ba[2]) <<8) + ba[3]) <<8) + ba[4]
        #return (ba[0] <<32) + (ba[1] <<24) + (ba[2] <<16) + (ba[3] <<8) + ba[4]

    def litNombreULat(self):
        octet = ord(self.latFile.read(1))
        if not octet&0x80: return octet
        result = ord(self.latFile.read(1))
        if not octet&0x40: return (octet&0x3F) * 0x100 + result
        result = result * 0x100 + ord(self.latFile.read(1))
        if not octet&0x20: return (octet&0x1F) * 0x10000 + result
        result = result * 0x100 + ord(self.latFile.read(1))
        if not octet&0x10: return (octet&0x0F) * 0x1000000 + result
        result = result * 0x100 + ord(self.latFile.read(1))
        if not octet&0x08: return result
        raise Exception('entier Ulatecon invalide à {:08X}'.format(self.latFile.tell()))

    def litNombreSLat(self):
        octet = ord(self.latFile.read(1))
        if octet&0xC0 == 0x00: return octet
        if octet&0xC0 == 0x40: return octet - 0x80
        result = ord(self.latFile.read(1))
        if octet&0x60 == 0x00: return (octet&0x3F) * 0x100 + result
        if octet&0x60 == 0x20: return (octet&0x3F) * 0x100 + result - 0x4000
        result = result * 0x100 + ord(self.latFile.read(1))
        if octet&0x30 == 0x00: return (octet&0x1F) * 0x10000 + result
        if octet&0x30 == 0x10: return (octet&0x1F) * 0x10000 + result - 0x200000
        result = result * 0x100 + ord(self.latFile.read(1))
        if octet&0x18 == 0x00: return (octet&0x0F) * 0x1000000 + result
        if octet&0x18 == 0x08: return (octet&0x0F) * 0x1000000 + result - 0x10000000
        result = result * 0x100 + ord(self.latFile.read(1))
        if (octet&0x08 == 0x00) and (result&0x80000000 == 0x00000000): return result
        if (octet&0x08 == 0x00) and (result&0x80000000 == 0x80000000): return result - 0x0100000000
        raise Exception('entier Slatecon invalide à {:08X}'.format(self.latFile.tell()))
    
    def litMotUtf8(self):
        longueur = ord(self.latFile.read(1))
        #return self.latFile.read(longueur).decode('utf-8')
        return bytes(self.latFile.read(longueur)).decode()
    
    def litChaine(self, longueur):
        #return self.latFile.read(longueur).decode('utf-8')
        return bytes(self.latFile.read(longueur)).decode()
    
    def litOctets(self, longueur):
        return bytes(self.latFile.read(longueur))
    
    def ejcritNombre1(self, entier):
        ba = bytearray(1)
        ba[0] = entier&0xFF
        self.latFile.write(ba)

    def ejcritNombre3(self, entier):
        ba = bytearray(3)
        #petit-boutiste
        ba[0] = entier&0xFF
        ba[1] = (entier//0x100)&0xFF
        ba[2] = (entier//0x10000)&0xFF
        self.latFile.write(ba)
        
    def ejcritNombre4(self, entier):
        ba = bytearray(4)
        #petit-boutiste
        ba[0] = entier&0xFF
        ba[1] = (entier//0x100)&0xFF
        ba[2] = (entier//0x10000)&0xFF
        ba[3] = (entier//0x1000000)&0xFF
        self.latFile.write(ba)
        
    def ejcritNombre5(self, entier):
        ba = bytearray(5)
        #gros-boutiste
        ba[0] = (entier//0x100000000)&0xFF
        ba[1] = (entier//0x1000000)&0xFF
        ba[2] = (entier//0x10000)&0xFF
        ba[3] = (entier//0x100)&0xFF
        ba[4] = entier&0xFF
        self.latFile.write(ba)
        
    def ejcritNombreULat(self, entier):
        # de 0 ah 2^7-1 : 0-127
        if entier < 0x80: 
            ba = bytearray(1)
            ba[0] = entier&0x7F
        # de 2^7 ah 2^14-1 : 128-16383
        elif entier < 0x4000:
            ba = bytearray(2)
            ba[0] = entier//0x100|0x80
            ba[1] = entier&0xFF
        # de 2^14 ah 2^21-1 : 16384-2097151
        elif entier < 0x200000:
            ba = bytearray(3)
            ba[0] = entier//0x10000|0xC0
            ba[1] = entier//0x100&0xFF
            ba[2] = entier&0xFF
        # de 2^21 ah 2^28 : 2097152-268435455
        elif entier < 0x010000000:
            ba = bytearray(4)
            ba[0] = entier//0x1000000|0xE0
            ba[1] = entier//0x10000&0xFF
            ba[2] = entier//0x100&0xFF
            ba[3] = entier&0xFF
        # de 2^28 ah 2^32-1 : 268435456-4294967295
        else:
            ba = bytearray(5)
            ba[0] = 0xF0
            ba[1] = entier//0x1000000&0xFF
            ba[2] = entier//0x10000&0xFF
            ba[3] = entier//0x100&0xFF
            ba[4] = entier&0xFF
        self.latFile.write(ba)

    def ejcritNombreSLat(self, entier):
        # de -2^6 ah 2^6-1 : de -64 a 63
        if entier >= -0x40 and entier < 0x40:
            ba = bytearray(1)
            ba[0] = entier&0x7F
        # de -2^13 ah -2^6-1 et de 2^6 ah 2^13-1 : de -8192 ah -65 et de 64 ah 8191
        elif entier >= -0x2000 and entier < 0x2000:
            ba = bytearray(2)
            ba[0] = entier//0x100&0x3F|0x80
            ba[1] = entier&0xFF
        # de -2^20 ah -2^13-1 et de 2^13 ah 2^20-1 : de -1048576 ah -8193 et de 8192 ah 1048575
        elif entier >= -0x100000 and entier < 0x100000:
            ba = bytearray(3)
            ba[0] = entier//0x10000&0x1F|0xC0
            ba[1] = entier//0x100&0xFF
            ba[2] = entier&0xFF
        # de -2^27 ah -2^20-1 et de 2^20 ah 2^27-1 : de -134217728 ah -1048577 et de 1048576 ah 134217727
        elif entier >= -0x8000000 and entier < 0x8000000:
            ba = bytearray(4)
            ba[0] = entier//0x1000000&0x0F|0xE0
            ba[1] = entier//0x10000&0xFF
            ba[2] = entier//0x100&0xFF
            ba[3] = entier&0xFF
        # de -2^31 ah -2^27-1 et de 2^27 ah 2^31-1 : de -2147483648 ah -134217729 et de 134217728 ah 2147483647
        else:
            ba = bytearray(5)
            ba[0] = entier//0x100000000&0x07|0xF0
            ba[1] = entier//0x1000000&0xFF
            ba[2] = entier//0x10000&0xFF
            ba[3] = entier//0x100&0xFF
            ba[4] = entier&0xFF
        self.latFile.write(ba)        

    def ejcritMotUtf8(self, mot):
        self.ejcritNombre1(len(mot.encode('utf8')))
        self.ejcritChaine(mot)
        
    def ejcritChaine(self, chaine):
        self.latFile.write(chaine.encode('utf-8'))
        
    def ejcritZejros(self, taille):
        self.latFile.write(bytearray(taille))
        
############################################
#calcule la clef B de hashage
def clefB(mot):
    mBytes = mot.encode('utf-8')
    clef = 0x55555555
    shifts = 0
    for octet in mBytes: 
        clef ^= (octet << shifts%23)
        shifts += 5
    return clef

       
if __name__ == '__main__':
    main()
