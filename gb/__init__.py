import struct
import time

class Link:
    SC = 1
    SI = 10
    SO = 2

    def __init__(self, p):
        self.p = p

    def tx(self, byte):
        rx = 0
        for i in range(7, -1, -1):
            bit = (byte >> i) & 1
            self.p.set_bit(self.SO, bit)
            self.p.set_bit(self.SC, 1)
            self.p.set_bit(self.SC, 0)
            rx |= self.p.get_bit(self.SI) << i
            self.p.set_bit(self.SC, 1)
        return rx

    def rx(self):
        return self.tx(0)

class GBlinkDL:
    def __init__(self, link):
        self.link = link
        self.connected = False
        self.carttype = None
        self.romsize = None
        self.ramsize = None
        self.checksum = None
        self.gamename = None
        self.rom = None

    def _connect(self):
        connected = False
        for i in range(100):
            if self.link.tx(0x9A) == 0xB4:
                connected = True
                break
            time.sleep(0.001)

        if not connected:
            return False
        connected = False

        for i in range(100):
            if self.link.tx(0x9A) == 0x1D:
                connected = True
                break
            time.sleep(0.001)

        return connected

    def _read8(self):
        time.sleep(0.00002)
        return self.link.rx()

    def _read16(self):
        return (self._read8() << 8) | self._read8()

    def _read_string(self, size):
        bstring = []
        for i in range(size):
            bstring.append(self._read8())
        return ''.join([chr(c) for c in bstring])

    def _read_header(self):
        self.carttype = self._read8()
        self.romsize = self._read8()
        self.ramsize = self._read8()
        self.checksum = self._read16()
        self.gamename = self._read_string(16)

    def _read_bytestring(self, size):
        bstring = b''
        for i in range(size):
            bstring += struct.pack("B", self._read8())
        return bstring

    def connect(self):
        if not self._connect():
            return False
        self._read_header()
        if self._read8() != 0:
            return False
        if self._read8() != 0xFF:
            return False
        self.connected = True
        self.rom = self._read_bytestring(0x4000)
        return True
