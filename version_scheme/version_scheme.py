"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""


class VersionScheme:

    @staticmethod
    def get_newest(scheme: dict, versions: list):
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
        if scheme["type"] == "github":
            if new["version_id"] > old["version_id"]:
                latest_version = new
        if scheme["type"] == tuple:
            # TODO
            pass
        return latest_version
