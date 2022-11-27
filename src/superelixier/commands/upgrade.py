"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import os
import textwrap
from concurrent import futures

from cleo.commands.command import Command
from requests import RequestException
from urllib3.exceptions import HTTPError

from superelixier import configuration
from superelixier.configuration import InvalidLocalException, MissingLocalException
from superelixier.file_handler import FileHandler
from superelixier.generic.generic_app import GenericApp
from superelixier.generic.generic_manager import GenericManager
from superelixier.helper.converters import create_app_jobs
from superelixier.helper.filesystem import make_path_native, remove_empty_dirs
from superelixier.helper.terminal import DENT, Ansi, clear, print_header

UX_INSTALLED_NEWER = f"""\
Installed is newer.
{Ansi.RESET}%s: Please make sure your version wasn't retracted because of problems with it."""


UPDATE_TRIGGER = {"update", "no_version_file", "not_installed"}


class Upgrade(Command):
    # cleo
    name = "upgrade"
    description = "Upgrade all apps specified in your configuration (default command)"
    # Upgrade
    job_list = []
    mt_on = True

    # logic
    def handle(self) -> int:
        clear()
        _ = configuration.auth  # Check authentication
        ret_code = 0
        for call in (self.__check_updates, self.__update_apps, self.__pre_exit_cleanup):
            if ret_code == 0:
                ret_code = call() or 0
        return ret_code

    def __check_updates(self) -> int | None:
        app_jobs: list[GenericApp] = []
        try:
            configuration.local
        except (MissingLocalException, InvalidLocalException) as e:
            self.line_error("A valid local.toml file is required for the upgrader.")
            for arg in e.args:
                self.line(textwrap.indent(arg, DENT))
            return -100
        for item in configuration.local.values():
            app_jobs += create_app_jobs(item.apps, item.path, self)
        if self.mt_on:
            with futures.ThreadPoolExecutor(max_workers=8) as executor:
                projects = {executor.submit(self.__report_update_status, project): project for project in app_jobs}
                for appconf in futures.as_completed(projects):
                    self.line(appconf.result())
                    if projects[appconf].update_status in UPDATE_TRIGGER:
                        self.job_list.append(projects[appconf])
        else:
            for appconf in app_jobs:
                self.line(self.__report_update_status(appconf))
                if appconf.update_status in UPDATE_TRIGGER:
                    self.job_list.append(appconf)

    @classmethod
    def __report_update_status(cls, project) -> str:
        try:
            project.execute()
            GenericManager.check_update(project)
        except (RequestException, HTTPError):
            project.update_status = "failed"
        finally:
            return cls.project_status_report(project)

    def __update_apps(self):
        for job in self.job_list:
            my_fsm = FileHandler(job)
            message = f"{job.name}: "
            match job.update_status:
                case "update":
                    message += "Updating"
                    print_header(message, Ansi.GREEN)
                    my_fsm.project_update()
                case "no_version_file":
                    message += "Updating (forced)"
                    print_header(message, Ansi.MAGENTA)
                    my_fsm.project_update()
                case "not_installed":
                    message += "Installing"
                    print_header(message, Ansi.CYAN)
                    my_fsm.project_install()

    @classmethod
    def project_status_report(cls, project: GenericApp):
        match project.update_status:
            case "no_update":
                color = Ansi.BRIGHT
                message = "No update available"
            case "installed_newer":
                color = Ansi.MAGENTA
                message = UX_INSTALLED_NEWER % project.name
            case "update":
                color = Ansi.GREEN
                message = "Update available"
            case "no_version_file":
                color = Ansi.MAGENTA
                message = "Update forced (no valid version info found)"
            case "not_installed":
                color = Ansi.CYAN
                message = "Will be installed"
            case "error":
                color = Ansi.RED
                message = "Could not determine the version installed"
            case "failed":
                color = Ansi.RED
                message = "Could not connect to URL or API"
            case _:
                color = Ansi.RED
                message = "Failed to check this project"
        return f"{color}{project.name}: {message}{Ansi.RESET}"

    @classmethod
    def __pre_exit_cleanup(cls) -> None:
        """
        Remove cache directories created by this program.
        """
        for target in configuration.local:
            cache = os.path.join(make_path_native(target), ".superelixier-cache")
            remove_empty_dirs(cache, delete_top=True)
