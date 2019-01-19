import cv2
import numpy as np

from ClassDefinitions import Key, Colour

def detect_all_black_keys(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (15,15), 0) #NOTE: This number may change. Needs more testing.

    _, thresh_inverted = cv2.threshold(blur, 0, 255,
                        cv2.THRESH_BINARY_INV +
                        cv2.THRESH_OTSU)

    _, thresh_normal = cv2.threshold(blur, 0, 255,
                        cv2.THRESH_OTSU)

    denoise_kernel = np.ones((3,3), np.uint8)
    # use opening to remove any artifacts present on the frame anywhere but the keys
    segmented_normal = cv2.morphologyEx(thresh_normal, cv2.MORPH_OPEN, denoise_kernel)
    # do the same for the inverted image. Since, it's inverted, we do closing instead
    segmented_inverted = cv2.morphologyEx(thresh_inverted, cv2.MORPH_CLOSE, denoise_kernel)

    kernel = np.ones((25, 25),np.uint8) # TODO: Assumption - this size is enough to remove the blacks. This may not be true for very high resolution images. Needs verification.
    all_black_keys_gone = cv2.morphologyEx(segmented_normal, cv2.MORPH_CLOSE, kernel)
    only_background = cv2.bitwise_not(all_black_keys_gone)
    only_black_keys = segmented_inverted - only_background

    # now that we have the frame with only the black keys highlighted, find the contours and their centers
    _, contours, _ = cv2.findContours(only_black_keys,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    centers = []
    for c in contours:
        M = cv2.moments(c)
        if M["m00"] == 0:
            M["m00"] = 1
    	cX = int(M["m10"] / M["m00"])
    	cY = int(M["m01"] / M["m00"])
        centers += [ (cX, cY) ]

    # instantiate Key() with the newly found centers
    blackKeys = []
    for p in centers:
        key = Key.Key(colour=Colour.Colour.Black, location=p, nativeColor=frame[ p[1] ][ p[0] ] ) # array indexing is inverse of image coordinates
        blackKeys += [key]

    return blackKeys
