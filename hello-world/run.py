from PIL import Image, ImageDraw
import cv2 as cv
import numpy as np
import easyocr

def sort_contours(cnts):
	# initialize the reverse flag and sort index
	reverse = False
	i = 0
	# construct the list of bounding boxes and sort them from top to
	# bottom
	boundingBoxes = [cv.boundingRect(c) for c in cnts]
	(cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
		key=lambda b:b[1][i], reverse=reverse))
	# return the list of sorted contours and bounding boxes
	return (cnts, boundingBoxes)

IMAGE_NAME='test.jpg'

reader = easyocr.Reader(['en'])
output = reader.readtext(IMAGE_NAME)

f = open("output.txt", "a")
f.write(str(output))
f.close()

MATCH_TEXT="helloworld"
foundCharacters=""

foundBounds = dict()

# print(output)
for match in output:
    cords = match[0]
    text = match[1]

    for char in text:
        if (char in MATCH_TEXT and char not in foundCharacters):
            foundCharacters += char
            foundBounds[char] = (cords, text)

# print(foundBounds)

img = cv.imread(IMAGE_NAME)

loc_img = img.copy()

letterCrops = dict()

for letter, match in foundBounds.items():
    bound = match[0]
    text = match[1]

    letterCountInText = text.replace(" ", "").index(letter)

    for l in text[:letterCountInText]:
        if (l in "ij\""):
            letterCountInText += 1

    p1 = bound[0]
    p2 = bound[2]

    bound_img = img[int(p1[1]):int(p2[1]), int(p1[0]):int(p2[0])]
    
    gray_img = cv.cvtColor(bound_img, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(gray_img,0,255,cv.THRESH_BINARY_INV+cv.THRESH_OTSU)

    # noise removal
    kernel = np.ones((3,3),np.uint8)
    opening = cv.morphologyEx(thresh,cv.MORPH_OPEN,kernel, iterations = 2)

    # if (letter == "o"):
    #     # test = bound_img.copy()
    #     # cv.rectangle(test,(x,y),(x+w,y+h),(0,255,0),2)
    #     cv.imwrite('gen.png', opening)

    contours, hierarchy = cv.findContours(opening, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    sorted_contors, _ = sort_contours(contours)

    print(len(sorted_contors), "Finding character '" + letter + "' in '" + text + "' at index:", letterCountInText)

    cnt = sorted_contors[letterCountInText]
    x,y,w,h = cv.boundingRect(cnt)

    letterCrops[letter] = bound_img[y:y+h, x:x+w]

    # cv.rectangle(loc_img, (p1[0]+x, p1[1]+y), (p1[0]+x+w, p1[1]+y+h), (0,255,0), 5)

# cv.imwrite('letter-locs.png', loc_img)

letterCrops[" "] = np.zeros((100, 100, 3), dtype=np.uint8)

images = []
for letter in "hello world":
    images.append(letterCrops[letter])

max_height = 0
total_width = 0

for image in images:
    image_h = image.shape[0]
    image_w = image.shape[1]

    if image_h > max_height:
        max_height = image_h
    total_width += image_w

final_image = np.zeros((max_height, total_width, 3), dtype=np.uint8)

current_x = 0
for image in images:
    image_h = image.shape[0]
    image_w = image.shape[1]

    final_image[0:image_h, current_x:current_x+image_w,:] = image
    current_x += image.shape[1]

cv.imwrite('final.png', final_image)