# router.py
import asyncio
from mtapi import asyncapi as amtapi

import random

class Router():
    def __init__(self, loop=None, debug=False,
                 address='192.168.88.1',
                 port='8728',
                 username='admin',
                 password='',
                 ipfw_list='sat_test'):

        self.loop = loop if loop else asyncio.get_event_loop()
        self.debug = False
        self.address = address
        self.port = port
        self.user = username
        self.password = password
        self.ipfw_list = ipfw_list

        self.api = amtapi.API(self.loop)
        self.api.set_debug(self.debug)
        self.commands = {'flush': self.flush,
                         'allow': self.allow,
                         'deny': self.deny}
          

    async def __aenter__(self):
        try:
            await self.api.connect(self.address, self.port)
        except:
            raise
        else:
            try:
                await self.api.login(self.user, self.password)
            except:
                raise
            else:
                return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.api.close()


    async def remove_from_ipfw_list(self, unparsed_ids):
        ids = []
        for status, data in unparsed_ids:
            if status == '!re':
                ids.append(data['.id'])
            elif status == '!trap':
                print("router {}: remove: {}".format(
                    self.address, data('message')))
                return
        response = await self.api.talk(
            '/ip/firewall/address-list/remove',
            '=.id='+','.join(ids))
        return ids


    async def flush(self, ip):
        # /ip/firewall/address-list/print ?list=sat_test
        ids = []
        response = await self.api.talk(
            '/ip/firewall/address-list/print',
            '=.proplist=.id',
            '?list='+self.ipfw_list)

        print("router {}: flush".format(
            self.address))
        ids = await self.remove_from_ipfw_list(response)
        print(ids)


    async def allow(self, ip):
        response = await self.api.talk(
            '/ip/firewall/address-list/add',
            '=list='+self.ipfw_list,
            '=address='+ip)
        print("router {}: allow {} {}".format(
            self.address, ip, response))


    async def deny(self, ip):
        # /ip/firewall/address-list/remove =.id=*3,*5
        response = await self.api.talk(
            '/ip/firewall/address-list/print',
            '=.proplist=.id',
            '?address='+ip,
            '?list='+self.ipfw_list)
        removed_ids = await self.remove_from_ipfw_list(response)        

        if (removed_ids):
            print("router {}: deny {}".format(
                self.address, ip))
            print(removed_ids)
        else:
            print("router {}: deny {} no such ip".format(
                self.address, ip))

