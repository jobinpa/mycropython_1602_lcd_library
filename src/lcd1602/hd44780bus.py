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
from machine import Pin
import utime as time


class HD44780Bus:
    """Provides a base abstract implementation of a bus for the HD44780 controller

    This class needs to be inherited and the following methods need to be implemented:
        * init()
        * write(command: int)
        * read(command: int) -> int
    These base implementation of these methods raise a `NotImplementedError`.
    """

    # ######################################################################## #
    # BUS DELAYS
    # See HD44780 datasheet, page 49
    # See HD44780 datasheet, page 58, figures 25 and 26
    # ######################################################################## #

    DELAYUS_TAS = 1
    """Address set-up time delay (tAS) in microseconds
    
    The Address Set-Up Time delay is the minimum amount of time required for
    the address signal to be stable before the read or write operation is
    initiated.
    
    Minimum:   60ns
    Current: 1000ns / 1us
    """

    DELAYUS_PWEH = 1
    """Enable pulse width (high) (PWEH) in microseconds
    
    The Enable pulse width time delay is the minimum amount of time the E pin
    must remain high.
    
    Minimum:  450ns
    Current: 1000ns / 1us
    
    The 1us delay covers the following:
        * The Enable pulse width time delay (PWEH) of at least 450ns.
        * During READ operations, the Data Delay Time (tDDR) of at most 360ns.
        * During WRITE operations, the Data Setup Time (tDSW) of at least 195ns.
    """

    DELAYUS_TCYCE = 1
    """Enable Cycle Time (tcycE) in microseconds
    
    This is the minimum time between raising edges of E
    
    Minimum: 1000ns / 1us
    Current: 1000ns / 1us
    
    Based on the timing diagram, we should wait half a cycle after setting E
    low before we are allowed to set it high again. This delay would also cover
    the 4ns delay required for the controller to update the address counter
    after a read or write operation (see HD44780 datasheet, page 25, Table 6
    and figure 10). However, as not all boards support waiting nanoseconds, we
    wait a full cycle of 1 microsecond.
    """

    def __init__(self, width: int, can_read: bool, can_control_backlight: bool):
        """Initializes a new instance of the HD44780Bus class

        Args:
            width (int): The bus width in bits.
            can_read (bool): True if the bus supports read operations, False otherwise.
            can_control_backlight (bool): True if the bus can control the backlight, False otherwise.

        Raises:
            TypeError: One of the arguments is of the wrong type.
            ValueError: One of the arguments is out of range.
        """
        _Helper.validate_integer_arg("width", width, allowed_values=[4, 8])
        _Helper.validate_boolean_arg("can_read", can_read)
        _Helper.validate_boolean_arg("can_control_backlight", can_control_backlight)

        self.width = width
        """The bus width in bits. Valid values are 4 and 8."""

        self.can_read = can_read
        """True if the bus supports read operations, False otherwise."""

        self.can_control_backlight = can_control_backlight
        """True if the bus can control the backlight, False otherwise."""

    def init(self):
        """Intializes the bus

        This method is called from within the LCD initialization routine. It is
        not necessary to call this method manually.
        """
        raise NotImplementedError()

    def write(self, cmd: int):
        """Sends a write operation the the LCD

        Args:
            cmd (int): The command as a 10-bit unsigned integer.

        Raises:
            TypeError: One of the arguments is of the wrong type.
            ValueError: One of the arguments is out of range --OR-- the command is not a write command.
        """
        raise NotImplementedError()

    def read(self, cmd: int) -> int:
        """Sends a read operation to the LCD

        Args:
            cmd (int): The command as a 10-bit unsigned integer.

        Returns:
            int: The result of the command as a 8-bit unsigned integer.

        Raises:
            TypeError: One of the arguments is of the wrong type.
            ValueError: One of the arguments is out of range --OR-- the command is not a read command.
            RuntimeError: Read operations are not supported as no RW pin was provided.
        """
        raise NotImplementedError()

    def set_backlight(self, enabled: bool):
        """Turns the LCD backlight ON or OFF

        Args:
            enabled (bool): True to turn the backlight ON, False to turn it OFF.

        Raises:
            TypeError: One of the arguments is of the wrong type.
            RuntimeError: The bus does not support controlling the backlight.
        """
        raise NotImplementedError()
