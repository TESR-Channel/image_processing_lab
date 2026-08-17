import cv2
import numpy as np

Window_name = "HougLine"
cv2.namedWindow(Window_name)

Original_img = cv2.imread('sudoku.jpg')
scale_percent = 60 # percent of original size
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

# define a null callback function
def Value_change(x):
    pass
 
cv2.createTrackbar("Low threshold", Window_name, 50, 500, Value_change)
cv2.createTrackbar("Max threshold", Window_name, 150, 500, Value_change)
cv2.createTrackbar("ApertureSize", Window_name, 1, 10, Value_change)

cv2.createTrackbar("Rtho", Window_name, 1, 10, Value_change)
cv2.createTrackbar("Degree", Window_name, 2, 180, Value_change)
cv2.createTrackbar("Threshold", Window_name, 109, 300, Value_change)

while True:
    low_threshold = cv2.getTrackbarPos("Low threshold",Window_name)
    max_threshold = cv2.getTrackbarPos("Max threshold",Window_name)
    apertureSize = cv2.getTrackbarPos("ApertureSize",Window_name)
    
    rtho = cv2.getTrackbarPos("Rtho",Window_name)
    if rtho < 1:
        rtho = 1
    Degree = cv2.getTrackbarPos("Degree",Window_name)
    if Degree < 1:
        Degree = 1
    threshold = cv2.getTrackbarPos("Threshold",Window_name)
    if threshold < 1:
        threshold = 1
    
    Result_img = Original_img.copy()
    edges_img = cv2.Canny(gray_img,low_threshold,max_threshold,apertureSize)
    lines = cv2.HoughLines(edges_img,rtho,Degree*np.pi/180,threshold)
    
    if lines is not None:
        for line in lines:
            rho,theta = line[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            cv2.line(Result_img,(x1,y1),(x2,y2),(0,0,255),3)
    
    img_Canny_edges = cv2.hconcat([Original_img,cv2.cvtColor(edges_img,cv2.COLOR_GRAY2BGR),Result_img])  
    cv2.imshow(Window_name,img_Canny_edges)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cv2.destroyAllWindows()