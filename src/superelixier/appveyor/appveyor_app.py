"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import json
import textwrap

import requests as rest
from requests import RequestException
from urllib3.exceptions import HTTPError

from superelixier import configuration
from superelixier.appveyor import API_URL
from superelixier.generic.generic_app import GenericApp
from superelixier.helper.terminal import DENT, Ansi
from superelixier.helper.types import JsonResponse


class AppveyorApp(GenericApp):
    def __init__(self, target: str, **kwargs: dict):
        super().__init__(target, **kwargs)
        self._branch: str = self._branch or "master"
        self._api_call: JsonResponse = None

    def execute(self):
        """
        Do (network) latency sensitive parts of object creation here.
        """
        self._api_call = self.__api_request()
        if self._api_call is None:
            self.update_status = "failed"
        else:
            self._version_latest = self.__get_latest_version()

    def __api_request(self) -> JsonResponse:
        try:
            api_response = rest.get(
                f"{API_URL}/projects/{self._user}/{self._project}/history?recordsNumber=20",
                headers=self.headers,
            )
            if api_response.status_code != 200:
                msg = textwrap.dedent(
                    f"""\
                    {Ansi.ERROR}{self.name}: HTTP Status {api_response.status_code}:
                    {textwrap.indent(json.loads(api_response.text)['message'], DENT)}"""
                )
                print(msg)
                return None
            history = json.loads(api_response.text)["builds"]
            job_id = None
            for build in history:
                if job_id:
                    break
                if build["status"] == "success" and build["branch"] == self._branch:
                    api_response = rest.get(
                        f"{API_URL}/projects/{self._user}/{self._project}/builds/{build['buildId']}"
                    )
                    if api_response.status_code == 200:
                        jobs = json.loads(api_response.text)["build"]["jobs"]
                        for job in jobs:
                            if job["status"] == "success":
                                job_id = job["jobId"]
                                break
            if job_id:
                artifacts = rest.get(f"{API_URL}/buildjobs/{job_id}/artifacts")
            else:
                return None
            api_response = json.loads(artifacts.text)
            if artifacts.status_code != 200:
                print(f"{Ansi.ERROR}{self.name}: HTTP Status {artifacts.status_code}: {api_response['message']}")
                return None
            # Handle hypothetical case where successful build has no artifacts. The JSON response would be []:
            if len(api_response) == 0:
                return None
            for file in api_response:
                file["jobId"] = job_id
        except (RequestException, HTTPError):
            return None
        return api_response

    def __get_latest_version(self) -> dict:
        from superelixier.appveyor.appveyor_manager import AppveyorManager

        my_list = AppveyorManager.build_blob_list(self)
        return my_list

    @property
    def api_call(self) -> JsonResponse:
        return self._api_call

    @property
    def headers(self):
        return {"Authorization": configuration.auth, "Content-type": "application/json"}
