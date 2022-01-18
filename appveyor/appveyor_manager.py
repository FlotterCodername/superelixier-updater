"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import re

from appveyor import API_URL
from appveyor.appveyor_app import AppveyorApp
from generic_app.generic_manager import GenericManager


class AppveyorManager(GenericManager):
    def __init__(self):
        super().__init__()

    @staticmethod
    def build_blob_list(app: AppveyorApp):
        my_dict = {"version_id": app.api_call[0]["created"], "blobs": []}
        for asset in app.api_call:
            filename = asset["fileName"]
            if re.fullmatch(app.blob_re, filename.split("/")[-1]) is not None:
                my_dict["blobs"].append(API_URL + "/buildjobs/" + asset["jobId"] + "/artifacts/" + filename)
        return my_dict
