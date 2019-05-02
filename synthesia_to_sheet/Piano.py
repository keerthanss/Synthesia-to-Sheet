import cv2
import numpy as np
import copy

from ClassDefinitions import Key, Color, Note

class Piano():
    """docstring for Piano."""
    def __init__(self):
        self.keys = []
        self.blackKeys = []
        self.whiteKeys = []
        self.CIndices = []
        self.meanBlackDistance = None

    def detect_all_black_keys(self, frame):
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
        for p in centers:
            key = Key.Key(color=Color.Color.Black, location=p, nativeColor=frame[ p[1] ][ p[0] ] ) # array indexing is inverse of image coordinates
            self.blackKeys.append(key)

    def get_white_keys_from(self, blackKeyLocation, distanceToNextBlackKey):
        locations = []
        if distanceToNextBlackKey < self.meanBlackDistance:
            locations.append((blackKeyLocation[0] + distanceToNextBlackKey / 2, blackKeyLocation[1]))
        else:
            locations.append((blackKeyLocation[0] + distanceToNextBlackKey / 3, blackKeyLocation[1]))
            locations.append((blackKeyLocation[0] + 2 * distanceToNextBlackKey / 3, blackKeyLocation[1]))

        return locations

    def get_key_distances(self, keysList):
        distances = []
        for index in xrange(1, len(keysList)):
            distances.append(keysList[index].Location[0] - keysList[index - 1].Location[0])

        return distances

    def detect_all_white_keys(self, frame):
        height, width, channels = frame.shape

        p1 = (0, self.blackKeys[0].Location[1])
        dummyFirstBlackKey = Key.Key(color=Color.Color.Black, location=p1, nativeColor=frame[p1[1]][p1[0]])
        p2 = (width - 1, self.blackKeys[-1].Location[1])
        dummyLastBlackKey = Key.Key(color=Color.Color.Black, location=p2, nativeColor=frame[p2[1]][p2[0]])

        # Add dummy black keys to the end and beginning to be able to detect white keys beyond the first and last actual black keys
        referenceBlackKeys = copy.deepcopy(self.blackKeys)
        referenceBlackKeys.insert(0, dummyFirstBlackKey)
        referenceBlackKeys.append(dummyLastBlackKey)

        blackKeyDifferences = self.get_key_distances(referenceBlackKeys)

        # Mean is used to determine whether one or two white keys are present between two black keys
        if len(blackKeyDifferences) > 0:
            self.meanBlackDistance = sum(blackKeyDifferences) / len(blackKeyDifferences)
        else:
            print "List of blackKeyDifferences is empty"
            exit(0)

        previousBlackKeyIndex = 0
        for diff in blackKeyDifferences:
            whiteKeyLocations = self.get_white_keys_from(referenceBlackKeys[previousBlackKeyIndex].Location, diff)
            for p in whiteKeyLocations:
                key = Key.Key(color=Color.Color.White, location=p, nativeColor=frame[ p[1] ][ p[0] ] )
                self.whiteKeys.append(key)
            previousBlackKeyIndex += 1

    def is_octave_pattern(self, lastFiveBlackKeys):
        octavePattern = np.array([-1, 1, -1, -1])
        distances = np.array(self.get_key_distances(lastFiveBlackKeys))
        deviationsFromMean = distances - self.meanBlackDistance
        truthArray = octavePattern * deviationsFromMean
        return (truthArray > 0).all()

    def get_index_of_first_C(self):
        for index in xrange(len(self.blackKeys) - 5):
            lastFiveBlackKeys = self.blackKeys[index : index+5]
            if self.is_octave_pattern(lastFiveBlackKeys):
                firstCSharp = lastFiveBlackKeys[0]
                # If the first C# is the left most key on the keyboard, then the first C is present 12 notes away (since there are 12 notes per octave)
                if not firstCSharp.is_right_of(self.keys[0]):
                    return len(Note.Note) - 1
                index = 0
                while self.keys[index].is_left_of(firstCSharp):
                    index += 1
                firstC = self.keys[index - 1]
                return index - 1

        print "Couldn't compute first occurrence of C"
        exit(0)

    def populate_octaves(self):
        # The leftmost key gets assigned to octave 1 irrespective of which key it is. Initialization of 'currentOctave' is done to make sure that happens even when the leftmost key is a C in which case the else condition is triggered and 'currentOctave' gets set to 1
        if self.keys[0] == self.keys[self.CIndices[0]]:
            currentOctave = 0
        else:
            currentOctave = 1
        nextCIndex = 0
        for key in self.keys:
            # For a key which has no C present to its right on the keyboard (i.e a key such that the rightmost C is to the left of it), nextCIndex is outside our list of CIndices. So, in such a case, we add the key to the current octave (taken care of by the first condition in the below if statment)
            if nextCIndex >= len(self.CIndices) or key.is_left_of(self.keys[self.CIndices[nextCIndex]]):
                key.Octave = currentOctave
            else:
                currentOctave += 1
                key.Octave = currentOctave
                nextCIndex += 1

    def populate_notes(self):
        keyIndex = 0
        while self.keys[keyIndex].Octave < 2:
            keyIndex += 1

        keyOffset = 12 - keyIndex + 1
        for index in xrange(keyIndex):
            self.keys[index].Note = Note.Note(keyOffset + index)

        noteNo = 0
        while keyIndex < len(self.keys):
            self.keys[keyIndex].Note = Note.Note(noteNo + 1)
            noteNo = (noteNo + 1) % 12
            keyIndex += 1

    def get_C_indices(self):
        lastCIndex = self.get_index_of_first_C()
        while lastCIndex < len(self.keys):
            self.CIndices.append(lastCIndex)
            lastCIndex += 12

    def get_all_keys(self):
        blackIndex = 0
        whiteIndex = 0
        while blackIndex < len(self.blackKeys) and whiteIndex < len(self.whiteKeys):
            if (self.whiteKeys[whiteIndex].is_left_of(self.blackKeys[blackIndex])):
                self.keys.append(self.whiteKeys[whiteIndex])
                whiteIndex += 1
            else:
                self.keys.append(self.blackKeys[blackIndex])
                blackIndex += 1

        while blackIndex < len(self.blackKeys):
            self.keys.append(self.blackKeys[blackIndex])
            blackIndex += 1

        while whiteIndex < len(self.whiteKeys):
            self.keys.append(self.whiteKeys[whiteIndex])
            whiteIndex += 1

    def get_index_of_middle_C(self):
        length = len(self.CIndices)
        return self.CIndices[(length-1)/2]

    def calibrate(self, frame):
        self.detect_all_black_keys(frame)
        self.detect_all_white_keys(frame)
        self.get_all_keys()
        self.get_C_indices()
        self.populate_octaves()
        self.populate_notes()
