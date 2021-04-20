"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import time

import colorama
from appveyor.appveyor_app import AppveyorApp
from appveyor.appveyor_manager import AppveyorManager
from config_loader.config_loader import ConfigLoader
from config_loader.eula import EulaChecker
from environment_handler.environment_handler import LockFile, LockFileException
from file_handler.file_handler import FileHandler
from generic_app.generic_app import GenericApp
from github.github_manager import GithubManager
from github.github_app import GithubApp
from html_seu.html_app import HTMLApp
from html_seu.html_manager import HTMLManager


class Main:
    def __init__(self):
        colorama.init(autoreset=True)
        try:
            self.__lock = LockFile()
        except LockFileException:
            time.sleep(7)
            exit()
        EulaChecker.check_eula()
        # Configuration
        configuration = ConfigLoader().configuration
        self.cfg_auth = configuration["auth"]
        self.cfg_available = configuration["available"]
        self.cfg_local = configuration["local"]
        # Managers
        self.__appveyor_manager = GithubManager(self.cfg_auth)
        self.__github_manager = GithubManager(self.cfg_auth)

        # Helper objects
        self.job_list = []

    def execute(self):
        """
        The execute() methods in the project are supposed to provide an idea of what the class does in a nutshell.
        Always put them directly after __init__().
        """
        self.__check_updates()
        self.__update_apps()
        input("Press Enter to continue...")

    def __check_updates(self):
        project_list = []
        for path in self.cfg_local:
            native_path = FileHandler.make_path_native(path)
            for list_item in self.cfg_local[path]:
                location_found = False
                for project in self.cfg_available["from_appveyor"]:
                    if list_item.lower() == project["name"].lower():
                        location_found = True
                        appveyor_project = AppveyorApp(project, native_path, self.__appveyor_manager.get_headers)
                        project_list.append(appveyor_project)
                        continue
                if location_found:
                    continue
                for project in self.cfg_available["from_github"]:
                    if list_item.lower() == project["name"].lower():
                        location_found = True
                        github_project = GithubApp(project, native_path, self.__github_manager.get_headers)
                        project_list.append(github_project)
                        continue
                if location_found:
                    continue
                for project in self.cfg_available["from_html"]:
                    if list_item.lower() == project["name"].lower():
                        location_found = True
                        html_project = HTMLApp(project, native_path)
                        project_list.append(html_project)
                if location_found:
                    continue
        for project in project_list:
            project.execute()
            if isinstance(project, AppveyorApp):
                AppveyorManager.check_update(project)
            if isinstance(project, GithubApp):
                GithubManager.check_update(project)
            elif isinstance(project, HTMLApp):
                HTMLManager.check_update(project)
            self.project_status_report(project)
            if project.update_status in ["update", "no_version_file", "not_installed"]:
                self.job_list.append(project)

    def __update_apps(self):
        for job in self.job_list:
            my_fsm = FileHandler(job)
            message = f'{job.name}: '
            if job.update_status == "update":
                message += "Updating"
                Main.print_header(message, colorama.Fore.GREEN)
                my_fsm.project_update()
            elif job.update_status == "no_version_file":
                message += "Updating (forced)"
                Main.print_header(message, colorama.Fore.MAGENTA)
                my_fsm.project_update()
            elif job.update_status == "not_installed":
                message += "Installing"
                Main.print_header(message, colorama.Fore.CYAN)
                my_fsm.project_install()

    @staticmethod
    def project_status_report(project: GenericApp):
        color = ''
        message = ''
        if project.update_status == "no_update":
            color = colorama.Style.BRIGHT
            message = "No update available"
        elif project.update_status == "installed_newer":
            color = colorama.Style.BRIGHT + colorama.Fore.MAGENTA
            message = "Installed is newer. " + colorama.Style.DIM + colorama.Fore.RESET + "Please make sure your version wasn't retracted because of problems with it."
        elif project.update_status == "update":
            color = colorama.Fore.GREEN
            message = "Update available"
        elif project.update_status == "no_version_file":
            color = colorama.Fore.MAGENTA
            message = "Update forced (no valid version info found)"
        elif project.update_status == "not_installed":
            color = colorama.Fore.CYAN
            message = "Will be installed"
        elif project.update_status == "error":
            color = colorama.Fore.RED
            message = "Could not determine the version installed"
        elif project.update_status == "failed":
            color = colorama.Fore.RED
            message = "Failed to make remote API call for version check"
        elif project.update_status == "unknown":
            color = colorama.Fore.RED
            message = "Failed to check this project"
        print(f"{color}{project.name}: {message}")

    @staticmethod
    def print_header(string, color=''):
        bar = (len(string) + 4) * "#"
        print(color + bar + "\n# " + string + " #\n" + bar)


if __name__ == '__main__':
    superelixier_updater = Main()
    superelixier_updater.execute()
