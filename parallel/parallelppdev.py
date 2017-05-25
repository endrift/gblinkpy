#!/usr/bin/env python
# parallel port access using the ppdev driver

import sys
import struct
import fcntl
import os

from . import IParallel

# Generated by h2py 0.1.1 from <linux/ppdev.h>,
# then cleaned up a bit by Michael P. Ashton and then a gain by chris ;-)
# Changes for Python2.2 support (c) September 2004 Alex.Perry@qm.com


def sizeof(type):
    return struct.calcsize(type)


def _IOC(dir, type, nr, size):
    return int((dir << _IOC_DIRSHIFT) | (type << _IOC_TYPESHIFT) |
               (nr << _IOC_NRSHIFT) | (size << _IOC_SIZESHIFT))


def _IO(type, nr):
    return _IOC(_IOC_NONE, type, nr, 0)


def _IOR(type, nr, size):
    return _IOC(_IOC_READ, type, nr, sizeof(size))


def _IOW(type, nr, size):
    return _IOC(_IOC_WRITE, type, nr, sizeof(size))

_IOC_SIZEBITS = 14
_IOC_SIZEMASK = (1 << _IOC_SIZEBITS) - 1
_IOC_NRSHIFT = 0
_IOC_NRBITS = 8
_IOC_TYPESHIFT = _IOC_NRSHIFT + _IOC_NRBITS
_IOC_TYPEBITS = 8
_IOC_SIZESHIFT = _IOC_TYPESHIFT + _IOC_TYPEBITS
IOCSIZE_MASK = _IOC_SIZEMASK << _IOC_SIZESHIFT
IOCSIZE_SHIFT = _IOC_SIZESHIFT

# Python 2.2 uses a signed int for the ioctl() call, so ...
if sys.version_info[0] < 3 or sys.version_info[1] < 3:
    _IOC_WRITE = 1
    _IOC_READ = -2
    _IOC_INOUT = -1
else:
    _IOC_WRITE = 1
    _IOC_READ = 2
    _IOC_INOUT = 3

_IOC_DIRSHIFT = _IOC_SIZESHIFT + _IOC_SIZEBITS
IOC_INOUT = _IOC_INOUT << _IOC_DIRSHIFT
IOC_IN = _IOC_WRITE << _IOC_DIRSHIFT
IOC_OUT = _IOC_READ << _IOC_DIRSHIFT

_IOC_NONE = 0
PP_IOCTL = ord('p')
PPCLAIM = _IO(PP_IOCTL,  0x8b)
PPCLRIRQ = _IOR(PP_IOCTL, 0x93, 'i')

PPDATADIR = _IOW(PP_IOCTL, 0x90, 'i')
PPEXCL = _IO(PP_IOCTL,  0x8f)
PPFCONTROL = _IOW(PP_IOCTL, 0x8e, 'BB')
PPGETFLAGS = _IOR(PP_IOCTL, 0x9a, 'i')
PPGETMODE = _IOR(PP_IOCTL, 0x98, 'i')
PPGETMODES = _IOR(PP_IOCTL, 0x97, 'I')
PPGETPHASE = _IOR(PP_IOCTL, 0x99, 'i')
PPGETTIME = _IOR(PP_IOCTL, 0x95, 'll')
PPNEGOT = _IOW(PP_IOCTL, 0x91, 'i')
PPRCONTROL = _IOR(PP_IOCTL, 0x83, 'B')
PPRDATA = _IOR(PP_IOCTL, 0x85, 'B')
# 'OBSOLETE__IOR' undefined in 'PPRECONTROL'
PPRELEASE = _IO(PP_IOCTL,  0x8c)
# 'OBSOLETE__IOR' undefined in 'PPRFIFO'
PPRSTATUS = _IOR(PP_IOCTL, 0x81, 'B')
PPSETFLAGS = _IOW(PP_IOCTL, 0x9b, 'i')
PPSETMODE = _IOW(PP_IOCTL, 0x80, 'i')
PPSETPHASE = _IOW(PP_IOCTL, 0x94, 'i')
PPSETTIME = _IOW(PP_IOCTL, 0x96, 'll')
PPWCONTROL = _IOW(PP_IOCTL, 0x84, 'B')
PPWCTLONIRQ = _IOW(PP_IOCTL, 0x92, 'B')
PPWDATA = _IOW(PP_IOCTL, 0x86, 'B')
# 'OBSOLETE__IOW' undefined in 'PPWECONTROL'
# 'OBSOLETE__IOW' undefined in 'PPWFIFO'
# 'OBSOLETE__IOW' undefined in 'PPWSTATUS'
PPYIELD = _IO(PP_IOCTL, 0x8d)
PP_FASTREAD = 1 << 3
PP_FASTWRITE = 1 << 2
PP_W91284PIC = 1 << 4
PP_FLAGMASK = PP_FASTWRITE | PP_FASTREAD | PP_W91284PIC
PP_MAJOR = 99
_ASMI386_IOCTL_H = None
_IOC_DIRBITS = 2
_IOC_DIRMASK = (1 << _IOC_DIRBITS) - 1
_IOC_NRMASK = (1 << _IOC_NRBITS) - 1
_IOC_TYPEMASK = (1 << _IOC_TYPEBITS) - 1


