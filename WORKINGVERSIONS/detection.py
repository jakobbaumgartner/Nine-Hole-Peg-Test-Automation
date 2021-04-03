import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import time
from tqdm import tqdm

from helperMethods import *


def findCircles(blurImg, tH):
    # Find candidates for setted pins.
    pinsCandidates = cv.HoughCircles(
        blurImg,
        cv.HOUGH_GRADIENT,
        3,
        50,
        param1=tH,
        param2=5,
        minRadius=3,
        maxRadius=10)
    # Find collection area for unsetted pins.
    collectionArea = cv.HoughCircles(
        blurImg,
        cv.HOUGH_GRADIENT,
        3,
        50,
        param1=tH,
        param2=100,
        minRadius=185,
        maxRadius=215)
    
    return pinsCandidates, collectionArea


def detectHand(currentSum, startSum):
    if (int(startSum) - int(currentSum) > 5000000):
        return True
    return False


def findRectangles(image, circle):
    t = time.time()
    
    
    x1 = int(circle[0] - circle[2] - 30)
    x2 = int(circle[0] + circle[2] + 30)
    y1 = int(circle[1] - circle[2] - 30)
    y2 = int(circle[1] + circle[2] + 30)

    image = image[y1:y2,x1:x2]# convert to HSV
    
    hsv_image = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    h, s, v = cv.split(hsv_image)


    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
           
    #blur       
    h = cv.GaussianBlur(h, (19,19), 3)
    h[h > 50] = 255

    edges = cv.Canny(h,50,100)

    elapsed = time.time()-t
    

    print(elapsed)
    cv.imshow('image',edges)
    cv.waitKey(0)
    cv.destroyAllWindows()


