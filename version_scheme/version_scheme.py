"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
from datetime import datetime
from github.github import GITHUB_DATE
from packaging import version


class VersionScheme:

    @staticmethod
    def get_newest(scheme: dict, versions: list):
        if len(versions) == 0:
            return {"version": "", "blobs": []}
        else:
            latest_version = versions[0]
            for my_version in versions:
                latest_version = VersionScheme.compare(scheme, latest_version, my_version)
            return latest_version

    @staticmethod
    def compare(scheme: dict, old: dict, new: dict):
        """
        When in doubt, this should return the 'new' version so that the app will be updated to what is currently advertised on the remote site, if nothing else.
        :param scheme:
        :param old:
        :param new:
        :return:
        """
        latest_version = old
        if scheme["type"] == "id":
            if new["version_id"] != old["version_id"]:
                latest_version = new
        elif scheme["type"] == "integer":
            if new["version_id"] > old["version_id"]:
                latest_version = new
        elif scheme["type"] == "tuple":
            if version.parse(new["version_id"]) > version.parse(old["version_id"]):
                latest_version = new
        elif scheme["type"] == "appveyor":
            # TODO: Actually check date, not just neq
            if new["version_id"] != old["version_id"]:
                latest_version = new
        elif scheme["type"] == "github":
            new_version_id = datetime.strptime(new["version_id"], GITHUB_DATE)
            old_version_id = datetime.strptime(old["version_id"], GITHUB_DATE)
            if new_version_id > old_version_id:
                latest_version = new
        return latest_version
