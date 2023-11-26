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
SCAN_MAX_TILT = 0.3

LASER_TARGET = (300, 300) # Slightly below center, will need to adjust


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
    
    def turn_to_target(self, target):
        # Target is an x, y tuple representing pixel in the camera we want to turn to
        # If far enough away, turn to target
        if (target[0] - LASER_TARGET[0]) ** 2 + (target[1] - LASER_TARGET[1]) ** 2 > 1000:
            rotation_msg = RotationCommand()
            rotation_msg.position = (target[0] - LASER_TARGET[0]) / 10
            rotation_msg.max_speed = 0.5
            self.write(rotation_msg.SerializeToString(), MsgType.ROTATION_COMMAND)
            return False
        
        # If closer but not close enough, turn a fixed amount
        elif (target[0] - LASER_TARGET[0]) ** 2 + (target[1] - LASER_TARGET[1]) ** 2 > 100:
            rotation_msg = RotationCommand()
            rotation_msg.position = 5
            rotation_msg.max_speed = 0.5
            self.write(rotation_msg.SerializeToString(), MsgType.ROTATION_COMMAND)
            return False
        
        # If close enough, stop turning
        return True

def main():
    module = VisionModule(ADDRESS, PORT)
    module.run()

if __name__ == "__main__":
    main()