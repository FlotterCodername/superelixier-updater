"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import os
import sys

IS_PYINSTALLER = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")
if IS_PYINSTALLER:
    DIR_APP: str = os.path.abspath(os.path.dirname(sys.executable))
else:
    DIR_APP: str = os.path.abspath(os.path.join(__file__, "..", "..", "..", ".."))
DIR_CFG: str = os.path.join(DIR_APP, "config")
