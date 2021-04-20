import math
from tqdm import tqdm
from imagePrepare import *
from points import *

def checkPoints(h, points):
    """
     checks if all given points are in the h (hsv) image
     returns TRUE / FALSE 
    """

    # check for every point if it is inside
    for point in points:
        if(h[int(point[1])][int(point[0])] < 200):
            return False
    return True



def findPinsLeft(h, height, width):
    """ find possible pins, that are still in holding area """

    s = math.sqrt(width**2 + height**2)
    delta = math.acos(height/s)*180/math.pi

    print("\ndelta: " + str(delta))
    

    s_height, s_width = h.shape

    possiblePins = [] # list of all possible pins positions

    # go over all points in image
    for y_num, y in tqdm(enumerate(h), total=s_height):
        for x_num, x in enumerate(y):
            
            if(h[y_num, x_num] > 50):  # check if center point is black ... if it is, than it is on pin

                for fi in range(-90,90,5): # for each point check all possible rotations ( but not "mirrored" )
                    status = True # if all tests check out, point is center of a pin

                    cornerPoints = redPoints([x_num, y_num], height, width,s, fi, delta)

                    # check if points are inside the image
                    for point in cornerPoints:
                        if(point[0] < 0 or point[1] < 0 ): 
                            status = False
                        if(point[0] > s_width-1 or point[1] > s_height-1): 
                            status = False
                    
                    # go thrue a list of checks of all points
                    center = [x_num, y_num]

                    if(status):
                        status = checkPoints(h, [center])
                    
                    if(status):
                        status = checkPoints(h, cornerPoints)
                    
                    if(status):
                        status = checkPoints(h, darkBluePoints(center, height, width, fi))
                    
                    if(status):
                        status = checkPoints(h, yellowPoints(center, height, width, fi))
                    
                    if(status):
                        status = checkPoints(h, pinkPoints(center, height, width, fi))

                    if(status):
                        status = checkPoints(h, brownPoints(center, width, fi))

                    # if all points are in the shape, save center point and fi as possible pin position

                    if(status):
                        possiblePins.append([center, fi])

    return possiblePins
                    
                    


