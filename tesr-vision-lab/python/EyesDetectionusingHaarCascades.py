import cv2

eye_cascade = cv2.CascadeClassifier("/home/pi/PythonCode/EyesDetection/haarcascade_eye.xml")

img = cv2.imread("/home/pi/PythonCode/EyesDetection/square-face.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

eyes = eye_cascade.detectMultiScale(gray,1.8,15)

for (x,y,w,h) in eyes:
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
        cv2.putText(img,"Eyes",(x,y-5),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        
cv2.imshow('img',img)
cv2.waitKey(0)
cv2.destroyAllWindows()
