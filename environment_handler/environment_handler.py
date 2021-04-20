"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import os
import sys
import colorama

LOCK_MSG = "ERROR: The previous Superelixier Updater instance is still running."


class LockFileException(BaseException):
    pass


class LockFile:

    def __init__(self):
        self.__locked = False
        self.__lockfile = os.path.join(os.path.dirname(sys.argv[0]), "superelixier.lock")
        try:
            if sys.platform == 'win32':
                if os.path.exists(self.__lockfile):
                    os.remove(self.__lockfile)
                self.__permission_win = os.open(self.__lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            else:  # POSIX
                import fcntl
                self.__permission = open(self.__lockfile, 'w')
                fcntl.lockf(self.__permission, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (OSError, IOError):
            self.__lock_exit()
        self.__locked = True

    def __del__(self):
        if not self.__locked:
            return
        if sys.platform == 'win32':
            os.close(self.__permission_win)
            os.remove(self.__lockfile)
        else:
            import fcntl
            fcntl.lockf(self.__permission, fcntl.LOCK_UN)
            if os.path.isfile(self.__lockfile):
                os.remove(self.__lockfile)

    @staticmethod
    def __lock_exit():
        print(colorama.Fore.RED + colorama.Style.BRIGHT + LOCK_MSG)
        raise LockFileException()
