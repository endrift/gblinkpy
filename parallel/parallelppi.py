#!/usr/bin/env python
# parallel port access using the ppi driver

import sys
import struct
import fcntl
import os

from . import IParallel

def sizeof(type):
    return struct.calcsize(type)

def _IOC(inout, group, num, len):
    return int(((inout) | (((len) & IOCPARM_MASK) << 16) | ((group) << 8) | (num)))

def _IO(group, num):
    return _IOC(_IOC_VOID, group, num, 0)

def _IOR(group, num, size):
    return _IOC(_IOC_OUT, group, num, sizeof(size))

def _IOW(group, num, size):
    return _IOC(_IOC_IN, group, num, sizeof(size))

IOCPARM_SHIFT = 13
IOCPARM_MASK = ((1 << IOCPARM_SHIFT) - 1)

_IOC_VOID = 0x20000000
_IOC_OUT = 0x40000000
_IOC_IN = 0x80000000
_IOC_INOUT = (_IOC_IN|_IOC_OUT)

PP_IOCTL = ord('P')

PPIGDATA   =    _IOR(PP_IOCTL, 10, 'B')
PPIGSTATUS =    _IOR(PP_IOCTL, 11, 'B')
PPIGCTRL   =    _IOR(PP_IOCTL, 12, 'B')
PPIGEPPD   =    _IOR(PP_IOCTL, 13, 'B')
PPIGECR    =    _IOR(PP_IOCTL, 14, 'B')
PPIGFIFO   =    _IOR(PP_IOCTL, 15, 'B')

PPISDATA   =    _IOW(PP_IOCTL, 16, 'B')
PPISSTATUS =    _IOW(PP_IOCTL, 17, 'B')
PPISCTRL   =    _IOW(PP_IOCTL, 18, 'B')
PPISEPPD   =    _IOW(PP_IOCTL, 19, 'B')
PPISECR    =    _IOW(PP_IOCTL, 20, 'B')
PPISFIFO   =    _IOW(PP_IOCTL, 21, 'B')

PPIGEPPA   =    _IOR(PP_IOCTL, 22, 'B')
PPISEPPA   =    _IOR(PP_IOCTL, 23, 'B')


class Parallel(IParallel):
    def __init__(self, port=0):
        if isinstance(port, int):
            self.device = "/dev/ppi%d" % port
        else:
            self.device = port
        self._fd = None
        self._fd = os.open(self.device, os.O_RDWR)
        try:
            self.set_data(0)
        except IOError:
            os.close(self._fd)
            self._fd = None
            raise

    def __del__(self):
        if self._fd is not None:
            os.close(self._fd)

    def set_control(self, lines):
        fcntl.ioctl(self._fd, PPISCTRL, struct.pack('B', lines))

    def get_control(self):
        ret = struct.pack('B', 0)
        ret = fcntl.ioctl(self._fd, PPIGCTRL, ret)
        return struct.unpack('B', ret)[0]

    def get_status(self):
        ret = struct.pack('B', 0)
        ret = fcntl.ioctl(self._fd, PPIGSTATUS, ret)
        return struct.unpack('B', ret)[0]

    def set_data(self, byte):
        fcntl.ioctl(self._fd, PPISDATA, struct.pack('B', byte))

    def get_data(self):
        ret = struct.pack('B', 0)
        ret = fcntl.ioctl(self._fd, PPIGDATA, ret)
        return struct.unpack('B', ret)[0]
