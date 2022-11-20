"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
from typing import get_args

BOOL = {"type": "boolean"}
INT = {"type": "integer"}
NULL = {"type": "null"}
STR = {"type": "string"}


def array_of(*x: dict):
    x_unpack = [*x]
    return {"type": "array", "items": x_unpack if len(x_unpack) != 1 else x_unpack[0]}


def any_of(*x: dict):
    return {"anyOf": [*x]}


def enum(literal):
    return {"enum": [*get_args(literal)]}
