# This file is part of the LCD1602 MicroPython LCD library
# Copyright (C) 2023 Pascal Jobin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from lcd1602._helper import _Helper
from lcd1602.hd44780cmds import HD44780Cmds
from lcd1602.hd44780bus import HD44780Bus
from machine import Pin, I2C
import utime as time


class HD44780BusI2C(HD44780Bus):
    """Provides a 4-bit I2C bus implementation for the HD44780 controller

    This bus requires the following I2C adapter pins to be connected:

        * sdc
        * sda

    The I2C bus supports read operations and can control the backlight.
    """

    _BACKLIGHT = 0b1000
    _E = 0b0100
    _RW = 0b0010
    _RS = 0b0001
    _DB_7_to_4 = 0b11110000

    def __init__(self, bus_id: int, scl: int, sda: int, addr: int | None = None):
        """Initializes a new instance of the HD44780BusI2C class

        Args:
            id (int):  The I2C peripheral/bus id. For example, a pin I2C1 SCL is the clock pin for I2C bus 1.
            scl (int): The pin number of the scl pin.
            sda (int): The pin number of the sda pin.
            addr (int, optional): The I2C address of the LCD. When not specified, the LCD is expected to be the only device on the I2C bus. Defaults to None.

        Raises:
            TypeError: One of the arguments is of the wrong type.
            ValueError: One of the arguments is out of range.
        """
        _Helper.validate_integer_arg("bus_id", bus_id)
        _Helper.validate_integer_arg("scl", scl)
        _Helper.validate_integer_arg("sdc", sda)

        if addr is not None:
            _Helper.validate_integer_arg("addr", addr, min_value=0)

        super().__init__(width=4, can_read=True, can_control_backlight=True)

        self._i2c = I2C(bus_id, scl=Pin(scl), sda=Pin(sda))
        self._addr = addr
        self._is_backlight_on = True

    def init(self):
        # Scan the I2C bus for LCD device
        devices = self._i2c.scan()

        # If no device was found, something is wrong with the wiring.
        if len(devices) == 0:
            raise RuntimeError("LCD does not respond. Please check the wiring.")

        # If no address was specified, we expect the LCD to be the only device
        # on the bus. If multiple devices were found, we cannot determine which
        # one is the LCD.
        if self._addr is None:
            if len(devices) > 1:
                raise RuntimeError(
                    f"Multiple devices found on the I2C bus. "
                    + f"Please specify the LCD's address: "
                    + f"{', '.join('0x{:02X}'.format(d) for d in devices)}."
                )
            self._addr = devices[0]

        # If the specified address is not in the list of devices, the address
        # must be wrong.
        if self._addr not in devices:
            raise RuntimeError(f"LCD does not respond at address 0x{self._addr:02X}. Please check the address.")

        # See HD44780 datasheet, page 46, Table 24 for 4-bit initialization procedure.

        # 1. Wait for more than 40ms after VCC rises to 2.7V.
        #    As an abundance of caution, we wait 3x more.
        time.sleep_ms(150)

        # 2. The following instructions put the controller into 8-bit mode
        #    regardless of the current (unknown) mode. The bus length is contained
        #    in the high nibble of the command, so we don't care about the low nibble.
        self._write_nibble(0b0000110000, high_nibble=True)  # Function set (8-bit bus)
        time.sleep_ms(5)  # Wait for >4.1ms (5ms)
        self._write_nibble(0b0000110000, high_nibble=True)  # Function set (8-bit bus)
        time.sleep_ms(1)  # Wait for >100us (1ms)
        self._write_nibble(0b0000110000, high_nibble=True)  # Function set (8-bit bus)
        time.sleep_ms(1)  # Wait for >100us (1ms)

        # 3. We are guaranteed that the controller is in 8-bit mode now. We can
        #    switch to 4-bit mode. As the controller is in 8-bit mode, it expects
        #    a single write operation. The bus length is contained in the high
        #    nibble of the command, so we don't care about the low nibble.
        self._write_nibble(0b0000100000, high_nibble=True)  # Function set (4-bit bus)
        time.sleep_ms(1)  # Wait for >100us (1ms)

        # The controller is now in 4-bit mode. The rest of the initialization
        # procedure is performed by the LCD class.

    def read(self, cmd: int) -> int:
        _Helper.validate_integer_arg("cmd", cmd, min_value=0, max_value=0b1111111111)

        # Command is a write operation when RW is low / false
        # Command is a ***read*** operation when RW is high / true
        if not (cmd & HD44780Cmds.BITMASK_RW):
            raise ValueError("Not a read command.")

        data = self._read_nibble(cmd, high_nibble=True)
        data = data | self._read_nibble(cmd, high_nibble=False)

        return data

    def write(self, cmd: int):
        _Helper.validate_integer_arg("cmd", cmd, min_value=0, max_value=0b1111111111)

        # Command is a ***write*** operation when RW is low / false
        # Command is a read operation when RW is high / true
        if cmd & HD44780Cmds.BITMASK_RW:
            raise ValueError("Not a write command.")

        self._write_nibble(cmd, high_nibble=True)
        self._write_nibble(cmd, high_nibble=False)

    def set_backlight(self, enabled: bool):
        self._is_backlight_on = enabled
        self.write(0)

    def _read_nibble(self, cmd: int, high_nibble: bool) -> int:
        # See I2C Serial Interface 1602 LCD Module, page 3.
        # The PCF8574-based piggy-back board connects the LCD's DB4-DB7 pins to
        # the PCF8574's P4-P7 pins (using the LCD's 4-bit bus mode). The PCF8574's
        # P0-P3 pins are connected to the LCD's RS, RW, E and backlight pins.
        # This is how a command byte sent on the I2C bus looks like:
        #      db7 db6 db5 db4 backlight e rw rs
        # The backlight bit is a piggy-back board thing. When high, the board
        # turns the backlight ON. When low, the board turns the backlight OFF.

        if self._addr is None:
            raise RuntimeError("Bus has not been initialized. Please call init() first.")

        # fmt: off
        # 
        payload = (HD44780BusI2C._BACKLIGHT if self._is_backlight_on else 0)
        payload = payload | (HD44780BusI2C._RW if (cmd & HD44780Cmds.BITMASK_RW) else 0)
        payload = payload | (HD44780BusI2C._RS if (cmd & HD44780Cmds.BITMASK_RS) else 0)
        # fmt: on

        self._i2c.writeto(self._addr, bytearray([payload]))
        time.sleep_us(HD44780Bus.DELAYUS_TAS)

        # Set E high.
        # Additionally, set the PCF8574's P7 to P4 pins high (these pins are
        # connected to the 4-bit bus of the LCD, corresponding to pins db7 to
        # db4). The PCF8574's P-pins function as quasi-bidirectional I/Os and
        # lack a dedicated direction control register. To read a value from these
        # pins, they must first be set to a high state. When the connected LCD
        # pin is also high, the PCF8574 pin maintains its high state. Conversely,
        # when the LCD pin is low, it draws a minimal amount of current provided
        # by the PCF8574's pin, effectively pulling it low. For more information,
        # please refer to page 6 of the PCF8574 datasheet.
        payload = payload | HD44780BusI2C._E | HD44780BusI2C._DB_7_to_4
        self._i2c.writeto(self._addr, bytearray([payload]))
        time.sleep_us(HD44780Bus.DELAYUS_PWEH)

        # Read data pins while E is high and the controller is driving these pins.
        data = self._i2c.readfrom(self._addr, 1)[0] >> 4
        if high_nibble:
            data = data << 4

        # Set E low
        # Also set the PCF8574's P7 to P4 pins low.
        payload = payload & ~HD44780BusI2C._E & ~HD44780BusI2C._DB_7_to_4
        self._i2c.writeto(self._addr, bytearray([payload]))

        # Wait a full cycle. Half a cycle would be enough, but not all boards
        # support waiting nanoseconds or fractions of a unit.
        time.sleep_us(int(HD44780Bus.DELAYUS_TCYCE))

        return data

    def _write_nibble(self, cmd: int, high_nibble: bool):
        # See I2C Serial Interface 1602 LCD Module, page 3.
        # The PCF8574-based piggy-back board connects the LCD's DB4-DB7 pins to
        # the PCF8574's P4-P7 pins (using the LCD's 4-bit bus mode). The PCF8574's
        # P0-P3 pins are connected to the LCD's RS, RW, E and backlight pins.
        # This is how a command byte sent on the I2C bus looks like:
        #      db7 db6 db5 db4 backlight e rw rs
        # The backlight bit is a piggy-back board thing. When high, the board
        # turns the backlight ON. When low, the board turns the backlight OFF.

        if self._addr is None:
            raise RuntimeError("Bus has not been initialized. Please call init() first.")

        # fmt: off
        payload = (cmd & HD44780Cmds.BITMASK_DB7_TO_DB4) \
            if high_nibble else \
                ((cmd & HD44780Cmds.BITMASK_DB3_TO_DB0) << 4)
        payload = payload | (HD44780BusI2C._BACKLIGHT if self._is_backlight_on else 0)
        payload = payload | (HD44780BusI2C._RW if (cmd & HD44780Cmds.BITMASK_RW) else 0)
        payload = payload | (HD44780BusI2C._RS if (cmd & HD44780Cmds.BITMASK_RS) else 0)
        # fmt: on

        self._i2c.writeto(self._addr, bytearray([payload]))
        time.sleep_us(HD44780Bus.DELAYUS_TAS)

        # Set E high
        payload = payload | HD44780BusI2C._E
        self._i2c.writeto(self._addr, bytearray([payload]))
        time.sleep_us(HD44780Bus.DELAYUS_PWEH)

        # Set E low
        payload = payload & ~HD44780BusI2C._E
        self._i2c.writeto(self._addr, bytearray([payload]))

        # Wait a full cycle. Half a cycle would be enough, but not all boards
        # support waiting nanoseconds or fractions of a unit.
        time.sleep_us(int(HD44780Bus.DELAYUS_TCYCE))
