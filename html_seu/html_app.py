"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import re
import requests as rest
from urllib3.exceptions import RequestError

from file_handler.downloader import Downloader
from generic_app.generic_app import GenericApp
from version_scheme.version_scheme import VersionScheme


class HTMLApp(GenericApp):

    def __init__(self, json_entry: dict, target):
        super().__init__(json_entry, target)
        self._url = json_entry["url"]
        self._version_scheme = json_entry["version_scheme"]
        self._web_call = None

    def execute(self):
        """
        Do (network) latency sensitive parts of object creation here.
        """
        self._web_call = self.__web_request()
        if self._web_call is None:
            self.update_status = "failed"
        else:
            self._version_latest = self.__get_latest_version()

    def __web_request(self):
        try:
            header = {'User-Agent': 'Superelixier Updater (Contact: @FroyoXSG on GitHub)'}
            request = rest.get(self._url, headers=header)
            if request.status_code != 200:
                return None
        except (rest.exceptions.ConnectionError, RequestError):
            return None
        return request.text

    def __get_latest_version(self):
        versions = []
        if "blob_permalink" in self._optionals:
            matches = re.findall(self._version_scheme["re"], self._web_call)
            for match in matches:
                my_dict = {
                    "version_id": match,
                    "blobs": [self._optionals["blob_permalink"]]
                }
                versions.append(my_dict)
        elif "blob_re" in self._optionals:
            matches = re.findall(self._optionals["blob_re"], self._web_call)
            for match in matches:
                re_match = re.search(self._version_scheme["re"], match).group(1)
                my_dict = {
                    "version_id": re_match,
                    "blobs": [Downloader.normalize_url(match, self._url)]
                }
                versions.append(my_dict)
        version = VersionScheme.get_newest(self._version_scheme, versions)
        return version

    @property
    def web_call(self):
        return self._web_call
