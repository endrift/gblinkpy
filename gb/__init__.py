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

class LinkSerial:
    def __init__(self, p):
        self.p = p

    def tx(self, byte):
        self.p.write(bytes([byte]))
        return self.p.read(1)[0]

    def rx(self):
        return self.tx(0)
