"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import json
import os
from datetime import datetime

from generic_app.generic_app import GenericApp


class GenericManager:

    @staticmethod
    def check_update(app: GenericApp):
        """
        Checks the local installation and any deferred updates against what has been determined to be the latest version on the remote site.
        Based on that, set update status that governs the appropriate course of action.
        :param app:
        :return:
        """
        if not os.path.isdir(app.appdir) and not app.update_status == "failed":
            app.update_status = "not_installed"
        elif not app.update_status == "failed":
            ver_info_file = os.path.join(app.target_dir, app.name, "superelixier.json")
            if os.path.isfile(ver_info_file):
                with open(ver_info_file, 'r') as file:
                    version_installed = json.load(file)
                if 'spec' not in version_installed:
                    version_installed['spec'] = 0
                comparison = GenericManager.compare(app.ver_scheme_type, app.version_latest, version_installed)
                if comparison:
                    if comparison["version_id"] == version_installed["version_id"]:
                        if comparison["version_id"] != app.version_latest["version_id"]:
                            if app.ver_scheme_spec > version_installed['spec']:
                                app.update_status = 'update'
                            else:
                                app.update_status = "installed_newer"
                        else:
                            app.update_status = "no_update"
                    else:
                        app.update_status = "update"
                else:
                    app.update_status = "unknown"
            else:
                app.update_status = "no_version_file"

    @staticmethod
    def compare(ver_scheme_type: str, old: dict, new: dict):
        """
        When in doubt, this should return the 'new' version so that the app will be updated to what is currently advertised on the remote site, if nothing else.
        :return:
        """
        latest_version = old
        try:
            if ver_scheme_type == "id":
                if new["version_id"] != old["version_id"]:
                    latest_version = new
            elif ver_scheme_type == "integer":
                if new["version_id"] > old["version_id"]:
                    latest_version = new
            elif ver_scheme_type == "tuple":
                from packaging import version
                if version.parse(new["version_id"]) > version.parse(old["version_id"]):
                    latest_version = new
            elif ver_scheme_type == "appveyor":
                new_version_id = GenericManager.slice_appveyor_date(new["version_id"])
                old_version_id = GenericManager.slice_appveyor_date(old["version_id"])
                if new_version_id > old_version_id:
                    latest_version = new
            elif ver_scheme_type == "github":
                from github import GITHUB_DATE
                new_version_id = datetime.strptime(new["version_id"], GITHUB_DATE)
                old_version_id = datetime.strptime(old["version_id"], GITHUB_DATE)
                if new_version_id > old_version_id:
                    latest_version = new
            return latest_version
        except KeyError:
            return None

    @staticmethod
    def get_newest(ver_scheme_type, versions: list):
        if len(versions) == 0:
            return {"version": "", "blobs": []}
        else:
            latest_version = versions[0]
            for my_version in versions:
                latest_version = GenericManager.compare(ver_scheme_type, latest_version, my_version)
            return latest_version

    @staticmethod
    def slice_appveyor_date(datestr: str):
        from appveyor import APPVEYOR_DATE
        datestr = datestr.split(".")[0]
        datestr_date = datetime.strptime(datestr, APPVEYOR_DATE)
        return datestr_date
