import sys

import colorama

RESET = colorama.Fore.WHITE + colorama.Style.NORMAL
GREEN = colorama.Fore.GREEN
MAGENTA = colorama.Style.BRIGHT + colorama.Fore.MAGENTA
CYAN = colorama.Style.BRIGHT + colorama.Fore.CYAN


def exit_app():
    input("Press ENTER to exit.")
    sys.exit()


def print_header(string, color='', *, frame_char='#'):
    bar = (len(string) + 4) * frame_char
    print("%s%s\n%s %s %s\n%s%s" % (color, bar, frame_char, string, frame_char, bar, RESET))
