import datetime

class MBC(object):
    def __init__(self, conn):
        self.conn = conn
        if conn.romsize < 8:
            self.nbanks = 2 << conn.romsize
        elif conn.romsize == 0x52:
            self.nbanks = 72
        elif conn.romsize == 0x53:
            self.nbanks = 80
        elif conn.romsize == 0x54:
            self.nbanks = 96

        if conn.ramsize == 1:
            self.ramsize = 0x800
        elif conn.ramsize == 2:
            self.ramsize = 0x2000
        elif conn.ramsize == 3:
            self.ramsize = 0x8000
        elif conn.ramsize == 4:
            self.ramsize = 0x20000
        elif conn.ramsize == 5:
            self.ramsize = 0x10000
        else:
            self.ramsize = 0

    def unlock_ram(self):
        self.conn.write(0x0000, 0xA)

    def select_rom_bank(self, bank):
        self.conn.write(0x2100, bank)

    def select_ram_bank(self, bank):
        self.conn.write(0x4000, bank)

    def dump_rom(self):
        rom = [self.conn.read_ec(0x0, 0x4000)]
        for i in range(1, self.nbanks):
            self.select_rom_bank(i)
            rom.append(self.conn.read_ec(0x4000, 0x4000))
        return b''.join(rom)

    def dump_ram(self):
        ram = []
        for i in range(self.ramsize / 0x800):
            if not i & 3:
                self.select_ram_bank(i / 4)
            ram.append(self.conn.read_ec(0xA000 + (i & 3) * 0x800, 0x800))
        return b''.join(ram)

    def restore_ram(self, ram):
        for i in range(self.ramsize):
            if not i & 0x1FFF:
                self.select_ram_bank(i / 0x2000)
            self.conn.write_ec(0xA000 + (i & 0x1FFF), ord(ram[i]))

class MBC1(MBC):
    BANK_MODE_ROM = 0
    BANK_MODE_RAM = 1
    def set_bank_mode(self, mode):
        self.conn.write(0x6000, mode)

    def select_rom_bank(self, bank):
        self.set_bank_mode(self.BANK_MODE_RAM)
        super(MBC1, self).select_rom_bank(bank & 0x1F)
        self.conn.write(0x4000, bank >> 5)

    def select_ram_bank(self, bank):
        self.set_bank_mode(self.BANK_MODE_RAM)
        super(MBC1, self).select_ram_bank(bank)

    def dump_rom(self):
        rom = [self.conn.read_ec(0x0, 0x4000)]
        for i in range(1, self.nbanks):
            self.select_rom_bank(i)
            rom.append(self.conn.read_ec(0x4000 if i & 0x1F else 0x0000, 0x4000))
        return b''.join(rom)

class MBC3(MBC):
    def latch_rtc(self):
        self.conn.write(0x6000, 0)
        self.conn.write(0x6000, 1)

    def read_rtc(self, reg):
        self.select_ram_bank(8 + reg)
        return self.conn.read(0xA000)

    def get_time(self, latch=True):
        if latch:
            self.latch_rtc()
        hour = ord(self.read_rtc(2))
        minute = ord(self.read_rtc(1))
        second = ord(self.read_rtc(0))
        return datetime.time(hour, minute, second)

class MBC5(MBC):
    def select_rom_bank(self, bank):
        super(MBC5, self).select_rom_bank(bank & 0xFF)
        self.conn.write(0x3000, bank >> 8)

    def set_rumble(self, on=True):
        self.select_ram_bank(8 * on)

class MBC7(MBC):
    ACCEL_OFFSET = 0x81D0

    def unlock_ram(self):
        super(MBC7, self).unlock_ram()
        self.select_ram_bank(0x40)

    def sample_accel(self):
        self.conn.write(0xA000, 0x55)
        self.conn.write(0xA010, 0xAA)
        self.accel_x_raw = ord(self.conn.read(0xA020)) | (ord(self.conn.read(0xA030)) << 8)
        self.accel_y_raw = ord(self.conn.read(0xA040)) | (ord(self.conn.read(0xA050)) << 8)
        self.accel_x = self.accel_x_raw - self.ACCEL_OFFSET
        self.accel_y = self.accel_y_raw - self.ACCEL_OFFSET

    def eeprom_init(self):
        self.conn.write(0xA080, 0)
        self.eeprom_shift_ins((0, 1))

    def eeprom_shift_in(self, b):
        self.conn.write(0xA080, 0x80 | ((b & 1) << 1))
        self.conn.write(0xA080, 0xC0 | ((b & 1) << 1))

    def eeprom_shift_inout(self, b):
        self.eeprom_shift_in(b)
        return ord(self.conn.read(0xA080)) & 1

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
