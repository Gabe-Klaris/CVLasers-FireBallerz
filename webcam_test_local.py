#!/usr/bin/env python3

# NAME: local_camera_reader.py
# PURPOSE: wrapper class for reading the most recent frame from a camera stream 
#          on the pi
# AUTHOR: Emma Bethel

import cv2
from picamera2 import Picamera2
from time import sleep


class LocalCameraFeed:

    # PURPOSE: constructor
    # PARAMTERS: N/A
    # RETURNS: N/A
    def __init__(self):
        self.cam = Picamera2()
        self.cam.start()
        sleep(1)

    # PURPOSE: retrieves and parses the most recent frame in the camera stream
    # PARAMETERS: N/A
    # RETURNS: the frame, as a 3D numpy array (such that each pixel is a trio 
    #          of RGB values)
    def read(self):
        frame = self.cam.capture_array('main')
        
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)


if __name__ == '__main__':
    feed = LocalCameraFeed()

    while True:
        frame = feed.read()

        cv2.imshow('Camera Feed', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break