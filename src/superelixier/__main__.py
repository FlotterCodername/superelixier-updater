"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import sys
import time
import traceback

from superelixier import runtime
from superelixier.application import DefaultCommand, cli
from superelixier.eula import check_terms
from superelixier.helper.lock_file import LockFile, LockFileException
from superelixier.helper.terminal import Ansi, clear, confirm_exit_app, print_header

__all__ = []

EXIT_CONFIRM_TRIGGER = {
    -200: -2,  # Layer 7 problem
    -100: -1,  # Layer 8 problem
    10: 0,     # No problem but ask for confirmation
    100: 1,    # Other problem
}


def main():
    if {"-n", "--no-interaction"}.intersection(set(sys.argv)):
        runtime.interaction = False
    ret_code: int = 0
    try:
        try:
            check_terms()
            lock = LockFile()  # noqa
            if len(sys.argv) == 1:
                ret_code = DefaultCommand().run(cli.create_io())
            else:
                ret_code = cli.run()
            lock.release()
        except LockFileException:
            time.sleep(7)
    except Exception:  # noqa
        clear()
        print_header("superelixier crashed!")
        tb = f"{Ansi.RED}{traceback.format_exc().strip()}{Ansi.RESET}"
        print("(╯°□°)╯︵ ┻━┻", "\n", tb, "\n", "┬─┬ノ( º _ ºノ)")
        ret_code = -200
    finally:
        if ret_code in EXIT_CONFIRM_TRIGGER:
            real_ret_code = EXIT_CONFIRM_TRIGGER[ret_code]
            confirm_exit_app(real_ret_code)
        else:
            sys.exit(ret_code)


if __name__ == "__main__":
    main()
