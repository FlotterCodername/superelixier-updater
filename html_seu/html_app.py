"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import re

import requests as rest
from requests import HTTPError

from file_handler.downloader import Downloader
from generic_app.generic_app import GenericApp
from generic_app.generic_manager import GenericManager
from html_seu import HEADERS


class HTMLApp(GenericApp):
    def __init__(self, target, **kwargs):
        super().__init__(target, **kwargs)
        self._web_call = None

    def execute(self):
        """
        Do (network) latency sensitive parts of object creation here.
        """
        self._web_call = self.__web_request()
        if self._web_call is None:
            self.update_status = "failed"
        else:
            try:
                self._version_latest = self.__get_latest_version()
            except Exception as e:
                print(f"Error checking {self.name}: {type(e)}: {e}")
                self.update_status = "unknown"

    def __web_request(self):
        try:
            request = rest.get(self._url, headers=HEADERS)
            if request.status_code != 200:
                return None
        except (ConnectionError, HTTPError):
            return None
        return request.text

    def __get_latest_version(self):
        versions = []
        if self.blob_permalink:
            matches = re.findall(self.ver_scheme_re, self._web_call)
            for match in matches:
                my_dict = {"version_id": match, "blobs": [self.blob_permalink]}
                versions.append(my_dict)
        elif self.blob_re:
            matches = re.finditer(self.blob_re, self._web_call)
            for match in matches:
                my_dict = {
                    "version_id": match.group("ver"),
                    "blobs": [Downloader.normalize_url(match.group("url"), self._url)],
                }
                versions.append(my_dict)
        version = GenericManager.get_newest(self._ver_scheme_type, versions)
        return version

    @property
    def web_call(self):
        return self._web_call
