"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import re

from superelixier.appveyor import API_URL
from superelixier.appveyor.appveyor_app import AppveyorApp
from superelixier.generic.generic_app import VersionInfo
from superelixier.generic.generic_manager import GenericManager


class AppveyorManager(GenericManager):
    def __init__(self):
        super().__init__()

    @classmethod
    def build_blob_list(cls, app: AppveyorApp) -> VersionInfo:
        my_version = VersionInfo(version_id=app.api_call[0]["created"], blobs=[])
        for asset in app.api_call:
            filename = asset["fileName"]
            if re.fullmatch(app.blob_re, filename.split("/")[-1]) is not None:
                my_version.blobs.append(API_URL + "/buildjobs/" + asset["jobId"] + "/artifacts/" + filename)
        return my_version
