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


class HD44780Cmds:
    """HD44780 commands

    Provides commands supported by the HD44780 controller. Each command is supplied
    with his arguments (when available).

    A command is expressed as a 10-bit unsigned integer:

        `RS RW DB7 DB6 DB5 DB4 DB3 DB2 DB1 DB0`

    To construct a command, use the bitwise `OR` operator (|) as follows:

        ```
        cmd = CXX_COMMAND | CXX_ARG1 | CXX_ARG2 | CXX_ARG3
        ```

    Please refer to the HD44780 datasheet page 24, Table 6, for more details about
    HD44780 commands.
    """

    # ######################################################################## #
    # COMMAND BIT MASKS
    #
    # These masks are used to extract specific bits from a command.
    # ######################################################################## #
    BITMASK_DB0 = 0b0000000001
    BITMASK_DB1 = 0b0000000010
    BITMASK_DB2 = 0b0000000100
    BITMASK_DB3 = 0b0000001000
    BITMASK_DB4 = 0b0000010000
    BITMASK_DB5 = 0b0000100000
    BITMASK_DB6 = 0b0001000000
    BITMASK_DB7 = 0b0010000000
    BITMASK_RW = 0b0100000000
    BITMASK_RS = 0b1000000000
    BITMASK_DB7_TO_DB4 = 0b0011110000
    BITMASK_DB3_TO_DB0 = 0b0000001111

    # ######################################################################## #
    # COMMANDS
    #
    # See HD44780 datasheet, page 24-25 Table 6, for more details about commands.
    # ######################################################################## #

    # Clear display
    C01_CLEAR = 0b0000000001

    # Return home
    C02_HOME = 0b0000000010

    # Entry mode set
    C03_ENTRY_MODE_SET = 0b0000000100
    C03_ARG_RIGHT_TO_LEFT = 0b0000000000
    C03_ARG_LEFT_TO_RIGHT = 0b0000000010
    C03_ARG_AUTOSCROLL_OFF = 0b0000000000
    C03_ARG_AUTOSCROLL_ON = 0b0000000001

    # Display on/off control
    C04_DISPLAY_CONTROL = 0b0000001000
    C04_ARG_DISPLAY_OFF = 0b0000000000
    C04_ARG_DISPLAY_ON = 0b0000000100
    C04_ARG_CURSOR_OFF = 0b0000000000
    C04_ARG_CURSOR_ON = 0b0000000010
    C04_ARG_CURSOR_BLINK_OFF = 0b0000000000
    C04_ARG_CURSOR_BLINK_ON = 0b0000000001

    # Cursor of display shift
    C05_CMD_SHIFT = 0b0000010000
    C05_ARG_CURSOR = 0b0000000000
    C05_ARG_CONTENT = 0b0000001000
    C05_ARG_LEFT = 0b0000000000
    C05_ARG_RIGHT = 0b0000000100

    # Function set
    C06_FUNCTION_SET = 0b0000100000
    C06_ARG_4BIT_BUS = 0b0000000000
    C06_ARG_8BIT_BUS = 0b0000010000
    C06_ARG_1LINE_DISPLAY = 0b0000000000
    C06_ARG_2LINES_DISPLAY = 0b0000001000
    C06_ARG_5X8_DOTS = 0b0000000000
    C06_ARG_5X11_DOTS = 0b0000000100

    # Set CGRAM address
    #     DB5-DB0: CGRAM address
    C07_SET_CGRAM_ADDRESS = 0b0001000000

    # Set DDRAM address
    #  DB6-DB0: DDRAM address
    #  When 1-line display mode:
    #     00H to 4FH
    #  When 2-line display mode:
    #     00H to 27H for the first line
    #     40H to 67H for the second line
    C08_SET_DDRAM_ADDRESS = 0b0010000000

    # Read busy flag and address
    #     DB7: 1=Busy, 0=Not busy
    #     DB6-DB0: Address counter
    C09_READ_BUSY_FLAG_AND_ADDR = 0b0100000000

    # Write data to RAM
    #     DB7-DB0: Data to be written to RAM
    C10_WRITE_DATA = 0b1000000000

    # Read data from RAM
    #     DB7-DB0: Data read from RAM
    C11_READ_DATA = 0b1100000000
