import cv2
import freenect
import numpy as np

#function to get RGB image from kinect
def get_video():
    array,_ = freenect.sync_get_video()
    array = cv2.cvtColor(array,cv2.COLOR_RGB2BGR)
    return array

eye_cascade = cv2.CascadeClassifier("/home/pi/PythonCode/EyesDetection/haarcascade_eye.xml")

while True:
        #get a frame from RGB camera
        frame = get_video()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        eyes = eye_cascade.detectMultiScale(gray,1.1,15)

        for (x,y,w,h) in eyes:
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
                cv2.putText(frame,"Eyes",(x,y-5),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)

        #display RGB image
        cv2.imshow('Result',frame)

        # quit program when 'esc' key is pressed
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
                break
cv2.destroyAllWindows()
