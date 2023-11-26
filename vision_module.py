# NAME: vision_module.py
# PURPOSE: Processes targets and gives instructions
# AUTHOR: Emma Bethel and William Soylemez

import os
import robomodules as rm
from messages import MsgType, message_buffers, TiltCommand, RotationCommand

# retrieving address and port of robomodules server (from env vars)
ADDRESS = os.environ.get("LOCAL_ADDRESS","localhost")
PORT = os.environ.get("LOCAL_PORT", 11295)

FREQUENCY = 2

SCAN_ROTATION_STEP = 10
SCAN_MAX_TILT = 1

class VisionModule(rm.ProtoModule):
    # sets up the module (subscriptions, connection to server, etc)
    def __init__(self, addr, port):
        self.subscriptions = [MsgType.TARGET]
        super().__init__(addr, port, message_buffers, MsgType, FREQUENCY, self.subscriptions)
        print("Vision module initialized")

        # Scanning state variables
        self.scan_direction = 1 # 1 for up, -1 for down

    # runs every time one of the subscribed-to message types is received
    def msg_received(self, msg, msg_type):
        # print(msg)
        pass

    # runs every 1 / FREQUENCY seconds
    def tick(self):
        
        self.scan_tick()

    def scan_tick(self):
        # Get tilt direction
        if self.scan_direction == 1:
            tilt = SCAN_MAX_TILT
        else:
            tilt = -SCAN_MAX_TILT
        self.scan_direction *= -1

        # Write messages to motor module
        tilt_msg = TiltCommand()
        tilt_msg.position = tilt
        self.write(tilt_msg.SerializeToString(), MsgType.TILT_COMMAND)
        rotation_msg = RotationCommand()
        rotation_msg.position = SCAN_ROTATION_STEP
        rotation_msg.max_speed = 0.5
        self.write(rotation_msg.SerializeToString(), MsgType.ROTATION_COMMAND)
    

def main():
    module = VisionModule(ADDRESS, PORT)
    module.run()


if __name__ == "__main__":
    main()