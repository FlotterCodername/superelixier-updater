"""
Copyright 2021 Fabian H. Schneider
"""
import colorama
import json
import main
import requests as rest
import os
from datetime import datetime
from github.github import HEADERS, GITHUB_DATE


class GithubProject:

    def __init__(self, json_entry: dict, target):
        self.__headers = HEADERS
        self.__headers["Authorization"] = main.github_token
        # Props from JSON
        self._name = json_entry["name"]
        self._user = json_entry["user"]
        self._project = json_entry["project"]
        self._blob_re = json_entry["blob_re"]
        self._blob_unwanted = json_entry["blob_unwanted"]
        self._appdatas = json_entry["appdatas"]
        # Runtime props
        self._project_dir = os.path.join(target, self._name)
        self._api_call = self.__web_request()
        self._date_latest = datetime.strptime(self._api_call[0]["published_at"], GITHUB_DATE)
        # Update status will be updated by GithubManager
        self.update_status = "unknown"

    def __web_request(self):
        releases = rest.get(f"https://api.github.com/repos/{self._user}/{self._project}/releases", headers=self.__headers)
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
    def project_dir(self):
        return self._project_dir

    @property
    def date_latest(self):
        return self._date_latest
