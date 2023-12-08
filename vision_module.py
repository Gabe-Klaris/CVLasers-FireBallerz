# NAME: vision_module.py
# PURPOSE: Processes targets and gives instructions
# AUTHOR: Emma Bethel and William Soylemez

import os
import robomodules as rm
from messages import MsgType, message_buffers, TiltCommand, RotationCommand, LaserCommand
from local_camera_reader import LocalCameraFeed
from shape_finders import find_triangles, find_circles, find_octagons, find_squares
import time

# retrieving address and port of robomodules server (from env vars)
ADDRESS = os.environ.get("LOCAL_ADDRESS","localhost")
PORT = os.environ.get("LOCAL_PORT", 11295)

FREQUENCY = 2

SCAN_ROTATION_STEP = 10
SCAN_TILT = (-0.3, 0)

ROTATE_TARGET_MULTIPLIER = 0.07
TILT_TARGET_MULTIPLIER = 0.003

LASER_TARGET = (300, 240) # Slightly below center, will need to adjust

TARGET_COLOR_KEY = {
    0: "red",
    1: "yellow",
    2: "blue",
    3: "green"
}
TARGET_SHAPE_KEY = {
    0: find_squares,
    1: find_circles,
    2: find_triangles,
    3: find_octagons
}

class VisionModule(rm.ProtoModule):
    # sets up the module (subscriptions, connection to server, etc)
    def __init__(self, addr, port):
        self.subscriptions = [MsgType.TARGET]
        super().__init__(addr, port, message_buffers, MsgType, FREQUENCY, self.subscriptions)
        print("Vision module initialized")

        # Scanning state variables
        self.scan_direction = 1 # 1 for up, -1 for down
        self.camera_feed = LocalCameraFeed()

        self.tilt(0)
        self.current_target_shape = None
        self.current_target_color = None

    # runs every time one of the subscribed-to message types is received
    def msg_received(self, msg, msg_type):
        if msg_type == MsgType.TARGET:
            self.current_target_shape = TARGET_SHAPE_KEY[msg.shape]
            self.current_target_color = TARGET_COLOR_KEY[msg.color]
            print("Target received: ", msg.shape, msg.color)
        pass

    # runs every 1 / FREQUENCY seconds
    def tick(self):
        
        # self.scan_tick()
        if False: # For moving camera
            self.tilt(float(input("Tilt: ")))
            self.rotate(float(input("Rotate: ")))
            return
        # self.turn_to_target((500, 300))
        
        # frame = self.camera_feed.read()
        # target_x, target_y = find_triangles(frame, "red")[0]
        # print(target_x)
        # self.rotate_to_target(target_x)
        if self.current_target_color is None or self.current_target_shape is None:
            return
        self.scan_tick()
        time.sleep(0.2)
        center = self.find_target(self.current_target_shape, self.current_target_color)
        print(center)
        if center is not None:
            self.rotate_to_target(center[0])
            self.tilt_to_target(center[1])
            time.sleep(0.3)
            self.fire()
            self.current_target_color, self.current_target_shape = None, None
        input("Done!")


    def find_target(self, shape_function, color):
        results = dict()
        for i in range(10):
            frame = self.camera_feed.read()
            centers = shape_function(frame, color)
            for center in centers:
                # Add center to results if close enough to existing result
                result_found = False
                for result in results:
                    if abs(result[0] - center[0]) < 10 and abs(result[1] - center[1]) < 10:
                        results[result] += 1
                        result_found = True
                        break
                if not result_found:
                    results[center] = 1
            time.sleep(0.05)
        if len(results) == 0:
            return None
        max_center = max(results, key=results.get)
        return max_center if results[max_center] >= 3 else None

    def scan_tick(self):
        # Get tilt direction
        if self.scan_direction == 1:
            tilt = SCAN_TILT[0]
        else:
            tilt = -SCAN_TILT[1]
        self.scan_direction *= -1

        # Write messages to motor module
        self.tilt(tilt)
        self.rotate(SCAN_ROTATION_STEP)
    
    def rotate_to_target(self, target_x):
        # Rotate to target
        self.rotate((target_x - LASER_TARGET[0]) * ROTATE_TARGET_MULTIPLIER) 
    
    def tilt_to_target(self, target_y):
        # Tilt to target
        self.tilt((target_y - LASER_TARGET[1]) * TILT_TARGET_MULTIPLIER)


    def rotate(self, angle):
        rotation_msg = RotationCommand()
        rotation_msg.position = angle
        rotation_msg.max_speed = 0.5
        self.write(rotation_msg.SerializeToString(), MsgType.ROTATION_COMMAND)

    def tilt(self, angle):
        tilt_msg = TiltCommand()
        tilt_msg.position = angle
        self.write(tilt_msg.SerializeToString(), MsgType.TILT_COMMAND)

    def fire(self):
        laser_msg = LaserCommand()
        laser_msg.seconds = 1
        self.write(laser_msg.SerializeToString(), MsgType.LASER_COMMAND)

def main():
    module = VisionModule(ADDRESS, PORT)
    module.run()

if __name__ == "__main__":
    main()