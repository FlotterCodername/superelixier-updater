"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
##############
# UNFINISHED #
##############
import json
from typing import Tuple, Optional, Dict

import requests as rest
from requests import HTTPError

import config_handler.config_handler
import settings
from github import GITHUB_API
from github.github_app import GithubApp
from helper.terminal import ERROR


def __query_artifacts(page: int = 1, per_page: int = 30, total_count: int = None) -> Tuple[Optional[Dict], Optional[bool], Optional[int]]:
    try:
        if page < 1 or per_page < 1:
            print(ERROR + ": Illegal usage passed to in __query_artifacts")
            raise ValueError
        artifacts = rest.get(
            # f"{GITHUB_API}/repos/{self._user}/{self._project}/actions/artifacts", headers=settings.github_headers, params={"page": page, "per_page": per_page}
            f"{GITHUB_API}/repos/hrydgard/ppsspp/actions/artifacts", headers=settings.github_headers, params={"page": page, "per_page": per_page}
        )
        api_response = json.loads(artifacts.text)
        if artifacts.status_code != 200:
            # print(ERROR + self.name + ": HTTP Status %s: %s" % (artifacts.status_code, api_response["message"]))
            print(ERROR + "HTTP Status %s: %s" % (artifacts.status_code, api_response["message"]))
            return None, None, total_count
        more = True
        if total_count == page-1 * per_page + len(api_response["artifacts"]):
            more = False
        total_count = api_response["total_count"]
        return api_response, more, total_count
    except (KeyError, ValueError, ConnectionError, HTTPError):
        return None, None, total_count


def __get_artifact_url(artifact_id: int, archive_format: str = "zip"):
    try:
        artifact = rest.get(
            # f"{GITHUB_API}/repos/{self._user}/{self._project}/artifacts/{artifact_id}/{archive_format}", headers=settings.github_headers
            f"{GITHUB_API}/repos/hrydgard/ppsspp/actions/artifacts/{artifact_id}/{archive_format}", headers=settings.github_headers
        )
        api_response = json.loads(artifact.text)
        if artifact.status_code != 200:
            # print(ERROR + self.name + ": HTTP Status %s: %s" % (artifacts.status_code, api_response["message"]))
            print(ERROR + "HTTP Status %s: %s" % (artifact.status_code, api_response["message"]))
            return None
    except (KeyError, ValueError, ConnectionError, HTTPError):
        return None
    return api_response


class GithubActionsApp(GithubApp):
    pass


if __name__ == '__main__':
    config_handler.config_handler.ConfigHandler()
    q, m, t = __query_artifacts()
    # print(json.dumps(q, indent=4))
    a = q["artifacts"][0]
    r = __get_artifact_url(a["id"])
    print(r)
