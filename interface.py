import APIs.sider_api as sider
import APIs.stitch_api as stitch
import APIs.drugbank_api as drugbank
import APIs.hpo_api as hpo
import APIs.omim_api as omim
#entre = input('Liste de symptômes (Séparé par ;) :')

entre = "headache ;nausea "

Liste_symptome = entre.strip().split(";")
for i in range(len(Liste_symptome)):
    Liste_symptome[i] = Liste_symptome[i].strip()
    
def getMedicamentSiderStitch(Liste_symptome):
    INDI = sider.getSiderid("good", Liste_symptome)
    SE = sider.getSiderid("bad", Liste_symptome)

    apiomim = omim.omim_api()
    INDI_from_OMIM = sider.getSiderIdFromCUI_Indi(apiomim.get_CUI_from_symptoms(Liste_symptome))
    INDI.extend(INDI_from_OMIM)

    #Recherche des médicaments traitant ou causant les symptomes dans STITCH
    ##Normalisation des siderid
                
    INDI = stitch.SiderIdNormalisation(INDI,"good")
    SE = stitch.SiderIdNormalisation(SE,"bad")


    #print("indication id : " + str(INDI))
    #print("side_effect id : " + str(SE))

    Heal = stitch.removeDG(stitch.getMed("good",INDI))
    Harm = stitch.removeDG(stitch.getMed("bad",SE))

    return {"indication": Heal, "side_effect": Harm}
    
def getMedicamentDrugbank(Liste_symptome):
    #Recherche des médicaments traitant ou causant les symptomes dans Drugbank
    drugbank_api = drugbank.drugbank_api(init=False)
    [med_tox, med_in] = drugbank_api.search(Liste_symptome)
    
    return {"indication": med_in, "side_effect": med_tox}
    
def getDiseaseHpo(Liste_symptome):
    #Recherche des médicaments traitant ou causant les symptomes dans HPO
    hpo_api = hpo.hpo_api()
    OMIM_IDs = hpo_api.listToId(Liste_symptome)
    api_omim = omim.omim_api()
    diseases = api_omim.get_diseases_names_from_OMIM_ids(OMIM_IDs)
    return diseases
    
getMedicamentSiderStitch(Liste_symptome)
getMedicamentDrugbank(Liste_symptome)
getDiseaseHpo(Liste_symptome)

