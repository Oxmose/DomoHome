# Copyright (c) 2016 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from __future__ import division
import logging
import time
import math


# Registers/etc:
PCA9685_ADDRESS    = 0x40
MODE1              = 0x00
MODE2              = 0x01
SUBADR1            = 0x02
SUBADR2            = 0x03
SUBADR3            = 0x04
PRESCALE           = 0xFE
LED0_ON_L          = 0x06
LED0_ON_H          = 0x07
LED0_OFF_L         = 0x08
LED0_OFF_H         = 0x09
ALL_LED_ON_L       = 0xFA
ALL_LED_ON_H       = 0xFB
ALL_LED_OFF_L      = 0xFC
ALL_LED_OFF_H      = 0xFD

# Bits:
RESTART            = 0x80
SLEEP              = 0x10
ALLCALL            = 0x01
INVRT              = 0x10
OUTDRV             = 0x04


logger = logging.getLogger(__name__)


def software_reset(i2c=None, **kwargs):
    """Sends a software reset (SWRST) command to all servo drivers on the bus."""
    # Setup I2C interface for device 0x00 to talk to all of them.
    if i2c is None:
        from OmegaExpansion import onionI2C
        self.i2c = onionI2C.OnionI2C()
    self.i2c.writeByte(0x06, 0)  # SWRST


class PCA9685(object):
    """PCA9685 PWM LED/servo controller."""

    def __init__(self, address=PCA9685_ADDRESS, i2c=None, **kwargs):
        """Initialize the PCA9685."""
        self.address = address
        # Setup I2C interface for the device.
        if i2c is None:
            from OmegaExpansion import onionI2C
            self.i2c = onionI2C.OnionI2C()
        self.set_all_pwm(0, 0)
        self.i2c.writeByte(self.address, MODE2, OUTDRV)
        self.i2c.writeByte(self.address, MODE1, ALLCALL)
        time.sleep(0.005)  # wait for oscillator
        mode1 = self.i2c.readBytes(self.address, MODE1, 1)[0]
        mode1 = mode1 & ~SLEEP  # wake up (reset sleep)
        self.i2c.writeByte(self.address, MODE1, mode1)
        time.sleep(0.005)  # wait for oscillator

    def set_pwm_freq(self, freq_hz):
        """Set the PWM frequency to the provided value in hertz."""
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq_hz)
        prescaleval -= 1.0
        logger.debug('Setting PWM frequency to {0} Hz'.format(freq_hz))
        logger.debug('Estimated pre-scale: {0}'.format(prescaleval))
        prescale = int(math.floor(prescaleval + 0.5))
        logger.debug('Final pre-scale: {0}'.format(prescale))
        oldmode = self.i2c.readBytes(self.address, MODE1, 1)[0];
        newmode = (oldmode & 0x7F) | 0x10    # sleep
        self.i2c.writeByte(self.address, MODE1, newmode)  # go to sleep
        self.i2c.writeByte(self.address, PRESCALE, prescale)
        self.i2c.writeByte(self.address, MODE1, oldmode)
        time.sleep(0.005)
        self.i2c.writeByte(self.address, MODE1, oldmode | 0x80)

    def set_pwm(self, channel, on, off):
        """Sets a single PWM channel."""
        self.i2c.writeByte(self.address, LED0_ON_L+4*channel, int(on) & 0xFF)
        self.i2c.writeByte(self.address, LED0_ON_H+4*channel, int(on) >> 8)
        self.i2c.writeByte(self.address, LED0_OFF_L+4*channel, int(off) & 0xFF)
        self.i2c.writeByte(self.address, LED0_OFF_H+4*channel, int(off) >> 8)

    def set_all_pwm(self, on, off):
        """Sets all PWM channels."""
        self.i2c.writeByte(self.address, ALL_LED_ON_L, int(on) & 0xFF)
        self.i2c.writeByte(self.address, ALL_LED_ON_H, int(on) >> 8)
        self.i2c.writeByte(self.address, ALL_LED_OFF_L, int(off) & 0xFF)
        self.i2c.writeByte(self.address, ALL_LED_OFF_H, int(off) >> 8)