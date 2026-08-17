import cv2
import numpy as np

img = cv2.imread('sudoku.jpg')
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray,50,150,apertureSize = 3)

cv2.imshow('Original',img)
cv2.imshow('Canny edge',edges)
cv2.waitKey(0)
cv2.destroyAllWindows()