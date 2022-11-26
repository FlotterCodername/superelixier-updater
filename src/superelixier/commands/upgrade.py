"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import os
from concurrent import futures

from cleo.commands.command import Command
from requests import RequestException
from urllib3.exceptions import HTTPError

from superelixier import configuration
from superelixier.file_handler import FileHandler
from superelixier.generic.generic_app import GenericApp
from superelixier.generic.generic_manager import GenericManager
from superelixier.helper.converters import definition_to_app
from superelixier.helper.filesystem import make_path_native, remove_empty_dirs
from superelixier.helper.terminal import Ansi, print_header, clear

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
        self.__check_updates()
        self.__update_apps()
        self.__pre_exit_cleanup()
        return 100

    def __check_updates(self) -> None:
        project_list: list[GenericApp] = []
        for path in configuration.local:
            native_path = make_path_native(path)
            for list_item in configuration.local[path]:
                norm_name = list_item.casefold()
                if norm_name in configuration.definitions:
                    appconf = configuration.definitions[norm_name]
                    project_list.append(definition_to_app(appconf, target=native_path))

        if self.mt_on:
            with futures.ThreadPoolExecutor(max_workers=8) as executor:
                projects = {executor.submit(self.__report_update_status, project): project for project in project_list}
                for appconf in futures.as_completed(projects):
                    self.line(appconf.result())
                    if projects[appconf].update_status in UPDATE_TRIGGER:
                        self.job_list.append(projects[appconf])
        else:
            for appconf in project_list:
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
