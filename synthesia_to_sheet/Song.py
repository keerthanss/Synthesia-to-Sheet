import cv2
import numpy as np

from sklearn.cluster import KMeans

class Song:
    """docstring for Song"""

    def __init__(self, piano):
        self.piano = piano
        self.key_presses = [] # list of key presses for each frame
        self.length_of_song = 0 # stores the length of the key_presses
        return

    def _identify_key_presses_in_frame(self, frame, kmeans_classifier, white_index, black_index):
        frame_colors = [ frame[ k.Location[1] ][ k.Location[0] ] for k in self.piano.keys ]
        labels = kmeans_classifier.predict(frame_colors)
        key_presses_in_frame = [ i for (i, _label) in enumerate(labels) if _label != white_index and _label != black_index ]
        self.key_presses.append( key_presses_in_frame )
        self.length_of_song  += 1
        print key_presses_in_frame
        return

    def _train_kmeans(self, list_of_frames, k=4, train_size=500):
        colors = []
        for frame in list_of_frames[0:train_size]:
            for key in self.piano.keys:
                y, x = key.Location
                current_color = frame[x][y]
                colors.append(current_color)
        kmeans = KMeans(n_clusters=k).fit(colors)
        cluster_centers = kmeans.cluster_centers_
        cluster_centers_1D = np.sqrt(np.sum(np.square(cluster_centers), axis=1))
        white_index = np.argmax(cluster_centers_1D)
        black_index = np.argmin(cluster_centers_1D)
        return kmeans, white_index, black_index

    def process_video(self, list_of_frames):
        kmeans, white_index, black_index = self._train_kmeans(list_of_frames, k=4, train_size=500) # NOTE: k=4 if both hands are shown in different colors, else k=3.
        find_keys_pressed = lambda frame: self._identify_key_presses_in_frame(frame, kmeans, white_index, black_index)
        map(find_keys_pressed, list_of_frames)

        # Debug helper - Plis test and tell :P
        # for i, frame in enumerate(list_of_frames):
        #     for idx in self.key_presses[i]:
        #         key = self.piano.keys[idx]
        #         cv2.circle(frame, key.Location, 3, (0,0,255), -1)
        #     cv2.imshow('frame',frame)
        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         break
        return
