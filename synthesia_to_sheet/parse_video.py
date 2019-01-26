import cv2

from calibrate import detect_all_black_keys
from calibrate import detect_all_white_keys
from calibrate import get_first_C_note

def get_frames(video_file):
    cap = cv2.VideoCapture(video_file)
    list_of_frames = []
    i = 0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if i < 1000: #NOTE: temporary fix
            list_of_frames.append(frame)
            i += 1
        else:
            break

    cap.release()
    cv2.destroyAllWindows()

    return list_of_frames

# method for temporary testing only
def display_frames(list_of_frames):
    blackKeys = detect_all_black_keys(list_of_frames[0])
    (whiteKeys, meanBlackDistance) = detect_all_white_keys(list_of_frames[0], blackKeys)
    get_first_C_note(blackKeys, whiteKeys, meanBlackDistance)

    # for frame in list_of_frames:
    for key in blackKeys:
        cv2.circle(list_of_frames[0], key.Location, 3, (0,0,255), -1)
    for key in whiteKeys:
        cv2.circle(list_of_frames[1], key.Location, 3, (0,0,255), -1)
        # cv2.imshow('frame',frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    cv2.imwrite('blackKeysFrame.png', list_of_frames[0])
    cv2.imwrite('whiteKeysFrame.png', list_of_frames[1])

    return
