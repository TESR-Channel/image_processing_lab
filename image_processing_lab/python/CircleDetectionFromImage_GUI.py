import cv2
import numpy as np

Window_name = "Circle detection"
cv2.namedWindow(Window_name)

Original_img = cv2.imread('ex2.jpg')

dp = 1
minDist = 1
# define a null callback function
def Value_change(x):
    pass
 
cv2.createTrackbar("dp", Window_name, 1, 10, Value_change)
cv2.createTrackbar("minDist", Window_name, 1, Original_img.shape[0], Value_change)

thickness = 5
while True:
    dp = cv2.getTrackbarPos("dp",Window_name)
    minDist = cv2.getTrackbarPos("minDist",Window_name)
    if dp < 1:
        dp = 1
    if minDist < 1:
        minDist = 1
        
    Result_img = Original_img.copy()
    grayimg = cv2.cvtColor(Original_img,cv2.COLOR_BGR2GRAY) #convert to gray color
    circles = cv2.HoughCircles(grayimg,cv2.HOUGH_GRADIENT,dp,minDist)
    #Draw detected circles
    if circles is not None:
        print("Found circle")
        circles = np.uint16(circles[0, :])
        print(circles)
        for (x, y, diameter) in circles :
            # draw the outer circle 
            cv2.circle(Result_img,(x,y), diameter,(0,0,255),thickness,cv2.LINE_AA)
            # draw center of circle
            cv2.circle(Result_img,(x,y), 2,(0,255,0),thickness)
            
    else:
        print("Cannot detect circle.")
    
    img_Circle_detection = cv2.hconcat([Original_img,Result_img])    
    cv2.imshow(Window_name,img_Circle_detection)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
cv2.destroyAllWindows()
