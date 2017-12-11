#! /usr/bin/env python

import socket
from zeroconf import ServiceBrowser, Zeroconf


class ZeroconfListener():

    def __init__(self, add_service_handler):
        self.add_service_handler = add_service_handler
        zeroconf = Zeroconf()
        ServiceBrowser(zeroconf, "_zapp._tcp.local.", self)

    def is_a_zapp_device(self, name):
        return name.startswith('zapp-') and name[5:13].isdigit()

    def remove_service(self, zeroconf, type, name):
        pass

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            if self.is_a_zapp_device(info.name):
                ip = socket.inet_ntoa(info.address)
                self.add_service_handler(name, ip)
