import interface as interface
import sys
import interface

try:
    if len(sys.argv) < 2:
        print('Please provide a list of symptoms, with the following syntax: python script.py "symptom1 ;symptom2 ;symptom3" ')
    else:
        my_string = sys.argv[1]
        symptoms_list = my_string.strip().replace("'", "").split(";")
        print("\nSymptoms: " + my_string)
        diseases = interface.getDiseaseHpo(symptoms_list)
        drug_from_stitch = interface.getMedicamentSiderStitch(symptoms_list)
        drug_from_drugbank = interface.getMedicamentDrugbank(symptoms_list)

        print("\nIndications for these symptoms: ", len(drug_from_stitch['indication'])+len(drug_from_drugbank['indication']), "hits")
        print('\n\tSTITCH: ', len(drug_from_stitch['indication']), "hits")
        for drug in drug_from_stitch['indication']:
            print('\t\t', drug)
        print('\n\tDRUGBANK: ', len(drug_from_drugbank['indication']), "hits")
        for drug in drug_from_drugbank['indication']:
            print('\t\t', drug)
        print("________________________________________________________")
        print("\nThese symptoms are side effects of: ", len(drug_from_stitch['side_effect'])+len(drug_from_drugbank['side_effect']), "hits")
        print('\n\tSTITCH: ', len(drug_from_stitch['side_effect']), "hits")
        for drug in drug_from_stitch['side_effect']:
            print('\t\t', drug)
        print('\n\tDRUGBANK: ', len(drug_from_drugbank['side_effect']), "hits")
        for drug in drug_from_drugbank['side_effect']:
            print('\t\t', drug)
        print("________________________________________________________")
        print("\nThese symptoms may be caused by the following diseases: ", len(diseases), "hits")
        print('\n\tHPO -> OMIM:')
        for disease in diseases:
            print('\t\t', "OMIM_ID :" + disease["OMIM_id"])
            print('\t\t', "Preferred label: " + disease["preferred_label"][0].replace('\"', '') if len(disease["preferred_label"]) > 0 else "No preferred label")
            for syn in (disease["synonyms"][0] if len(disease["synonyms"]) > 0 else "No synonyms").split("|"):
                print('\t\t', "Synonym: " + syn.replace('\"', ''))
            print("               ____")   
except Exception as e:
    print("No hit for theses symptoms")

