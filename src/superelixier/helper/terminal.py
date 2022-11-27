"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import os
import sys
from dataclasses import dataclass

import colorama

from superelixier.helper.shell import clear as clear_str

DENT = " " * 2


@dataclass
class Ansi:
    BRIGHT = colorama.Style.BRIGHT
    DIM = colorama.Style.DIM
    RED = colorama.Fore.RED
    GREEN = colorama.Fore.GREEN
    YELLOW = colorama.Fore.YELLOW
    MAGENTA = colorama.Style.BRIGHT + colorama.Fore.MAGENTA
    CYAN = colorama.Style.BRIGHT + colorama.Fore.CYAN
    RESET = colorama.Fore.WHITE + colorama.Style.NORMAL + colorama.Back.RESET
    ERROR = RED + "Error: "
    WARNING = MAGENTA + "Warning: "


def confirm_exit_app(return_code) -> None:
    from superelixier import runtime

    if runtime.interaction:
        input("Press ENTER to exit...")
    sys.exit(return_code)


def print_header(string, color="", *, frame_char="#") -> None:
    bar = (len(string) + 4) * frame_char
    print(f"{color}{bar}\n{frame_char} {string} {frame_char}\n{bar}{Ansi.RESET}")


def clear() -> None:
    os.system(clear_str)
