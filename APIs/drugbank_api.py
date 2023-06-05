import os
import xml.etree.ElementTree as ET
import whoosh.index
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser

class drugbank_api():
    def __init__(self, init=False):
        if init:
            # We define the schema for the index
            self.schema = Schema(drug_name=ID(stored=True), toxicity=TEXT(stored=True), indications=TEXT(stored=True))

            # Create the index
            self.index_dir = os.path.join("APIs", "index_drugbank")
            if not os.path.exists(self.index_dir):
                os.mkdir(self.index_dir)
            self.index = create_in(self.index_dir, self.schema)

            # Parse the DrugBank XML file and extract the relevant data
            self.tree = ET.parse(os.path.join("data", "DRUGBANK", "drugbank.xml"))
            self.root = self.tree.getroot()

            self.writer = self.index.writer()
            for drug in self.root.findall(".//{http://www.drugbank.ca}drug"):
                drug_name = drug.find("{http://www.drugbank.ca}name").text
                toxicity_element = drug.find(".//{http://www.drugbank.ca}toxicity")
                # we add the drug name, toxicity and indication to the index
                if toxicity_element is not None:
                    toxicity = toxicity_element.text
                    self.writer.add_document(drug_name=drug_name, toxicity=toxicity)
                indications_element = drug.find(".//{http://www.drugbank.ca}indication")
                if indications_element is not None:
                    indications = indications_element.text
                    self.writer.add_document(drug_name=drug_name, indications=indications)
            self.writer.commit()
        else:
            self.index_dir = os.path.join("APIs", "index_drugbank")
            self.index = whoosh.index.open_dir(self.index_dir)

    def toxicitySearch(self, symptom):
        searcher = self.index.searcher()
        query = QueryParser("toxicity", self.index.schema).parse(symptom)
        results = searcher.search(query, limit=None)
        res = [hit["drug_name"] for hit in results]
        return set(res)

    def indicationsSearch(self, symptom):
        searcher = self.index.searcher()
        query = QueryParser("indications", self.index.schema).parse(symptom)
        results = searcher.search(query, limit=None)
        res = [hit["drug_name"] for hit in results]
        return set(res)

    def search(self, symptoms):
        toxicityResults = []
        indicationsResults = []
        for symptom in symptoms:
            tox = self.toxicitySearch(symptom)
            ind = self.indicationsSearch(symptom)
            toxicityResults.append(tox)
            indicationsResults.append(ind)
        if toxicityResults:
            toxic = list(set.intersection(*toxicityResults))
            # print(str(len(to)) + " Drugs with all symptoms: " + str(to))
        if indicationsResults:
            indic = list(set.intersection(*indicationsResults))
            # print(str(len(id)) + " Drugs with all indications: " + str(id))
        return toxic, indic