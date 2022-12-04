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
from superelixier.definition import Definition
from superelixier.generic.generic_app import GenericApp
from superelixier.github import GITHUB_API
from superelixier.helper.terminal import Ansi


class GithubApp(GenericApp):
    def __init__(self, definition: Definition, target: str = None):
        super().__init__(definition, target)
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
            releases = rest.get(f"{GITHUB_API}/repos/{self.user}/{self.project}/releases", headers=self.headers)
            releases_latest = rest.get(f"{GITHUB_API}/repos/{self.user}/{self.project}/releases/latest", headers=self.headers)
            api_response = json.loads(releases.text)
            api_response_latest = json.loads(releases_latest.text)
            if releases.status_code != 200 or releases_latest.status_code != 200:
                if releases.status_code != 200:
                    print(Ansi.ERROR + self.name + ": HTTP Status %s: %s" % (releases.status_code, api_response["message"]) + Ansi.RESET)
                if releases_latest.status_code != 200:
                    print(Ansi.ERROR + self.name + ": HTTP Status %s: %s" % (releases_latest.status_code, api_response_latest["message"]) + Ansi.RESET)
                return None
            if api_response_latest not in api_response:
                api_response.append(api_response_latest)
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
    def blob_re(self):
        return self.definition.github.blob_re

    @property
    def user(self):
        return self.definition.github.user

    @property
    def prerelease(self):
        return self.definition.github.prerelease

    @property
    def project(self):
        return self.definition.github.project

    @property
    def versioning(self):
        return "github"

    @property
    def headers(self):
        return {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": configuration.auth["github_token"],
            "User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)",
        }
