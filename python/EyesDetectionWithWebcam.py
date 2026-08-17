import cv2

eye_cascade = cv2.CascadeClassifier("./haarcascade_eye.xml")

cap = cv2.VideoCapture(0)

while True:
    ret,img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    eyes = eye_cascade.detectMultiScale(gray,1.1,15)

    for (x,y,w,h) in eyes:
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
        cv2.putText(img,"Eyes",(x,y-5),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        
    cv2.imshow('img',img)
    k = cv2.waitKey(30) & 0xFF # press esc
    if k == 27:
        break
    
cap.release()
cv2.destroyAllWindows()

