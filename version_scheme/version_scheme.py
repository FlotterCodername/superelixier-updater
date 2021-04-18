"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
from datetime import datetime

from github.github import GITHUB_DATE


class VersionScheme:

    @staticmethod
    def get_newest(scheme: dict, versions: list):
        if len(versions) == 0:
            return {"version": "", "blobs": []}
        else:
            latest_version = versions[0]
            for version in versions:
                latest_version = VersionScheme.compare(scheme, latest_version, version)
            return latest_version

    @staticmethod
    def compare(scheme: dict, old: dict, new: dict):
        latest_version = old
        if scheme["type"] == "integer":
            if new["version_id"] > old["version_id"]:
                latest_version = new
        if scheme["type"] == "appveyor":
            # TODO: Actually check date, not just neq
            if new["version_id"] != old["version_id"]:
                latest_version = new
        if scheme["type"] == "github":
            new_version_id = datetime.strptime(new["version_id"], GITHUB_DATE)
            old_version_id = datetime.strptime(old["version_id"], GITHUB_DATE)
            if new_version_id > old_version_id:
                latest_version = new
        if scheme["type"] == tuple:
            # TODO: Actually check tuple, not just neq
            if new["version_id"] != old["version_id"]:
                latest_version = new
            pass
        return latest_version
