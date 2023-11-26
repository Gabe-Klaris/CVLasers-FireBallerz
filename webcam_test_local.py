# NAME: read_local_camera_feed.py
# PURPOSE: reading and displaying (using OpenCV) a video feed from a local 
#          camera on a Raspberry Pi
# AUTHOR: Mostly this guy tbh https://pyimagesearch.com/2015/03/30/accessing-the-raspberry-pi-camera-with-opencv-and-python/

import cv2

from picamera import PiCamera
from picamera.array import PiRGBArray
from time import sleep

# setting resulution (can definitely play this; these cameras should be capable 
# of up to 1080p, though larger image sizes take longer to process)
RESOLUTION = (640, 480)

# set up/connect to camera
camera = PiCamera()
camera.resolution = RESOLUTION
camera.framerate = 32
raw_capture = PiRGBArray(camera, size=RESOLUTION)

# allow the camera to warmup
sleep(0.1)

# capture frames from the camera
for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the current frame
	image = frame.array

	# show the frame
	cv2.imshow("Frame", image)
	
    # clear the stream in preparation for the next frame
	raw_capture.truncate(0)

	# if the `q` key was pressed, break from the loop
	if cv2.waitKey(1) & 0xFF == ord("q"):
		break       