import cv2
import numpy as np
import time
import glob

from artnet import ArtDmxPacket

strip_1 = ArtDmxPacket(target_ip='127.0.0.1', universe=1, packet_size=360)
strip_2 = ArtDmxPacket(target_ip='127.0.0.1', universe=2, packet_size=360)
strip_3 = ArtDmxPacket(target_ip='127.0.0.1', universe=3, packet_size=360)
strip_4 = ArtDmxPacket(target_ip='127.0.0.1', universe=4, packet_size=360)
strip_5 = ArtDmxPacket(target_ip='127.0.0.1', universe=5, packet_size=450)
strip_6 = ArtDmxPacket(target_ip='127.0.0.1', universe=6, packet_size=450)
strip_7 = ArtDmxPacket(target_ip='127.0.0.1', universe=7, packet_size=450)
strip_8 = ArtDmxPacket(target_ip='127.0.0.1', universe=8, packet_size=450)
strip_9 = ArtDmxPacket(target_ip='127.0.0.1', universe=9, packet_size=450)

LEN_LOOKUP = {0: 120, 1: 120, 2: 120, 3: 120, 4: 150, 5: 150, 6: 150, 7: 150, 8: 150}

LED_STRIPS = [strip_1, strip_2, strip_3, strip_4, strip_5, strip_7, strip_7, strip_8, strip_9]


def current_ms():
    return time.time_ns() // 1000000


_NUM_STRIPS = 11
_STRIP_LENGTH = 200
_PIXELS_IN_UNIVERSE = 170
u_lookup = {0: 0}
dmx_data_start = np.zeros(510, dtype=np.uint8)
dmx_data_short = np.zeros(300, dtype=np.uint8)
dmx_data_long = np.zeros(450, dtype=np.uint8)


def process_frame(frame, average=False, order_bgr=True):
    rows, cols, dims = frame.shape
    if cols != 150 or rows != 9:
        frame = cv2.resize(frame, dsize=(150, 9), interpolation=cv2.INTER_CUBIC)
    for strip in range(9):
        pixel_row = frame[strip]
        if strip < 4:
            pixel_row = pixel_row[:120]
        if order_bgr:
            row = np.reshape(pixel_row, (pixel_row.shape[0]*pixel_row.shape[1]))
        else:
            # swap columns 0 and 2 to get RGB
            pixel_row[:, [2, 0]] = pixel_row[:, [0, 2]]
            row = np.reshape(pixel_row, (pixel_row.shape[0]*pixel_row.shape[1]))
        LED_STRIPS[strip].send_nparray(row)
        #print(f'{strip}, {len(row)}: {row}')

def get_pixel_rgb(frame, x, y):
    b, g, r = frame[x][y]
    return r, g, b

def average_area(area):
    if len(area.shape) == 3:
        b, g, r = np.mean(np.mean(area, axis=0), axis=0).astype(np.uint8)
    else:
        b, g, r = np.mean(area, axis=0).astype(np.uint8)
    return r, g, b

print('starting video')
videos = glob.glob('videos/*')
for v in videos:
    cap = cv2.VideoCapture(v)
    fps = cap.get(cv2.CAP_PROP_FPS)

    # get total number of frames
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    running_time = fps * total_frames * 30

    ms_per_frame = 1000 // fps

    skip_next_frame = False

    for i in range(int(total_frames)):
        frame_start = current_ms()
        ret, frame = cap.read()
        if not ret or skip_next_frame:
            skip_next_frame = False
            continue
        row, cols, dims = frame.shape
        print(total_frames, row, cols, dims)
        process_frame(frame)
        frame_end = current_ms()
        time_left = ms_per_frame - (frame_end - frame_start)
        if time_left > 0:
            time.sleep(time_left / 1000)
        else:
            print("WE ARE GOING TOO SLOW!")
            skip_next_frame = True

print('finished video')
