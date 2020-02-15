import usocket
import machine
from ustruct import unpack, unpack_from
import neopixel

LED_1_PIN = machine.Pin(1)
LED_2_PIN = machine.Pin(2)
LED_3_PIN = machine.Pin(3)
LED_4_PIN = machine.Pin(4)

MY_UNIVERSES = (1, 2, 3)

led1 = neopixel.NeoPixel(LED_1_PIN, 200, bpp=4)
led2 = neopixel.NeoPixel(LED_2_PIN, 200, bpp=4)
led3 = neopixel.NeoPixel(LED_3_PIN, 200, bpp=4)
led4 = neopixel.NeoPixel(LED_4_PIN, 200, bpp=4)

# sACN vectors
VECTOR_ROOT_E131_DATA       = (0x00, 0x00, 0x00, 0x04)
VECTOR_ROOT_E131_EXTENDED   = (0x00, 0x00, 0x00, 0x08)
VECTOR_E131_DATA_PACKET     = (0x00, 0x00, 0x00, 0x02)
VECTOR_DMP_SET_PROPERTY     = 0x02

lookup_output = {1: led1, 2: led2, 3: led3}

def is_artnet(packet):
    if packet[:8] != b'Art-Net\0x00':
        return False
    return True

def convert_to_sk(data, universe):
    # TODO
    return data, led1

def handle_artnet(packet):
    op_code, version, sequence, physical, universe, length = unpack('!HHBBHH', packet[8:18])
    if op_code != 0x5000:
        # not OpDmx, ignore
        return
    if universe not in MY_UNIVERSES:
        return
    dmx_data = unpack_from('{}H'.format(length), packet, offset=18)
    led_data, output = convert_to_sk(dmx_data, universe)
    output.show()

def is_sacn(packet):
    if tuple(packet[18:22]) != VECTOR_ROOT_E131_DATA or \
       tuple(packet[40:44]) != VECTOR_E131_DATA_PACKET or \
       packet[117] != VECTOR_DMP_SET_PROPERTY:
        return False
    return True


def handle_sacn(packet):
    # TODO 
    priority, addr, sequence, options, universe  = unpack('!BHBBH', packet[108:115])
    if universe not in MY_UNIVERSES:
        return
    preview = (options & 0b10000000) >> 7
    stream_terminated = (options & 0b01000000) >> 6
    force_sync = (options & 0b00100000) >> 5
    dmx_data = unpack('512H', packet[126:638])
    led_data, output = convert_to_sk(dmx_data, universe)


while True:
    packet = sock.recv(1144) # 1144 is longest possible sACN packet
    if is_artnet(packet):
        handle_artnet(packet)
    elif is_sacn(packet):
        handle_sacn(packet)
    


    

    