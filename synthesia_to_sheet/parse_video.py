import cv2

def get_frames(video_file):
    cap = cv2.VideoCapture('vtest.avi')
    list_of_frames = []

    while(cap.isOpened()):
        ret, frame = cap.read()
        list_of_frames += [frame]
    cap.release()
    cv2.destroyAllWindows()

    return list_of_frames
