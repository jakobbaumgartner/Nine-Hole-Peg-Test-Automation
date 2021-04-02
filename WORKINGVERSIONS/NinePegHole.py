import numpy as np 
import cv2 as cv
import matplotlib.pyplot as plt
import time


cap = cv.VideoCapture(1)
runningFrameCounter = 0
setupFrameCounter = 0
maxFrame = 5
settedPinsCounter = 0
confirmedPins = 0
yArea = [0, 0]
startSum = 0
allPinsSetted = False
allPinsDown = False
start = False

def calculateThreshold(grayImage):
	tO = cv.threshold(grayImage, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)[0]
	tL = tO / 2
	tH = tO

	return tL, tH

def gammaImage(grayImage, gamma):
	dtype = grayImage.dtype
	grayImage = grayImage.astype('float')
	if dtype.kind in ('u', 'i'):
		minValue = np.iinfo(dtype).min
		maxValue = np.iinfo(dtype).max
	else:
		minValue = np.min(grayImage)
		maxValue = np.max(grayImage)
	rangeValue = maxValue - minValue

	grayImage = (grayImage - minValue) / float(rangeValue)
	gammaImg = grayImage**gamma
	gammaImg = float(rangeValue) * gammaImg + minValue

	gammaImg[gammaImg < 0] = 0
	gammaImg[gammaImg >255] = 255

	return gammaImg.astype(dtype)

def rgbToHsv(rgbImage):
	r = rgbImage[:, :, 2]
	g = rgbImage[:, :, 1]
	b = rgbImage[:, :, 0]

	cMax = np.maximum(r, np.maximum(g, b))
	cMin = np.minimum(r, np.minimum(g, b))
	delta = cMax - cMin + 1e-7

	h = np.zeros_like(r)
	s = np.zeros_like(r)
	v = np.zeros_like(r)

	h[cMax == r] = 60.0 * ((g[cMax == r] - b[cMax == r]) / (delta[cMax == r]) % 6.0)
	h[cMax == g] = 60.0 * ((b[cMax == g] - r[cMax == g]) / (delta[cMax == g]) + 2)
	h[cMax == b] = 60.0 * ((r[cMax == b] - g[cMax == b]) / (delta[cMax == b]) + 4)

	s[delta != 0] = delta[delta != 0] / (cMax[delta != 0] + 1e-7)

	v = cMax

	return h, s, v

def prepareImage(frame):
	# Gray image of frame.
	grayImg = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
	# HSV space of (colored) frame.
	h, s, v = rgbToHsv(frame / 255)
	# Gamma image to improve contrast on gray image.
	gammaImg = gammaImage(grayImg, 0.8)
	# Blurred gamma image.
	blurImg = cv.GaussianBlur(gammaImg, (3, 3), 0)
	# Automatic thresholding on blur image.
	tH = calculateThreshold(blurImg)[1]

	return blurImg, tH, h, s, v

def findCircles(blurImg, tH):
	# Find candidates for setted pins.
	pinsCandidates = cv.HoughCircles(blurImg, cv.HOUGH_GRADIENT, 3, 50, param1 = tH, param2 = 5, minRadius = 3, maxRadius = 10)
	# Find collection area for unsetted pins.
	collectionArea = cv.HoughCircles(blurImg, cv.HOUGH_GRADIENT, 3, 50, param1 = tH, param2 = 100, minRadius = 100, maxRadius = 150)	

	return pinsCandidates, collectionArea

def detectHand(currentSum, startSum):
	if (int(startSum) - int(currentSum) > 5000000):
		return True
	return False

def calculateFps():
	maxFps = 120
	start = time.time()
	for i in range(0, maxFps):
		ret, frame = cap.read()
	end = time.time()
	fps = maxFps / (end - start)
	return fps

if __name__ == '__main__':

	print("Calculating FPS... ")
	fps = calculateFps()
	print("Setup finished.")

	# Cammera running loop.
	while(True):
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

			# Find collection area and use its y coordinate to determine searching area for setted pins.
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
					if (x < frame.shape[1] / 2 and (y > yArea[0] and y < yArea[1])):
						# Look in hsv space for green circle.
						if ((h[y, x] > 70 and h[y, x] < 170) and s[y, x] > 0.15):
							settedPinsCounter += 1
							cv.circle(frame, (x, y), r, (255, 255, 255), 1)

			# Count setted pins on each *maxFrame* frame.
			if runningFrameCounter % maxFrame == 0:
				confirmedPins = np.round(settedPinsCounter / maxFrame).astype('int')
				settedPinsCounter = 0

			print(confirmedPins)

			# Set flag if all pins are setted.
			if (confirmedPins == 9):
				allPinsSetted = True
				print("ALL PINS SETTED")
			# Set flag if all pins are down.
			if (allPinsSetted and (confirmedPins == 0)):
				allPinsDown = True
			# Break loop after all pins are down (if they were setted before) and hand is not in the image.
			if (not handInImage and allPinsDown):
				endTime = time.time()
				elapsedTime = round(endTime - startTime, 2)
				print("FINISHED IN ", elapsedTime, "SECONDS")
				start = False

		cv.imshow('frame', frame)
		if cv.waitKey(1) & 0xFF == ord('q'):
			break

	cap.release()
	cv.destroyAllWindows()