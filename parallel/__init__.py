# portable parallel port access with python
# this is a wrapper module for different platform implementations
#
# (C)2001-2002 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause

import sys

class IParallel(object):
    STROBE = 0x01
    LINEFEED = 0x02
    RESET = 0x04
    SELECT_PRINTER = 0x08

    ERROR = 0x08
    SELECT = 0x10
    PAPER_OUT = 0x20
    ACK = 0x40
    BUSY = 0x80

    def set_bit(self, pin, b):
        if pin < 1:
            raise IndexError
        if pin == 1:
            reg = self.get_control() & ~self.STROBE
            if not b:
                reg |= self.STROBE
            self.set_control(reg)
        elif pin <= 9:
            pin -= 2
            reg = self.get_data() & ~(1 << pin)
            if b:
                reg |= 1 << pin
            self.set_data(reg)
        elif pin == 14:
            reg = self.get_control() & ~self.LINEFEED
            if not b:
                reg |= self.LINEFEED
            self.set_control(reg)
        elif pin == 16:
            reg = self.get_control() & ~self.RESET
            if b:
                reg |= self.RESET
            self.set_control(reg)
        elif pin == 17:
            reg = self.get_control() & ~self.SELECT_PRINTER
            if not b:
                reg |= self.SELECT_PRINTER
            self.set_control(reg)
        else:
            raise IndexError

    def get_bit(self, pin):
        if pin < 1:
            raise IndexError
        if pin == 1:
            reg = self.get_control() & self.STROBE
            return not reg
        if pin <= 9:
            pin -= 2
            reg = self.get_data() & (1 << pin)
            return bool(reg)
        if pin == 10:
            reg = self.get_status() & self.ACK
            return bool(reg)
        if pin == 11:
            reg = self.get_status() & self.BUSY
            return not reg
        if pin == 12:
            reg = self.get_status() & self.PAPER_OUT
            return bool(reg)
        if pin == 13:
            reg = self.get_status() & self.SELECT
            return bool(reg)
        if pin == 14:
            reg = self.get_control() & self.LINEFEED
            return not reg
        if pin == 15:
            reg = self.get_status() & self.ERROR
            return bool(reg)
        if pin == 16:
            reg = self.get_control() & self.RESET
            return bool(reg)
        if pin == 17:
            reg = self.get_control() & self.SELECT_PRINTER
            return not reg
        raise IndexError

# choose an implementation, depending on os
if sys.platform == 'win32':
    from parallel.parallelwin32 import Parallel  # noqa
elif sys.platform.startswith('linux'):
    from parallel.parallelppdev import Parallel  # noqa
elif sys.platform.startswith('freebsd'):
    from parallel.parallelppi import Parallel  # noqa
else:
    raise "Sorry no implementation for your platform available."
