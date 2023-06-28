# LCD1602 MicroPython LCD library

## Table of Contents

- [LCD1602 MicroPython LCD library](#lcd1602-micropython-lcd-library)
  - [Overview](#overview)
  - [Hardware and software requirements](#hardware-and-software-requirements)
  - [Installation](#installation)
  - [Library quick reference](#library-quick-reference)
  - [References](#references)
  - [Contributing](#contributing)
  - [Licensing](#licensing)

## Overview

Welcome to the LCD1602 MicroPython LCD library! This is a personal project. My
goal was to build an electronic component library from scratch using the
component's datasheet as a starting point. I chose a 16x2 Liquid Crystal Display
(LCD) with an HD44780 display controller, as this component is relatively simple
and well-documented, making it suitable for a project of this kind.

My design constraints were the following:

1. The library should be written in MicroPython.
2. The library should be compatible with the Raspberry Pi Pico W.
3. The library should provide support for both 4-bit and 8-bit buses, as well as
   the I2C bus.
4. The library should expose all LCD features common to all supported buses..
5. The library interface should be intuitive, easy to use, and abstract
   complexities of the LCD's internal workings, such has automatically handling
   DDRAM address selection when writing text.

## Hardware and software requirements

As a personal project, this library has only been tested on a limited set of
software and hardware.  While it is expected to work well with different setups,
I currently lack the means to test them extensively.

Hardware:

- Raspberry Pi Pico W
- 16x2 LCD display with an HD44780 compatible display controller

Software:

- MicroPython v1.20

## Installation

__When using [Visual Studio Code](https://code.visualstudio.com/) with the
  [MicroPico (formerly Pico-W-Go)](https://marketplace.visualstudio.com/items?itemName=paulober.pico-w-go)
  extension__

1. Copy the `lcd1602` folder (under `/src` ) into the root of your project.
2. Add the following import to your `main.py` file:

   ```python
   from lcd1602 import LCD1602
   ```

3. Create an instance of the LCD1602 class using one of the `LCD1602.begin_XXX`
   method:

   ```python
   # Replace the pin numbers as needed

   # In this example, `begin_4bit` and `begin_8bit` both assume pin `rw` is
   # connected to ground (so the LCD is in write-only mode). To operate the
   # LCD in read-write mode, you must provide the `rw=RW_PIN_NUMBER` argument
   # when calling `begin_4bit` / `begin_8bit` (the i2c mode is always in
   # read-write mode).
   lcd = LCD1602.begin_4bit(rs=2, e=3, db_7_to_4=[7, 6, 5, 4])
   # lcd = LCD1602.begin_8bit(rs=2, e=3, db_7_to_0=[7, 6, 5, 4, 3, 2, 1, 0])
   # lcd = LCD1602.begin_i2c(bus_id=1, scl=27, sda=26)

   # Write "Hello World!" at position (column=0, line=1) on the LCD screen
   lcd.write_text(0, 1, "Hello World!")
   ```

4. Make sure the Raspberry Pi Pico W board is connected and it is selected in
   Visual Studio Code.
5. Upload the project to your Raspberry Pi Pico W board with the
   `MicroPico: Upload Project to Pico` command.
6. Run your program.

__When using [Thonny](https://thonny.org/), the Python IDE for beginners__

1. Make sure the Raspberry Pi Pico W board is connected and it is selected
   in Thonny.
2. In Thonny's top navigation bar, click `View -> Files`.
3. In the left panel, under `This computer`, navigate to the folder
   containing the `lcd1602` folder (`/src`).
4. Right-click on the `lcd1602` folder, then select `Upload to`. This will take
   a while to complete.
5. Add the following import to your `main.py` file:

   ```python
   from lcd1602 import LCD1602
   ```

6. Create an instance of the LCD1602 class using one of the `LCD1602.begin_XXX`
   method:

   ```python
   # Replace the pin numbers as needed

   # In this example, `begin_4bit` and `begin_8bit` both assume pin `rw` is
   # connected to ground (so the LCD is in write-only mode). To operate the
   # LCD in read-write mode, you must provide the `rw=RW_PIN_NUMBER` argument
   # when calling `begin_4bit` / `begin_8bit` (the i2c mode is always in
   # read-write mode).
   lcd = LCD1602.begin_4bit(rs=2, e=3, db_7_to_4=[7, 6, 5, 4])
   # lcd = LCD1602.begin_8bit(rs=2, e=3, db_7_to_0=[7, 6, 5, 4, 3, 2, 1, 0])
   # lcd = LCD1602.begin_i2c(bus_id=1, scl=27, sda=26)

   # Write "Hello World!" at position (column=0, line=1) on the LCD screen
   lcd.write_text(0, 1, "Hello World!")
   ```

7. Run your program.

## Library quick reference

Method name                            | Description
:------------------------------------- | :------------------------------------------------------------------------------
`begin_4bit(rs, e, db_7_to_4, rw, bl)` | Creates and initializes an instance for a 4-bit bus. __(See notes 1 and 2)__.
`begin_8bit(rs, e, db_7_to_0, rw, bl)` | Creates and initializes an instance for an 8-bit bus. __(See notes 1 and 2)__.
`begin_i2c(scl, sda)`                  | Creates and initializes an instance for an I2C bus. __(See note 1)__.
`clear()`                              | Clears the display and sets the cursor position to home.
`create_character(lcdcharcode, bitmap)`| Creates a custom character. __(See notes 3 and 4)__.
`execute_command(cmd)`                 | Executes an LCD command. __(See note 45__.
`get_cursor_position()`                | Gets the cursor position as a tuple (col, line). __(See notes 6 and 7)__.
`home()`                               | Sets the cursor position to (0, 0) and resets scrolling.
`init()`                               | Initializes the display.
`is_command_supported(cmd)`            | Indicates whether an LCD command is supported or not. __(See note 5)__.
`map_character(char, lcdcharcode)`     | Maps a Unicode character to an LCD character. __(See note 3)__.
`move_cursor_left()`                   | Moves the cursor left by one position.
`move_cursor_right()`                  | Moves the cursor right by one position.
`read_code(col, line)`                 | Reads an LCD character code at a given position. __(See note 6)__.
`scroll_display_left()`                | Scrolls the entire display left by one position.
`scroll_display_right()`               | Scrolls the entire display right by one position.
`set_autoscroll_on()`                  | Turns auto-scroll ON.
`set_autoscroll_off()`                 | Turns auto-scroll OFF.
`set_backlight_on()`                   | Turns auto-scroll ON. __(See note 8)__.
`set_backlight_off()`                  | Turns auto-scroll OFF. __(See note 8)__.
`set_cursor_position(col, line)`       | Sets the cursor position. __(See note 7)__.
`set_cursor_type(cursor_type)`         | Sets the cursor type. See class `LCDCursor`.
`set_display_on()`                     | Turns the display ON. This does not affect the LCD backlight.
`set_display_off()`                    | Turns the display OFF. This does not affect the LCD backlight.
`set_left_to_right()`                  | Sets the entry mode to left to right.
`set_right_to_left()`                  | Sets the entry mode to right to left.
`unmap_character(char)`                | Unmaps a Unicode character previously mapped using the `map_character()` function.
`write_code(col, line, lcdcharcode)`   | Writes a single LCD char code at a given position. __(See notes 3 and 7)__.
`write_codes(col, line, lcdcharcodes)` | Writes a list of LCD char codes starting at a given position. __(See notes 3 and 7)__.
`write_text(col, line, text)`          | Writes text starting at a given position. __(See notes 3 and 7)__.
------------------------------------------------------------------------------------------------------------------------
__NOTES:__

1. This is a class function. Arguments are pin numbers. The RW pin, when part
   of the function arguments, is optional. This pin is required to use read
   commands, such as `get_cursor_position` and `read_code`. The BL pin, when
   part of the functions arguments, is also optional. When specified, this pin
   is assumed to be connected to custom circuitry allowing the bus to turn
   the LCD backlight ON or OFF. This pin is required to use `set_backlight_on`
   and `set_backlight_off`.

   When not specified, this pin is
   assumed to be connected to ground, putting the LCD in write-only mode. The BL
   pin, when part of the function arguments, is also optional. This pin is
   normally connected to some custom circuitry controlling the backlight. When
   omitted, the functions turning the backlight ON and OFF are not available.

2. The following pins are optional:

   - `rw` (READ-WRITE): When omitted, the LCD operates in write-only mode, and
     the LCD functions `get_cursor_position` and `read_code` are NOT available.
     IMPORTANT: If this pin is not connected, LCD pin `rw` MUST be connected
     to ground otherwise, the LCD will become unresponsive.

   - `bl` (BACKLIGHT): When omitted, the LCD backlight control functions
     `set_backlight_on` and `set_backlight_off` are NOT available. If provided,
     it is assumed that this pin is connected to custom circuitry controlling
     the backlight. The circuitry should activate the backlight when the pin is
     HIGH and deactivate it when the pin is LOW.

3. LCD character codes are integer values ranging from 0 to 255. Character codes
   0 to 7 are reserved for custom characters. Custom characters can be mapped to
   any [Unicode](https://www.lookuptables.com/text/unicode-characters) character
   using the `map_character` function. This mapping enables the custom
   characters to be utilized when writting text to the LCD with the `write_text`
   function. Fortunately, most [ASCII](https://www.asciitable.com/) characters
   are natively supported without requiring any custom character or mapping. For
   more information about the character codes natively supported by the HD44780
   display controller, please refer to the HD44780 Datasheet, page 18-19.

4. A character bitmap is a list of eight 5-bit integers representing the
   character's pixels. Each integer represents a pixel row, from top to bottom.
   The bottom row is generally left blank, with all bits set to 0, as it is used
   to display the cursor when it is visible.

5. Executing LCD commands is an advanced function that is rarely required, as
   this library provides high-level functions for comontly used LCD operations.
   For more information about LCD commands, please refer to the HD44780
   Datasheet, page 24, Table 6.

6. The availability of this function is dependent on the LCD bus supporting read
   operations. The 4-bit and 8-bit buses support read operations only when the
   RW pin is supplied. The I2C bus always supports read operations.

7. Column and line numbers are 0-based. The LCD supports 40 columns (numbered
   from 0 to 39) and 2 lines (numbered from 0 to 1). However, only 16 continuous
   columns can be displayed at the same time. For more information about
   scrolling the display content, please see the `scroll_display_left` and
   `scroll_display_right` functions.

8. The availability of this function is dependent on the LCD bus having some
   circuitry to control the backlight. The I2C bus comes with such circuitry,
   while the 4-bit and 8-bit buses require this circuitry to be provided
   by the user.

## References

- ["HD44780U (LCD-II)"](https://cdn-shop.adafruit.com/datasheets/HD44780.pdf),
   (PDF). Hitachi. Last retrieved on 2023-08-01.

- ["I2C Serial Interface 1602 LCD Module"](https://handsontec.com/dataspecs/module/I2C_1602_LCD.pdf),
   (PDF). Handson Technology. Last retrieved on 2023-08-01.

- ["PCF8574; PCF8574A Remote 8-bit I/O expander for I2C-bus with interrupt"](https://www.nxp.com/docs/en/data-sheet/PCF8574_PCF8574A.pdf),
   (PDF). NXP Semiconductors. Last retrieved on 2023-08-01.

__IMPORTANT__:  These references are provided solely for informational purposes.
These links connect to resources offered by third-party entities, which are
entirely independent of and unrelated to this library. The inclusion of these
references does not imply any endorsement or affiliation between these entities
and the library.

## Contributing

Please see [the contributing guide](CONTRIBUTING.md) for detailed instructions
on how you can contribute to this project.

## Licensing

![GPLv3Logo](https://www.gnu.org/graphics/gplv3-127x51.png)

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.
