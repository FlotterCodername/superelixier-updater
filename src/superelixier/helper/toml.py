"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
from typing import Any, BinaryIO

import tomli
import tomli_w

__all__ = ["dump", "dumps", "load", "loads", "TOMLDecodeError"]

TOMLDecodeError = tomli.TOMLDecodeError


def dump(obj: dict[str, Any] | Any, fp: BinaryIO, multiline_strings: bool = True) -> None:
    tomli_w.dump(__check_serializable(obj), fp, multiline_strings=multiline_strings)


def dumps(obj: dict[str, Any] | Any, multiline_strings: bool = True) -> str:
    return tomli_w.dumps(__check_serializable(obj), multiline_strings=multiline_strings)


def load(fp: BinaryIO) -> Any:
    return tomli.load(fp)


def loads(s: str | bytes) -> Any:
    if isinstance(s, bytes):
        s = s.decode()
    if not isinstance(s, str):
        raise TypeError(f"s must be str or bytes, not {type(s)}")
    return tomli.loads(s)


def __check_serializable(obj: Any) -> dict[str, Any]:
    if not isinstance(obj, dict):
        if all({hasattr(obj, "toJSON"), callable(obj.toJSON), isinstance(obj.toJSON(), dict)}):
            obj = obj.toJSON()
        else:
            raise TypeError(f"obj must be dict or JSONSerializable to dict, not {type(obj)}")
    if not all({isinstance(k, str) for k in obj}):
        raise ValueError("obj keys must be str")
    return obj
