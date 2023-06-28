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


class LCDCursor:
    """Cursor types supported by the LCD `set_cursor_type()` method."""

    NONE = 0
    """No cursor."""

    UNDERSCORE = 1
    """Underscore cursor."""

    BLINKING_BLOCK = 2
    """Blinking block cursor."""

    COMBINED = 3
    """Underscore cursor with blinking block cursor on top."""
