#! /usr/bin/env python

import json
import requests


class Service():

    def __init__(self, device_name):
        self.volume = 10
        self.device_name = device_name

    def trigger(self, bt_num, service_typ):
        print('service trigger %s %s %s' % (self.device_name, bt_num, service_typ))
        try:
            with open('services.json') as service_file:
                service_data = json.load(service_file)
                if not isinstance(service_data, object):
                    raise TypeError()
        except IOError as exc:
            print('Cannot read File!')
        except ValueError as exc:
            print('Cannot parse File as json!')
        except TypeError as exc:
            print('Is not json array')
        else:
            for device in service_data:
                if device in self.device_name:
                    for num, service in enumerate(service_data[device]):
                        if num == bt_num:
                            try:
                                my_servive = service[service_typ]
                                loc = my_servive['loc']
                                req = my_servive.get('req', 'GET')
                                prt = str(my_servive.get('prt', 80))
                                pth = my_servive.get('pth', '/')
                                bdy = my_servive.get('bdy')
                                hdr = my_servive.get('hdr')

                                if my_servive.get('sonosVolumeUp'):
                                    self.volume += 2
                                    bdy = bdy % (self.volume)
                                if my_servive.get('sonosVolumeDown'):
                                    self.volume -= 2
                                    bdy = bdy % (self.volume)
                                requests.request(req,
                                                 'http://' + loc + ':' + prt + pth,
                                                 headers=hdr, data=bdy, timeout=0.5)
                            except KeyError:
                                pass  # ignore if not exists
