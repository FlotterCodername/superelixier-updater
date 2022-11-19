"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import os
import sys
import time
import traceback
from concurrent import futures

from requests import RequestException
from urllib3.exceptions import HTTPError

from superelixier import configuration
from superelixier.appveyor.appveyor_app import AppveyorApp
from superelixier.config_handler.eula import check_eula
from superelixier.environment_handler import LockFile, LockFileException
from superelixier.file_handler import FileHandler
from superelixier.generic.generic_app import GenericApp
from superelixier.generic.generic_manager import GenericManager
from superelixier.github.github_app import GithubApp
from superelixier.helper.filesystem import make_path_native, remove_empty_dirs
from superelixier.helper.terminal import Ansi, color_handling, exit_app, print_header
from superelixier.html.html_app import HTMLApp


def main():
    try:
        try:
            color_handling()
            lock = LockFile()  # noqa
            check_eula()
            superelixier_updater = Program()
            superelixier_updater.execute()
            del lock
            exit_app()
        except LockFileException:
            time.sleep(7)
    except Exception:  # noqa
        color_handling(init=False)
        print_header("superelixier crashed!")
        tb = f"{Ansi.RED}{traceback.format_exc().strip()}{Ansi.RESET}"
        print("(╯°□°)╯︵ ┻━┻", "\n", tb, "\n", "┬─┬ノ( º _ ºノ)")
        exit_app()
    finally:
        color_handling(init=False)
        sys.exit()


class Program:
    __MT_ON = True
    __UPDATE_TRIGGER = {"update", "no_version_file", "not_installed"}

    def __init__(self):
        self.job_list = []

    def execute(self) -> None:
        """
        The execute() methods in the project are supposed to provide an idea of what the class does in a nutshell.
        Always put them directly after __init__().
        """
        self.__check_updates()
        self.__update_apps()
        self.__pre_exit_cleanup()

    def __check_updates(self) -> None:
        project_list: list[GenericApp] = []
        for path in configuration.local:
            native_path = make_path_native(path)
            for list_item in configuration.local[path]:
                if list_item.casefold() in configuration.available:
                    appconf = configuration.available[list_item.casefold()]
                    if appconf["repo"]:
                        job = None
                        if appconf["repo"] == "appveyor":
                            job = AppveyorApp(native_path, **appconf)
                        elif appconf["repo"] == "github":
                            job = GithubApp(native_path, **appconf)
                        elif appconf["repo"] == "html":
                            job = HTMLApp(native_path, **appconf)
                        if job is not None:
                            project_list.append(job)

        if self.__MT_ON:
            with futures.ThreadPoolExecutor(max_workers=8) as executor:
                projects = {
                    executor.submit(Program.__report_update_status, project): project for project in project_list
                }
                for appconf in futures.as_completed(projects):
                    print(appconf.result())
                    if projects[appconf].update_status in self.__UPDATE_TRIGGER:
                        self.job_list.append(projects[appconf])
        else:
            for appconf in project_list:
                print(Program.__report_update_status(appconf))
                if appconf.update_status in self.__UPDATE_TRIGGER:
                    self.job_list.append(appconf)

    @classmethod
    def __report_update_status(cls, project) -> str:
        try:
            project.execute()
            GenericManager.check_update(project)
        except (RequestException, HTTPError):
            project.update_status = "failed"
        finally:
            return Program.project_status_report(project)

    def __update_apps(self):
        for job in self.job_list:
            my_fsm = FileHandler(job)
            message = f"{job.name}: "
            if job.update_status == "update":
                message += "Updating"
                print_header(message, Ansi.GREEN)
                my_fsm.project_update()
            elif job.update_status == "no_version_file":
                message += "Updating (forced)"
                print_header(message, Ansi.MAGENTA)
                my_fsm.project_update()
            elif job.update_status == "not_installed":
                message += "Installing"
                print_header(message, Ansi.CYAN)
                my_fsm.project_install()

    @classmethod
    def project_status_report(cls, project: GenericApp):
        color = ""
        message = ""
        if project.update_status == "no_update":
            color = Ansi.BRIGHT
            message = "No update available"
        elif project.update_status == "installed_newer":
            color = Ansi.MAGENTA
            message = (
                f"Installed is newer.\r\n {Ansi.RESET}{project.name}: Please make sure your version wasn't retracted "
                "because of problems with it."
            )
        elif project.update_status == "update":
            color = Ansi.GREEN
            message = "Update available"
        elif project.update_status == "no_version_file":
            color = Ansi.MAGENTA
            message = "Update forced (no valid version info found)"
        elif project.update_status == "not_installed":
            color = Ansi.CYAN
            message = "Will be installed"
        elif project.update_status == "error":
            color = Ansi.RED
            message = "Could not determine the version installed"
        elif project.update_status == "failed":
            color = Ansi.RED
            message = "Could not connect to URL or API"
        elif project.update_status == "unknown":
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


if __name__ == "__main__":
    main()
