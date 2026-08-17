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

diameter = int((x+y)/2)

R = 255
G = 0
B = 0
thickness = 2
# Draw a red Circle with thickness of 2 px
cv2.circle(img,(x,y), diameter,(B,G,R),thickness)
cv2.imshow('Draw circle',img)

cv2.waitKey(0)
cv2.destroyAllWindows()