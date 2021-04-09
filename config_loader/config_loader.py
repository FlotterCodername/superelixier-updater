"""
Copyright 2021 Fabian H. Schneider
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
