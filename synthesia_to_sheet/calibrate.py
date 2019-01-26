import cv2
import numpy as np
import copy

from ClassDefinitions import Key, Color

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
            continue
    	cX = int(M["m10"] / M["m00"])
    	cY = int(M["m01"] / M["m00"])
        centers.append( (cX, cY) )

    centers = sorted(centers)
    # instantiate Key() with the newly found centers
    blackKeys = []
    for p in centers:
        key = Key.Key(color=Color.Color.Black, location=p, nativeColor=frame[ p[1] ][ p[0] ] ) # array indexing is inverse of image coordinates
        blackKeys.append(key)

    return blackKeys

def get_white_keys_from(blackKeyLocation, distanceToNextBlackKey, meanBlackDistance):
    locations = []
    if distanceToNextBlackKey < meanBlackDistance:
        locations.append((blackKeyLocation[0] + distanceToNextBlackKey / 2, blackKeyLocation[1]))
    else:
        locations.append((blackKeyLocation[0] + distanceToNextBlackKey / 3, blackKeyLocation[1]))
        locations.append((blackKeyLocation[0] + 2 * distanceToNextBlackKey / 3, blackKeyLocation[1]))

    return locations

def get_key_distances(keysList):
    distances = []
    for index in xrange(1, len(keysList)):
        distances.append(keysList[index].Location[0] - keysList[index - 1].Location[0])

    return distances

def detect_all_white_keys(frame, blackKeys):
    height, width, channels = frame.shape
    whiteKeys = []

    p1 = (0, blackKeys[0].Location[1])
    dummyFirstBlackKey = Key.Key(color=Color.Color.Black, location=p1, nativeColor=frame[p1[1]][p1[0]])
    p2 = (width - 1, blackKeys[-1].Location[1])
    dummyLastBlackKey = Key.Key(color=Color.Color.Black, location=p2, nativeColor=frame[p2[1]][p2[0]])

    # Add dummy black keys to the end and beginning to be able to detect white keys beyond the first and last actual black keys
    referenceBlackKeys = copy.deepcopy(blackKeys)
    referenceBlackKeys.insert(0, dummyFirstBlackKey)
    referenceBlackKeys.append(dummyLastBlackKey)

    blackKeyDifferences = get_key_distances(referenceBlackKeys)

    # Mean is used to determine whether one or two white keys are present between two black keys
    if len(blackKeyDifferences) > 0:
        meanBlackDistance = sum(blackKeyDifferences) / len(blackKeyDifferences)
    else:
        print "List of blackKeyDifferences is empty"
        exit(0)

    previousBlackKeyIndex = 0
    for diff in blackKeyDifferences:
        whiteKeyLocations = get_white_keys_from(referenceBlackKeys[previousBlackKeyIndex].Location, diff, meanBlackDistance)
        for p in whiteKeyLocations:
            key = Key.Key(color=Color.Color.White, location=p, nativeColor=frame[ p[1] ][ p[0] ] )
            whiteKeys.append(key)
        previousBlackKeyIndex += 1

    return whiteKeys, meanBlackDistance

def is_octave_pattern(lastFiveBlackKeys, meanBlackDistance):
    octavePattern = np.array([-1, 1, -1, -1])
    distances = np.array(get_key_distances(lastFiveBlackKeys))
    deviationsFromMean = distances - meanBlackDistance
    truthArray = octavePattern * deviationsFromMean
    return (truthArray > 0).all()

def get_first_C_note(blackKeys, whiteKeys, meanBlackDistance):
    for index in xrange(len(blackKeys) - 5):
        lastFiveBlackKeys = blackKeys[index : index+5]
        if is_octave_pattern(lastFiveBlackKeys, meanBlackDistance):
            print "First C# found at", lastFiveBlackKeys[0].Location
            return

    print "Couldn't compute first occurrence of C#"
