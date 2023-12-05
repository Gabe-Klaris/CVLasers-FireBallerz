# NAME: vision_module.py
# PURPOSE: Processes targets and gives instructions
# AUTHOR: Emma Bethel and William Soylemez

import os
import robomodules as rm
from messages import MsgType, message_buffers, TiltCommand, RotationCommand
from local_camera_reader import LocalCameraFeed
from shape_finders import find_triangles, find_circles, find_octagons, find_squares
import time

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
        # self.camera_feed = LocalCameraFeed()

    # runs every time one of the subscribed-to message types is received
    def msg_received(self, msg, msg_type):
        # print(msg)
        pass

    # runs every 1 / FREQUENCY seconds
    def tick(self):
        
        # self.scan_tick()
        if False: # For moving camera
            self.tilt(float(input("Tilt: ")))
            self.rotate(float(input("Rotate: ")))
            return
        # self.turn_to_target((500, 300))
        
        frame = self.camera_feed.read()
        target_x, target_y = find_triangles(frame, "red")[0]
        print(target_x)
        self.rotate_to_target(target_x)

    def find_target(self, shape_function, color):
        results = dict()
        for i in range(10):
            frame = self.camera_feed.read()
            centers = shape_function(frame, color)
            for center in centers:
                # Add center to results if close enough to existing result
                for result in results:
                    if abs(result[0] - center[0]) < 10 and abs(result[1] - center[1]) < 10:
                        results[result] += 1
                        break
                    else:
                        results[center] = 1
            time.sleep(0.05)

        max_center = max(results, key=results.get)
        return max_center if results[max_center] >= 3 else None

    def scan_tick(self):
        # Get tilt direction
        if self.scan_direction == 1:
            tilt = SCAN_MAX_TILT
        else:
            tilt = -SCAN_MAX_TILT
        self.scan_direction *= -1

        # Write messages to motor module
        self.tilt(tilt)
        self.rotate(SCAN_ROTATION_STEP)
    
    def rotate_to_target(self, target_x):
        # Target is an x, y tuple representing pixel in the camera we want to turn to
        # If far enough away, turn to target
        if (target_x - LASER_TARGET[0]) > 30:
            print("Turning by " + str((target_x - LASER_TARGET[0]) / 10))
            self.rotate((target_x - LASER_TARGET[0]) / 10)
            return False
        
        # If closer but not close enough, turn a fixed amount
        elif (target_x - LASER_TARGET[0]) > 5:
            print("Turning by 5")
            self.rotate(5)
            return False
        
        # If close enough, stop turning
        return True

    def rotate(self, angle):
        rotation_msg = RotationCommand()
        rotation_msg.position = angle
        rotation_msg.max_speed = 0.5
        self.write(rotation_msg.SerializeToString(), MsgType.ROTATION_COMMAND)

    def tilt(self, angle):
        tilt_msg = TiltCommand()
        tilt_msg.position = angle
        self.write(tilt_msg.SerializeToString(), MsgType.TILT_COMMAND)

def main():
    module = VisionModule(ADDRESS, PORT)
    module.run()

if __name__ == "__main__":
    main()