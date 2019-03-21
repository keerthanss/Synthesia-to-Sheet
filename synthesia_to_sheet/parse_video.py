import cv2

def get_frames(video_file):
    cap = cv2.VideoCapture(video_file)
    list_of_frames = []
    i = 0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if i < 750: #NOTE: temporary fix
            list_of_frames.append(frame)
            i += 1
        else:
            break

    cap.release()
    cv2.destroyAllWindows()

    return list_of_frames
