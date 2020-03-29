import usocket
import machine
from ustruct import unpack, unpack_from
import neopixel


_MY_UNIVERSES = (1, 2, 3)
_LED_BUFFER_LEN = const(_NUM_LEDS*3)

led1 = neopixel.NeoPixel(machine.Pin(1), _NUM_LEDS, bpp=4)
led2 = neopixel.NeoPixel(machine.Pin(2), _NUM_LEDS, bpp=4)
led3 = neopixel.NeoPixel(machine.Pin(3), _NUM_LEDS, bpp=4)
led4 = neopixel.NeoPixel(machine.Pin(4), _NUM_LEDS, bpp=4)

# sACN vectors
VECTOR_ROOT_E131_DATA       = const(b'\x00\x00\x00\x04')
VECTOR_ROOT_E131_EXTENDED   = const(b'\x00\x00\x00\x08')
VECTOR_E131_DATA_PACKET     = const(b'\x00\x00\x00\x02')
VECTOR_DMP_SET_PROPERTY     = const(0x02)

lookup_output = {1: (led1, 0), 2: (led2, 0), 3: (led3, 0)}

def is_artnet(packet):
    if packet[:8] != b'Art-Net\0x00':
        return False
    return True

def get_led_and_offset(universe):
    return lookup_output[universe]

def update_strip(data, universe):
    '''less pythonic but should run faster.'''
    led_strip, offset = get_led_and_offset(universe)
    pixel = offset
    for i in range(0, _LED_BUFFER_LEN, 3):
        led_index = pixel * 4
        led_strip[led_index] = data[i]
        led_strip[led_index+1] = data[i+1]
        led_strip[led_index+2] = data[i+2]
        led_strip[led_index+3] = 0
        pixel += 1
    led_strip.show()
    
def handle_artnet(packet):
    op_code, version, sequence, physical, subnet_universe, net, length = unpack('!HHBBBBH', packet[8:18])
    if op_code != 0x5000 or version != 14:
        # not OpDmx
        return
    universe = subnet_universe & 0x7 # first 3 bits
    subnet = subnet_universe >> 4    # high 4 bits
    if universe not in _MY_UNIVERSES:
        return
    dmx_data = unpack_from('{}H'.format(length), packet, offset=18)
    update_strip(dmx_data, universe)

def is_sacn(packet):
    if packet[18:22] != VECTOR_ROOT_E131_DATA or \
       packet[40:44] != VECTOR_E131_DATA_PACKET or \
       packet[117] != VECTOR_DMP_SET_PROPERTY:
        return False
    return True


def handle_sacn(packet):
    # TODO 
    priority, addr, sequence, options, universe  = unpack('!BHBBH', packet[108:115])
    if universe not in _MY_UNIVERSES:
        return
    # preview = (options & 0b10000000) >> 7
    # stream_terminated = (options & 0b01000000) >> 6
    # force_sync = (options & 0b00100000) >> 5
    dmx_data = unpack('512H', packet[126:638])
    update_strip(dmx_data, universe)

while True:
    packet = sock.recv(1144) # 1144 is longest possible sACN packet
    if is_artnet(packet):
        handle_artnet(packet)
    elif is_sacn(packet):
        handle_sacn(packet)