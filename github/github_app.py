"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import colorama
import json
import requests as rest
from datetime import datetime

from generic_app.generic_app import GenericApp
from github.github import HEADERS, GITHUB_DATE


class GithubApp(GenericApp):

    def __init__(self, json_entry: dict, target, token=""):
        super().__init__(json_entry, target)
        self.__headers = HEADERS
        self.__headers["Authorization"] = token
        self._api_call = None
        self._date_latest = None
        # Update status is managed by GithubManager
        self.update_status = "unknown"

    def execute(self):
        """
        Do (network) latency sensitive parts of object creation here.
        """
        self._api_call = self.__web_request()
        self._date_latest = datetime.strptime(self._api_call[0]["published_at"], GITHUB_DATE)

    def __web_request(self):
        releases = rest.get(f"https://api.github.com/repos/{self._user}/{self._project}/releases",
                            headers=self.__headers)
        api_response = json.loads(releases.text)
        if releases.status_code != 200:
            print(colorama.Fore.RED + f'{self.name}: HTTP Status {releases.status_code}: {api_response["message"]}')
            return None
        else:
            return api_response

    @property
    def api_call(self):
        return self._api_call

    @property
    def date_latest(self):
        return self._date_latest
