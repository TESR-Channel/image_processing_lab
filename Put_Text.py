import cv2
# read image
img = cv2.imread("Square_500x500.jpg")
cv2.imshow('original',img)

# get dimensions of image
dimensions = img.shape
print(dimensions)

# height, width, number of channels in image
height = img.shape[0]
width = img.shape[1]

x = int(width/2)
y = int(height/2)

R = 255
G = 0
B = 0

thickness = 2

font = cv2.FONT_HERSHEY_SIMPLEX
fontsize = 1
cv2.putText(img,'OpenCV',(x,y), font, fontsize ,(B,G,R),thickness,cv2.LINE_AA)
cv2.imshow('Put Text',img)

cv2.waitKey(0)
cv2.destroyAllWindows()
