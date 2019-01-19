import cv2

def get_frames(video_file):
    cap = cv2.VideoCapture(video_file)
    list_of_frames = []

    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret:
            list_of_frames += [frame]
        else:
            break

    cap.release()
    cv2.destroyAllWindows()

    return list_of_frames
