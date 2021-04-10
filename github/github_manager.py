"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import json
import os
import re

from github.github import HEADERS
from github.github_app import GithubApp
from version_scheme.version_scheme import VersionScheme


class GithubManager:

    def __init__(self, cfg_auth):
        self._headers = HEADERS
        self._headers["Authorization"] = cfg_auth["github_token"]

    @staticmethod
    def check_update(app: GithubApp):
        if not os.path.isdir(app.appdir):
            app.update_status = "not_installed"
        elif not app.update_status == "failed":
            ver_info_file = os.path.join(app.target_dir, app.name, "superelixier.json")
            if os.path.isfile(ver_info_file):
                with open(ver_info_file, 'r') as file:
                    version_installed = json.load(file)
                comparison = VersionScheme.compare(app.version_scheme, app.version_latest, version_installed)
                if comparison == version_installed:
                    app.update_status = "no_update"
                else:
                    app.update_status = "update"
            else:
                app.update_status = "no_version_file"

    @staticmethod
    def build_blob_list(app: GithubApp):
        my_dict = {
            "version_id": app.api_call[0]["published_at"],
            "blobs": []
        }
        for asset in app.api_call[0]["assets"]:
            filename = asset['browser_download_url'].split("/")[-1]
            if re.fullmatch(app.blob_re, filename) is not None:
                my_dict["blobs"].append(asset["browser_download_url"])
        return my_dict

    @property
    def get_headers(self):
        return self._headers
