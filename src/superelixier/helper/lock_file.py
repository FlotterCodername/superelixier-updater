"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import os
import sys

from superelixier import runtime
from superelixier.helper.environment import DIR_APP
from superelixier.helper.terminal import Ansi

LOCK_MSG = Ansi.ERROR + Ansi.BRIGHT + "The previous Superelixier Updater instance is still running." + Ansi.RESET


class LockFileException(Exception):
    pass


class LockFile:
    def __init__(self) -> None:
        self.__lockfile = os.path.join(DIR_APP, "superelixier.lock")
        try:
            if sys.platform == "win32":
                if os.path.exists(self.__lockfile):
                    os.remove(self.__lockfile)
                self.__permission_win = os.open(self.__lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            else:  # POSIX
                import fcntl

                self.__permission = open(self.__lockfile, "w")
                fcntl.lockf(self.__permission, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (OSError, IOError):
            self.__lock_exit()
        runtime.locked = True

    def release(self) -> None:
        if not runtime.locked:
            return
        if sys.platform == "win32":
            os.close(self.__permission_win)
            os.remove(self.__lockfile)
        else:
            import fcntl

            fcntl.lockf(self.__permission, fcntl.LOCK_UN)
            if os.path.isfile(self.__lockfile):
                os.remove(self.__lockfile)
        runtime.locked = False

    @classmethod
    def __lock_exit(cls) -> None:
        print(LOCK_MSG)
        raise LockFileException()
