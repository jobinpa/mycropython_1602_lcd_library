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
from lcd1602._datapin import _DataPin
from lcd1602.hd44780cmds import HD44780Cmds
from lcd1602.hd44780bus import HD44780Bus
from machine import Pin
import utime as time


class HD44780Bus8(HD44780Bus):
    """Provides a 8-bit bus implementation for the HD44780 controller

    This bus requires the following LCD pins to be connected:

        * RS
        * E
        * DB7 to DB0

    Pin RW is optional however, read operations are supported only when this pin
    is provided. RW MUST be connected to ground if it is not provided so the
    controller is always in write mode.

    Pin BL (backlight control) is optional. When provided, it is assumed to be
    connected to some circuitry that controls the backlight. This circuitry
    should turn the backlight ON when the pin is HIGH and OFF when the pin is LOW.
    """

    def __init__(self, rs: int, e: int, db_7_to_0: list[int], rw: int | None = None, bl: int | None = None):
        """Initializes a new instance of the HD44780Bus8 class

        Args:
            rs (int): The pin number of the RS pin.
            e (int): The pin number of the E pin.
            db_7_to_0 (list[int]): The pin numbers of the DB7 to DB0 pins.
            rw (int, optional): The pin number of the RW pin. Defaults to None.
            bl (int, optional): The pin number of the BL (backlight control) pin. Defaults to None.

        Raises:
            TypeError: One of the arguments is of the wrong type.
            ValueError: One of the arguments is out of range.
        """
        _Helper.validate_integer_arg("rs", rs)
        _Helper.validate_integer_arg("e", e)
        _Helper.validate_integer_list_arg("db_7_to_0", db_7_to_0, length=8)

        if rw is not None:
            _Helper.validate_integer_arg("rw", rw)

        if bl is not None:
            _Helper.validate_integer_arg("bl", bl)

        super().__init__(width=8, can_read=rw is not None, can_control_backlight=bl is not None)

        self._e_pin = Pin(e, value=0, mode=Pin.OUT)
        self._rs_pin = Pin(rs, value=0, mode=Pin.OUT)
        self._rw_pin = None if rw is None else Pin(rw, value=0, mode=Pin.OUT)
        self._bl_pin = None if bl is None else Pin(bl, value=0, mode=Pin.OUT)
        self._data_pins = [_DataPin(pin) for pin in db_7_to_0]

    def init(self):
        # See HD44780 datasheet, page 44, Table 23 for 8-bit initialization procedure.

        # 1. Wait for more than 40ms after VCC rises to 2.7V.
        #    As an abundance of caution, we wait 3x more.
        time.sleep_ms(150)

        # 2. The following instructions put the controller into 8-bit mode
        #    regardless of the current (unknown) mode.
        self.write(0b0000110000)  # Function set (8-bit bus)
        time.sleep_ms(5)  # Wait for >4.1ms (5ms)
        self.write(0b0000110000)  # Function set (8-bit bus)
        time.sleep_ms(1)  # Wait for >100us (1ms)
        self.write(0b0000110000)  # Function set (8-bit bus)
        time.sleep_ms(1)  # Wait for >100us (1ms)

        # The controller is now in 8-bit mode. The rest of the initialization
        # procedure is performed by the LCD class.

    def write(self, cmd: int):
        _Helper.validate_integer_arg("cmd", cmd, min_value=0, max_value=0b1111111111)

        # Command is a ***write*** operation when RW is low / false
        # Command is a read operation when RW is high / true
        if cmd & HD44780Cmds.BITMASK_RW:
            raise ValueError("Not a write command.")

        # Set command pins
        self._rs_pin.value(cmd & HD44780Cmds.BITMASK_RS)

        if self._rw_pin is not None:
            self._rw_pin.value(cmd & HD44780Cmds.BITMASK_RW)

        self._data_pins[0].value(cmd & HD44780Cmds.BITMASK_DB7)
        self._data_pins[1].value(cmd & HD44780Cmds.BITMASK_DB6)
        self._data_pins[2].value(cmd & HD44780Cmds.BITMASK_DB5)
        self._data_pins[3].value(cmd & HD44780Cmds.BITMASK_DB4)
        self._data_pins[4].value(cmd & HD44780Cmds.BITMASK_DB3)
        self._data_pins[5].value(cmd & HD44780Cmds.BITMASK_DB2)
        self._data_pins[6].value(cmd & HD44780Cmds.BITMASK_DB1)
        self._data_pins[7].value(cmd & HD44780Cmds.BITMASK_DB0)

        time.sleep_us(HD44780Bus.DELAYUS_TAS)

        # Set E high
        self._e_pin.on()
        time.sleep_us(HD44780Bus.DELAYUS_PWEH)

        # Set E low
        self._e_pin.off()

        # Wait a full cycle. Half a cycle would be enough, but not all boards
        # support waiting nanoseconds or fractions of a unit.
        time.sleep_us(int(HD44780Bus.DELAYUS_TCYCE))

    def read(self, cmd: int) -> int:
        _Helper.validate_integer_arg("cmd", cmd, min_value=0, max_value=0b1111111111)

        # Command is a write operation when RW is low / false
        # Command is a ***read*** operation when RW is high / true
        if not (cmd & HD44780Cmds.BITMASK_RW):
            raise ValueError("Not a read command.")

        if self._rw_pin is None:
            raise RuntimeError("Read commands are not supported as no RW pin was provided (bus is write-only).")

        # Set data pins to input mode
        for pin in self._data_pins:
            pin.mode(Pin.IN)

        # Set command pins
        self._rs_pin.value(cmd & HD44780Cmds.BITMASK_RS)

        if self._rw_pin is not None:
            self._rw_pin.value(cmd & HD44780Cmds.BITMASK_RW)

        time.sleep_us(HD44780Bus.DELAYUS_TAS)

        # Set E high
        self._e_pin.on()
        time.sleep_us(HD44780Bus.DELAYUS_PWEH)

        # Read data pins while E is high and the controller is driving these pins.
        data = 0
        data = data | self._data_pins[0].value() << 7
        data = data | self._data_pins[1].value() << 6
        data = data | self._data_pins[2].value() << 5
        data = data | self._data_pins[3].value() << 4
        data = data | self._data_pins[4].value() << 3
        data = data | self._data_pins[5].value() << 2
        data = data | self._data_pins[6].value() << 1
        data = data | self._data_pins[7].value() << 0

        # Set E low
        self._e_pin.off()

        # Wait a full cycle. Half a cycle would be enough, but not all boards
        # support waiting nanoseconds or fractions of a unit.
        time.sleep_us(int(HD44780Bus.DELAYUS_TCYCE))

        # Set data pins back to output mode
        for pin in self._data_pins:
            pin.mode(Pin.OUT)

        return data

    def set_backlight(self, enabled: bool):
        if self._bl_pin is None:
            raise RuntimeError("Backlight control is not available as no BL pin was provided.")
        self._bl_pin.value(enabled)
