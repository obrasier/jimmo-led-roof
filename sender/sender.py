import cv2
import numpy as np
import time
import glob

from artnet import ArtDmxPacket

_ASPECT_RATIO = (16, 9)
_SHORT_STRIP_LEDS = 120
_LONG_STRIP_LEDS = 150
_VIDEO_HEIGHT = _LONG_STRIP_LEDS
_VIDEO_WIDTH = (_VIDEO_HEIGHT // _ASPECT_RATIO[1]) * _ASPECT_RATIO[0]
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

def linspace_generator(start, stop, num_steps, dtype=int):
    for x in range(num_steps):
        yield dtype(x * (stop - start) / (num_steps - 1))

def current_ms():
    return time.time_ns() // 1000000

def process_frame(frame, order_rgb=False):
    rows, cols, dims = frame.shape
    if cols != _VIDEO_WIDTH or rows != _VIDEO_HEIGHT:
        frame = cv2.resize(frame, dsize=(_VIDEO_WIDTH, _VIDEO_HEIGHT), interpolation=cv2.INTER_CUBIC)
    for strip, col in enumerate(linspace_generator(0, _VIDEO_WIDTH - 1, _NUM_STRIPS)):
        pixel_col = frame[:, col]
        if strip < 4:
            pixel_col = pixel_col[:_SHORT_STRIP_LEDS]
        if order_rgb:
            # swap columns 0 and 2 to convert BGR -> RGB
            pixel_col[:, [2, 0]] = pixel_col[:, [0, 2]]
        dmx_data = np.reshape(pixel_col, (pixel_col.shape[0]*pixel_col.shape[1]))
        LED_STRIPS[strip].send_nparray(dmx_data)
        print(f'{strip}, {len(col)}: {col}')

print('starting video')
videos = glob.glob('videos/*')
for v in videos:
    cap = cv2.VideoCapture(v)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # if the video is too high FPS, get the frames we will use
    if fps > _MAX_FPS:
        duration = total_frames // int(fps)
        frames_used = linspace_generator(0, total_frames - 1, duration * _MAX_FPS)
        next_frame = next(frames_used)
        high_fps = True
        ms_per_frame = 1000 // _MAX_FPS
    else:
        ms_per_frame = 1000 // fps
        high_fps = False
    skip_next_frame = False

    for frame_num in range(total_frames):
        # read the frame first.
        frame_start = current_ms()
        ret, frame = cap.read()

        # if the FPS is too high, check if we need to skip this frame
        # must be called before checking skip_next_frame
        if high_fps:
            if frame_num == next_frame:
                next_frame = next(frames_used)
            else:
                continue
        
        if not ret or skip_next_frame:
            skip_next_frame = False
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