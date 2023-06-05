import os
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
import whoosh.index

class omim_api():
    def __init__(self, init=False):
        # disease_synonyms is not stored since we'll search on disease_synonyms and get the disease_preferred_label
        self.schema = Schema(OMIM_id=ID(stored=True, unique=True), disease_preferred_label=TEXT(stored=True), disease_synonyms=TEXT(stored=True), CUI=ID(stored=True, unique=True), symptoms=TEXT(stored=True))
        self.index_dir = os.path.join("APIs", "index_omim")

        if init:
            if not os.path.exists(self.index_dir):
                os.mkdir(self.index_dir)
            self.ix = create_in(self.index_dir, self.schema)

            writer = self.ix.writer()
            with open(os.path.join('data', 'OMIM', 'omim.txt'), "r", encoding="utf-8") as f:
                li = f.read().split("*RECORD*")
            filtered = []
            for i in range(1, len(li)):
                dic = {}
                dic["TI"] = li[i].split("*FIELD* TI")[1].split("*FIELD*")[0].replace("\n", " ").strip() if "*FIELD* TI" in li[i] else ""
                if dic["TI"].startswith("^"):
                    # ignoring the records that have been moved
                    continue
                dic["CS"] = li[i].split("*FIELD* CS")[1].split("*")[0].replace("\n", " ").strip() if "*FIELD* CS" in li[i] else ""
                om_id = dic["TI"].split(" ")[0]
                if om_id.startswith("*") or om_id.startswith("#") or om_id.startswith("%") or om_id.startswith("+"):
                    dic["ID"] = om_id[1:]
                else:
                    dic["ID"] = om_id
                filtered.append(dic)
            for i in range(len(filtered)):
                writer.add_document(OMIM_id=filtered[i]["ID"], disease_synonyms=filtered[i]["TI"].split(" ")[1], symptoms=filtered[i]["CS"])
            
            header = True
            with open(os.path.join('data', 'OMIM', 'omim_onto.csv'), "r", encoding="utf-8") as f:
                for row in f:
                    # ignoring the header
                    if not header:
                        # parsing the csv file without splitting on commas inside quotes
                        row = row.strip().split(",")
                        for i in range(len(row)):
                            if row[i].startswith('"') and not row[i].endswith('"'):
                                row[i+1] = row[i] + "," + row[i+1]
                                row[i] = "skip"
                        row = [e for e in row if e!="skip"]

                        om_id=row[0].split("/")[-1]
                        dpl = row[1]
                        ds = row[2]
                        cui = row[5]
                        if (row[4]!='true'):
                            writer.add_document(OMIM_id=om_id, disease_preferred_label=dpl, disease_synonyms=ds, CUI=cui)
                    else:
                        header = False
            writer.commit()
        else:
            self.ix = whoosh.index.open_dir(self.index_dir)

    def search(self, field, searched):
        searched_lower_joined = " ".join([e for e in searched])
        searcher = self.ix.searcher()
        query_parser = QueryParser(field, schema=self.schema)
        query = query_parser.parse(searched_lower_joined)
        results = searcher.search(query, limit=None, terms=True)
        results_merged = self.merge_on_OMIM_id(results)
        # results_merged = results
        results_intersected = self.intersect(results_merged, field, searched)
        return results_intersected
    
    def merge_on_OMIM_id(self, results):
        # merging the results of the search on OMIM_id since documents from omim.txt and omim_onto.csv are indexed
        merged = []
        # print(len(results))
        for res in results:
            res = res.fields()
            for m in merged:
                if m["OMIM_id"] == res["OMIM_id"]:
                    # a record with the same OMIM_id already exists
                    if "disease_preferred_label" in res:
                        m["disease_preferred_label"] = res["disease_preferred_label"]
                    if "disease_synonyms" in res and "disease_preferred_label" in res:
                        m["disease_synonyms"] = res["disease_synonyms"]
                    if "CUI" in res:
                        m["CUI"] = res["CUI"]
                    if "symptoms" in res:
                        m["symptoms"] = res["symptoms"]
                    break
            # a record with the same OMIM_id does not exist
            merged.append(res)
        # print(len(merged), merged)
        return merged
    
    def intersect(self, results, field, list_of_words):
        # returns the documents that contain all the words (or word parts if "*" is used) in list_of_words in the field field
        # results is a list of dictionaries
        inter = []
        effective_list_of_words = []
        for word in list_of_words:
            if "*" in word:
                effective_list_of_words.extend(word.split("*"))
            else:
                effective_list_of_words.append(word)
        for d in results:
            if field in d:
                if all([e.lower() in d[field].lower() for e in effective_list_of_words]):
                    inter.append(d)
        return inter
    
    def get(self, from_field, to_field, searched):
        # returns the values of the field to_field for the documents that contain all the words in searched in the field from_field
        results = self.search(from_field, searched)
        # print("get: " , results)
        return list(set([res[to_field] for res in results if to_field in res]))
    
    def get_CUI_from_symptoms(self, searched):
        # returns the CUIs of the diseases that have the symptoms searched
        symp = self.get("symptoms", "OMIM_id", searched)
        return list(set(self.get("OMIM_id", "CUI", symp)))
    
    def get_diseases_names_from_OMIM_ids(self, searched):
        # returns the disease names of the diseases that have the OMIM_id searched
        diseases = []
        for omim_id in searched:
            one_disease = {"OMIM_id": omim_id}
            one_disease["preferred_label"] = self.get("OMIM_id", "disease_preferred_label", [omim_id])
            one_disease["synonyms"] = self.get("OMIM_id", "disease_synonyms", [omim_id])
            diseases.append(one_disease)
        return diseases




if __name__ == "__main__":
    if 'api' not in locals():
        api = omim_api()

    print(api.search("symptoms", ["headache", "nausea"]))
    print(api.search("OMIM_id", ["190900"]))
    print(api.search("CUI", ["C1412770"]))
    print(api.search("disease_synonyms", ["BLUE CONE PIGMENT"]))
    print(api.get("symptoms", "CUI", ["Abnormal blue cone ERG"]))
    print(api.get_CUI_from_symptoms(["Abnormal blue cone ERG", "Defective blue and yellow vision"]))
    print("\n\n\n\n\n",api.get_diseases_names_from_OMIM_ids(["190900", "MTHU010133","612893"]))
