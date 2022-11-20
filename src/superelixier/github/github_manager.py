"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import re

from superelixier.generic.generic_app import VersionInfo
from superelixier.generic.generic_manager import GenericManager
from superelixier.github.github_app import GithubApp


class GithubManager(GenericManager):
    def __init__(self):
        super().__init__()

    @classmethod
    def build_blob_list(cls, app: GithubApp) -> VersionInfo:
        latest_release = None
        for release in app.api_call:
            if release["prerelease"] and app.prerelease:
                latest_release = release
                break
            if not release["prerelease"]:
                latest_release = release
                break
        my_version = VersionInfo(version_id=latest_release["published_at"], blobs=[])
        for asset in latest_release["assets"]:
            filename = asset["browser_download_url"].split("/")[-1]
            if re.fullmatch(app.blob_re, filename) is not None:
                my_version.blobs.append(asset["browser_download_url"])
        return my_version
