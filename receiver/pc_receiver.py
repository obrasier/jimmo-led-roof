import socket
from struct import unpack, unpack_from


_MY_UNIVERSES = (1, 2, 3, 4, 5, 6, 7, 8, 9)

# sACN vectors
VECTOR_ROOT_E131_DATA       = (b'\x00\x00\x00\x04')
VECTOR_ROOT_E131_EXTENDED   = (b'\x00\x00\x00\x08')
VECTOR_E131_DATA_PACKET     = (b'\x00\x00\x00\x02')
VECTOR_DMP_SET_PROPERTY     = (0x02)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('127.0.0.1', 6454))


def is_artnet(packet):
    if packet[:8] != b'Art-Net\x00':
        return False
    return True

    
def handle_artnet(packet):
    op_code, version, sequence, physical, subnet_universe, net, length = unpack('!HHBBBBH', packet[8:18])
    if op_code != 0x5000 or version != 14:
        # not OpDmx
        return
    universe = subnet_universe & 0x7
    subnet = subnet_universe >> 4
    print(universe, subnet, length)
    if universe not in _MY_UNIVERSES:
        return
    dmx_data = unpack_from('!{}B'.format(length), packet, offset=18)
    print(f'{universe}: {dmx_data}')


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
    dmx_data = unpack('512B', packet[126:638])
    print(f'{universe}: {dmx_data}')

while True:
    packet = sock.recv(1144) # 1144 is longest possible sACN packet
    if is_artnet(packet):
        handle_artnet(packet)
    elif is_sacn(packet):
        handle_sacn(packet)