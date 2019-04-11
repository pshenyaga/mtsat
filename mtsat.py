# mtsat.py

import json

config = "./mtsat.conf"

class mtsat:
    groups = {}
    routers = {}
    commands = {}
    
    @classmethod
    def parse_config(cls):
        mt_config = []
        with open(config, 'r') as conf:
            mt_config = json.load(conf)

        cls.groups = mt_config.get("groups")
        cls.routers = mt_config.get("routers")
    
    @classmethod
    def parse_input(cls, in_file):
        with open(in_file, 'r') as _if:
            for cmd_line in _if:
                action = ip = group = None
                if 'flush' in cmd_line:
                    cls.commands.update({"flush": None})
                else:
                    action, ip, group = cmd_line.strip().split(':')
                    if cls.commands.get(ip, None):
                        del cls.commands[ip]
                    else:
                        cls.commands.update(
                            {ip: {"action": action, "group": group}})

    @classmethod
    def flush(cls):
        pass

    @classmethod
    def allow(cls):
        pass

    @classmethod
    def deny(cls):
        pass

    @classmethod
    def print_config(cls):
        print(cls.groups)
        print(cls.routers)

def main():
    in_file = "test_input.txt"
    mtsat.parse_input(in_file)

if __name__ == "__main__":
    main()

