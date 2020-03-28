import cv2
import numpy as np
import time 

current_ms = lambda: time.time_ns() // 1000000 

_NUM_STRIPS = 11
_STRIP_LENGTH = 200
_PIXELS_IN_UNIVERSE = 170
u_lookup = {0: 0}
dmx_data_start = np.zeros(510, dtype=np.uint8)
dmx_data_short = np.zeros(300, dtype=np.uint8)
dmx_data_long = np.zeros(450, dtype=np.uint8)

cap = cv2.VideoCapture("simple_colours.mp4")
fps = cap.get(cv2.CAP_PROP_FPS)

# get total number of frames
total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
running_time = fps * total_frames * 30


def send_data(dmx_data, strip_num):
    universe = u_lookup[strip_num]

def process_frame(frame, average=False):
    if average:
        process_average_area(frame)
    strip_num = 0
    if not average:
        for y in range(5, 95, 10):
            # pixels are stored as BGR - this needs to be reflected in the receiver
            row = np.reshape(frame[y], (frame[y].shape[0]*frame[y].shape[1]))
            



def get_pixel_rgb(frame, x, y):
    b, g, r = frame[x][y]
    return r, g, b

def process_average_area(frame):

    area = frame[0:50, 0:50]
    if len(area.shape) == 3:
        b, g, r = np.mean(np.mean(area, axis=0), axis=0).astype(np.uint8)
    else:
        b, g, r = np.mean(area, axis=0).astype(np.uint8)
    
print('starting video')

_TIME_PER_FRAME_MS = 1000 // fps

skip_next_frame = False

for i in range(int(total_frames)):
    frame_start = current_ms()
    ret, frame = cap.read()
    if skip_next_frame:
        skip_next_frame = False
        continue
    row, cols, dims = frame.shape
    print(total_frames, row, cols, dims)
    process_frame(frame)
    frame_end = current_ms()
    time_left = _TIME_PER_FRAME_MS - (frame_end - frame_start)
    if time_left > 0:
        time.sleep(time_left / 1000)
    else:
        print("WE ARE GOING TOO SLOW!")
        skip_next_frame = True
        
print('finished video')