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
from superelixier.helper.terminal import Ansi, clear, exit_app, print_header


def main():
    try:
        try:
            clear()
            check_terms()
            lock = LockFile()  # noqa
            if len(sys.argv) == 1:
                DefaultCommand().run(cli.create_io())
            else:
                cli.run()
            del lock
            exit_app(0)
        except LockFileException:
            time.sleep(7)
    except Exception:  # noqa
        clear()
        print_header("superelixier crashed!")
        tb = f"{Ansi.RED}{traceback.format_exc().strip()}{Ansi.RESET}"
        print("(╯°□°)╯︵ ┻━┻", "\n", tb, "\n", "┬─┬ノ( º _ ºノ)")
        exit_app(-1)
    finally:
        clear()
        sys.exit()


if __name__ == "__main__":
    main()
