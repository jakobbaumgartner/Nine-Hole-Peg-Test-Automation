import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import time
import math
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
   
    


    print("\n---\nExecution time [s]: " + str( time.time()-t))
    cv.imshow('image',image)
    cv.waitKey(0)
    cv.destroyAllWindows()


def findRectangles2(image, circle):
    t = time.time() # algoritem execution time
    
    # cut out only area of interest
    x1 = int(circle[0] - circle[2] - 30) 
    x2 = int(circle[0] + circle[2] + 30)
    y1 = int(circle[1] - circle[2] - 30)
    y2 = int(circle[1] + circle[2] + 30)

    image = image[y1:y2,x1:x2]
    
    height, width, channels = image.shape

    image_small = cv.resize(image,(int(width/6), int(height/6)) )
    
    # convert to hsv
    hsv_image = cv.cvtColor(image_small, cv.COLOR_BGR2HSV)
    h, s, v = cv.split(hsv_image)
               
    # blur       
    # h = cv.GaussianBlur(h, (19,19), 3)

    # treshold
    h[h > 50] = 255

    # convert image to smaller one, for faster computations

    # h_small = cv.resize(h,(int(width/6), int(height/6)) )
    h[h > 100] = 255
    h[h <= 100] = 0

    # detect edges
    edges = cv.Canny(h,50,100)

    # find contours
    contours, hierarchy =  cv.findContours(edges, 1,2)

    cv.drawContours(image, contours, -1, (0,255,0), 3)

    half_length = 20 # half of length of peg on its side
    quarter_length = int(half_length/2)

    
    s_height, s_width = h.shape
    both_in = 0

    # print(h.shape)
 
    # go over all elements
    for y_num, y in enumerate(h):
        for x_num, x in enumerate(y):
            for fi in range(-90,90,30):
                # calculate upper and lower point
                # (top left if 0,0)
                upper_x = x_num - half_length * int(math.cos(fi)) 
                upper_y = y_num - half_length * int(math.sin(fi)) 
                lower_x = x_num + half_length * int(math.cos(fi)) 
                lower_y = y_num + half_length * int(math.sin(fi)) 

                # remove points that are out of frame
                if(upper_x < 0 or upper_y < 0 or lower_x < 0 or lower_y < 0): 
                    break
                if(upper_x > s_width-1 or upper_y > s_height-1 or lower_x > s_width-1 or lower_y > s_height-1): 
                    break
                

                # check if center point is black ... if it is, than it is on pin
                if(h[y_num, x_num] < 50):
                    # check if upper point is black 
                    if(h[upper_y, upper_x] < 50):
                        # check if lower point is black
                        if(h[lower_y, lower_x] < 50):
                        
                            # calculate two more points, on quarters o--o--X--o--o
                            q_upper_x = x_num - quarter_length * int(math.cos(fi)) 
                            q_upper_y = y_num - quarter_length * int(math.sin(fi)) 
                            q_lower_x = x_num + quarter_length * int(math.cos(fi)) 
                            q_lower_y = y_num + quarter_length * int(math.sin(fi)) 
                            
                            # check if upper quarter point is in
                            if(h[q_upper_y, q_upper_x] < 50):
                                # check if lower quarter point is in
                                if(h[q_lower_y, q_lower_x] < 50):
                                    cv.line(image_small, (lower_x, lower_y), (upper_x, upper_y),(0,0,255), 1)

                                    
                            
                     


                


                


    


    print("\n---\nExecution time [s]: " + str( time.time()-t))
    cv.namedWindow("h", cv.WINDOW_NORMAL) 
    # cv.namedWindow("h small", cv.WINDOW_NORMAL) 
    cv.namedWindow("image_small", cv.WINDOW_NORMAL) 
    cv.imshow('h',h)
    # cv.imshow('h small',h_small)
    cv.imshow('image_small', image_small)
    cv.waitKey(0)
    cv.destroyAllWindows()
