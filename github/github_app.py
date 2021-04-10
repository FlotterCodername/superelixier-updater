"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import colorama
import json
import os
import random
import requests as rest
import string
from datetime import datetime
from github.github import HEADERS, GITHUB_DATE


class GithubApp:

    def __init__(self, json_entry: dict, target, token=""):
        self.__headers = HEADERS
        self.__headers["Authorization"] = token
        # Props from JSON
        self._name = json_entry["name"]
        self._user = json_entry["user"]
        self._project = json_entry["project"]
        self._blob_re = json_entry["blob_re"]
        self._blob_unwanted = json_entry["blob_unwanted"]
        self._appdatas = json_entry["appdatas"]
        # Runtime props
        self._appdir = os.path.join(target, json_entry["name"])
        self._target_dir = target
        self._api_call = None
        self._date_latest = None
        self._random_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=32))
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
    def name(self):
        return self._name

    @property
    def user(self):
        return self._user

    @property
    def project(self):
        return self._project

    @property
    def blob_re(self):
        return self._blob_re

    @property
    def blob_unwanted(self):
        return self._blob_unwanted

    @property
    def appdatas(self):
        return self._appdatas

    @property
    def api_call(self):
        return self._api_call

    @property
    def appdir(self):
        return self._appdir

    @property
    def target_dir(self):
        return self._target_dir

    @property
    def date_latest(self):
        return self._date_latest

    @property
    def random_id(self):
        return self._random_id
