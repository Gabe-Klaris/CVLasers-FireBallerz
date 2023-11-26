#!/usr/bin/env python3

# NAME: remote_camera_reader.py
# PURPOSE: wrapper class for reading the most recent frame from a remote camera 
#          stream on your local computer
# AUTHOR: this dude on stackoverflow tbh https://stackoverflow.com/a/54755738

import os, cv2, threading, queue, time

from shape_finders import find_triangles

ADDRESS = os.environ.get("STREAM_ADDRESS","192.168.0.89")
PORT = os.environ.get("STREAM_PORT", 9000)


class RemoteCameraFeed:

    # PURPOSE: constructor
    # PARAMETERS: source - URI of the remote stream
    #                      (e.g. tcp://192.168.0.89:9000)
    # RETURNS: N/A
    def __init__(self, source):
        self.cap = cv2.VideoCapture(source)
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

    # PURPOSE: continously reads from camera feed such that unused frames will 
    #          be discarded
    # PARAMETERS: N/A
    # RETURNS: N/A
    def _reader(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()   # discard previous (unprocessed) frame
                except queue.Empty:
                    pass
            self.q.put(frame)

    # PURPOSE: retrieves and parses the most recent frame in the camera stream
    # PARAMETERS: N/A
    # RETURNS: the frame, as a 3D numpy array (such that each pixel is a trio 
    #          of RGB values)
    def read(self):
        return self.q.get()


if __name__ == '__main__':
    feed = RemoteCameraFeed(f'tcp://{ADDRESS}:{PORT}')

    while True:
        frame = feed.read()

        # Find triangles
        centers = find_triangles(frame, (255, 0, 0), 1000)
        for center in centers:
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
        print(centers)
        cv2.imshow('Camera Feed', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
