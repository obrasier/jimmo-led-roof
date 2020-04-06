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

LED_STRIPS = [strip_1, strip_2, strip_3, strip_4, strip_5, strip_7, strip_7, strip_8, strip_9]
_VIDEO_WIDTH = 150
_VIDEO_HEIGHT = 84

def current_ms():
    return time.time_ns() // 1000000

def process_frame(frame, average=False, order_bgr=True):
    rows, cols, dims = frame.shape
    if cols != 150 or rows != 84:
        frame = cv2.resize(frame, dsize=(_VIDEO_WIDTH, _VIDEO_HEIGHT), interpolation=cv2.INTER_CUBIC)
    for strip, row in enumerate(np.linspace(0, _VIDEO_HEIGHT, 9, dtype=int)):
        pixel_row = frame[row]
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
