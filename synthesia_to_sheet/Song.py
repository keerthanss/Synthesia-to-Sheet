import cv2
import numpy as np

from sklearn.cluster import KMeans

from ClassDefinitions.Hand import Hand

class Song:
    """docstring for Song"""

    def __init__(self, piano):
        self.piano = piano
        self.key_presses = [] # list of key presses for each frame
        self.length_of_song = 0 # stores the length of the key_presses

        self._kmeans = None
        self._color_map = dict()
        self._BLACK = 100
        self._WHITE = 200
        return

    def _store_presses_in_key(self, frame_index, key_presses_in_frame, labels):
        key_presses_in_frame = set(key_presses_in_frame)
        for i,k in enumerate(self.piano.keys):
            if k.IsPressed:
                if i in key_presses_in_frame:
                    continue
                else:
                    k.IsPressed = False
                    k.Presses[-1][-1] = frame_index
            else:
                if i in key_presses_in_frame:
                    k.IsPressed = True
                    new_press = [self._color_map[labels[i]], frame_index, None] # hand, start_frame, end_frame
                    k.Presses.append(new_press)
                else:
                    continue
        return

    def _identify_key_presses_in_frame(self, frame):
        frame_colors = [ frame[ k.Location[1] ][ k.Location[0] ] for k in self.piano.keys ]
        labels = self._kmeans.predict(frame_colors)
        key_presses_in_frame = [ i for (i, _label) in enumerate(labels) if self._color_map[_label] not in [self._BLACK, self._WHITE] ]
        self.key_presses.append( key_presses_in_frame )
        self.length_of_song  += 1
        self._store_presses_in_key(self.length_of_song, key_presses_in_frame, labels)
        print key_presses_in_frame
        return

    def _train_kmeans(self, list_of_frames, k=4, train_size=500):
        colors = []
        for frame in list_of_frames[0:train_size]:
            for key in self.piano.keys:
                y, x = key.Location
                current_color = frame[x][y]
                colors.append(current_color)
        self._kmeans = KMeans(n_clusters=k).fit(colors)
        cluster_centers = self._kmeans.cluster_centers_
        cluster_centers_1D = np.sqrt(np.sum(np.square(cluster_centers), axis=1))
        self._init_color_map(list_of_frames, cluster_centers_1D)
        return

    def _init_color_map(self, list_of_frames, cluster_centers_1D):
        k = cluster_centers_1D.shape[0]
        white_index = np.argmax(cluster_centers_1D)
        black_index = np.argmin(cluster_centers_1D)
        remaining_colors = [ i for (i, _) in enumerate(cluster_centers_1D) if i != white_index and i != black_index ]
        if k == 3:
            self._color_map[white_index] = self._WHITE
            self._color_map[black_index] = self._BLACK
            self._color_map[remaining_colors[0]] = Hand.Generic
            return

        # For k = 4, we need to map hand to color
        # first we need a reference frame in which both hand presses are present
        # then we categorise based on the location
        left_index, right_index = 0, 0

        for frame in list_of_frames:
            frame_colors = [ frame[ k.Location[1] ][ k.Location[0] ] for k in self.piano.keys ]
            number_of_distinct_colors = np.unique(self._kmeans.predict(frame_colors)).shape[0]
            if number_of_distinct_colors == 4:
                reference_frame = frame
                break

        frame_colors = [ reference_frame[ k.Location[1] ][ k.Location[0] ] for k in self.piano.keys ]
        labels = self._kmeans.predict(frame_colors)
        temp_idx1, temp_idx2 = 0, 0
        for l in labels:
            if temp_idx1 == 0:
                if l == remaining_colors[0]:
                    temp_idx1 = l
            elif temp_idx2 == 0:
                if l == remaining_colors[1]:
                    temp_idx2 = l
            else:
                break

        y1, _ = self.piano.keys[temp_idx1].Location
        y2, _ = self.piano.keys[temp_idx2].Location

        left_index = remaining_colors[ 0 if y1 < y2 else 1 ]
        right_index = filter(lambda x : x not in [left_index, white_index, black_index], range(4))[0]

        self._color_map[white_index] = self._WHITE
        self._color_map[black_index] = self._BLACK
        self._color_map[left_index] = Hand.Left
        self._color_map[right_index] = Hand.Right
        return

    def process_video(self, list_of_frames):
        self._train_kmeans(list_of_frames, k=4, train_size=500) # NOTE: k=4 if both hands are shown in different colors, else k=3.
        map(self._identify_key_presses_in_frame, list_of_frames)
        self._store_presses_in_key(self.length_of_song, [], []) # mark the ending in case some keys are pressed until the last frame

        # Debug helper - Plis test and tell :P
        # for i, frame in enumerate(list_of_frames):
        #     for idx in self.key_presses[i]:
        #         key = self.piano.keys[idx]
        #         cv2.circle(frame, key.Location, 3, (0,0,255), -1)
        #     cv2.imshow('frame',frame)
        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         break
        #
        # for i, k in enumerate(self.piano.keys):
        #     if k.Presses:
        #         print i, k.Presses
        return
