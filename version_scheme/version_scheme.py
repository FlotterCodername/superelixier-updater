"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
from datetime import datetime
from appveyor import APPVEYOR_DATE
from github import GITHUB_DATE
from packaging import version


class VersionScheme:

    def __init__(self, *, is_type: str = 'noupdate', spec: int = 0, version_re: str = None):
        self.__is_type = is_type
        self.__version_re = version_re
        self.__spec = spec

    @property
    def is_type(self):
        return self.__is_type

    @property
    def version_re(self):
        return self.__version_re

    @property
    def spec(self):
        return self.__spec


def get_newest(scheme: VersionScheme, versions: list):
    if len(versions) == 0:
        return {"version": "", "blobs": []}
    else:
        latest_version = versions[0]
        for my_version in versions:
            latest_version = compare(scheme, latest_version, my_version)
        return latest_version


def compare(scheme: VersionScheme, old: dict, new: dict):
    """
    When in doubt, this should return the 'new' version so that the app will be updated to what is currently advertised on the remote site, if nothing else.
    :param scheme:
    :param old:
    :param new:
    :return:
    """
    latest_version = old
    try:
        if scheme.is_type == "id":
            if new["version_id"] != old["version_id"]:
                latest_version = new
        elif scheme.is_type == "integer":
            if new["version_id"] > old["version_id"]:
                latest_version = new
        elif scheme.is_type == "tuple":
            if version.parse(new["version_id"]) > version.parse(old["version_id"]):
                latest_version = new
        elif scheme.is_type == "appveyor":
            new_version_id = slice_appveyor_date(new["version_id"])
            old_version_id = slice_appveyor_date(old["version_id"])
            if new_version_id > old_version_id:
                latest_version = new
        elif scheme.is_type == "github":
            new_version_id = datetime.strptime(new["version_id"], GITHUB_DATE)
            old_version_id = datetime.strptime(old["version_id"], GITHUB_DATE)
            if new_version_id > old_version_id:
                latest_version = new
        return latest_version
    except KeyError:
        return None


def slice_appveyor_date(datestr: str):
    datestr = datestr.split(".")[0]
    datestr_date = datetime.strptime(datestr, APPVEYOR_DATE)
    return datestr_date
