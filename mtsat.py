# mtsat.py

import json

config = "./dev_mtsat.conf"

with open(config, 'r') as conf:
    mt_config_l = json.load(conf)

print(mt_config_l)
