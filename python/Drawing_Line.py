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

x1 = 0
y1 = 0
x2 = width
y2 = height

R = 0
G = 0
B = 255
thickness = 2

# Draw a diagonal blue line with thickness of 2 px (x,y)
cv2.line(img,(x1,y1),(x2,y2),(B,G,R),thickness)
cv2.imshow('Draw line',img)

cv2.waitKey(0)
cv2.destroyAllWindows()
