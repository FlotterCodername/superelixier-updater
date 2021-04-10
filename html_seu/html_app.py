"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import html
from urllib.parse import urlparse
import re
from urllib import request as rq
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
        self._version_latest = self.__get_latest_version()

    def __web_request(self):
        request = rq.urlretrieve(self._url)
        return request[0]

    def __get_latest_version(self):
        with open(self._web_call, 'r') as file:
            matches = re.findall(self._blob_re, file.read())
        versions = []
        for match in matches:
            my_dict = {
                "version_id": re.findall(self._version_scheme["re"], match),
                "blobs": [self.__normalize_url(match)]
            }
            versions.append(my_dict)
        version = VersionScheme.get_newest(self._version_scheme, versions)
        return version

    def __normalize_url(self, url):
        url = html.unescape(url)
        host_address = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(self._url))
        host_address_re = "^" + host_address.replace('.', '\\.') + ".*"
        if re.match(host_address_re, url) is None:
            url = host_address + url
        return url

    @property
    def web_call(self):
        return self._web_call