def _IOC_DIR(nr):
    return (nr >> _IOC_DIRSHIFT) & _IOC_DIRMASK


def _IOC_NR(nr):
    return (nr >> _IOC_NRSHIFT) & _IOC_NRMASK


def _IOC_SIZE(nr):
    return (nr >> _IOC_SIZESHIFT) & _IOC_SIZEMASK


def _IOC_TYPE(nr):
    return (nr >> _IOC_TYPESHIFT) & _IOC_TYPEMASK


def _IOWR(type, nr, size):
    return _IOC(_IOC_READ | _IOC_WRITE, type, nr, sizeof(size))

# Constants from <linux/parport.h>

PARPORT_CONTROL_STROBE = 0x1
PARPORT_CONTROL_AUTOFD = 0x2
PARPORT_CONTROL_INIT = 0x4
PARPORT_CONTROL_SELECT = 0x8
PARPORT_STATUS_ERROR = 8
PARPORT_STATUS_SELECT = 0x10
PARPORT_STATUS_PAPEROUT = 0x20
PARPORT_STATUS_ACK = 0x40
PARPORT_STATUS_BUSY = 0x80

IEEE1284_MODE_NIBBLE = 0
IEEE1284_MODE_BYTE = 1
IEEE1284_MODE_COMPAT = 1 << 8
IEEE1284_MODE_BECP = 1 << 9
IEEE1284_MODE_ECP = 1 << 4
IEEE1284_MODE_ECPRLE = IEEE1284_MODE_ECP | (1 << 5)
IEEE1284_MODE_ECPSWE = 1 << 10
IEEE1284_MODE_EPP = 1 << 6
IEEE1284_MODE_EPPSL = 1 << 11
IEEE1284_MODE_EPPSWE = 1 << 12
IEEE1284_DEVICEID = 1 << 2
IEEE1284_EXT_LINK = 1 << 14

IEEE1284_ADDR = 1 << 13
IEEE1284_DATA = 0

PARPORT_EPP_FAST = 1
PARPORT_W91284PIC = 2


