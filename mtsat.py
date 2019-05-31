# mtsat.py
import json
import asyncio
from mtapi import asyncapi as amtapi
from mtapi import error as mt_error
from router import Router

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
    async def router_task(cls, r_name, *commands):
        router = None
        print(cls.routers[r_name])
        try:
            async with Router(
                cls.loop, debug=True, **cls.routers[r_name]) as router:
                for command in commands:
                    action, ip = command
                    await router.commands[action](ip)
        except:
            raise
#        try:
#            router = await amtapi.connect(
#                cls.loop, debug=True, **cls.routers[r_name])
#        except mt_error.FatalError as e:
#            print("Connection closed.")
#        except mt_error.TrapError as e:
#            print(e)
#        except asyncio.futures.TimeoutError:
#            print("Time out.")
#        except OSError as e:
#            print(e)
#        else:
#            for command in commands:
#                action, ip = command
#                print("Sending '{} {}' to {}".format(
#                    action, ip, r_name))
#                await asyncio.sleep(random.randint(1,3))
#        finally:
#            if router:
#                await router.close()

    @classmethod
    async def main_task(cls, commands,):
        cmds_per_router = {}
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
                rname = cls.groups[command["group"]]
                add_command(rname, command)

        tasks = [
            cls.router_task(rname, *rcommands)
            for rname, rcommands in cmds_per_router.items()]
        await asyncio.gather(*tasks, loop=cls.loop)

    @classmethod
    def run(cls, config, in_file):
        # getting config and command file
        try:
            cls.routers, cls.groups = cls.parse_config(config)
        except FileNotFoundError as e:
            print(e)
            return

        try:
            commands = cls.parse_input(in_file)
        except FileNotFoundError as e:
            print(e)
            return

        print("Running...")
        cls.loop = asyncio.get_event_loop()
        try:
            cls.loop.run_until_complete(cls.main_task(commands))
        except KeyboardInterrupt as e:
            for task in asyncio.Task.all_tasks():
                task.cancel()

if __name__ == "__main__":
    config = "dev_mtsat.conf"
    in_file = "test_deny.txt"
    mtsat.run(config, in_file)
