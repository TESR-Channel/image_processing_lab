import cv2
import numpy as np

window_name = "Color detection with Trackbar and mouseClick RGB"
cv2.namedWindow(window_name)

img_Original = cv2.imread('ex3.png')
scale_percent = 80 # percent of original size
width = int(img_Original.shape[1] * scale_percent / 100)
height = int(img_Original.shape[0] * scale_percent / 100)
dim = (width, height)
img_Original = cv2.resize(img_Original, dim, interpolation = cv2.INTER_AREA)
img_hsv = cv2.cvtColor(img_Original, cv2.COLOR_BGR2HSV) # convert BGR to HSV

# create a black image
BGR_img = np.zeros(img_Original.shape, np.uint8)

def mouseClickRGB(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN: #checks mouse left button down condition
        colorsBGR = img_Original[y,x]
        colorsB = img_Original[y,x,0]
        colorsG = img_Original[y,x,1]
        colorsR = img_Original[y,x,2]
        
        img_HSV = cv2.cvtColor(img_Original, cv2.COLOR_BGR2HSV)
        colorsHSV = img_HSV[y,x]
        colorsH = img_HSV[y,x,0]
        colorsS = img_HSV[y,x,1]
        colorsV = img_HSV[y,x,2]
        print("Coordinates of pixel: X: ",x,"Y: ",y)
        print("BRG Format: ",colorsBGR," -> HSV format: ",colorsHSV)
        print("Red: ",colorsR)
        print("Green: ",colorsG)
        print("Blue: ",colorsB)
        print("H: ",colorsH)
        print("S: ",colorsS)
        print("V: ",colorsV)
        
        cv2.setTrackbarPos("H",window_name,colorsH)
        cv2.setTrackbarPos("S",window_name,colorsS)
        cv2.setTrackbarPos("V",window_name,colorsV)

# define a null callback function
def null(x):
    pass
 
cv2.createTrackbar("H", window_name, 0, 179, null)
cv2.createTrackbar("S", window_name, 0, 255, null)
cv2.createTrackbar("V", window_name, 0, 255, null)
cv2.createTrackbar("thresh", window_name, 30, 60, null)
cv2.setMouseCallback(window_name,mouseClickRGB)
while True:
    h_Fillter = cv2.getTrackbarPos("H",window_name)
    s_Fillter = cv2.getTrackbarPos("S",window_name)
    v_Fillter = cv2.getTrackbarPos("V",window_name)
    thresh = cv2.getTrackbarPos("thresh",window_name)
    
    HSV_Fillter = [h_Fillter,s_Fillter,v_Fillter]
    BGR_Fillter = cv2.cvtColor( np.uint8([[HSV_Fillter]] ), cv2.COLOR_HSV2BGR)[0][0]
    b = BGR_Fillter[0]
    g = BGR_Fillter[1]
    r = BGR_Fillter[2]
    # Create BGR Filter image
    BGR_img[:] = [b,g,r] 
    

    minHSV = np.array([h_Fillter - thresh, s_Fillter - thresh, v_Fillter - thresh])
    maxHSV = np.array([h_Fillter + thresh, s_Fillter + thresh, v_Fillter + thresh])

    maskColor = cv2.inRange(img_hsv, minHSV, maxHSV)
    img_output = cv2.bitwise_and(img_Original,img_Original,mask = maskColor)
    
    img_Color_detection = cv2.hconcat([img_Original,BGR_img,img_output])
    # display trackbars and image
    cv2.imshow(window_name,img_Color_detection)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
cv2.destroyAllWindows()