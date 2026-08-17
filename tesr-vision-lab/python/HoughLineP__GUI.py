import cv2
import numpy as np

Original_img = cv2.imread('Line.jpg')
scale_percent = 40 # percent of original size
width = int(Original_img.shape[1] * scale_percent / 100)
height = int(Original_img.shape[0] * scale_percent / 100)
dim = (width, height)

Original_img = cv2.resize(Original_img, dim, interpolation = cv2.INTER_AREA)
gray_img = cv2.cvtColor(Original_img,cv2.COLOR_BGR2GRAY)

low_threshold = 1
max_threshold = 1
apertureSize = 1

rtho = 1
Degree = 1
threshold = 1
minLineLength = 1
maxLineGap = 1

Window_name_controlPanel_Canny = "2. Control Panel Canny Edge"
Window_name_controlPanel_HoughLineP = "3. Control Panel HouhgLineP (Result)"
cv2.namedWindow(Window_name_controlPanel_Canny)
cv2.namedWindow(Window_name_controlPanel_HoughLineP)

# define a null callback function
def Value_change(x):
    pass
 
cv2.createTrackbar("Low threshold", Window_name_controlPanel_Canny, 51, 500, Value_change)
cv2.createTrackbar("Max threshold", Window_name_controlPanel_Canny, 187, 500, Value_change)
cv2.createTrackbar("ApertureSize", Window_name_controlPanel_Canny, 3, 10, Value_change)

cv2.createTrackbar("Rtho", Window_name_controlPanel_HoughLineP, 1, 10, Value_change)
cv2.createTrackbar("Degree", Window_name_controlPanel_HoughLineP, 1, 180, Value_change)
cv2.createTrackbar("Threshold", Window_name_controlPanel_HoughLineP, 112, 300, Value_change)
cv2.createTrackbar("minLineLength", Window_name_controlPanel_HoughLineP, 65, 300, Value_change)
cv2.createTrackbar("maxLineGap", Window_name_controlPanel_HoughLineP, 220, 300, Value_change)

while True:
    low_threshold = cv2.getTrackbarPos("Low threshold",Window_name_controlPanel_Canny)
    max_threshold = cv2.getTrackbarPos("Max threshold",Window_name_controlPanel_Canny)
    apertureSize = cv2.getTrackbarPos("ApertureSize",Window_name_controlPanel_Canny)
    
    rtho = cv2.getTrackbarPos("Rtho",Window_name_controlPanel_HoughLineP)
    if rtho < 1:
        rtho = 1
    Degree = cv2.getTrackbarPos("Degree",Window_name_controlPanel_HoughLineP)
    if Degree < 1:
        Degree = 1
    threshold = cv2.getTrackbarPos("Threshold",Window_name_controlPanel_HoughLineP)
    if threshold < 1:
        threshold = 1
    minLineLength = cv2.getTrackbarPos("minLineLength",Window_name_controlPanel_HoughLineP)
    if minLineLength < 1:
        minLineLength = 1
    maxLineGap = cv2.getTrackbarPos("maxLineGap",Window_name_controlPanel_HoughLineP)
    if maxLineGap < 1:
        maxLineGap = 1
    
    Result_img = Original_img.copy()
    edges_img = cv2.Canny(gray_img,low_threshold,max_threshold,apertureSize)
    lines = cv2.HoughLinesP(edges_img,rtho,Degree*np.pi/180,threshold,minLineLength=minLineLength,maxLineGap=maxLineGap)
    
    if lines is not None:
        print("Found lines.")
        for line in lines:
            x1,y1,x2,y2 = line[0]
            cv2.line(Result_img,(x1,y1),(x2,y2),(0,255,0),3)
    
    #img_Canny_edges = cv2.hconcat([Original_img,cv2.cvtColor(edges_img,cv2.COLOR_GRAY2BGR),Result_img])  
    
    cv2.imshow("1. Original Image",Original_img)
    cv2.imshow(Window_name_controlPanel_Canny,edges_img)
    cv2.imshow(Window_name_controlPanel_HoughLineP,Result_img)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cv2.destroyAllWindows()