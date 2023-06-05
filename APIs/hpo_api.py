from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
import os
import sqlite3
import whoosh.index

class hpo_api():
    def __init__(self, init=False):
        self.schema = Schema(name_and_synonyms=TEXT(stored=True), id=ID(stored=True))
        self.index_dir = os.path.join("APIs", "index_hpo")
        if init:
            # init whoosh
            
            # create the index
            if not os.path.exists(self.index_dir):
                os.mkdir(self.index_dir)
            self.ix = create_in(self.index_dir, self.schema)
            
            # parse the hpo.obo file and extract the relevant data
            writer = self.ix.writer()
            with open(os.path.join('data', 'HPO', 'hpo.obo'), "r", encoding="utf-8") as f:
                li = f.read().split("[Term]")
            filtered = []
            for i in range(1, len(li)):
                dic = {}
                dic["ID"] = li[i].split("id: ")[1].split("\n")[0].strip()
                dic["name"] = li[i].split("name: ")[1].split("\n")[0].strip()
                li_synonyms = li[i].split("synonym: ")
                if len(li_synonyms) > 1:
                    dic["synonyms"] = ""
                    for j in range(1, len(li_synonyms)):
                        dic["synonyms"] += " ; " + li_synonyms[j][1:].split("\"")[0].strip()
                filtered.append(dic)
            for i in range(len(filtered)):
                writer.add_document(name_and_synonyms=filtered[i]["name"]+(filtered[i]["synonyms"] if "synonyms" in filtered[i] else ""), id=filtered[i]["ID"])
            writer.commit()
        else:
            self.index_dir = os.path.join("APIs", "index_hpo")
            self.ix = whoosh.index.open_dir(self.index_dir)
            self.schema = self.ix.schema
        
    def search(self, term):
        #search the ID of the term that match the value as name or synonym
        with self.ix.searcher() as searcher:
            query = QueryParser("name_and_synonyms", self.schema).parse(term)
            results = searcher.search(query, limit=None)

            # we need to select only the results that match the whole term (or all the parts if * is used)
            real_results = []
            words_to_match = term.split("*")
            # print("words_to_match: ", words_to_match)
            for i in range(len(results)):
                for name in results[i]["name_and_synonyms"].split(" ; "):
                    if all([w in name for w in words_to_match]):
                        real_results.append(results[i])
                        break
            # print("len real_results: ", len(real_results))
            # print("len results: ", len(results))

            if len(real_results) > 0:
                return [r["id"] for r in real_results]
            else:
                return []

    def searchList(self, list_term):
        #search the IDs of the terms that match the list values as name or synonym
        IDs = []
        for term in list_term:
            curr_ids = self.search(term)
            for curr_id in curr_ids:
                if curr_id not in IDs:
                    IDs.append(curr_id)
        return IDs


    def sypmtomsIDtoDiseaseId(self, symptomsID):
        #search the IDs of the diseases that match the symptomsID
        diseasesID = []
        connector = sqlite3.connect(os.path.join("data", "HPO", "hpo_annotations.sqlite"))
        cursor = connector.cursor()
        for i in symptomsID:
            cursor.execute("SELECT disease_id FROM phenotype_annotation WHERE sign_id = ? AND disease_db = ? ", (i, 'OMIM'))
            el = cursor.fetchall()
            diseasesID.extend([e[0] for e in el])
        connector.close()
        setDiseasesID = set(diseasesID)
        result = []
        for i in setDiseasesID:
            result.append([i, diseasesID.count(i)])
        final = []
        for i in result:
            if int(i[1]) <= len(symptomsID):
                final.append(i[0])
        return final


    def listToId(self, symptomList):
        return self.sypmtomsIDtoDiseaseId(self.searchList(symptomList))