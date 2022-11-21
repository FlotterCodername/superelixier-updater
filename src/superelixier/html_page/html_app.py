"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import re

import requests as rest
from requests import RequestException
from urllib3.exceptions import HTTPError

from superelixier.definition import Definition
from superelixier.file_handler.downloader import Downloader
from superelixier.generic.generic_app import GenericApp, VersionInfo
from superelixier.generic.generic_manager import GenericManager
from superelixier.html_page import HEADERS


class HTMLApp(GenericApp):
    def __init__(self, definition: Definition, target: str = None):
        super().__init__(definition, target)
        self._url = self.definition.html.url
        self._versioning = self.definition.html.versioning
        self._blob_re = self.definition.html.blob_re
        self._blob_permalink = self.definition.html.blob_permalink
        self._blob_permalink_re = self.definition.html.blob_permalink_re
        self._versioning_spec = self.definition.html.versioning_spec
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
                print(f"Error checking {self.name}: {e.__class__.__name__}")
                self.update_status = "unknown"

    def __web_request(self):
        try:
            request = rest.get(self._url, headers=HEADERS)
            if request.status_code != 200:
                return None
        except (RequestException, HTTPError):
            return None
        return request.text

    def __get_latest_version(self):
        versions: list[VersionInfo] = []
        if self._blob_permalink:
            matches = re.findall(self._blob_permalink_re, self._web_call)
            for match in matches:
                versions.append(VersionInfo(version_id=match, blobs=[self._blob_permalink]))
        elif self._blob_re:
            matches = re.finditer(self._blob_re, self._web_call)
            for match in matches:
                versions.append(
                    VersionInfo(
                        version_id=match.group("ver"), blobs=[Downloader.normalize_url(match.group("url"), self._url)]
                    )
                )
        version = GenericManager.get_newest(self._versioning, versions)
        return version

    @property
    def versioning(self):
        return self.definition.html.versioning

    @property
    def web_call(self):
        return self._web_call
