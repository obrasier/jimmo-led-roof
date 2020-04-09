import socket
from struct import pack, unpack, unpack_from
import time

# ArtPoll packet
# talk to me information
# bits 7-5 - 0
# bit 4 - VLC (visible light communication) transmission
# we don't support this, set to 1
# bit 3 - diagnostics broadcast/unicast
# if they exist they're probs broadcast, set to 0
# bit 2 - diagnostics true/false
# true - set to 1
# bit 1 - ArtPollReply
# only respond to ArtPoll/ArtAddress packets - 0
# bit 0 - unused, set to 0
# self.header.append(0b00010100)


class ArtDmxPacket:

    def __init__(self, target_ip='127.0.0.1', universe=0, packet_size=512):
        self.target_ip = target_ip
        self.port = 6454
        self.universe = universe
        self.subnet = 0
        self.net = 0
        self.opcode = 0x5000
        self.packet_size = packet_size
        self.header = bytearray()
        self.buffer = bytearray(self.packet_size)
        self.sequence = 0x00
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.make_header()

    def make_header(self):
        self.header = b'Art-Net\x00'
        version = 0x000e  # version is 14
        physical = 0x00
        # universe information
        # bit 15 - 0
        # bit 14-8 - Net (1-128)
        # bit 7-4 - SubNet (1-16)
        # bit 3-0 - Universe (1-16)
        # low byte first
        # a subnet is a group of 16 universes
        # a net is 16 subnets
        # we can have 128 nets
        subnet_universe = (self.subnet << 4 | self.universe) & 0xFF
        net = self.net & 0x7F  # 7 makes bit 15 = 0
        
        self.header += pack('!HHBBBBH', self.opcode, version,
                            self.sequence, physical, subnet_universe, net, self.packet_size)

    def update(self):
        packet = bytearray()
        packet.extend(self.header)
        if len(self.buffer) > 512:
            raise Exception('Buffer too long')
        if len(self.buffer) != self.packet_size:
            raise Exception('Buffer and size mismatch')
        packet.extend(self.buffer)
        try:
            self.sock.sendto(packet, (self.target_ip, self.port))
        except:
            print('Error sending packet.')

    def close(self):
        self.sock.close()

    def set_value(self, address, value):
        if address > self.packet_size - 1 or address < 0:
            # out of range
            return
        self.buffer[address] = value

    def set_rgb(self, pixel, r, g, b):
        address = pixel * 3
        self.set_value(address, r)
        self.set_value(address+1, g)
        self.set_value(address+2, b)

    def set_all_rgb(self, r, g, b):
        for p in range(0, self.packet_size, 3):
            self.set_rgb(p, r, g, b)
        self.update()

    def clear(self):
        self.buffer = bytearray(self.packet_size)
        self.update()

    def send_nparray(self, np_array):
        self.buffer = np_array.tobytes()
        self.update()
