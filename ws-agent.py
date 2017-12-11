#! /usr/bin/env python

import json


import discovery
import ws
import service


class WSAgent():
    zeptrion_devices = {}

    def __init__(self):
        discovery.ZeroconfListener(self.on_add_device)

    def on_ws_message(self, ip, message):
        try:
            message_data = json.loads(message)
        except ValueError as exc:
            print('Cannot parse File as json!')
        else:
            if 'eid2' in message_data.keys():
                name = self.zeptrion_devices[ip].name
                diffs = [a + b for a, b in zip(self.zeptrion_devices[ip].bta,
                         message_data['eid2'].get('bta'))]
                for num, diff in enumerate(diffs):
                    service_type = None
                    if '.P' == diff:
                        service_type = 'pressed'
                    if 'P.' == diff:
                        service_type = 'released'
                    if service_type:
                        service.trigger(name, num, service_type)

                self.zeptrion_devices[ip].bta = message_data['eid2'].get('bta')

    def on_close_ws(self, ip):
        try:
            del self.zeptrion_devices[ip]
            print('removed zeptrion device [%s]' % (ip))
        except KeyError:
            pass                        # ignore if "ws" was already closed

    def on_add_device(self, name, ip):
        if ip not in self.zeptrion_devices:
            conn = ws.Connection(ip, self.on_close_ws, self.on_ws_message)
            conn.name = name
            self.zeptrion_devices[ip] = conn
            self.zeptrion_devices[ip].bta = '.........'
            print('new zeptrion device [%s][%s]' %
                  (ip, self.zeptrion_devices[ip].name))

    def run(self):
        try:
            input('Press enter to exit...\n\n')
        finally:
            exit(0)


if __name__ == '__main__':
    app = WSAgent()
    app.run()
