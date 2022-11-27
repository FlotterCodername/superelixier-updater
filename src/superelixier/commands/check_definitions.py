"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import os
from concurrent.futures import ThreadPoolExecutor

from cleo.commands.command import Command
from cleo.helpers import argument, option
from requests import RequestException
from urllib3.exceptions import HTTPError

from superelixier import configuration
from superelixier.generic.generic_manager import GenericManager
from superelixier.helper.converters import create_app_jobs
from superelixier.helper.environment import DIR_APP


class CheckDefinitions(Command):
    # cleo
    name = "check definitions"
    description = "Check the validity of app definitions in the /definitions directory."
    arguments = [
        argument(name="apps", description="Which app definitions to check (default: all)", optional=True, multiple=True)
    ]
    options = [
        option("static", "s", "Do not try to remote app files, just analyze the definition itself"),
    ]

    def handle(self) -> int:
        ret_code = 0
        arg_apps = self.argument("apps")
        op_s = self.option("static")
        if not arg_apps:
            arg_apps = configuration.definitions.keys()
        app_jobs = create_app_jobs(arg_apps, os.path.join(DIR_APP, ".tmp"), self)
        width = max(len(i.name) for i in app_jobs)
        if not op_s:
            ok = []
            with ThreadPoolExecutor(max_workers=8) as executor:
                for project in app_jobs:
                    executor.submit(self.__check_update_status, project)
            for app in (*app_jobs,):
                p = (width - len(app.name)) * " "
                match app.update_status:
                    case "error" | "unknown":
                        self.line_error(f"<fg=red>{app.name}</>:{p} [!] Unknown problem")
                        continue
                    case "failed":
                        self.line_error(f"<fg=red>{app.name}</>:{p} [!] Could not connect to URL or API")
                        continue
                if not app.version_latest.blobs:
                    ret_code = 1
                    self.line_error(
                        f"<fg=red>{app.name}</>:{p} [!] 0 matching links for version ID {app.version_latest.version_id}"
                    )
                elif len(app.version_latest.blobs) == 1:
                    ok.append(app.name)
                    if self.io.is_verbose():
                        self.line(f"{app.name}:{p} 1 matching links for version ID {app.version_latest.version_id}")
                else:
                    ret_code = 1
                    num, ver_id = len(app.version_latest.blobs), app.version_latest.version_id
                    self.line_error(f"<fg=red>{app.name}</>:{p} [!] {num} matching links for version ID {ver_id}")
            if ok and not self.io.is_verbose():
                self.line("")
                n = "\n"
                self.line(f"OK definitions:{n}- {f'{n}- '.join(ok)}")
            return ret_code

    @classmethod
    def __check_update_status(cls, project):
        # TODO: Duplicate code, refactor
        try:
            project.execute()
            GenericManager.check_update(project)
        except (RequestException, HTTPError):
            project.update_status = "failed"
