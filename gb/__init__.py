class LinkParallel:
    SC = 1
    SI = 10
    SO = 2

    def __init__(self, p):
        self.p = p
        self.p.set_bit(self.SC, 1)

    def tx(self, byte):
        rx = 0
        for i in range(7, -1, -1):
            bit = (byte >> i) & 1
            self.p.set_bit(self.SO, bit)
            self.p.set_bit(self.SC, 0)
            rx |= self.p.get_bit(self.SI) << i
            self.p.set_bit(self.SC, 1)
        return rx

    def rx(self):
        return self.tx(0)

    def rxb(self, n=1):
        bstring = b''
        for i in range(size):
            bstring += struct.pack("B", self.rx())
        return bstring

class LinkSerial:
    SPAN = 0x400
    DEBUG = False

    def __init__(self, p):
        self.p = p

    def tx(self, byte):
        self.p.write(bytes([byte]))
        b = self.p.read(1)[0]
        if self.DEBUG:
            print("%02X-%02X" % (byte, b))
        return b

    def rx(self):
        return self.tx(0)

    def txb(self, block):
        self.p.write(bytes(block))
        return self.p.read(len(block))

    def rxb(self, n=1):
        bstring = b''
        while n > 0:
            self.p.write(bytes([0] * min(self.SPAN, n)))
            bstring += self.p.read(min(self.SPAN, n))
            n -= self.SPAN
        return bstring
