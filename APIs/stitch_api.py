import os
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
import whoosh.index

#
# Index pour chemical.sources.v5.0_light.tsv
#

class stitch_api():
    def __init__(self, init=False):
        self.schema = Schema(cidm=TEXT(stored=True), cids=TEXT(stored=True), atc=TEXT(stored=True))
        self.index_dir = os.path.join("APIs", "index_stitch")

        if init:
            if not os.path.exists(self.index_dir):
                os.mkdir(self.index_dir)
            self.ix = create_in(self.index_dir, self.schema)

            writer = self.ix.writer()
            with open(os.path.join(os.path.join(os.path.split(os.path.dirname(__file__))[0]),'data', 'STITCH-ATC', 'chemical.sources.v5.0_light.tsv'), "r", encoding="utf-8") as f:
                for row in f:
                    row = row.strip().split("\t")
                    writer.add_document(cidm=row[0], cids=row[1], atc=row[3])
            writer.commit()
        else:
            self.ix = whoosh.index.open_dir(self.index_dir)

    def search(self, searched):
        searcher = self.ix.searcher()
        query_parser = QueryParser("cidm", schema=self.schema)
        query = query_parser.parse(searched)
        results = searcher.search(query,limit=None)
        return results

if not os.path.exists(os.path.join("APIs", "index_stitch")):
    os.mkdir(os.path.join("APIs", "index_stitch"))
    api = stitch_api(init=True)
else:
    api = stitch_api()


#
#Parsing of br08303.keg
#

atc_dict = {}

with open(os.path.join(os.path.join(os.path.split(os.path.dirname(__file__))[0]),"data", "STITCH-ATC", "br08303.keg"), "r", encoding="utf-8") as f:
    for row in f:
        if row[0] in ['B','C','D','E','F']:
            if (row[0]=='B'):
                row = row.strip().split("  ")
            elif (row[0]=='C'):
                row = row.strip().split("  "*2)
            elif (row[0]=='D'):
                row = row.strip().split("  "*3)
            elif (row[0]=='E'):
                row = row.strip().split("  "*4)
            else :
                row = row.strip().split("  "*5)
            for i in range(len(row[1])) : 
                if row[1][i]==' ':
                    atc = row[1][:i]
                    chemical = row[1][i+1:].strip()
                    atc_dict[atc]=chemical
                    break

def getMed(option,liste_sider_id1):
    """
    Parameters
    ----------
    
    option : String
        "good" for indication, "bad" for secondary effect.
    liste_sider_id1 : List
        List of list of sider id from the first row (the only row if option good).
    liste_sider_id2 : List
        List of list of sider id from the second row (only if option bad).
    Returns
    -------
    List of medication.
    """
    
    if option == "good":
        
        Liste_ATC = []
        
        for sym in liste_sider_id1:
            meds = []
            for id1 in sym:
                results = api.search(id1)
                
                for hit in results:
                    meds.append(hit.get("atc"))
            
            #med contient tous les code atc des médicament associé à l'id sider courant 
            
            Liste_ATC.append(meds)
        
        #On cherche des médicaments qui traite l'ensemble des symptomes donc on fait l'intersection 
        
        ATC = set(Liste_ATC[0])
        
        for atc in Liste_ATC:
            ATC = ATC & set(atc)
            
        Medicament = []
        
        for code_atc in ATC:
            code_atc = code_atc.strip()
            
            Medicament.append(atc_dict[code_atc])
            
        return Medicament

    elif option == "bad":
        
        Liste_ATC = []
        
        for k in range(len(liste_sider_id1)):
            meds = []
            for i in range(len(liste_sider_id1[k])):
                if len(liste_sider_id1[k][1])>0:
                    results = api.search(liste_sider_id1[k][0][i])
                
                    for hit in results:
                        # print("i : "+str(i) +" and k : "+str(k))
                        # print(str(liste_sider_id1[k][1][i]))
                        if hit.get("cids")==liste_sider_id1[k][1][i]:
                            meds.append(hit.get("atc"))
            
            #med contient tous les code atc des médicament associé à l'id sider courant 
            
            Liste_ATC.append(meds)
            
        #On cherche des médicaments qui traite l'ensemble des symptomes donc on fait l'intersection 
        
        ATC = set(Liste_ATC[0])
        
        for atc in Liste_ATC:
            ATC = ATC & set(atc)
        
        Medicament = []
        
        for code_atc in ATC:
            code_atc = code_atc.strip()
            
            Medicament.append(atc_dict[code_atc])
            
        return Medicament
            
    else:
        print("Error : option must be good or bad")
        return

def SiderIdNormalisation(liste_sider_id,option):
    """
    Parameters
    ----------
    liste_sider_id : List of String
        list of sider id from getSiderId().
    option : String
        good or bad.

    Returns
    -------
    None.
    """
    if option=="good":
        INDI = liste_sider_id
        
        for i in range(len(INDI)):
            for j in range(len(INDI[i])):
                INDI[i][j]=INDI[i][j].replace("1","m",1)
        return INDI
    
    elif option=="bad":
        SE  = liste_sider_id
        for i in range(len(SE)):
            for j in range(len(SE[i][0])):
                SE[i][0][j]=SE[i][0][j].replace("1","m",1)
                SE[i][1][j]=SE[i][1][j].replace("0","s",1)
        return SE
    else:
        print("Error : option must be good or bad")
        return

def removeDG(Liste):
    L = []
    for k in Liste:
        L.append(k.split("[")[0].strip())
    return list(set(L))