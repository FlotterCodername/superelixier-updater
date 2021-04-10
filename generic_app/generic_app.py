"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import os
import random
import string


class GenericApp:

    def __init__(self, json_entry: dict, target):
        """
        Do not instantiate this. Always use the child classes.

        :param json_entry:
        :param target:
        """
        # Props from JSON
        self._name = json_entry["name"]
        self._blob_re = json_entry["blob_re"]
        self._blob_unwanted = json_entry["blob_unwanted"]
        self._appdatas = json_entry["appdatas"]
        # Runtime props
        self._appdir = os.path.join(target, json_entry["name"])
        self._target_dir = target
        self._api_call = None
        self._date_latest = None
        self._random_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=32))
        # Update status managed by child classes
        self.update_status = "unknown"

    @property
    def name(self):
        return self._name

    @property
    def blob_re(self):
        return self._blob_re

    @property
    def blob_unwanted(self):
        return self._blob_unwanted

    @property
    def appdatas(self):
        return self._appdatas

    @property
    def appdir(self):
        return self._appdir

    @property
    def target_dir(self):
        return self._target_dir

    @property
    def random_id(self):
        return self._random_id
