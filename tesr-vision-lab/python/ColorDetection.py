import cv2
import numpy as np

img = cv2.imread('ex1.png')
cv2.imshow('Original Image',img)
img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) # convert BGR to HSV

Green = [20, 174, 64]
Yellow = [0, 255, 255]
Red = [30,0,230]

BGR_Fillter = Red
hsv_Fillter = cv2.cvtColor( np.uint8([[BGR_Fillter]] ), cv2.COLOR_BGR2HSV)[0][0]
thresh = 30

minHSV = np.array([hsv_Fillter[0] - thresh, hsv_Fillter[1] - thresh, hsv_Fillter[2] - thresh])
maxHSV = np.array([hsv_Fillter[0] + thresh, hsv_Fillter[1] + thresh, hsv_Fillter[2] + thresh])

maskColor = cv2.inRange(img_hsv, minHSV, maxHSV)

cv2.imshow('Detect Color', maskColor)
cv2.waitKey(0)