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


# Helper methods used to perform argument validation
class _Helper:
    @classmethod
    def validate_boolean_arg(cls, arg_name, value):
        if not isinstance(value, bool):
            raise TypeError("Argument '{}' must be a boolean".format(arg_name))

    @classmethod
    def validate_integer_arg(cls, arg_name, value, allowed_values=None, min_value=None, max_value=None, inclusive=True):
        if not isinstance(value, int):
            raise TypeError("Argument '{}' must be an integer".format(arg_name))

        if allowed_values is None:
            if min_value is not None and max_value is not None and min_value == max_value and inclusive:
                if value != min_value:
                    raise ValueError("Argument '{}' must be equal to {}".format(arg_name, max_value))

            if min_value is not None and value < min_value:
                raise ValueError("Argument '{}' must greater than or equal to {}".format(arg_name, min_value))

            if max_value is not None and inclusive and value > max_value:
                raise ValueError("Argument '{}' must be lower than or equal to {}".format(arg_name, max_value))

            if max_value is not None and not inclusive and value >= max_value:
                raise ValueError("Argument '{}' must be lower than {}".format(arg_name, max_value))
        else:
            if value not in allowed_values:
                raise ValueError("Argument '{}' must be one of {}.".format(arg_name, ", ".join(map(str, allowed_values))))

    @classmethod
    def validate_integer_list_arg(cls, arg_name, value, length=None, min_value=None, max_value=None, inclusive=True):
        if not isinstance(value, (tuple, list)):
            raise TypeError("Argument '{}' must be a list of integers".format(arg_name))

        if length is not None and len(value) != length:
            raise ValueError("Argument '{}' must be a list of exactly {} integers".format(arg_name, length))

        for element in value:
            if min_value is not None and element < min_value:
                raise ValueError(
                    "Argument '{}' must be a list of integers greater than or equal to {}".format(arg_name, min_value)
                )

            if max_value is not None and inclusive and element > max_value:
                raise ValueError(
                    "Argument '{}' must be a list of integers lower than or equal to {}".format(arg_name, max_value)
                )

            if max_value is not None and not inclusive and element >= max_value:
                raise ValueError("Argument '{}' must be a list of integers lower than {}".format(arg_name, max_value))

    @classmethod
    def validate_string_arg(cls, arg_name, value, min_length=None, max_length=None):
        if not isinstance(value, str):
            raise TypeError("Argument '{}' must be a string".format(arg_name))

        if min_length is not None and max_length is not None and min_length == max_length and len(value) != min_length:
            raise ValueError("Argument '{}' must be a string of exactly {} character(s)".format(arg_name, max_length))

        if min_length is not None and len(value) < min_length:
            raise ValueError("Argument '{}' must be a string of at least {} character(s)".format(arg_name, min_length))

        if max_length is not None and len(value) > max_length:
            raise ValueError("Argument '{}' must be a string of at most {} character(s)".format(arg_name, max_length))
