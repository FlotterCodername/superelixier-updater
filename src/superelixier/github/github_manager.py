"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import re

from dateutil.parser import parse

from superelixier.generic.generic_app import VersionInfo
from superelixier.generic.generic_manager import GenericManager
from superelixier.github.github_app import GithubApp


class GithubManager(GenericManager):
    def __init__(self):
        super().__init__()

    @classmethod
    def build_blob_list(cls, app: GithubApp) -> VersionInfo:
        releases = [i for i in app.api_call]
        if not app.prerelease:
            for r in (i for i in releases if "prerelease" not in i or i["prerelease"]):
                releases.remove(r)
        releases_by_date = {k: None for k in {i["published_at"] for i in releases if i["published_at"] is not None}}
        for r in releases:
            if r["published_at"] is not None:
                if r["published_at"] in releases_by_date:
                    del releases_by_date[r["published_at"]]
                releases_by_date[parse(r["published_at"])] = r
        latest_release = releases_by_date[max(releases_by_date)]
        my_version = VersionInfo(version_id=latest_release["published_at"], blobs=[])
        for asset in latest_release["assets"]:
            filename = asset["browser_download_url"].split("/")[-1]
            if re.fullmatch(app.blob_re, filename) is not None:
                my_version.blobs.append(asset["browser_download_url"])
        return my_version
