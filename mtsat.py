# mtsat.py

import json

config = "./mtsat.conf"

class mtsat:
    groups = {}
    routers = {}
    
    @classmethod
    def parse_config(cls):
        mt_config = []
        with open(config, 'r') as conf:
            mt_config = json.load(conf)

        cls.groups = mt_config.get("groups")
        cls.routers = mt_config.get("routers")

    @classmethod
    def print_config(cls):
        print(cls.groups)
        print(cls.routers)

if __name__ == "__main__":
    mtsat.parse_config()
    mtsat.print_config()

