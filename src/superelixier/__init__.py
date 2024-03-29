"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
from importlib.metadata import version

from packaging.version import parse

from superelixier.configuration import configuration  # noqa

__all__ = ["__version__", "__version_obj__", "configuration", "runtime"]

__version__ = version(__name__)
__version_obj__ = parse(__version__)


class Runtime:
    __instance__ = {}

    def __init__(self):
        if self.__instance__ == {}:
            self.__instance__ = self.__dict__
            self.interaction: bool = True
            self.locked: bool = False
        else:
            self.__instance__ = self.__dict__


runtime = Runtime()
