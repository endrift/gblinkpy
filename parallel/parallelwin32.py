# pyparallel driver for win32
# see __init__.py
#
# (C) 2002 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
# thanks to Dincer Aydin dinceraydin@altavista.net for his work on the
# winioport module: www.geocities.com/dinceraydin/ the graphic below is
# borrowed form him ;-)


#    LPT1 = 0x0378 or 0x03BC
#    LPT2 = 0x0278 or 0x0378
#    LPT3 = 0x0278
#
#   Data Register (base + 0) ........ outputs
#
#     7 6 5 4 3 2 1 0
#     . . . . . . . *  D0 ........... (pin 2), 1=High, 0=Low (true)
#     . . . . . . * .  D1 ........... (pin 3), 1=High, 0=Low (true)
#     . . . . . * . .  D2 ........... (pin 4), 1=High, 0=Low (true)
#     . . . . * . . .  D3 ........... (pin 5), 1=High, 0=Low (true)
#     . . . * . . . .  D4 ........... (pin 6), 1=High, 0=Low (true)
#     . . * . . . . .  D5 ........... (pin 7), 1=High, 0=Low (true)
#     . * . . . . . .  D6 ........... (pin 8), 1=High, 0=Low (true)
#     * . . . . . . .  D7 ........... (pin 9), 1=High, 0=Low (true)
#
#   Status Register (base + 1) ...... inputs
#
#     7 6 5 4 3 2 1 0
#     . . . . . * * *  Undefined
#     . . . . * . . .  Error ........ (pin 15), high=1, low=0 (true)
#     . . . * . . . .  Selected ..... (pin 13), high=1, low=0 (true)
#     . . * . . . . .  No paper ..... (pin 12), high=1, low=0 (true)
#     . * . . . . . .  Ack .......... (pin 10), high=1, low=0 (true)
#     * . . . . . . .  Busy ......... (pin 11), high=0, low=1 (inverted)
#
#   ctrl Register (base + 2) ..... outputs
#
#     7 6 5 4 3 2 1 0
#     . . . . . . . *  Strobe ....... (pin 1),  1=low, 0=high (inverted)
#     . . . . . . * .  Auto Feed .... (pin 14), 1=low, 0=high (inverted)
#     . . . . . * . .  Initialize ... (pin 16), 1=high,0=low  (true)
#     . . . . * . . .  Select ....... (pin 17), 1=low, 0=high (inverted)
#     * * * * . . . .  Unused
import ctypes
import os
from . import IParallel

LPT1 = 0
LPT2 = 1

LPT1_base = 0x0378
LPT2_base = 0x0278

# need to patch PATH so that the DLL can be found and loaded
os.environ['PATH'] = os.environ['PATH'] + ';' + os.path.abspath(os.path.dirname(__file__))
try:
    inpout = ctypes.windll.inpoutx64
except:
    inpout = ctypes.windll.inpout32


class Parallel(IParallel):
    def __init__(self, port=LPT1):
        if port == LPT1:
            self.dataRegAdr = LPT1_base
        elif port == LPT2:
            self.dataRegAdr = LPT2_base
        else:
            self.dataRegAdr = port
        self.statusRegAdr = self.dataRegAdr + 1
        self.ctrlRegAdr = self.dataRegAdr + 2

    def set_data(self, value):
        inpout.Out32(self.dataRegAdr, value)

    def get_data(self):
        return inpout.Inp32(self.dataRegAdr)

    def set_data_dir(self, level):
        """set for port as input, clear for output"""
        ctrlReg = self.get_control()
        if level:
            ctrlReg |= 0x20
        else:
            ctrlReg &= ~0x20
        inpout.Out32(self.ctrlRegAdr, ctrlReg)

    def get_status(self):
        return inpout.Inp32(self.statusRegAdr)

    def set_control(self, value):
        inpout.Out32(self.ctrlRegAdr, value)

    def get_control(self):
        return inpout.Inp32(self.ctrlRegAdr)
