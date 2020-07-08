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

IMAGE_NAME='hello-world-book-5.jpg'

reader = easyocr.Reader(['en'])
output = reader.readtext(IMAGE_NAME)

# output = [([[160, 225], [1376, 225], [1376, 580], [160, 580]], 'Variable', 0.9960167407989502), ([[1404.1719674096712, 251.05416938902394], [2295.532351969975, 352.6011258467245], [2255.828032590329, 698.945830610976], [1364.467648030025, 596.3988741532754]], 'loops', 0.6074603199958801), ([[154, 743], [2592, 743], [2592, 1015], [154, 1015]], 'Fixed numbers, like the one', 0.1877637803554535), ([[711, 1066], [2520, 1066], [2520, 1284], [711, 1284]], 'use constants in the', 0.7918238639831543), ([[155, 1077], [679, 1077], [679, 1290], [155, 1290]], 'If you', 0.2787467837333679), ([[2550, 1157], [2592, 1157], [2592, 1265], [2550, 1265]], '', 0.9234929084777832), ([[158, 1353], [2529, 1353], [2529, 1570], [158, 1570]], 'ber of times whenever the', 0.2614792585372925), ([[173, 1640], [2592, 1640], [2592, 1874], [173, 1874]], "hard-coded, because it's def", 0.719630241394043), ([[162, 1977], [1002, 1977], [1002, 2160], [162, 2160]], 'we want.', 0.5784410834312439), ([[1244, 2414], [2592, 2414], [2592, 2613], [1244, 2613]], 'we want the nu', 0.23706801235675812), ([[166, 2425], [1208, 2425], [1208, 2625], [166, 2625]], 'Sometimes', 0.5596449971199036), ([[161, 2712], [2592, 2712], [2592, 2954], [161, 2954]], 'mined bythe user, or byan', 0.16396555304527283), ([[153, 2977], [2592, 2977], [2592, 3258], [153, 3258]], 'For that, we need a variabl', 0.2586270272731781), ([[159, 3475], [2492, 3475], [2492, 3770], [159, 3770]], "For example, let's say you", 0.3903290331363678), ([[2517, 3492], [2592, 3492], [2592, 3620], [2517, 3620]], 'V', 0.6437931060791016), ([[154, 3749], [2592, 3749], [2592, 4049], [154, 4049]], "shooter game. You'd have t", 0.5289808511734009), ([[1972, 4017], [2563, 4017], [2563, 4297], [1972, 4297]], 'wiped', 0.9728983640670776), ([[819, 4098], [1614, 4098], [1614, 4292], [819, 4292]], 'as aliens', 0.2163277566432953), ([[1621.9052920399595, 4113.62856040085], [1968.561788779961, 4076.0954532713868], [1989.0947079600405, 4269.37143959915], [1642.438211220039, 4307.904546728613]], 'get', 0.6472988128662109), ([[176, 4115], [777, 4115], [777, 4287], [176, 4287]], 'screen', 0.5989675521850586), ([[2378, 4307], [2582, 4307], [2582, 4501], [2378, 4501]], 'of', 0.6929961442947388), ([[183, 4374], [1872, 4374], [1872, 4593], [183, 4593]], 'of counter to keep', 0.41677263379096985), ([[1868.5319288672708, 4384.082096018158], [2356.474341503356, 4321.521386541915], [2379.468071132729, 4495.917903981842], [1891.5256584966444, 4559.478613458085]], 'track', 0.7953242659568787)]

print(output)

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