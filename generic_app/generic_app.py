"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import os
import random
import string

from version_scheme.version_scheme import VersionScheme


class GenericApp:

    def __init__(self, json_entry: dict, target: str):
        """
        Do not instantiate this. Always use the child classes.

        :param json_entry:
        :param target:
        """
        # Props from JSON
        self._url = None
        self._name = json_entry["name"]
        self._optionals = {}
        optional_keys = ["blob_re", "blob_permalink", "installer", "branch", "prerelease"]
        self.__set_optionals(json_entry, optional_keys)
        self._blob_unwanted = json_entry["blob_unwanted"]
        self._appdatas = json_entry["appdatas"]
        # Runtime props
        self._appdir = os.path.join(target, json_entry["name"])
        self._target_dir = target
        self._version_latest = {}
        self._version_scheme = VersionScheme()
        self._random_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=32))
        # Update status managed by manager classes
        self.update_status = "unknown"

    def __set_optionals(self, json_entry: dict, optional_keys: list):
        for key in optional_keys:
            if key in json_entry:
                self._optionals.update({key: json_entry[key]})
            else:
                self._optionals.update({key: None})

    @property
    def name(self):
        return self._name

    @property
    def optionals(self):
        return self._optionals

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
    def url(self):
        return self._url

    @property
    def version_latest(self):
        return self._version_latest

    @property
    def version_scheme(self):
        return self._version_scheme

    @property
    def random_id(self):
        return self._random_id
