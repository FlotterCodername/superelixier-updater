"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import json

import requests as rest
from requests import RequestException
from urllib3.exceptions import HTTPError

from superelixier import configuration
from superelixier.generic.generic_app import GenericApp
from superelixier.github import GITHUB_API
from superelixier.helper.terminal import Ansi


class GithubApp(GenericApp):
    def __init__(self, target, **kwargs):
        super().__init__(target, **kwargs)
        self._prerelease = self._prerelease or False
        self._api_call = None

    def execute(self):
        """
        Do (network) latency sensitive parts of object creation here.
        """
        self._api_call = self.__api_request()
        if self._api_call is None:
            self.update_status = "failed"
            return
        self._version_latest = self.__get_latest_version()
        if not self._version_latest:
            self.update_status = "failed"
            return

    def __api_request(self):
        try:
            releases = rest.get(f"{GITHUB_API}/repos/{self._user}/{self._project}/releases", headers=self.headers)
            api_response = json.loads(releases.text)
            if releases.status_code != 200:
                print(Ansi.ERROR + self.name + ": HTTP Status %s: %s" % (releases.status_code, api_response["message"]))
                return None
        except (RequestException, HTTPError):
            return None
        return api_response

    def __get_latest_version(self):
        from superelixier.github.github_manager import GithubManager

        my_list = GithubManager.build_blob_list(self)
        return my_list

    @property
    def api_call(self):
        return self._api_call

    @property
    def headers(self):
        return {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": configuration.auth["github_token"],
            "User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)",
        }
