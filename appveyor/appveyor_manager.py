"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import re

from appveyor.appveyor import HEADERS
from appveyor.appveyor_app import AppveyorApp
from generic_app.generic_manager import GenericManager


class AppveyorManager(GenericManager):
    API_URL = "https://ci.appveyor.com/api"

    def __init__(self, cfg_auth):
        super().__init__()
        self._headers = HEADERS
        self._headers["Authorization"] = cfg_auth["appveyor_token"]

    @staticmethod
    def build_blob_list(app: AppveyorApp):
        my_dict = {
            "version_id": app.api_call[0]["created"],
            "blobs": []
        }
        if "blob_re" in app.optionals:
            for asset in app.api_call:
                filename = asset['fileName']
                if re.fullmatch(app.optionals["blob_re"], filename.split("/")[-1]) is not None:
                    my_dict["blobs"].append(AppveyorManager.API_URL + "/buildjobs/" + asset["jobId"] + "/artifacts/" + filename)
        else:
            print(f"{app.name} Error: \"blob_re\" is not configured but is required")
            app.update_status = "failed"
        return my_dict

    @property
    def get_headers(self):
        return self._headers
