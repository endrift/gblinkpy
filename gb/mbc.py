import datetime

class MBC(object):
    ROM_BANK_SIZE = 0x4000
    RAM_BANK_SIZE = 0x2000
    def __init__(self, conn):
        self.conn = conn
        if conn.romsize < 8:
            self.nbanks = (0x8000 // self.ROM_BANK_SIZE) << conn.romsize
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

    def dump_rom(self, cb=None, retries=None):
        rom = [self.conn.read_ec(0x0, self.ROM_BANK_SIZE)]
        for i in range(1, self.nbanks):
            self.select_rom_bank(i)
            rom.append(self.conn.read_ec(0x4000, self.ROM_BANK_SIZE, retries))
            if cb:
                cb(i, rom[-1])
        return b''.join(rom)

    def dump_ram(self):
        ram = []
        for i in range(self.ramsize // 0x800):
            if not i & ((self.RAM_BANK_SIZE // 0x800) - 1):
                self.select_ram_bank(i // (self.RAM_BANK_SIZE // 0x800))
            ram.append(self.conn.read_ec(0xA000 + (i & ((self.RAM_BANK_SIZE // 0x800) - 1)) * 0x800, 0x800))
        return b''.join(ram)

    def restore_ram(self, ram):
        for i in range(self.ramsize):
            if not i & (self.RAM_BANK_SIZE - 1):
                self.select_ram_bank(i // self.RAM_BANK_SIZE)
            self.conn.write_ec(0xA000 + (i & (self.RAM_BANK_SIZE - 1)), ram[i])

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

    def dump_rom(self, cb=None, retries=None):
        rom = [self.conn.read_ec(0x0, 0x4000)]
        for i in range(1, self.nbanks):
            self.select_rom_bank(i)
            rom.append(self.conn.read_ec(0x4000 if i & 0x1F else 0x0000, 0x4000, retries))
            if cb:
                cb(i, rom[-1])
        return b''.join(rom)

class MBC2(MBC):
    def __init__(self, conn):
        super(MBC2, self).__init__(conn)
        self.ramsize = 0x100

    def dump_ram(self):
        bs = self.conn.read_ec(0xA000, 0x200)
        ram = []
        for i in range(self.ramsize):
            ram.append(((bs[i * 2 + 1] & 0xF) << 4) | (bs[i * 2] & 0xF))
        return bytes(ram)

    def restore_ram(self, ram):
        for i in range(len(ram)):
            b = ram[i]
            self.conn.write_ec(0xA000 + i * 2, 0xF0 | (b & 0xF))
            self.conn.write_ec(0xA001 + i * 2, 0xF0 | (b >> 4))

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

class MBC6(MBC):
    ROM_BANK_SIZE = 0x2000
    RAM_BANK_SIZE = 0x1000
    def select_rom_bank(self, bank, block=0):
        self.conn.write(0x27FF + block * 0x1000, bank)
        self.conn.write(0x2800 + block * 0x1000, 0)

    def select_ram_bank(self, bank, block=0):
        self.conn.write(0x400 + block * 0x400, bank)

class MBC7(MBC):
    ACCEL_OFFSET = 0x81D0

    EWDS = (0, 0, 0, 0)
    WRAL = (0, 0, 0, 1)
    ERAL = (0, 0, 1, 0)
    EWEN = (0, 0, 1, 1)
    WRITE = (0, 1)
    READ = (1, 0)
    ERASE = (1, 1)

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
        self.conn.write(0xA080, 0x80)

    def eeprom_send_command(self, header, address=0):
        self.eeprom_init()
        self.eeprom_shift_ins((0, 1))
        if len(header) == 2:
            self.eeprom_shift_ins(header)
            self.eeprom_shift_address(address)
        else:
            self.eeprom_shift_ins(header)
            self.eeprom_shift_ins([0] * (10 - len(header)))

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

    def eeprom_wait(self):
        # Clock the EEPROM while it's still doing stuff
        while self.eeprom_shift_inout(0) == (0,):
            pass

    def ram_read(self, address):
        self.eeprom_send_command(self.READ, address)
        bs = self.eeprom_shift_outs(16)
        b = 0
        for i in range(len(bs)):
            b |= bs[i] << (15 - i)
        return b

    def enable_write(self):
        self.eeprom_send_command(self.EWEN)

    def disable_write(self):
        self.eeprom_send_command(self.EWDS)

    def ram_write(self, address, word):
        self.eeprom_send_command(self.WRITE, address)
        # FIXME: Is there a prettier way to do this?
        bs = [ord(x) - ord('0') for x in '{:016b}'.format(word)]
        self.eeprom_shift_ins(bs)
        self.eeprom_wait()

    def dump_ram(self):
        bstring = b''
        for i in range(0x80):
            word = self.ram_read(i)
            bstring += chr(word >> 8)
            bstring += chr(word & 0xFF)
        return bstring

    def restore_ram(self, ram):
        self.enable_write()
        for i in range(0x80):
            word = ram[i * 2] << 8
            word += ram[i * 2 + 1]
            self.ram_write(i, word)
        self.disable_write()

class GBCamera(MBC):
    def select_camera(self):
        self.select_ram_bank(0x10)

    def set_camera_defaults(self):
        self.set_exposure(0x1000)

    def set_dither_matrix(self, matrix):
        self.select_camera()
        for x in range(4):
            for y in range(4):
                for l in range(3):
                    self.conn.write(0xA006 + y * 3 + x * 12 + l, matrix[y][x][l])

    def set_exposure(self, value):
        self.select_camera()
        self.conn.write(0xA002, value >> 8)
        self.conn.write(0xA003, value & 0xFF)

    def take_photo(self):
        self.select_camera()
        self.conn.write(0xA000, 1)
        while ord(self.conn.read_ec(0xA000)) & 1:
           time.sleep(0.05)

class TAMA5(MBC):
    def __init__(self, conn):
        super(TAMA5, self).__init__(conn)
        self.ramsize = 0x20

    def unlock_ram(self):
        self.conn.write(0xA001, 0xA)
        for _ in range(200):
            if ord(self.conn.read_ec(0xA000)) & 3 == 1:
                break

    def select_rom_bank(self, bank):
        self.unlock_ram()
        self.conn.write(0xA001, 0)
        self.conn.write(0xA000, bank & 0xF)
        self.conn.write(0xA001, 1)
        self.conn.write(0xA000, bank >> 4)

    def select_ram_bank(self, bank):
        pass

    def dump_ram(self):
        self.unlock_ram()
        ram = []
        for i in range(self.ramsize):
            self.conn.write(0xA001, 6)
            self.conn.write(0xA000, (i >> 4) + 2)
            self.conn.write(0xA001, 7)
            self.conn.write(0xA000, i & 0xF)
            self.conn.write(0xA001, 0xD)
            hi = ord(self.conn.read_ec(0xA000)) & 0xF
            self.conn.write(0xA001, 0xC)
            lo = ord(self.conn.read_ec(0xA000)) & 0xF
            ram.append((hi << 4) | lo)
        return bytes(ram)

    def restore_ram(self, ram):
        self.unlock_ram()
        for i in range(self.ramsize):
            self.conn.write(0xA001, 4)
            self.conn.write(0xA000, i & 0xF)
            self.conn.write(0xA001, 5)
            self.conn.write(0xA000, i >> 4)
            self.conn.write(0xA001, 6)
            self.conn.write(0xA000, i >> 4)
            self.conn.write(0xA001, 7)
            self.conn.write(0xA000, i & 0xF)



MAPPINGS = {
    0x00: MBC,
    0x01: MBC1,
    0x02: MBC1,
    0x03: MBC1,
    0x05: MBC2,
    0x06: MBC2,
    0x08: MBC,
    0x09: MBC,
    #0x0B: MMM01,
    #0x0C: MMM01,
    #0x0D: MMM01,
    0x0F: MBC3,
    0x10: MBC3,
    0x11: MBC3,
    0x12: MBC3,
    0x13: MBC3,
    0x19: MBC5,
    0x1A: MBC5,
    0x1B: MBC5,
    0x1C: MBC5,
    0x1D: MBC5,
    0x1E: MBC5,
    0x20: MBC6,
    0x22: MBC7,
    0xFC: GBCamera,
    0xFD: TAMA5,
    #0xFE: HuC3,
    #0xFF: HuC1
}

def detect(conn):
    if conn.carttype not in MAPPINGS:
        return None
    return MAPPINGS[conn.carttype](conn)
