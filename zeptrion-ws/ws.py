#! /usr/bin/env python

import threading
import websocket


class Connection(object):

    def __init__(self, ip, close_handler, message_handler):
        self.ip = ip
        self.close_handler = close_handler
        self.message_handler = message_handler
        self.ping = threading.Condition()
        self.stop_event = threading.Event()
        self.url = 'ws://%s/' % self.ip
        self.ws = websocket.WebSocketApp(self.url,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close,
                                         on_ping=self.on_ping)

        self.ws.on_open = self.on_open
        ws_thread = threading.Thread(target=self.ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()

    def on_message(self, ws, message):
        print("ws connection message from %s >> %s" % (self.ip, message))
        self.message_handler(self.ip, message)

    def on_error(self, ws, error):
        print("ws error connection to %s" % self.ip)
        print(error)

    def on_close(self, ws):
        print("closed ws connection to %s" % self.ip)
        self.stop_event.set()
        self.close_handler(self.ip)

    def on_open(self, ws):
        print("open ws connection to %s" % self.ip)
        self.stop_event.clear()
        ping_thread = threading.Thread(target=self.ping_monitoring)
        ping_thread.daemon = True
        ping_thread.start()

    def on_ping(self, ws, message):
        print("ws connection ping from %s" % self.ip)
        with self.ping:
            self.ping.notify_all()

    def ping_monitoring(self):
        while True:
            with self.ping:
                notifyed = self.ping.wait(64)
            print("ws connection monitoring of %s" % self.ip)
            if notifyed is False:
                self.ws.close()
                self.stop_event.set()   # this ends the while loop
                break  # kill while
