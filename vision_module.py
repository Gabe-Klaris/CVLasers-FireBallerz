#!/usr/bin/env python3

# NAME: blank_module.py
# PURPOSE: empty robomodule (for use as a template)
# AUTHOR: Emma Bethel

import os
import robomodules as rm
from messages import MsgType, message_buffers

# retrieving address and port of robomodules server (from env vars)
ADDRESS = os.environ.get("LOCAL_ADDRESS","localhost")
PORT = os.environ.get("LOCAL_PORT", 11295)

FREQUENCY = 2


class VisionModule(rm.ProtoModule):
    # sets up the module (subscriptions, connection to server, etc)
    def __init__(self, addr, port):
        self.subscriptions = [MsgType.TARGET]
        super().__init__(addr, port, message_buffers, MsgType, FREQUENCY, self.subscriptions)
        print("Blank module initialized")

    # runs every time one of the subscribed-to message types is received
    def msg_received(self, msg, msg_type):
        print(msg)

    # runs every 1 / FREQUENCY seconds
    def tick(self):
        pass
        

def main():
    module = VisionModule(ADDRESS, PORT)
    module.run()


if __name__ == "__main__":
    main()