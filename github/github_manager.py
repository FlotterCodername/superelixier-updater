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
        # Just a default value for both
        prerelease = app.api_call[0]
        latest_release = app.api_call[0]
        for release in app.api_call:
            if release["prerelease"]:
                prerelease = release
            elif not release["prerelease"]:
                latest_release = release
                break
            else:
                print(f"{app.name} Error: Unexpected value received from GitHub")
                app.update_status = "failed"
        my_dict = {
            "version_id": latest_release["published_at"],
            "blobs": []
        }
        if "blob_re" in app.optionals:
            for asset in latest_release["assets"]:
                filename = asset['browser_download_url'].split("/")[-1]
                if re.fullmatch(app.optionals["blob_re"], filename) is not None:
                    my_dict["blobs"].append(asset["browser_download_url"])
        else:
            print(f"{app.name} Error: \"blob_re\" is not configured but is required")
            app.update_status = "failed"
        return my_dict

    @property
    def get_headers(self):
        return self._headers
