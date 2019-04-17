# mtsat.py

import json
import asyncio
from mtapi import hlapi

class mtsat:
    loop = None
    routers = {}
    groups = {}
    connected = {}
    
    @classmethod
    def parse_config(cls,config):
        mt_config = []
        routers = {}
        groups = {}
        with open(config, 'r') as conf:
            mt_config = json.load(conf)

        routers = mt_config.get("routers")
        groups = mt_config.get("groups")
        return routers, groups
    
    @classmethod
    def parse_input(cls, in_file):
        commands = []
        with open(in_file, 'r') as _if:
            prev_ip = None
            for cmd_line in _if:
                action = ip = group = None
                if 'flush' in cmd_line:
                    commands.append(
                        {"action": "flush",
                         "ip": None,
                         "group": None})
                else:
                    action, ip, group = cmd_line.strip().split(':')
                    if ip == prev_ip:
                        commands.pop()
                    else:
                        commands.append(
                            {"action": action,
                             "ip": ip,
                             "group": group})
                    prev_ip = ip

        return commands

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
    def send_to_all(cls, command):
        print("Sending to all routers: {}".format(command["action"]))

    @classmethod
    def add_to_ipfw_list(cls, router, list_name, ip):
        pass

    @classmethod
    def remove_from_ipfw_list(cls, router, list_name, ip):
        pass

    @classmethod
    def router_task(cls, r_name, *commands):
        print(
            "Connecting to router: {}".format(
                r_name))
        print(
            "Sending '{} {}' to {}".format(
                command["action"], command["ip"], r_name))

    @classmethod
    def main_task(cls, commands):
        cmd_per_router = {}
        for command in commands:
            if not command["group"]:
                # send command to all routers
                cls.send_to_all(command)
            else:
                r_name = cls.groups[command["group"]]
                router = cls.connected.get(r_name, None)
                if router:
                    print("Sending {} to {}".format(
                        command["action"]+" "+command["ip"], r_name))
                else:
                    print("Connecting to {}".format(r_name))
                    cls.connected.update({r_name: "connected"})
                    print("Sending {} to {}".format(
                        command["action"]+" "+command["ip"], r_name))

    @classmethod
    def run(cls, config, in_file):
        # getting config and command file
        try:
            cls.routers, cls.groups = cls.parse_config(config)
        except FileNotFoundError as e:
            print(e)

        try:
            commands = cls.parse_input(in_file)
        except FileNotFoundError as e:
            print(e)

        print(cls.routers, cls.groups)
        print("Running...")
        cls.main_task(commands)

if __name__ == "__main__":
    config = "dev_mtsat.conf"
    in_file = "test_input.txt"
    mtsat.run(config, in_file)
