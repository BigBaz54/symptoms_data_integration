import os
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
import whoosh.index

class medra_api():
    def __init__(self, init=False):
        self.schema = Schema(id=ID(stored=True), symptoms=TEXT(stored=True))
        self.index_dir = os.path.join("APIs", "index_medra")

        if init:
            if not os.path.exists(self.index_dir):
                os.mkdir(self.index_dir)
            self.ix = create_in(self.index_dir, self.schema)

            writer = self.ix.writer()
            with open(os.path.join(os.path.join(os.path.split(os.path.dirname(__file__))[0]),'data', 'SIDER4', 'meddra.tsv'), "r", encoding="utf-8") as f:
                for row in f:
                    row = row.strip().split("\t")
                    writer.add_document(id=row[0], symptoms=row[3])
            writer.commit()
        else:
            self.ix = whoosh.index.open_dir(self.index_dir)

    def search(self, searched):
        searcher = self.ix.searcher()
        query_parser = QueryParser("symptoms", schema=self.schema)
        query = query_parser.parse(searched)
        results = searcher.search(query,limit=None)
        return results

if not os.path.exists(os.path.join("APIs", "index_medra")):
    os.mkdir(os.path.join("APIs", "index_medra"))
    apim = medra_api(init=True)
else:
    apim = medra_api()
    
class medra_indi_api():
    def __init__(self, init=False):
        self.schema = Schema(id1=TEXT(stored=True),id=ID(stored=True), symptoms=TEXT(stored=True))
        self.index_dir = os.path.join("APIs", "index_medra_indi")

        if init:
            if not os.path.exists(self.index_dir):
                os.mkdir(self.index_dir)
            self.ix = create_in(self.index_dir, self.schema)

            writer = self.ix.writer()
            with open(os.path.join(os.path.join(os.path.split(os.path.dirname(__file__))[0]),'data', 'SIDER4', 'meddra_all_indications.tsv'), "r", encoding="utf-8") as f:
                for row in f:
                    row = row.strip().split("\t")
                    writer.add_document(id1=row[0],id=row[1], symptoms=row[6])
            writer.commit()
        else:
            self.ix = whoosh.index.open_dir(self.index_dir)

    def search(self, searched):
        searcher = self.ix.searcher()
        query_parser = QueryParser("id", schema=self.schema)
        query = query_parser.parse(searched)
        results = searcher.search(query,limit=None)
        return results

if not os.path.exists(os.path.join("APIs", "index_medra_indi")):
    os.mkdir(os.path.join("APIs", "index_medra_indi"))
    apii = medra_indi_api(init=True)
else:
    apii = medra_indi_api()
class medra_se_api():
    def __init__(self, init=False):
        self.schema = Schema(id1=TEXT(stored=True),id2=TEXT(stored=True),id=ID(stored=True), symptoms=TEXT(stored=True))
        self.index_dir = os.path.join("APIs", "index_medra_se")

        if init:
            if not os.path.exists(self.index_dir):
                os.mkdir(self.index_dir)
            self.ix = create_in(self.index_dir, self.schema)

            writer = self.ix.writer()
            with open(os.path.join(os.path.join(os.path.split(os.path.dirname(__file__))[0]),'data', 'SIDER4', 'meddra_all_se.tsv'), "r", encoding="utf-8") as f:
                for row in f:
                    row = row.strip().split("\t")
                    writer.add_document(id1=row[0],id2=row[1],id=row[2], symptoms=row[5])
            writer.commit()
        else:
            self.ix = whoosh.index.open_dir(self.index_dir)
        
    def search(self, searched):
        searcher = self.ix.searcher()
        query_parser = QueryParser("id", schema=self.schema)
        query = query_parser.parse(searched)
        results = searcher.search(query,limit=None)
        return results

if not os.path.exists(os.path.join("APIs", "index_medra_se")):
    os.mkdir(os.path.join("APIs", "index_medra_se"))
    apis = medra_se_api(init=True)
else:
    apis = medra_se_api()


def getSiderid(option, Liste_symptome):
    """
    

    Parameters
    ----------
    option : String
        "good" for indication, "bad" for secondary effect.
    Liste_symptome : List of String
        list of symptome.

    Returns
    -------
    List of list of siderid (1 per symptom) if option good
    List of (List of siderid1,List of siderid2) (1 per symptom) if option bad.

    """
    
    ID = []
    
    for sym in Liste_symptome:
        SY = []
        
        results = apim.search(sym)
        
        for hit in results:
            SY.append(hit.get("id"))
    
        SY = set(SY)
        
        if option=="good" :
            liste_sider_id1 = []
            for ids in SY:
                results = apii.search(ids)
                
                for hit in results:
                        liste_sider_id1.append(hit.get("id1"))
                
            ID.append(liste_sider_id1)
                    
        elif option=="bad" :
            liste_sider_id1 = []
            liste_sider_id2 = []
            for ids in SY:
                results = apis.search(ids)
                
                for hit in results:
                        liste_sider_id1.append(hit.get("id1"))
                        liste_sider_id2.append(hit.get("id2"))
                
            ID.append((liste_sider_id1,liste_sider_id2))
            
        else:
            print("Error : option must be good or bad")
            return
        
    return ID

def getSiderIdFromCUI_Indi(Liste_CUI):
    """
    Parameters
    ----------
    Liste_CUI : List of String
        List of CUI id.

    Returns
    -------
    List of String
        List of sider id.

    """
    R = []
    for cui in Liste_CUI:
        results = apii.search(cui)
        
        for hit in results:
            R.append(hit.get("id1"))
    return R

def GetCUIFromSymptome(Liste_symptome):
    """
    Parameters
    ----------
    Liste_symptome : List of String
        List of symptome.

    Returns
    -------
    CUI : List of String
        List of CUI id.

    """
    CUI = []
    for sym in Liste_symptome:
        SY = []
        
        results = apim.search(sym)
        
        for hit in results:
            SY.append(hit.get("id"))
    
        SY = set(SY)
        CUI.append(SY)
        
    return CUI