"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import re

from generic_app.generic_manager import GenericManager
from github.github import HEADERS
from github.github_app import GithubApp


class GithubManager(GenericManager):

    def __init__(self, cfg_auth):
        super().__init__()
        self._headers = HEADERS
        self._headers["Authorization"] = cfg_auth["github_token"]

    @staticmethod
    def build_blob_list(app: GithubApp):
        latest_release = None
        for release in app.api_call:
            if release["prerelease"] and app.prerelease:
                latest_release = release
                break
            if not release["prerelease"]:
                latest_release = release
                break
        if latest_release:
            my_dict = {
                "version_id": latest_release["published_at"],
                "blobs": []
            }
            if app.optionals["blob_re"]:
                for asset in latest_release["assets"]:
                    filename = asset['browser_download_url'].split("/")[-1]
                    if re.fullmatch(app.optionals["blob_re"], filename) is not None:
                        my_dict["blobs"].append(asset["browser_download_url"])
                return my_dict
            else:
                print(f"{app.name} Error: \"blob_re\" is not configured but is required")
                return None
        else:
            return None

    @property
    def get_headers(self):
        return self._headers
