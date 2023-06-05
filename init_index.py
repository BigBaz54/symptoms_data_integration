import APIs.sider_api as sider
import APIs.stitch_api as stitch
import APIs.drugbank_api as drugbank
import APIs.hpo_api as hpo
import APIs.omim_api as omim

# not needed cause inititalized in sider_api
# sider.medra_api(init=True)
# sider.medra_indi_api(init=True)
# sider.medra_se_api(init=True)
# stitch.stitch_api(init=True)
drugbank.drugbank_api(init=True)
hpo.hpo_api(init=True)
omim.omim_api(init=True)