"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import json
import os

from html.html_app import HTMLApp
from version_scheme.version_scheme import VersionScheme


class HTMLManager:

    def __init__(self):
        pass

    @staticmethod
    def check_update(app: HTMLApp):
        if not os.path.isdir(app.appdir):
            app.update_status = "not_installed"
        elif not app.update_status == "failed":
            ver_info_file = os.path.join(app.target_dir, app.name, "superelixier.json")
            if os.path.isfile(ver_info_file):
                with open(ver_info_file, 'r') as file:
                    version_installed = json.load(file)
                comparison = VersionScheme.compare(app.version_scheme, app.version_latest, version_installed)
                if comparison == version_installed:
                    app.update_status = "no_update"
                else:
                    app.update_status = "update"
            else:
                app.update_status = "no_version_file"

    @property
    def get_headers(self):
        return self._headers
