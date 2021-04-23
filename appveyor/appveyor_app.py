"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import colorama
import json
import requests as rest
from urllib3.exceptions import RequestError

from generic_app.generic_app import GenericApp


class AppveyorApp(GenericApp):
    API_URL = "https://ci.appveyor.com/api"

    def __init__(self, json_entry: dict, target, headers):
        super().__init__(json_entry, target)
        self.__headers = headers
        self._user = json_entry["user"]
        self._project = json_entry["project"]
        self._api_call = None
        self._version_scheme["type"] = "appveyor"

    def execute(self):
        """
        Do (network) latency sensitive parts of object creation here.
        """
        self._api_call = self.__api_request()
        if self._api_call is None:
            self.update_status = "failed"
        else:
            self._version_latest = self.__get_latest_version()

    def __api_request(self):
        try:
            jobs = rest.get(f"{AppveyorApp.API_URL}/projects/{self._user}/{self._project}",
                            headers=self.__headers)
            api_response = json.loads(jobs.text)
            if jobs.status_code != 200:
                print(colorama.Fore.RED + f'{self.name}: HTTP Status {jobs.status_code}: {api_response["message"]}')
                return None
            job_id = api_response["build"]["jobs"][0]["jobId"]
            artifacts = rest.get(f"{AppveyorApp.API_URL}/buildjobs/{job_id}/artifacts")
            api_response = json.loads(artifacts.text)
            if artifacts.status_code != 200:
                print(colorama.Fore.RED + f'{self.name}: HTTP Status {artifacts.status_code}: {api_response["message"]}')
                return None
            # If a build has no artifacts on Appveyor, the JSON response will be []:
            if len(api_response) == 0:
                # TODO: Ability to get last successful build if newest one has failed.
                self.update_status = "failed"
            for file in api_response:
                file["jobId"] = job_id
        except (rest.exceptions.ConnectionError, RequestError):
            return None
        return api_response

    def __get_latest_version(self):
        from appveyor.appveyor_manager import AppveyorManager
        my_list = AppveyorManager.build_blob_list(self)
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
