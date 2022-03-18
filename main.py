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
from typing import List

from requests import RequestException
from urllib3.exceptions import HTTPError

import helper.terminal
import settings
from appveyor.appveyor_app import AppveyorApp
from config_handler.config_handler import ConfigHandler
from config_handler.eula import EulaChecker
from environment_handler.environment_handler import LockFile, LockFileException
from file_handler.file_handler import FileHandler
from file_handler.fs_helper import make_path_native, remove_empty_dirs
from generic_app.generic_app import GenericApp
from generic_app.generic_manager import GenericManager
from github.github_app import GithubApp
from helper.terminal import BRIGHT, CYAN, GREEN, MAGENTA, RED, RESET, color_handling, print_header
from html_seu.html_app import HTMLApp


class Main:

    ConfigHandler()
    cfg_auth = settings.app_config["auth"]
    cfg_available = settings.app_config["available"]
    cfg_local = settings.app_config["local"]
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
        project_list: List[GenericApp] = []
        for path in self.cfg_local:
            native_path = make_path_native(path)
            for list_item in self.cfg_local[path]:
                if list_item.casefold() in self.cfg_available:
                    appconf = self.cfg_available[list_item.casefold()]
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
                projects = {executor.submit(Main.__report_update_status, project): project for project in project_list}
                for appconf in futures.as_completed(projects):
                    print(appconf.result())
                    if projects[appconf].update_status in self.__UPDATE_TRIGGER:
                        self.job_list.append(projects[appconf])
        else:
            for appconf in project_list:
                print(Main.__report_update_status(appconf))
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
            return Main.project_status_report(project)

    def __update_apps(self):
        for job in self.job_list:
            my_fsm = FileHandler(job)
            message = f"{job.name}: "
            if job.update_status == "update":
                message += "Updating"
                print_header(message, GREEN)
                my_fsm.project_update()
            elif job.update_status == "no_version_file":
                message += "Updating (forced)"
                print_header(message, MAGENTA)
                my_fsm.project_update()
            elif job.update_status == "not_installed":
                message += "Installing"
                print_header(message, CYAN)
                my_fsm.project_install()

    @classmethod
    def project_status_report(cls, project: GenericApp):
        color = ""
        message = ""
        if project.update_status == "no_update":
            color = BRIGHT
            message = "No update available"
        elif project.update_status == "installed_newer":
            color = MAGENTA
            message = (
                f"Installed is newer.\r\n {RESET}{project.name}: Please make sure your version wasn't retracted "
                "because of problems with it."
            )
        elif project.update_status == "update":
            color = GREEN
            message = "Update available"
        elif project.update_status == "no_version_file":
            color = MAGENTA
            message = "Update forced (no valid version info found)"
        elif project.update_status == "not_installed":
            color = CYAN
            message = "Will be installed"
        elif project.update_status == "error":
            color = RED
            message = "Could not determine the version installed"
        elif project.update_status == "failed":
            color = RED
            message = "Could not connect to URL or API"
        elif project.update_status == "unknown":
            color = RED
            message = "Failed to check this project"
        return f"{color}{project.name}: {message}{RESET}"

    @classmethod
    def __pre_exit_cleanup(cls) -> None:
        """
        Remove cache directories created by this program.
        """
        for target in cls.cfg_local:
            cache = os.path.join(make_path_native(target), ".superelixier-cache")
            remove_empty_dirs(cache, delete_top=True)


if __name__ == "__main__":
    try:
        try:
            color_handling()
            lock = LockFile()
            EulaChecker.check_eula()
            superelixier_updater = Main()
            superelixier_updater.execute()
            del lock
            input("Press Enter to continue...")
        except LockFileException:
            time.sleep(7)
    except Exception:  # noqa
        color_handling(init=False)
        helper.terminal.print_header("superelixier crashed!"),
        string_builder = (
            "(╯°□°)╯︵ ┻━┻",
            "",
            f"{helper.terminal.RED}{traceback.format_exc()}{helper.terminal.RESET}",
            "",
            "┬─┬ノ( º _ ºノ)",
        )
        print("\n".join(string_builder))
        input("Press Enter to continue...")
    finally:
        color_handling(init=False)
        sys.exit()
