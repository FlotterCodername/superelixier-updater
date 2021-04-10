"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
from urllib import request as rq
from generic_app.generic_app import GenericApp


class HTMLApp(GenericApp):

    def __init__(self, json_entry: dict, target):
        super().__init__(json_entry, target)
        self._url = json_entry["url"]
        self._web_call = None
        self._version_latest = None
        # Update status is managed by HTMLManager
        self.update_status = "unknown"

    def execute(self):
        """
        Do (network) latency sensitive parts of object creation here.
        """
        self._web_call = self.__web_request()
        self._version_latest = {}

    def __web_request(self):
        rq.urlretrieve(self._url, f"{self._name}.html")
        return {}

    @property
    def web_call(self):
        return self._web_call

    @property
    def version_latest(self):
        return self._version_latest
