import struct
import time

class LinkDL:
    DELAY = 0.001

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
            if self._write8(0x9A) == 0xB4:
                connected = True
                break

        if not connected:
            return False
        connected = False
        time.sleep(0.001)

        for i in range(100):
            if self._write8(0x9A) == 0x1D:
                connected = True
                break

        return connected

    def _read8(self):
        time.sleep(self.DELAY)
        return self.link.rx()

    def _write8(self, value):
        time.sleep(self.DELAY)
        return self.link.tx(value)

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

    def read(self, address, length=1):
        self._write8(0x59)
        self._write8(address >> 8)
        self._write8(address & 0xFF)
        self._write8(length >> 8)
        self._write8(length & 0xFF)
        return self._read_bytestring(length)

    def write(self, address, value):
        self._write8(0x49)
        self._write8(address >> 8)
        self._write8(address & 0xFF)
        self._write8(value)

class MBC(object):
    def __init__(self, dl):
        self.dl = dl
        if dl.romsize < 8:
            self.nbanks = 2 << dl.romsize
        elif dl.romsize == 0x52:
            self.nbanks = 72
        elif dl.romsize == 0x53:
            self.nbanks = 80
        elif dl.romsize == 0x54:
            self.nbanks = 96

        if dl.ramsize == 1:
            self.ramsize = 0x800
        elif dl.ramsize == 2:
            self.ramsize = 0x2000
        elif dl.ramsize == 3:
            self.ramsize = 0x8000
        elif dl.ramsize == 4:
            self.ramsize = 0x20000
        elif dl.ramsize == 5:
            self.ramsize = 0x10000
        else:
            self.ramsize = 0

    def unlock_ram(self):
        self.dl.write(0x0000, 0xA)

    def select_rom_bank(self, bank):
        self.dl.write(0x2100, bank)

    def select_ram_bank(self, bank):
        self.dl.write(0x4000, bank)

    def dump_rom(self):
        rom = [self.dl.rom]
        for i in range(1, self.nbanks):
            self.select_rom_bank(i)
            rom.append(self.dl.read(0x4000, 0x4000))
        return b''.join(rom)

    def dump_ram(self):
        ram = []
        for i in range(self.ramsize / 0x800):
            if not i & 3:
                self.select_ram_bank(i / 4)
            ram.append(self.dl.read(0xA000 + (i & 3) * 0x800, 0x800))
        return b''.join(ram)

class MBC1(MBC):
    BANK_MODE_ROM = 0
    BANK_MODE_RAM = 1
    def set_bank_mode(self, mode):
        self.dl.write(0x6000, mode)

    def select_rom_bank(self, bank):
        self.set_bank_mode(self.BANK_MODE_ROM)
        super(MBC1, self).select_rom_bank(bank & 0x1F)
        self.dl.write(0x4000, bank >> 5)

    def select_ram_bank(self, bank):
        self.set_bank_mode(self.BANK_MODE_RAM)
        super(MBC1, self).select_ram_bank(bank)

class MBC7(MBC):
    ACCEL_OFFSET = 0x81D0

    def unlock_ram(self):
        super(MBC7, self).unlock_ram()
        self.select_ram_bank(0x40)

    def sample_accel(self):
        self.dl.write(0xA000, 0x55)
        self.dl.write(0xA010, 0xAA)
        self.accel_x_raw = ord(self.dl.read(0xA020)) | (ord(self.dl.read(0xA030)) << 8)
        self.accel_y_raw = ord(self.dl.read(0xA040)) | (ord(self.dl.read(0xA050)) << 8)
        self.accel_x = self.accel_x_raw - self.ACCEL_OFFSET
        self.accel_y = self.accel_y_raw - self.ACCEL_OFFSET

    def eeprom_init(self):
        self.dl.write(0xA080, 0)
        self.eeprom_shift_ins((0, 1))

    def eeprom_shift_in(self, b):
        self.dl.write(0xA080, 0x80 | ((b & 1) << 1))
        self.dl.write(0xA080, 0xC0 | ((b & 1) << 1))

    def eeprom_shift_inout(self, b):
        self.eeprom_shift_in(b)
        return ord(self.dl.read(0xA080)) & 1

    def eeprom_shift_out(self):
        self.eeprom_shift_inout(0)

    def eeprom_shift_ins(self, bs):
        for b in bs:
            self.eeprom_shift_in(b)

    def eeprom_shift_inouts(self, bs):
        o = []
        for b in bs:
            o.append(self.eeprom_shift_inout(b))
        return tuple(o)

    def eeprom_shift_outs(self, n):
        return self.eeprom_shift_inouts([0] * n)

    def eeprom_shift_address(self, addr):
        for i in range(7, -1, -1):
            self.eeprom_shift_in(addr >> i)

    def ram_read(self, address):
        self.eeprom_init()
        self.eeprom_shift_ins((1, 0))
        self.eeprom_shift_address(address)
        bs = self.eeprom_shift_outs(16)
        self.eeprom_shift_in(0)
        b = 0
        for i in range(len(bs)):
            b |= bs[i] << (15 - i)
        return b

    def dump_ram(self):
        bstring = b''
        for i in range(0x80):
            word = self.ram_read(i)
            bstring += chr(word >> 8)
            bstring += chr(word & 0xFF)
        return bstring
