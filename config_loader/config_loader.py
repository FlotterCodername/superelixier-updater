"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import json
import os
import sys


class ConfigLoader:

    def __init__(self):
        self._configuration = {}
        cfg_dir = os.path.join(os.path.dirname(sys.argv[0]), "config")
        for cfg in ["auth", "available", "local"]:
            self._configuration[cfg] = json.load(open(os.path.join(cfg_dir, f"{cfg}.json"), 'r'))

    @property
    def configuration(self):
        return self._configuration
