# mtsat.py
import sys
import json
import asyncio
import logging
from mtapi import asyncapi as amtapi
from mtapi import error as mt_error
from . router import Router

CONFIG = "/usr/local/etc/mtsat.conf"
LOGFILE = "/var/log/mtsat.log"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class mtsat:
    loop = None
    timeout = 5
    routers = {}
    groups = {}
    ipfw_list=""
    debug = False;
    logger = logging.getLogger('mtsat')


    @classmethod
    def parse_config(cls,config):
        mt_config = []
        with open(config, 'r') as conf:
            mt_config = json.load(conf)

        opt = mt_config.get("options", {})
        cls.ipfw_list = opt.get("ipfw_list", "NODENY-ALLOW")
        cls.debug = opt.get("debug", False)
        cls.logger.setLevel(
            logging.DEBUG) if cls.debug else cls.logger.setLevel(logging.WARN)


        cls.routers = mt_config.get("routers", {})
        cls.groups = mt_config.get("groups", {})
        

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
    async def router_task(cls, r_name, *commands):
        router = None
        try:
            async with Router(
                cls.loop,
                debug=cls.debug,
                ipfw_list=cls.ipfw_list,
                **cls.routers[r_name]) as router:
                for command in commands:
                    action, ip = command
                    await router.commands[action](ip)
        except asyncio.TimeoutError as e:
            cls.logger.error("{}: connection timeout".format(r_name))
        except mt_error.FatalError as e:
            cls.logger.error("{}: connection closed.".format(r_name))
        except mt_error.TrapError as e:
            cls.logger.error("{}: {}".format(r_name, e))
        except OSError as e:
            cls.logger.error("{}: {}".format(r_name, e))


    @classmethod
    async def main_task(cls, commands,):
        cmds_per_router = {}
        unknown_groups = set()
        def add_command(rname, command):
            nonlocal cmds_per_router
            if not cmds_per_router.get(rname, None):
                cmds_per_router.update(
                    {rname: [(command['action'], command['ip'])]}
                )
            else:
                cmds_per_router[rname].append((command['action'], command['ip']))

        for command in commands:
            if not command["group"]:
                # send command to all routers
                for rname in cls.routers.keys():
                    add_command(rname, command)
            else:
                group = command["group"]
                if group in unknown_groups:
                    continue
                rnames = cls.groups.get(group)
                if rnames:
                    if not isinstance(rnames, list):
                        rnames = list((rnames,))
                    for rname in rnames:
                        add_command(rname, command)
                else:
                    unknown_groups.add(group)
                    cls.logger.error("Unknown group: {}".format(group))

        tasks = [
            cls.router_task(rname, *rcommands)
            for rname, rcommands in cmds_per_router.items()]
        await asyncio.gather(*tasks, loop=cls.loop)

    @classmethod
    def run(cls, config, in_file):
        try:
            cls.parse_config(config)
        except FileNotFoundError as e:
            cls.logger.critical(e)
            return

        try:
            commands = cls.parse_input(in_file)
        except FileNotFoundError as e:
            cls.logger.critical(e)
            return

        cls.loop = asyncio.get_event_loop()
        try:
            cls.loop.run_until_complete(cls.main_task(commands))
        except KeyboardInterrupt as e:
            for task in asyncio.Task.all_tasks():
                task.cancel()

def main():
    logging.basicConfig(
        filename = LOGFILE,
        format = LOG_FORMAT,
        datefmt= DATE_TIME_FORMAT)
    if len(sys.argv) > 1:
        in_file = sys.argv[1]
        mtsat.run(CONFIG, in_file)
    else:
        mtsat.logger.critical("No input file specified")
