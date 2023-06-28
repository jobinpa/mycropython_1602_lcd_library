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

import utime as time
from lcd1602._helper import _Helper
from lcd1602.hd44780cmds import HD44780Cmds
from lcd1602.lcdcursor import LCDCursor
from lcd1602.hd44780bus import HD44780Bus
from lcd1602.hd44780bus4 import HD44780Bus4
from lcd1602.hd44780bus8 import HD44780Bus8
from lcd1602.hd44780busI2C import HD44780BusI2C


class LCD1602:
    """LCD1602 display

    Provides common operations for HD44780-based 1602 LCD display. To create a
    new instance, call one of the begin_XXX() methods.
    """

    # ######################################################################## #
    # LCD commands execution time (in microseconds)
    #
    # See HD44780 datasheet, page 24-25 Table 6, for more details about commands.
    #
    # The datasheet provides two execution times: a long one for CLEAR and HOME
    # commands and a short one for all other commands. The execution times are
    # based on a 270KHz clock (fOSC). The minimum fOSC supported by the HD44780
    # is 190KHz as per page 49. For greater compatibility, all execution times
    # have been scaled to the minimum fOSC using the formula provided on page 25
    # Table 6 (last row):
    #
    #     exec_time_adjusted = exec_time_at_270 * 270 / 190
    #
    # One microsocond has been added to execution times to account for faster
    # chipsets. This way, we are certain a given command is done executing after
    # the specified time has elapsed.
    # ######################################################################## #
    _EXECTIMEUS_LONG = 2161  # 1.52ms @ 270KHz, 2.16ms @ 190KHz
    _EXECTIMEUS_SHORT = 53  # 37us @ 270KHz, 52us @ 190KHz

    # ######################################################################## #
    # LCD DDRAM address offsets and line length
    #
    # See HD44780 datasheet, page 29 (Set DDRAM Address) for more details about
    # LCD lines.
    #
    # The 1602 LCD can store two lines of 40 characters each however, only 16
    # characters per line can be displayed at any given time. Lines are not
    # stored contiguously in DDRAM. The first line starts at address 0x00 while
    # the second line starts at address 0x40.
    # ######################################################################## #
    _LINE_ADDR_OFFSETS = {0: 0x00, 1: 0x40}
    _LINE_LENGTH = 40

    def __init__(self, bus: HD44780Bus):
        """Creates a new LCD1602 instance

        Creating a new LCD1602 instance DOES NOT initialize the display. It is
        important to call the `init` method before attempting any operation on
        the display. The preferred way to create and initialize a new LCD1602
        instance is to use one of the `begin_XXX` class methods.

        Args:
            bus HD44780Bus: The bus used to communicate with the LCD.

        Returns:
            LCD1602: A new LCD1602 instance that has not been initialized yet.

        Raises:
            TypeError: One of the arguments is of the wrong type.
            ValueError: One of the arguments is out of range.
        """
        if not isinstance(bus, HD44780Bus):
            raise TypeError("Invalid bus.")
        self._bus = bus

        # These fields are initialiazed in init()
        self._character_map = {}
        self._display_control = 0
        self._entry_mode = 0
        self._function_set = 0

    @classmethod
    def begin_4bit(
        cls,
        rs: int,
        e: int,
        db_7_to_4: list[int],
        rw: int | None = None,
        bl: int | None = None,
    ):
        """Creates and initializes an instance for a 4-bit bus.

        This method automatically calls `init()` after creating the LCD instance,
        ensuring that the LCD is ready for use.

        When provided, the BL pin must be connected to custom circuitry controlling
        the backlight, as the LCD generally does not have such circuitry built-in.

        Args:
            rs (int): The pin number of the RS (Register Select) pin.
            e (int): The pin number of the E (Enable) pin.
            db_7_to_4 (list[int]): A list of pin numbers representing the 4 data lines (db7 to db4) of the LCD.
            rw (int | None): The pin number of the RW (Read/Write) pin. Defaults to None. This pin is required only for read operations. When not provided, the RW pin must be connected to ground.
            bl (int, optional): The pin number of the BL (Backlight Control) pin. Defaults to None. This pin is required to control the backlight using custom circuitry.

        Raises:
            TypeError: One of the arguments is of the wrong type.
            ValueError: One of the arguments is out of range.

        Returns:
            LCD1602: A new LCD1602 instance that has been initialized and is ready to use.
        """
        _Helper.validate_integer_arg("rs", rs)
        _Helper.validate_integer_arg("e", e)
        _Helper.validate_integer_list_arg("db_7_to_4", db_7_to_4, length=4)

        if rw is not None:
            _Helper.validate_integer_arg("rw", rw)

        if bl is not None:
            _Helper.validate_integer_arg("bl", bl)

        lcd = cls(HD44780Bus4(rs, e, db_7_to_4, rw, bl))
        lcd.init()
        return lcd

    @classmethod
    def begin_8bit(
        cls,
        rs: int,
        e: int,
        db_7_to_0: list[int],
        rw: int | None = None,
        bl: int | None = None,
    ):
        """Creates and initializes an instance for a 8-bit bus.

        This method automatically calls `init()` after creating the LCD instance,
        ensuring that the LCD is ready for use.

        When provided, the BL pin must be connected to custom circuitry controlling
        the backlight, as the LCD generally does not have such circuitry built-in.

        Args:
            rs (int): The pin number of the RS (Register Select) pin.
            e (int): The pin number of the E (Enable) pin.
            db_7_to_0 (list[int]): A list of pin numbers representing the 8 data lines (db7 to db0) of the LCD.
            rw (int | None): The pin number of the RW (Read/Write) pin. Defaults to None. This pin is required only for read operations. When not provided, the RW pin must be connected to ground.
            bl (int, optional): The pin number of the BL (Backlight Control) pin. Defaults to None. This pin is required to control the backlight using custom circuitry.

        Raises:
            TypeError: One of the arguments is of the wrong type.
            ValueError: One of the arguments is out of range.

        Returns:
            LCD1602: A new LCD1602 instance that has been initialized and is ready to use.
        """
        _Helper.validate_integer_arg("rs", rs)
        _Helper.validate_integer_arg("e", e)
        _Helper.validate_integer_list_arg("db_7_to_0", db_7_to_0, length=8)

        if rw is not None:
            _Helper.validate_integer_arg("rw", rw)

        if bl is not None:
            _Helper.validate_integer_arg("bl", bl)

        lcd = cls(HD44780Bus8(rs, e, db_7_to_0, rw, bl))
        lcd.init()
        return lcd

    @classmethod
    def begin_i2c(cls, bus_id: int, scl: int, sda: int, addr: int | None = None):
        """Creates and initializes an instance for an I2C bus

        This method automatically calls `init()` after creating the LCD instance.
        The instance returned by this method is ready to use.

        Args:
            bus_id (int): The I2C peripheral/bus id. For example, a pin I2C1 SCL is the clock pin for I2C bus 1.
            scl (int): The pin number of the scl pin.
            sda (int): The pin number of the sda pin.
            addr (int, optional): The I2C address of the LCD. When not specified, the LCD is expected to be the only device on the I2C bus. Defaults to None.

        Raises:
            TypeError: One of the arguments is of the wrong type.
            ValueError: One of the arguments is out of range.

        Returns:
            LCD1602: A new LCD1602 instance that has been initialized and is ready to use.
        """
        _Helper.validate_integer_arg("bus_id", bus_id)
        _Helper.validate_integer_arg("scl", scl)
        _Helper.validate_integer_arg("sdc", sda)

        if addr is not None:
            _Helper.validate_integer_arg("addr", addr, min_value=0)

        lcd = cls(HD44780BusI2C(bus_id, scl=scl, sda=sda, addr=addr))
        lcd.init()
        return lcd

    def clear(self):
        """Clears the display and sets the cursor position to home

        This command writes 20H (blank) to all DDRAM addresses (not only the
        ones that are displayed). It also resets any scrolling and sets the
        display entry mode to left to right.
        """
        self.execute_command(HD44780Cmds.C01_CLEAR)

    def create_character(self, lcdcharcode: int, bitmap: list[int]):
        """Creates a custom character

        It is possible to define up to 8 custom characters using character codes
        0 to 7. Each character is represented by a 5x8 bitmap specified as a list
        of eight 5-bit integers. Each bit represents a pixel that is ON when the
        bit is high. The last row is normally filled with 0s as it is used to
        display the cursor (when the cursor is visible).

        IMPORTANT: At the end of this command, the Character Generator RAM (CGRAM)
        will be selected. This is generally not a problem, unless `execute_command()`
        is used to send low-level commands to the LCD. In this case, it may be
        necessary to select the Data Display RAM (DDRAM) using the `set_cursor_position()`
        method before attempting any read or write operation.

        Args:
            lcdcharcode (int): The custom character code (0 to 7).
            bitmap (list[int]): The character's bitmap represented as a list of eight 5-bit integers.

        Raises:
            TypeError: One of the arguments is of the wrong type.
            ValueError: One of the arguments is out of range.
        """
        _Helper.validate_integer_arg("lcdcharcode", lcdcharcode, min_value=0, max_value=7)
        _Helper.validate_integer_list_arg("bitmap", bitmap, length=8, min_value=0b00000, max_value=0b11111)

        # As per datasheet, page 19, Table 5
        # The CGRAM address is equals to the character code shifted by 3 bits to the left.
        custom_char_addr = lcdcharcode << 3
        self.execute_command(HD44780Cmds.C07_SET_CGRAM_ADDRESS | custom_char_addr)

        # Write bitmap to the CGRAM.
        for byte in bitmap:
            self.execute_command(HD44780Cmds.C10_WRITE_DATA | byte)

    def execute_command(self, cmd: int) -> int | None:
        """Executes an LCD command

        Executing LCD commands is an advanced function that is rarely required,
        as this library provides high-level functions for comontly used LCD
        operations. For more information about LCD commands, please refer to the
        HD44780 Datasheet, page 24, Table 6. The class `HD44780Cmds` provides
        constants for all commands.

        A bus may or may not support read operations. To verify whether a given
        command is supported or not, please use the `is_command_supported` function.

        This method returns a 8-bit unsigned value when the command is a read
        operation. It returns None when the command is a write operation.

        Args:
            cmd (int): The command (10-bit unsigned integer). See class `HD44780Cmds` for a list of commands.

        Returns:
            int | None: The command output (read operation) or None (write operation) as an 8-bit unsigned integer.

        Raises:
            RuntimeError: The command is not supported.
        """
        if not self.is_command_supported(cmd):
            raise RuntimeError("Command is not supported.")

        # Execute the command. The command is a read operation if the RW bit is set.
        is_read_op = cmd & HD44780Cmds.BITMASK_RW
        data = self._bus.read(cmd) if is_read_op else self._bus.write(cmd)

        # The HD44780 datasheet, page 24-25, provides two execution times: a
        # long one for clear and home command and a short one for all other commands
        is_long_cmd = (cmd == HD44780Cmds.C01_CLEAR) or (cmd == HD44780Cmds.C02_HOME)
        exec_delay = LCD1602._EXECTIMEUS_LONG if is_long_cmd else LCD1602._EXECTIMEUS_SHORT

        # If the bus supports reading, we use the busy flag to determine when
        # the command is done executing. Otherwise, we fallback on a fixed delay.
        if self._bus.can_read:
            busy_flag_check_started_at = time.ticks_ms()

            while True:
                # Busy flag is db7. When high, the LCD is busy.
                is_busy = self._bus.read(HD44780Cmds.C09_READ_BUSY_FLAG_AND_ADDR) & HD44780Cmds.BITMASK_DB7
                if not is_busy:
                    break

                # We could enter in an infinite loop if the LCD is not responding.
                # This conditional branch prevents this from happening by checking
                # if we have exceeded the expected fixed delay for the command.
                # If so, we print an error and break the loop.
                if abs(time.ticks_diff(busy_flag_check_started_at, time.ticks_ms())) >= exec_delay:
                    print("LCD ERROR! Cannot read busy flag.")
                    break
        else:
            # Bus does not support reading. Using fixed delay
            time.sleep_us(exec_delay)

        return data

    def get_cursor_position(self) -> tuple[int, int]:
        """Gets the cursor position as a tuple (col, line)

        IMPORTANT: The availability of this function is dependent on the LCD bus
        supporting read operations. The 4-bit and 8-bit buses support read
        operations only when the RW pin is supplied. The I2C bus always supports
        read operations.

        Column and line numbers are 0-based. The LCD supports 40 columns (numbered
        from 0 to 39) and 2 lines (numbered from 0 to 1). However, only 16
        continuous columns can be displayed at the same time. For more information
        about scrolling the display content, please see the `scroll_display_left`
        and `scroll_display_right` functions.

        Returns:
            tuple[int, int]: The cursor´s position as a tuple containing the column index (0 to 39) and the line index (0 or 1).

        Raises:
            RuntimeError: The command is not supported. The bus does not support read operations.
        """
        if not self._bus.can_read:
            raise RuntimeError("Command is not supported. Bus does not support read operations.")

        data = self.execute_command(HD44780Cmds.C09_READ_BUSY_FLAG_AND_ADDR)
        assert data is not None

        # db7 is the busy flag indicator. We ignore it
        cursor_addr = data & ~HD44780Cmds.BITMASK_DB7

        # Calculate the line index
        line_idx = -1
        for current_line_idx in LCD1602._LINE_ADDR_OFFSETS:
            current_line_addr_start = LCD1602._LINE_ADDR_OFFSETS[current_line_idx]
            current_line_addr_end = current_line_addr_start + (LCD1602._LINE_LENGTH - 1)
            if cursor_addr >= current_line_addr_start and cursor_addr <= current_line_addr_end:
                line_idx = current_line_idx
                break

        # This should never happen.
        if line_idx < 0:
            raise RuntimeError("Unable to calculate line index from cursor´s address.")

        # Calculate the column index
        col_idx = cursor_addr - LCD1602._LINE_ADDR_OFFSETS[line_idx]

        return (col_idx, line_idx)

    def home(self):
        """Sets the cursor position to (0, 0) and resets scrolling"""
        self.execute_command(HD44780Cmds.C02_HOME)

    def init(self):
        """Initializes the display

        This method MUST be called before attempting any other operations on the
        LCD, unless the LCD instance was created using one of the `begin_XXX`
        class methods. This command initializes the bus and the LCD, making it
        ready to use.

        After initialization, the LCD is in the following state:

            * Display is cleared
            * Cursor is at the home position (0, 0)
            * No cursur is displayed
            * Auto-scroll is off
            * Entry mode is set to left to right
            * All custom characters have been replaced with a blank character
            * Character mappings have been cleared
            * Backlight is ON (if the bus supports backlight control)
        """
        # 1. Clear character mappings
        self._character_map = {}

        # 2. Initialize the bus
        self._bus.init()

        # 3. Function set
        # fmt: off
        self._function_set = HD44780Cmds.C06_FUNCTION_SET \
            | HD44780Cmds.C06_ARG_2LINES_DISPLAY \
            | HD44780Cmds.C06_ARG_5X8_DOTS \
            | (HD44780Cmds.C06_ARG_4BIT_BUS if self._bus.width == 4 else HD44780Cmds.C06_ARG_8BIT_BUS)
        self.execute_command(self._function_set)
        # fmt: on

        # 4. Clear display
        self.execute_command(HD44780Cmds.C01_CLEAR)

        # 5. Entry mode set
        # fmt: off
        self._entry_mode = HD44780Cmds.C03_ENTRY_MODE_SET \
            | HD44780Cmds.C03_ARG_LEFT_TO_RIGHT \
            | HD44780Cmds.C03_ARG_AUTOSCROLL_OFF
        self.execute_command(self._entry_mode)
        # fmt: on

        # 6. Display control
         # fmt: off
        self._display_control = (
            HD44780Cmds.C04_DISPLAY_CONTROL
            | HD44780Cmds.C04_ARG_DISPLAY_ON
            | HD44780Cmds.C04_ARG_CURSOR_OFF
            | HD44780Cmds.C04_ARG_CURSOR_BLINK_OFF
        )
        self.execute_command(self._display_control)
        # fmt: on

        # 7. Clear CGRAM (custom chars)
        for i in range(0, 8):
            self.create_character(0, [0, 0, 0, 0, 0, 0, 0, 0])

        # 8. Set cursor position to home
        self.home()

        # 9. Turn backlight on
        if self._bus.can_control_backlight:
            self.set_backlight_on()

    def is_command_supported(self, cmd: int) -> bool:
        """Indicates whether an LCD command is supported or not

        This method will return False when a command performing a read operation
        is issued on a bus that does not support reading.

        Args:
            cmd (int): The command (10-bit unsigned integer). See class`HD44780Cmds` for a list of commands.

        Returns:
            bool: True if the command is supported, False otherwise.
        """
        if not isinstance(cmd, int):
            return False

        if cmd < 0 or cmd > 0b1111111111:
            return False

        # A command is a read operation when the RW bit is HIGH.
        is_read_op = cmd & HD44780Cmds.BITMASK_RW
        if is_read_op and not self._bus.can_read:
            return False

        return True

    def map_character(self, char: str, lcdcharcode: int):
        """Maps a Unicode character to an LCD character

        Mapping a character enables this character to be utilized when writing
        text to the LCD with the `write_text` function. Fortunately, most
        [ASCII](https://www.asciitable.com/) characters are natively supported
        without requiring any custom character or mapping. For more information
        about the character codes natively supported by the HD44780 display
        controller, please refer to the HD44780 Datasheet, page 18-19.

        LCD character codes are integer values ranging from 0 to 255. Character
        codes 0 to 7 are reserved for custom characters. See the
        `create_character()` method for more details.

        Args:
            char (str): The Unicode character to map.
            lcdcharcode (int): The LCD character code to map the Unicode character to.

        Raises:
            TypeError: One of the arguments is of the wrong type.
            ValueError: One of the arguments is out of range.
        """
        _Helper.validate_string_arg("char", char, min_length=1, max_length=1)
        _Helper.validate_integer_arg("lcdcharcode", lcdcharcode, min_value=0, max_value=0xFF)
        self._character_map[char] = lcdcharcode

    def move_cursor_left(self):
        """Moves the cursor left by one position

        Moving the cursor left from column index 0 will put the cursor at the
        end (index 39) of the other line.

        Moving the cursor outside the LCD visible area does not automatically
        scroll the display.
        """
        # fmt: off
        cmd = HD44780Cmds.C05_CMD_SHIFT \
            | HD44780Cmds.C05_ARG_CURSOR \
            | HD44780Cmds.C05_ARG_LEFT
        # fmt: on
        self.execute_command(cmd)

    def move_cursor_right(self):
        """Moves the cursor to the right by one position

        Moving the cursor right from column index 39 will put the cursor at the
        beginning (index 0) of the other line.

        Moving the cursor outside the LCD visible area does not automatically
        scroll the display.
        """
        # fmt: off
        cmd = HD44780Cmds.C05_CMD_SHIFT \
            | HD44780Cmds.C05_ARG_CURSOR \
            | HD44780Cmds.C05_ARG_RIGHT
        # fmt: on
        self.execute_command(cmd)

    def read_code(self, col: int, line: int) -> int:
        """Reads an LCD character code at a given position

        IMPORTANT: The availability of this function is dependent on the LCD bus
        supporting read operations. The 4-bit and 8-bit buses support read
        operations only when the RW pin is supplied. The I2C interface always
        supports read operations.

        This command will first set the cursor to the desired position, read the
        code, then move the cursor right (if the entry mode is left to right) or
        eft (if the entry mode is right to left) by one position.

        Args:
            col (int): The column index (0 to 39).
            line (int): The line index (0 or 1).

        Returns:
            int: The LCD character code as a integer (0 to 255).

        Raises:
            TypeError: One of the arguments is of the wrong type.
            ValueError: One of the arguments is out of range.
        """

        # fmt: off
        _Helper.validate_integer_arg("col", col, min_value=0, max_value=LCD1602._LINE_LENGTH, inclusive=False)
        _Helper.validate_integer_arg("line", line, min_value=0, max_value=len(LCD1602._LINE_ADDR_OFFSETS), inclusive=False)
        # fmt: on

        if not self._bus.can_read:
            raise RuntimeError("Command is not supported. Bus does not support read operations.")

        self.set_cursor_position(col, line)
        data = self.execute_command(HD44780Cmds.C11_READ_DATA)
        assert data is not None
        return data

    def scroll_display_left(self):
        """Scrolls the entire display left by one position

        This command does not affect the cursor position. Both lines will scroll
        at the same time.
        """
        # fmt: off
        cmd = HD44780Cmds.C05_CMD_SHIFT \
            | HD44780Cmds.C05_ARG_CONTENT \
            | HD44780Cmds.C05_ARG_RIGHT # Scrolling left move content to the right
        # fmt: on
        self.execute_command(cmd)

    def scroll_display_right(self):
        """Scrolls the entire display right by one position

        This command does not affect the cursor position. Both lines will scroll
        at the same time.
        """
        # fmt: off
        cmd = HD44780Cmds.C05_CMD_SHIFT \
            | HD44780Cmds.C05_ARG_CONTENT \
            | HD44780Cmds.C05_ARG_LEFT
        # fmt: on
        self.execute_command(cmd)

    def set_autoscroll_on(self):
        """Turns auto-scroll ON

        The display will automatically scroll to the right (when the entry mode
        is left to right) or to the left (when the entry mode is right to left)
        when characters are written. Please note both lines will scroll at the
        the same time.
        """
        self._entry_mode = self._entry_mode | HD44780Cmds.C03_ARG_AUTOSCROLL_ON
        self.execute_command(self._entry_mode)

    def set_autoscroll_off(self):
        """Turns auto-scroll OFF"""
        self._entry_mode = self._entry_mode & ~HD44780Cmds.C03_ARG_AUTOSCROLL_ON
        self.execute_command(self._entry_mode)

    def set_backlight_on(self):
        """Turns the LCD backlight ON

        IMPORTANT: This is not a native LCD operation. It requires a bus with
        the appropriate circuitry. The I2C interface does have such circuitry
        built-in. The 4-bit and 8-bit buses support backlight control only when
        the BL pin is supplied. This pin is assumed to be connected to the
        appropriate circuitry to control the backlight.
        """
        if not self._bus.can_control_backlight:
            raise RuntimeError("Operation is not supported. Bus does not support backlight control.")
        self._bus.set_backlight(True)

    def set_backlight_off(self):
        """Turns the LCD backlight OFF

        IMPORTANT: This is not a native LCD operation. It requires a bus with
        the appropriate circuitry. The I2C interface does have such circuitry
        built-in. The 4-bit and 8-bit buses support backlight control only when
        the BL pin is supplied. This pin is assumed to be connected to the
        appropriate circuitry to control the backlight.
        """
        if not self._bus.can_control_backlight:
            raise RuntimeError("Operation is not supported. Bus does not support backlight control.")
        self._bus.set_backlight(False)

    def set_cursor_position(self, col: int, line: int):
        """Sets the cursor position

        Column and line numbers are 0-based. The LCD supports 40 columns
        (numbered from 0 to 39) and 2 lines (numbered from 0 to 1). However,
        only 16 continuous columns can be displayed at the same time. For more
        information about scrolling the display content, please see the
        `scroll_display_left` and `scroll_display_right` functions.

        Moving the cursor outside the LCD visible area does not automatically
        scroll the display.

        Args:
            col (int): The column index (0 to 39).
            line (int): The line index (0 or 1).

        Raises:
            TypeError: One of the arguments is of the wrong type.
            ValueError: One of the arguments is out of range.
        """
        # fmt: off
        _Helper.validate_integer_arg("col", col, min_value=0, max_value=LCD1602._LINE_LENGTH, inclusive=False)
        _Helper.validate_integer_arg("line", line, min_value=0, max_value=len(LCD1602._LINE_ADDR_OFFSETS), inclusive=False)
        # fmt: on
        addr = LCD1602._LINE_ADDR_OFFSETS[line] + col
        self.execute_command(HD44780Cmds.C08_SET_DDRAM_ADDRESS | addr)

    def set_cursor_type(self, cursor_type: int):
        """Sets the cursor type

        See class `LCDCursor` as this class contains constants representing the
        different cursor types:

        * 0: No cursor (`LCDCursor.NONE`)
        * 1: Underscore cursor (`LCDCursor.UNDERSCORE`)
        * 2: Blinking block cursor (`LCDCursor.BLINKING_BLOCK`)
        * 3: Underscore and blinking block cursor (`LCDCursor.COMBINED`)

        Args:
            cursor_type (int): The cursor type to set. See class `LCDCursor`.

        Raises:
            TypeError: One of the arguments is of the wrong type.
            ValueError: One of the arguments is out of range.
        """
        _Helper.validate_integer_arg("cursor_type", cursor_type, min_value=0, max_value=3)

        if cursor_type == LCDCursor.NONE:
            self._display_control = self._display_control & ~HD44780Cmds.C04_ARG_CURSOR_ON
            self._display_control = self._display_control & ~HD44780Cmds.C04_ARG_CURSOR_BLINK_ON
            self.execute_command(self._display_control)
        elif cursor_type == LCDCursor.UNDERSCORE:
            self._display_control = self._display_control | HD44780Cmds.C04_ARG_CURSOR_ON
            self._display_control = self._display_control & ~HD44780Cmds.C04_ARG_CURSOR_BLINK_ON
            self.execute_command(self._display_control)
        elif cursor_type == LCDCursor.BLINKING_BLOCK:
            self._display_control = self._display_control & ~HD44780Cmds.C04_ARG_CURSOR_ON
            self._display_control = self._display_control | HD44780Cmds.C04_ARG_CURSOR_BLINK_ON
            self.execute_command(self._display_control)
        elif cursor_type == LCDCursor.COMBINED:
            self._display_control = self._display_control | HD44780Cmds.C04_ARG_CURSOR_ON
            self._display_control = self._display_control | HD44780Cmds.C04_ARG_CURSOR_BLINK_ON
            self.execute_command(self._display_control)

    def set_display_on(self):
        """Turns the display ON. This does not affect the LCD backlight"""
        self._display_control = self._display_control | HD44780Cmds.C04_ARG_DISPLAY_ON
        self.execute_command(self._display_control)

    def set_display_off(self):
        """Turns the display OFF. This does not affect the LCD backlight"""
        self._display_control = self._display_control & ~HD44780Cmds.C04_ARG_DISPLAY_ON
        self.execute_command(self._display_control)

    def set_left_to_right(self):
        """Sets the entry mode to left to right"""
        self._entry_mode = self._entry_mode | HD44780Cmds.C03_ARG_LEFT_TO_RIGHT
        self.execute_command(self._entry_mode)

    def set_right_to_left(self):
        """Sets the entry mode to right to left"""
        self._entry_mode = self._entry_mode & ~HD44780Cmds.C03_ARG_LEFT_TO_RIGHT
        self.execute_command(self._entry_mode)

    def unmap_character(self, char: str):
        """Unmaps a Unicode character previously mapped using the `map_character()` function

        Args:
            char (str): The character to unmap.

        Raises:
            TypeError: One of the arguments is of the wrong type.
            ValueError: One of the arguments is out of range.
        """
        _Helper.validate_string_arg("char", char, min_length=1, max_length=1)
        if char in self._character_map:
            del self._character_map[char]

    def write_code(self, col: int, line: int, lcdcharcode: int):
        """Writes a single LCD character code at a given position

        Column and line numbers are 0-based. The LCD supports 40 columns
        (numbered from 0 to 39) and 2 lines (numbered from 0 to 1). However,
        only 16 continuous columns can be displayed at the same time. For more
        information about scrolling the display content, please see the
        `scroll_display_left` and `scroll_display_right` functions.

        LCD character codes are integer values ranging from 0 to 255. Character
        codes 0 to 7 are reserved for custom characters. For more information
        about the character codes natively supported by the HD44780 display
        controller, please refer to the HD44780 Datasheet, page 18-19.

        Args:
            col (int): The column index (0 to 39).
            line (int): The line index (0 or 1).
            lcdcharcode (int): The LCD character code to write.

        Raises:
            TypeError: One of the arguments is of the wrong type.
            ValueError: One of the arguments is out of range.
        """
        # fmt: off
        _Helper.validate_integer_arg("col", col, min_value=0, max_value=LCD1602._LINE_LENGTH, inclusive=False)
        _Helper.validate_integer_arg("line", line, min_value=0, max_value=len(LCD1602._LINE_ADDR_OFFSETS), inclusive=False)
        _Helper.validate_integer_arg("lcdcharcode", lcdcharcode, min_value=0, max_value=0xFF)
        # fmt: on

        self.set_cursor_position(col, line)
        self.execute_command(HD44780Cmds.C10_WRITE_DATA | lcdcharcode)

    def write_codes(self, col: int, line: int, lcdcharcodes: list[int]):
        """Writes a list of LCD char codes starting at a given position

        Column and line numbers are 0-based. The LCD supports 40 columns
        (numbered from 0 to 39) and 2 lines (numbered from 0 to 1). However,
        only 16 continuous columns can be displayed at the same time. For more
        information about scrolling the display content, please see the
        `scroll_display_left` and `scroll_display_right` functions.

        LCD character codes are integer values ranging from 0 to 255. Character
        codes 0 to 7 are reserved for custom characters. For more information
        about the character codes natively supported by the HD44780 display
        controller, please refer to the HD44780 Datasheet, page 18-19.

        Args:
            col (int): The column index (0 to 39).
            line (int): The line index (0 or 1).
            lcdcharcodes (list[int]): A list of LCD character codes to write.

        Raises:
            TypeError: One of the arguments is of the wrong type.
            ValueError: One of the arguments is out of range.
        """
        # fmt: off
        _Helper.validate_integer_arg("col", col, min_value=0, max_value=LCD1602._LINE_LENGTH, inclusive=False)
        _Helper.validate_integer_arg("line", line, min_value=0, max_value=len(LCD1602._LINE_ADDR_OFFSETS), inclusive=False)
        _Helper.validate_integer_list_arg("lcdcharcodes", lcdcharcodes, min_value=0, max_value=0xFF)
        # fmt: on

        self.set_cursor_position(col, line)
        for byte in lcdcharcodes:
            self.execute_command(HD44780Cmds.C10_WRITE_DATA | byte)

    def write_text(self, col: int, line: int, text: str):
        """Writes text starting at a given position

        Column and line numbers are 0-based. The LCD supports 40 columns
        (numbered from 0 to 39) and 2 lines (numbered from 0 to 1). However,
        only 16 continuous columns can be displayed at the same time. For more
        information about scrolling the display content, please see the
        `scroll_display_left` and `scroll_display_right` functions.

        Most [ASCII](https://www.asciitable.com/) characters are natively
        supported without requiring any custom character or mapping. The LCD
        allows up to 7 custom characters to be defined. These custom characters
        can be mapped to any [Unicode](https://www.lookuptables.com/text/unicode-characters)
        character using the `map_character` function. This mapping enables the
        custom characters to be utilized when writing text to the LCD with the
        `write_text` function. For more information about the character codes
        natively supported by the HD44780 display controller, please refer to the
        HD44780 Datasheet, page 18-19. Any unmapped character with a Unicode code
        greater than 255 is replaced with a blank character.

        Args:
            col (int): The column index (0 to 39).
            line (int): The line index (0 or 1).
            text (str): The text to write.

        Raises:
            TypeError: One of the arguments is of the wrong type.
            ValueError: One of the arguments is out of range.
        """

        # fmt: off
        _Helper.validate_integer_arg("col", col, min_value=0, max_value=LCD1602._LINE_LENGTH, inclusive=False)
        _Helper.validate_integer_arg("line", line, min_value=0, max_value=len(LCD1602._LINE_ADDR_OFFSETS), inclusive=False)
        _Helper.validate_string_arg("text", text)
        # fmt: on

        self.set_cursor_position(col, line)

        for char in text:
            # If the character has been mapped, use the mapped value as the character
            # code otherwise, use the character's Unicode code.
            charcode = self._character_map[char] if char in self._character_map else ord(char)

            # If the character code is greater than 0xFF, replace it with a blank.
            # 0x20 is guaranteed to be a blank as per HD44780 datasheet, page 26,
            if charcode > 0xFF:
                charcode = 0x20

            self.execute_command(HD44780Cmds.C10_WRITE_DATA | charcode)
