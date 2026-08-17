import cv2
import numpy as np

img = cv2.imread('ex3.png')
cv2.imshow('Original Image',img)
img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) # convert BGR to HSV

# get dimensions of image
dimensions = img.shape
print(dimensions)

# height, width, number of channels in image
height = dimensions[0]
width = dimensions[1]

Green = [20, 174, 64] # BGR format
Yellow = [0, 255, 255]
Red = [30,0,230]
Blue = [254,72,3]

BGR_Fillter = Blue
hsv_Fillter = cv2.cvtColor( np.uint8([[BGR_Fillter]] ), cv2.COLOR_BGR2HSV)[0][0]
print(hsv_Fillter)
thresh = 30

minHSV = np.array([hsv_Fillter[0] - thresh, hsv_Fillter[1] - thresh, hsv_Fillter[2] - thresh])
maxHSV = np.array([hsv_Fillter[0] + thresh, hsv_Fillter[1] + thresh, hsv_Fillter[2] + thresh])

maskColor = cv2.inRange(img_hsv, minHSV, maxHSV)

contours = cv2.findContours(maskColor, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2] # find contour
circle_count = 0
if len(contours) > 0 :
    print("Found Contour")
    for circle in contours:
        circle_count = circle_count + 1
        (x,y),diameter = cv2.minEnclosingCircle(circle)
        # Draw a red Circle with thickness of 2 px
        cv2.circle(img,(int(x),int(y)), int(diameter),(255,0,0),2)

    Textoutput = "Circle = " + str(circle_count)

    font = cv2.FONT_HERSHEY_SIMPLEX
    fontsize = 1   
    cv2.putText(img,Textoutput,(width-200,height-20), font, fontsize ,(255,0,0),2,cv2.LINE_AA)
    
else:
    print("Not Found Contour")

print(circle_count)
cv2.imshow('Detect Color', img)
cv2.waitKey(0)
cv2.destroyAllWindows()