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


def exit_app():
    input("Press ENTER to exit.")
    sys.exit()


def print_header(string, color='', *, frame_char='#'):
    bar = (len(string) + 4) * frame_char
    print("%s%s\n%s %s %s\n%s%s" % (color, bar, frame_char, string, frame_char, bar, RESET))
