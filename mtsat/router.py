# router.py
import asyncio
import logging
from mtapi import asyncapi as amtapi

import random

class Router():
    def __init__(self, loop=None, debug=False,
                 address='192.168.88.1',
                 port='8728',
                 username='admin',
                 password='',
                 ipfw_list='sat_test',
                 timeout=5):

        self.loop = loop if loop else asyncio.get_event_loop()
        self.debug = debug
        self.address = address
        self.port = port
        self.user = username
        self.password = password
        self.ipfw_list = ipfw_list

        self.api = amtapi.API(self.loop)
        #self.api.set_debug(True)
        self.api.set_debug(self.debug)
        self.timeout=timeout
        self.commands = {'flush': self.flush,
                         'allow': self.allow,
                         'deny': self.deny}
        self.logger = logging.getLogger('mtsat.router')
          

    async def __aenter__(self):
        await asyncio.wait_for(
            self.api.connect(self.address, self.port), timeout=self.timeout)
        await asyncio.wait_for(
            self.api.login(self.user, self.password), timeout=self.timeout)
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.api.close()


    async def remove_from_ipfw_list(self, unparsed_ids):
        ids = []
        for status, data in unparsed_ids:
            if status == '!re':
                ids.append(data['.id'])
            elif status == '!trap':
                self.logger.debug("{}: remove: {}".format(
                    self.address, data['message']))
                continue
        #for i in range(0, len(ids), 1000):
        for i in range(0, len(ids)):
            self.logger.debug("{}: remove_from_ipfw_list: removing id: {}".format(self.address, ids[i]))
            #response = await asyncio.wait_for(self.api.talk(
            #    '/ip/firewall/address-list/remove',
            #    '=.id='+','.join(ids[i:i+10])), timeout = self.timeout)
            response = await asyncio.wait_for(self.api.talk(
                '/ip/firewall/address-list/remove',
                '=.id='+ids[i]), timeout = self.timeout)
        return ids


    async def flush(self, ip):
        ids = []
        self.logger.debug(
	    "{}: flush: Fetching ip addresses".format(self.address))
        response = await asyncio.wait_for(self.api.talk(
            '/ip/firewall/address-list/print',
            '=.proplist=.id',
            '?list='+self.ipfw_list), timeout=self.timeout)

        self.logger.debug("{}: flush".format(
            self.address))
        ids = await self.remove_from_ipfw_list(response)

    async def allow(self, ip):
        response = await asyncio.wait_for(self.api.talk(
            '/ip/firewall/address-list/add',
            '=list='+self.ipfw_list,
            '=address='+ip), timeout=self.timeout)
        status, data = response[0]
        if status == '!done':
            self.logger.debug("{}: allow {}".format(
                self.address, ip))
        else:
            self.logger.warning("{}: allow {} - {}".format(
                self.address, ip, data['message']))


    async def deny(self, ip):
        response = await asyncio.wait_for(self.api.talk(
            '/ip/firewall/address-list/print',
            '=.proplist=.id',
            '?address='+ip,
            '?list='+self.ipfw_list), timeout=self.timeout)
        removed_id = await self.remove_from_ipfw_list(response)        

        if (removed_id):
            self.logger.debug("{}: deny {}".format(
                self.address, ip))
            self.logger.debug("{}: deny: removed id: {}".format(
	        self.address, removed_id))
        else:
            self.logger.warning("{}: deny {} no such ip".format(
                self.address, ip))

