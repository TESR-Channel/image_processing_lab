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

x1 = width/4
y1 = height/4
x2 = (width*3)/4
y2 = (height*3)/4

R = 255
G = 0
B = 0
thickness = 2

# Draw a red rectangle with thickness of 2 px 
cv2.rectangle(img,(int(x1),int(y1)),(int(x2),int(y2)),(B,G,R),thickness)
cv2.imshow('Draw rectangle',img)

cv2.waitKey(0)
cv2.destroyAllWindows()