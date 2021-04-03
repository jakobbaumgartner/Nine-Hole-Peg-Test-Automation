import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import time


def calculateThreshold(grayImage):
    tO = cv.threshold(grayImage, 0, 255,
                      cv.THRESH_BINARY + cv.THRESH_OTSU)[0]
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
    gammaImg[gammaImg > 255] = 255

    return gammaImg.astype(dtype)


def rgbToHsv(self, rgbImage):
    r = rgbImage[:, :, 2]
    g = rgbImage[:, :, 1]
    b = rgbImage[:, :, 0]

    cMax = np.maximum(r, np.maximum(g, b))
    cMin = np.minimum(r, np.minimum(g, b))
    delta = cMax - cMin + 1e-7

    h = np.zeros_like(r)
    s = np.zeros_like(r)
    v = np.zeros_like(r)

    h[cMax == r] = 60.0 * \
        ((g[cMax == r] - b[cMax == r]) / (delta[cMax == r]) % 6.0)
    h[cMax == g] = 60.0 * \
        ((b[cMax == g] - r[cMax == g]) / (delta[cMax == g]) + 2)
    h[cMax == b] = 60.0 * \
        ((r[cMax == b] - g[cMax == b]) / (delta[cMax == b]) + 4)

    s[delta != 0] = delta[delta != 0] / (cMax[delta != 0] + 1e-7)

    v = cMax

    return h, s, v


def prepareImage(self, frame):
    # Gray image of frame.
    grayImg = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # HSV space of (colored) frame.
    h, s, v = rgbToHsv(frame / 255)
    # Gamma image to improve contrast on gray image.
    gammaImg = gammaImage(grayImg, 0.8)
    # Blurred gamma image.
    blurImg = cv.GaussianBlur(gammaImg, (3, 3), 0)
    # Automatic thresholding on blur image.
    tH = self.calculateThreshold(self, blurImg)[1]

    return blurImg, tH, h, s, v
