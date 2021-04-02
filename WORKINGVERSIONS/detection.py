import numpy as np 
import cv2 as cv
import matplotlib.pyplot as plt
import time

class Detection:
    def findCircles(self, blurImg, tH):
        # Find candidates for setted pins.
        pinsCandidates = cv.HoughCircles(blurImg, cv.HOUGH_GRADIENT, 3, 50, param1 = tH, param2 = 5, minRadius = 3, maxRadius = 10)
        # Find collection area for unsetted pins.
        collectionArea = cv.HoughCircles(blurImg, cv.HOUGH_GRADIENT, 3, 50, param1 = tH, param2 = 100, minRadius = 100, maxRadius = 150)	

        return pinsCandidates, collectionArea

    def detectHand(self, currentSum, startSum):
        if (int(startSum) - int(currentSum) > 5000000):
            return True
        return False