import cv2
import numpy as np

_NUM_STRIPS = 11
_STRIP_LENGTH = 200
_PIXELS_IN_UNIVERSE = 170
u_lookup = {0: 0}
dmx_data_start = np.zeros(510, dtype=np.uint8)
dmx_data_short = np.zeros(300, dtype=np.uint8)
dmx_data_long = np.zeros(450, dtype=np.uint8)

cap = cv2.VideoCapture("IMG_3388.MP4")

# get total number of frames
total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)


def send_data(dmx_data, strip_num):
    universe = u_lookup[strip_num]

def process_frame(frame):
    rows, columns, channels = frame.shape
    y_spacing = rows // _NUM_STRIPS
    x_spacing = columns // _STRIP_LENGTH
    strip_num = 0
    pixel = 0
    dmx_data = [0]*170


def process_average_area(frame):

    area = frame[0:50, 0:50]
    if len(area.shape) == 3:
        b, g, r = np.mean(np.mean(area, axis=0), axis=0).astype(np.uint8)
    else:
        b, g, r = np.mean(area, axis=0).astype(np.uint8)
    

while True:
    ret, frame = cap.read()
    row, cols = frame.shape

    for i in range(rows):
        for j in range(cols):
            k = frame[i,j]
            print k
    cv2.imshow("Video", frame)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break