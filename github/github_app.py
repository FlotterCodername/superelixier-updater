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
from github.github import GITHUB_DATE
from github.github_manager import GithubManager


class GithubApp(GenericApp):

    def __init__(self, json_entry: dict, target, headers):
        super().__init__(json_entry, target)
        self.__headers = headers
        self._user = json_entry["user"]
        self._project = json_entry["project"]
        self._api_call = None
        self._version_scheme["type"] = "github"

    def execute(self):
        """
        Do (network) latency sensitive parts of object creation here.
        """
        self._api_call = self.__api_request()
        self._version_latest = datetime.strptime(self._api_call[0]["published_at"], GITHUB_DATE)

    def __api_request(self):
        releases = rest.get(f"https://api.github.com/repos/{self._user}/{self._project}/releases",
                            headers=self.__headers)
        api_response = json.loads(releases.text)
        if releases.status_code != 200:
            print(colorama.Fore.RED + f'{self.name}: HTTP Status {releases.status_code}: {api_response["message"]}')
            return None
        else:
            return api_response

    def __get_latest_version(self):
        my_list = GithubManager.build_blob_list(self)
        return my_list

    @property
    def user(self):
        return self._user

    @property
    def project(self):
        return self._project

    @property
    def api_call(self):
        return self._api_call
