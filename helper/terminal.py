import os
import sys

import colorama

BRIGHT = colorama.Style.BRIGHT
RED = colorama.Fore.RED
GREEN = colorama.Fore.GREEN
MAGENTA = colorama.Style.BRIGHT + colorama.Fore.MAGENTA
CYAN = colorama.Style.BRIGHT + colorama.Fore.CYAN
RESET = colorama.Fore.WHITE + colorama.Style.NORMAL + colorama.Back.RESET

ERROR = RED + "Error: "
WARNING = MAGENTA + "Warning: "


def exit_app() -> None:
    input("Press ENTER to exit.")
    sys.exit()


def print_header(string, color="", *, frame_char="#") -> None:
    bar = (len(string) + 4) * frame_char
    print(f"{color}{bar}\n{frame_char} {string} {frame_char}\n{bar}{RESET}")


def color_handling(init: bool = True) -> None:
    if init:
        os.system("cls")
        os.system("color 0f")
        colorama.init()
        print(colorama.Back.BLACK + colorama.Fore.WHITE, end="")
    else:
        os.system("color")
        print(colorama.Style.RESET_ALL, end="")
        os.system("cls")
