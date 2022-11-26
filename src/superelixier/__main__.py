"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import sys
import time
import traceback

from superelixier.application import DefaultCommand, cli
from superelixier.eula import check_terms
from superelixier.helper.lock_file import LockFile, LockFileException
from superelixier.helper.terminal import Ansi, clear, confirm_exit_app, print_header

exit_confirm_trigger = {-100: -1, 100: 0}


def main():
    ret_code: int = 0
    try:
        try:
            check_terms()
            lock = LockFile()  # noqa
            if len(sys.argv) == 1:
                ret_code = DefaultCommand().run(cli.create_io())
            else:
                ret_code = cli.run()
            del lock
        except LockFileException:
            time.sleep(7)
    except Exception:  # noqa
        clear()
        print_header("superelixier crashed!")
        tb = f"{Ansi.RED}{traceback.format_exc().strip()}{Ansi.RESET}"
        print("(╯°□°)╯︵ ┻━┻", "\n", tb, "\n", "┬─┬ノ( º _ ºノ)")
        ret_code = -100
    finally:
        if ret_code in exit_confirm_trigger:
            confirm_exit_app(exit_confirm_trigger[ret_code])


if __name__ == "__main__":
    main()
