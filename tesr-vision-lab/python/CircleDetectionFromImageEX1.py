import cv2
import numpy as np

img = cv2.imread('ex1.jpg')
cv2.imshow('Original Image',img)
# get dimensions of image
dimensions = img.shape
print(dimensions)

grayimg = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) #convert to gray color
circles = cv2.HoughCircles(grayimg,cv2.HOUGH_GRADIENT,1,dimensions[0]/10)

thickness = 5
#Draw detected circles
if circles is not None:
    print("Found circle")
    circles = np.uint16(circles[0, :])
    print(circles)
    for (x, y, diameter) in circles :
        # draw the outer circle 
        cv2.circle(img,(x,y), diameter,(0,0,255),thickness,cv2.LINE_AA)
        # draw center of circle
        cv2.circle(img,(x,y), 2,(0,255,0),thickness)
        
else:
    print("Cannot detect circle.")
    
cv2.imshow('Detected circles',img)
cv2.waitKey(0)
cv2.destroyAllWindows()
