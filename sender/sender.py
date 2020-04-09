import cv2
import numpy as np
import time
import glob
from collections import deque
from artnet import ArtDmxPacket

_SHORT_STRIP_LEDS = 120
_LONG_STRIP_LEDS = 150
_VIDEO_WIDTH = _LONG_STRIP_LEDS
_VIDEO_HEIGHT = 84
_MAX_FPS = 30

strip_1 = ArtDmxPacket(target_ip='127.0.0.1', universe=1, packet_size=_SHORT_STRIP_LEDS*3)
strip_2 = ArtDmxPacket(target_ip='127.0.0.1', universe=2, packet_size=_SHORT_STRIP_LEDS*3)
strip_3 = ArtDmxPacket(target_ip='127.0.0.1', universe=3, packet_size=_SHORT_STRIP_LEDS*3)
strip_4 = ArtDmxPacket(target_ip='127.0.0.1', universe=4, packet_size=_SHORT_STRIP_LEDS*3)
strip_5 = ArtDmxPacket(target_ip='127.0.0.1', universe=5, packet_size=_LONG_STRIP_LEDS*3)
strip_6 = ArtDmxPacket(target_ip='127.0.0.1', universe=6, packet_size=_LONG_STRIP_LEDS*3)
strip_7 = ArtDmxPacket(target_ip='127.0.0.1', universe=7, packet_size=_LONG_STRIP_LEDS*3)
strip_8 = ArtDmxPacket(target_ip='127.0.0.1', universe=8, packet_size=_LONG_STRIP_LEDS*3)
strip_9 = ArtDmxPacket(target_ip='127.0.0.1', universe=9, packet_size=_LONG_STRIP_LEDS*3)

LED_STRIPS = [strip_1, strip_2, strip_3, strip_4, strip_5, strip_7, strip_7, strip_8, strip_9]
_NUM_STRIPS = len(LED_STRIPS)


def current_ms():
    return time.time_ns() // 1000000

def process_frame(frame, order_rgb=False):
    rows, cols, dims = frame.shape
    if cols != _VIDEO_WIDTH or rows != _VIDEO_HEIGHT:
        frame = cv2.resize(frame, dsize=(_VIDEO_WIDTH, _VIDEO_HEIGHT), interpolation=cv2.INTER_CUBIC)
    for strip, row in enumerate(np.linspace(0, _VIDEO_HEIGHT, _NUM_STRIPS, endpoint=False, dtype=int)):
        pixel_row = frame[row]
        if strip < 4:
            pixel_row = pixel_row[:_SHORT_STRIP_LEDS]
        if order_rgb:
            # swap columns 0 and 2 to convert BGR -> RGB
            pixel_row[:, [2, 0]] = pixel_row[:, [0, 2]]
        dmx_data = np.reshape(pixel_row, (pixel_row.shape[0]*pixel_row.shape[1]))
        LED_STRIPS[strip].send_nparray(dmx_data)
        #print(f'{strip}, {len(row)}: {row}')

print('starting video')
videos = glob.glob('videos/*')
for v in videos:
    cap = cv2.VideoCapture(v)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # if the video is too high FPS, get the frames we will use and
    # put them in a deque, so we can pop off the frames we need
    if fps > _MAX_FPS:
        frames_used = deque()
        duration = total_frames / fps
        for n in np.linspace(0, total_frames-1, _MAX_FPS * duration, endpoint=False, dtype=int):
            frames_used.appendleft(n)
        high_fps = True
        ms_per_frame = 1000 // _MAX_FPS
    else:
        ms_per_frame = 1000 // fps
        high_fps = False
    skip_next_frame = False

    if high_fps:
        next_frame = frames_used.pop()

    for frame_num in range(total_frames):
        # read the frame first.
        frame_start = current_ms()
        ret, frame = cap.read()
        if not ret or skip_next_frame:
            skip_next_frame = False
            continue

        # if the FPS is too high, check if we need to skip this frame
        if high_fps: 
            if frame_num == next_frame:
                next_frame = frames_used.pop()
            else:
                continue

        process_frame(frame)
        frame_end = current_ms()
        time_left = ms_per_frame - (frame_end - frame_start)
        if time_left > 0:
            time.sleep(time_left / 1000)
        else:
            print("WE ARE GOING TOO SLOW!")
            skip_next_frame = True

print('finished video')