class Parallel(IParallel):
    """Class for controlling the pins on a parallel port

    This class provides bit-level access to the pins on a PC parallel
    port.  It is primarily designed for programs which must control
    special circuitry - most often non-IEEE-1284-compliant devices
    other than printers - using 'bit-banging' techniques.

    The current implementation makes ioctl() calls to the Linux ppdev
    driver, using the Python fcntl library.  It might be rewritten in
    C for extra speed.  This particular implementation is written for
    Linux; all of the upper-level calls can be ported to Windows as
    well.

    On Linux, the ppdev device driver, from the Linux 2.4 parallel
    port subsystem, is used to control the parallel port hardware.
    This driver must be made available from a kernel compile.  The
    option is called "Support user-space parallel-port drivers".  When
    using the module, be sure to unload the lp module first: usually
    the lp module claims exclusive access to the parallel port, and if
    it is loaded, this class will fail to open the parallel port file,
    and throw an exception.

    The primary source of information about the Linux 2.4 parallel
    port subsystem is Tim Waugh's documentation, the source for which
    is available in the kernel tree.  This document (called,
    appropriately enough, "The Linux 2.4 Parallel Port Subsystem"),
    thoroughly describes the parallel port drivers and how to use
    them.

    This class provides a method for each of the ioctls supported by
    the ppdev module.  The ioctl methods are named, in uppercase, the
    same as the ioctls they invoke.  The documentation for these
    methods was taken directly from the documentation for their
    corresponding ioctl, and modified only where necessary.

    Unless you have special reason to use the Linux ioctls, you should
    use instead the upper-level functions, which are named in
    lowerCase fashion and should be portable between Linux and
    Windows.  This way, any code you write for this class will (or
    should) also work with the Windows version of this class.

    """
    def __init__(self, port=0):
        if isinstance(port, int):
            self.device = "/dev/parport%d" % port
        else:
            self.device = port
        self._fd = None
        self._fd = os.open(self.device, os.O_RDWR)
        try:
            self.PPEXCL()
            self.PPCLAIM()
            self.set_data_dir(1)
            self.set_data(0)
        except IOError:
            os.close(self._fd)
            self._fd = None
            raise

    def __del__(self):
        if self._fd is not None:
            self.PPRELEASE()
            os.close(self._fd)

    def PPCLAIM(self):
        """
        Claims access to the port. As a user-land device driver
        writer, you will need to do this before you are able to
        actually change the state of the parallel port in any
        way. Note that some operations only affect the ppdev driver
        and not the port, such as PPSETMODE; they can be performed
        while access to the port is not claimed.
        """
        fcntl.ioctl(self._fd, PPCLAIM)

    def PPEXCL(self):
        """
        Instructs the kernel driver to forbid any sharing of the port
        with other drivers, i.e. it requests exclusivity. The PPEXCL
        command is only valid when the port is not already claimed for
        use, and it may mean that the next PPCLAIM ioctl will fail:
        some other driver may already have registered itself on that
        port.

        Most device drivers don't need exclusive access to the
        port. It's only provided in case it is really needed, for
        example for devices where access to the port is required for
        extensive periods of time (many seconds).

        Note that the PPEXCL ioctl doesn't actually claim the port
        there and then---action is deferred until the PPCLAIM ioctl is
        performed.
        """
        fcntl.ioctl(self._fd, PPEXCL)

    def PPRELEASE(self):
        """
        Releases the port. Releasing the port undoes the effect of
        claiming the port. It allows other device drivers to talk to
        their devices (assuming that there are any).
        """
        fcntl.ioctl(self._fd, PPRELEASE)

    def PPDATADIR(self, out):
        """
        Controls the data line drivers. Normally the computer's
        parallel port will drive the data lines, but for byte-wide
        transfers from the peripheral to the host it is useful to turn
        off those drivers and let the peripheral drive the
        signals. (If the drivers on the computer's parallel port are
        left on when this happens, the port might be damaged.)
        This is only needed in conjunction with PPWDATA or PPRDATA.
        The 'out' parameter indicates the desired port direction.  If
        'out' is true or non-zero, the drivers are turned on (forward
        direction); otherwise, the drivers are turned off (reverse
        direction).
        """
        if out:
            msg = struct.pack('i', 0)
        else:
            msg = struct.pack('i', 1)
        fcntl.ioctl(self._fd, PPDATADIR, msg)

    def set_data_dir(self, out):
        """Activates or deactivates the data bus line drivers (pins 2-9)"""
        self._dataDir = out
        self.PPDATADIR(out)

    def set_control(self, lines):
        fcntl.ioctl(self._fd, PPWCONTROL, struct.pack('B', lines))

    def get_control(self):
        ret = struct.pack('B', 0)
        ret = fcntl.ioctl(self._fd, PPRCONTROL, ret)
        return struct.unpack('B', ret)[0]

    def get_status(self):
        ret = struct.pack('B', 0)
        ret = fcntl.ioctl(self._fd, PPRSTATUS, ret)
        return struct.unpack('B', ret)[0]

    def set_data(self, byte):
        fcntl.ioctl(self._fd, PPWDATA, struct.pack('B', byte))

    def get_data(self):
        ret = struct.pack('B', 0)
        ret = fcntl.ioctl(self._fd, PPRDATA, ret)
        return struct.unpack('B', ret)[0]
