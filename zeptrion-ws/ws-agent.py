#! /usr/bin/env python

import json
import threading


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
                diffs = [a + b for a, b in zip(self.zeptrion_devices[ip].bta,
                         message_data['eid2'].get('bta'))]
                for num, diff in enumerate(diffs):
                    service_type = None
                    if '.P' == diff:
                        service_type = 'pressed'
                        self.zeptrion_devices[ip].timer = threading.Timer(0.25, self.tick_event, args=(ip, num))
                        self.zeptrion_devices[ip].timer.start()
                    if 'P.' == diff:
                        service_type = 'released'
                        self.zeptrion_devices[ip].timer.cancel()
                    if service_type:
                        self.zeptrion_devices[ip].service.trigger(num, service_type)

                self.zeptrion_devices[ip].bta = message_data['eid2'].get('bta')

    def tick_event(self, ip, num):
        if 'P' in self.zeptrion_devices[ip].bta:
            self.zeptrion_devices[ip].service.trigger(num, "tick")
            self.zeptrion_devices[ip].timer = threading.Timer(0.25, self.tick_event, args=(ip, num,))
            self.zeptrion_devices[ip].timer.start()

    def on_close_ws(self, ip):
        try:
            del self.zeptrion_devices[ip]
            print('removed zeptrion device [%s]' % (ip))
        except KeyError:
            pass                        # ignore if "ws" was already closed

    def on_add_device(self, name, ip):
        if ip not in self.zeptrion_devices:
            conn = ws.Connection(ip, self.on_close_ws, self.on_ws_message)
            self.zeptrion_devices[ip] = conn
            self.zeptrion_devices[ip].bta = '.........'
            self.zeptrion_devices[ip].timer = None
            self.zeptrion_devices[ip].service = service.Service(name)
            print('new zeptrion device [%s][%s]' % (ip, name))

    def run(self):
        try:
            input('Press enter to exit...\n\n')
        finally:
            exit(0)


if __name__ == '__main__':
    app = WSAgent()
    app.run()
