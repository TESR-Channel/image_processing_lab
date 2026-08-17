import cv2
import numpy as np

Window_name = "Canny Edge"
cv2.namedWindow(Window_name)

Original_img = cv2.imread('sudoku.jpg')
scale_percent = 50 # percent of original size
width = int(Original_img.shape[1] * scale_percent / 100)
height = int(Original_img.shape[0] * scale_percent / 100)
dim = (width, height)

Original_img = cv2.resize(Original_img, dim, interpolation = cv2.INTER_AREA)
gray_img = cv2.cvtColor(Original_img,cv2.COLOR_BGR2GRAY)

low_threshold = 1
max_threshold = 1
apertureSize = 1

# define a null callback function
def Value_change(x):
    pass
 
cv2.createTrackbar("Low threshold", Window_name, 1, 500, Value_change)
cv2.createTrackbar("Max threshold", Window_name, 1, 500, Value_change)
cv2.createTrackbar("ApertureSize", Window_name, 1, 10, Value_change)

while True:
    low_threshold = cv2.getTrackbarPos("Low threshold",Window_name)
    max_threshold = cv2.getTrackbarPos("Max threshold",Window_name)
    apertureSize = cv2.getTrackbarPos("ApertureSize",Window_name)
    
    edges_img = cv2.Canny(gray_img,low_threshold,max_threshold,apertureSize)
    
    img_Canny_edges = cv2.hconcat([Original_img,cv2.cvtColor(gray_img,cv2.COLOR_GRAY2BGR),cv2.cvtColor(edges_img,cv2.COLOR_GRAY2BGR)])    
    cv2.imshow(Window_name,img_Canny_edges)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cv2.destroyAllWindows()