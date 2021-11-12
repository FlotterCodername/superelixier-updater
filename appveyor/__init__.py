"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
API_URL = "https://ci.appveyor.com/api"
APPVEYOR_DATE = "%Y-%m-%dT%H:%M:%S"  # API date must be sliced to this. 2021-04-23T20:26:34
HEADERS = {
    "Authorization": "",
    "Content-type": "application/json",
}
