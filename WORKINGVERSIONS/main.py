import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import time

from camera import *
from detection import *
from helperMethods import *
from holdingArea import *

# demo = True -> running test video, demo = False -> running camera
demo = True
# testing mode for running just specific functions, not whole program
testingMode = False


settedPinsCounter = 0
confirmedPins = 0
yArea = [0, 0]
startSum = 0
allPinsSetted = False
allPinsDown = False
start = False

if testingMode:
    # testing mode for running just specific functions, not whole program

    print("\n\n --- DEMO MODE --- \n")

    demoImage0 = cv.imread('../DEMO/WIN_20210401_12_22_10_Pro.jpg')

    blurImg, tH, h, s, v = prepareImage(frame)

    findCircles(blurImg, tH)




    cv.imshow('image',demoImage0)
    cv.waitKey(0)
    cv.destroyAllWindows()



else:
    if (not demo):
        cap = cv.VideoCapture(1)
    else:
        cap = cv.VideoCapture('../DEMO/TestVideo.mp4')

    runningFrameCounter = 0
    setupFrameCounter = 0
    maxFrame = 5

    # Cammera running loop.
    while (True):
        # Original frame from video live feed.

        setupFrameCounter += 1

       
        ret, frame = cap.read()

        if (start == False and setupFrameCounter == 1):
            startSum = frame.sum()

        currentSum = frame.sum()
        handInImage = detectHand(currentSum, startSum)

        if (handInImage and (start == False)):
            print("TIME STARTED")
            startTime = time.time()
            start = True

        # Start moving pins.
        if (start):
            blurImg, tH, h, s, v = prepareImage(frame)
            pinsCandidates, collectionArea = findCircles(blurImg, tH)

            runningFrameCounter += 1
            currentSum = frame.sum()
            handInImage = detectHand(currentSum, startSum)

            # Find collection area and use its y coordinate to determine
            # searching area for setted pins.
            if collectionArea is not None:
                collectionArea = np.floor(collectionArea[0, :]).astype('int')
                for (x, y, r) in collectionArea:
                    cv.circle(frame, (x, y), r, (255, 255, 255), 2)
                    yArea = [y - r, y + r]

            # Find actual setted pins with green circles on top.
            if pinsCandidates is not None:
                pinsCandidates = np.floor(pinsCandidates[0, :]).astype('int')
                for (x, y, r) in pinsCandidates:
                    # Look only on the left side of platform.
                    if (x < frame.shape[1] /
                            2 and (y > yArea[0] and y < yArea[1])):
                        # Look in hsv space for green circle.
                        if ((h[y, x] > 70 and h[y, x] < 170)
                                and s[y, x] > 0.15):
                            settedPinsCounter += 1
                            cv.circle(frame, (x, y), r, (255, 255, 255), 1)

            # Count setted pins on each *maxFrame* frame.
            if runningFrameCounter % maxFrame == 0:
                confirmedPins = np.round(
                    settedPinsCounter / maxFrame).astype('int')
                settedPinsCounter = 0

            print(confirmedPins)

            # Set flag if all pins are setted.
            if (confirmedPins == 9):
                allPinsSetted = True
                print("ALL PINS SETTED")
            # Set flag if all pins are down.
            if (allPinsSetted and (confirmedPins == 0)):
                allPinsDown = True
            # Break loop after all pins are down (if they were setted before)
            # and hand is not in the image.
            if (not handInImage and allPinsDown):
                endTime = time.time()
                elapsedTime = round(endTime - startTime, 2)
                allPinsSetted = False
                allPinsDown = False
                setupFrameCounter = 0
                print("FINISHED IN ", elapsedTime, "SECONDS")
                start = False

        cv.imshow('frame', frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    
    cap.release()
    cv.destroyAllWindows()
