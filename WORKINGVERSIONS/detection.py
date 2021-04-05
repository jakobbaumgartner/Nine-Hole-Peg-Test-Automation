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
    t = time.time() # algoritem execution time
    
    # cut out only area of interest
    x1 = int(circle[0] - circle[2] - 30) 
    x2 = int(circle[0] + circle[2] + 30)
    y1 = int(circle[1] - circle[2] - 30)
    y2 = int(circle[1] + circle[2] + 30)

    image = image[y1:y2,x1:x2]
    
    # convert to hsv
    hsv_image = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    h, s, v = cv.split(hsv_image)

    # convert to gray
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
               
    # blur       
    h = cv.GaussianBlur(h, (19,19), 3)

    # treshold
    h[h > 50] = 255

    # detect edges
    edges = cv.Canny(h,50,100)

    # find contours
    contours, hierarchy =  cv.findContours(edges, 1,2)

    # method 1 of finding number of pins left, calculating total contour area
    #  and deviding by approximate area of one pin
    area = 0

    
    
    # array of potential lengths, that are long enough to be a pin
    potential_lengths = []

    for num, cnt in enumerate(contours):

        # we use every second contour, as they are for some reason drawn twice almost same
        # HACK: to fix later

        # min_len     
        potential_lengths.append([])

        if num%2 == 0:

            cnt = cv.approxPolyDP(cnt, 2, True)
            area  += cv.contourArea(cnt)
            cv.drawContours(image, [cnt], -1, (255,50,25), 3)
            
            # we look at the distance between all points in the contour
            # we create vectors: (point1, point2, distanceSquared)

            for point in cnt:
                # print("point : " + str(point[0]))
                cv.circle(image, (point[0,0], point[0,1]),1,(0,0,255))
                
                for point2 in cnt:
                    if(point[0] != point2[0]).all():
                        
                        # if not same point
                        distanceSquared = (point[0,0]-point2[0,0])**2 + (point[0,1]-point2[0,1])**2
                        if(distanceSquared > 10500 and distanceSquared < 11000):
                            potential_lengths[num].append([point, point2, distanceSquared])
                        # print("P1: " + str(point[0]) + "  P2: " + str(point2[0]) + "  Distance: " + str(distanceSquared))
                        
        for line in potential_lengths[num]:
            cv.line(image, (line[0][0][0], line[0][0][1]),(line[1][0][0], line[1][0][1]), (0,255,0), 1)
            # print(line[1][0][0])

        
    # for element in potential_lengths[2]:
    #     print(element)
            

    print("Št.pinov glede na površino:  " +  str(int(area / 3200)))
   
    
    
   
    # cv.circle(image, )










    print("\n---\nExecution time [s]: " + str( time.time()-t))
    cv.imshow('image',image)
    cv.waitKey(0)
    cv.destroyAllWindows()


