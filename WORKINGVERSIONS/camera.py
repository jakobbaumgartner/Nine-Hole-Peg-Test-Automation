import numpy as np 
import cv2 as cv
import matplotlib.pyplot as plt
import time

class Camera:
    
    def calculateFps(self):
        maxFps = 120
        start = time.time()
        for i in range(0, maxFps):
            ret, frame = cap.read()
        end = time.time()
        fps = maxFps / (end - start)
        
        return fps