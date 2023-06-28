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
from machine import Pin


# `Pin.mode()` is not supported by all MicroPython implementations. We need to be
# able to switch between `Pin.OUT` and `Pin.IN` to perform read operations on the
# LCD, such as reading the busy flag, the address counter or the cursor position.
# The `_DataPin` class implements this feature through his `mode()` method. It also
# implements a subset of the `Pin` class interface which covers the needs of the
# LCD1602 library, making it a drop-in replacement to the `Pin` class.
class _DataPin:
    def __init__(self, pin_num: int):
        self._pin_num = pin_num
        self._pin = Pin(pin_num, Pin.OUT, value=0)

    def on(self):
        self._pin.on()

    def off(self):
        self._pin.off()

    def value(self, value: ... = None) -> ...:
        if value is None:
            return self._pin.value()
        else:
            return self._pin.value(value)

    def mode(self, mode: int):
        self._pin = Pin(self._pin_num, mode)
