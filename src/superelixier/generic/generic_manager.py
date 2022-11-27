"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import os
from datetime import datetime

from superelixier.generic.generic_app import GenericApp, VersionInfo, UPDATER_JSON_SPEC


class GenericManager:
    @classmethod
    def check_update(cls, app: GenericApp):
        """
        Checks the local installation and any deferred updates against what has been determined to be the latest version
        on the remote site. Based on that, set update status that governs the appropriate course of action.
        :param app:
        """
        if app.update_status == "failed":
            return
        if not os.path.isdir(app.appdir):
            app.update_status = "not_installed"
            return
        ver_info_file = os.path.join(app.target_dir, app.name, "superelixier.json")
        if not os.path.isfile(ver_info_file):
            app.update_status = "no_version_file"
            return
        if app.definition.repo_type != app.version_installed.repo:
            app.update_status = "update"
            return
        if app.versioning == "id":
            if app.version_latest.version_id != app.version_installed.version_id:
                app.update_status = "update"
            else:
                app.update_status = "no_update"
            return
        comparison = GenericManager.compare(app.versioning, app.version_latest, app.version_installed)
        if comparison:
            if comparison.version_id == app.version_installed.version_id:
                if comparison.version_id != app.version_latest.version_id:
                    if UPDATER_JSON_SPEC > app.version_installed.spec:
                        app.update_status = "update"
                    else:
                        app.update_status = "installed_newer"
                else:
                    app.update_status = "no_update"
            else:
                app.update_status = "update"
        else:
            app.update_status = "unknown"

    @classmethod
    def compare(cls, versioning: str, old: VersionInfo, new: VersionInfo):
        """
        When in doubt, this should return the 'new' version so that the app will be updated to what is currently
        advertised on the remote site, if nothing else.
        """
        latest_version = old
        try:
            match versioning:
                case "id":
                    if new.version_id != old.version_id:
                        latest_version = new
                case "integer":
                    if new.version_id > old.version_id:
                        latest_version = new
                case "tuple":
                    from packaging import version

                    if version.parse(new.version_id) > version.parse(old.version_id):
                        latest_version = new
                case "appveyor":
                    new_version_id = GenericManager.slice_appveyor_date(new.version_id)
                    old_version_id = GenericManager.slice_appveyor_date(old.version_id)
                    if new_version_id > old_version_id:
                        latest_version = new
                case "github":
                    from superelixier.github import GITHUB_DATE

                    new_version_id = datetime.strptime(new.version_id, GITHUB_DATE)
                    old_version_id = datetime.strptime(old.version_id, GITHUB_DATE)
                    if new_version_id > old_version_id:
                        latest_version = new
            return latest_version
        except KeyError:
            return None

    @classmethod
    def get_newest(cls, versioning, versions: list[VersionInfo]):
        if len(versions) == 0:
            return VersionInfo("", [])
        else:
            latest_version = versions[0]
            for my_version in versions:
                latest_version = GenericManager.compare(versioning, latest_version, my_version)
            return latest_version

    @classmethod
    def slice_appveyor_date(cls, datestr: str):
        from superelixier.appveyor import APPVEYOR_DATE

        datestr = datestr.split(".")[0]
        datestr_date = datetime.strptime(datestr, APPVEYOR_DATE)
        return datestr_date
