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

""" LCD1602 MicroPython LCD library

This library offers a convenient way to control a 16x2 HD44780-based Liquid Crystal
Display (LCD) from a MicroPython board. The following bus types are supported:

    * 4-bit bus (using the LCD pins) - `hd44780bus4`
    * 8-bit bus (using the LCD pins) - `hd44780bus8`
    * I2C bus - `hd44780busI2C`

The core class is `LCD1602`. This class provides high-level methods to perform
common LCD operations, such as writing text. For example, to write "Hello World!"
on the top left corner of the LCD, you can use the following code (it is assumed
the LCD is connected to board through a 4-bit bus):

    ```
    from lcd1602 import LCD1602
    lcd = LCD1602.begin_4bit(rs=2, e=3, db_7_to_4=[7, 6, 5, 4], rw=1)
    #lcd = LCD1602.begin_8bit(rs=2, e=3, db_7_to_0=[7, 6, 5, 4, 3, 2, 1, 0], rw=1)
    #lcd = LCD1602.begin_i2c(bus_id=1, scl=27, sda=26)
    lcd.write_text(0, 0, "Hello World!")
    ```

For more advanced scenarios requiring full control over the LCD, the `LCD1602`
class provides a `send_command` method that can be used to send native LCD commands
to the display:

    ```
    from lcd1602 import LCD1602, HD44780Cmds
    lcd = LCD1602.begin_4bit(rs=2, e=3, db_7_to_4=[7, 6, 5, 4], rw=1)
    #lcd = LCD1602.begin_8bit(rs=2, e=3, db_7_to_0=[7, 6, 5, 4, 3, 2, 1, 0], rw=1)
    #lcd = LCD1602.begin_i2c(bus_id=1, scl=27, sda=26)
    data = lcd.send_command(HD44780Cmds.C09_READ_BUSY_FLAG_AND_ADDR)
    print(bin(data))
    ```
"""

from lcd1602.lcdcursor import LCDCursor
from lcd1602.hd44780cmds import HD44780Cmds
from lcd1602.hd44780bus import HD44780Bus
from lcd1602.hd44780bus4 import HD44780Bus4
from lcd1602.hd44780bus8 import HD44780Bus8
from lcd1602.hd44780busI2C import HD44780BusI2C
from lcd1602.lcd1602 import LCD1602
