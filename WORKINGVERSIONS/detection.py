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
   
   # convert to HSV
    
    hsv_image = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    h, s, v = cv.split(hsv_image)
    # print(h)

    # remove values of area not of interest
    yp = 0
    for y in tqdm(h):
        yp += 1
        xp = 0
        for x in y:
            xp +=1 
            if(not ((xp-int(circle[0]))**2 + (yp-int(circle[1]))**2 < (int(circle[2]) + 40)**2)):
                h[yp-1,xp-1] = 0
                s[yp-1,xp-1] = 0
                v[yp-1,xp-1] = 0
            else:
                if(h[yp-1,xp-1] >= 60):
                    h[yp-1,xp-1] = 0
                    s[yp-1,xp-1] = 0
                    v[yp-1,xp-1] = 0
                else:
                    h[yp-1,xp-1] = 100
                    s[yp-1,xp-1] = 0
                    v[yp-1,xp-1] = 255
           
    h = cv.GaussianBlur(h, (19,19), 3)

    img = cv.merge([h,s,v])
    img = cv.cvtColor(img, cv.COLOR_HSV2BGR)
    
    contours,hierarchy = cv.findContours(h, 1, 2)
    cv.drawContours(img, contours, -1, (0,255,0), 3)

    cv.imshow('image',img)
    cv.waitKey(0)
    cv.destroyAllWindows()
    