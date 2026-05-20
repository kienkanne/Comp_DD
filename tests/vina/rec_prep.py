from compdd.vina._vina_prep_rec import _vina_prep_rec
from compdd.configs.root_config import load_config

cfg = load_config("/localscratch/kbui/COMPDD/sample_configs/sample_docking.yaml")

_vina_prep_rec(cfg)