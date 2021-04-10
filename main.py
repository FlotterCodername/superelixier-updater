"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import colorama
import os
from config_loader.config_loader import ConfigLoader
from file_handler.file_handler import FileHandler
from github.github_manager import GithubManager
from github.github_app import GithubApp


class Main:
    def __init__(self):
        # Configuration
        configuration = ConfigLoader().configuration
        self.cfg_auth = configuration["auth"]
        self.cfg_available = configuration["available"]
        self.cfg_local = configuration["local"]
        # Managers
        self.__github_manager = GithubManager(self.cfg_auth)

        # Helper objects
        self.job_list = []

    def execute(self):
        """
        The execute() methods in the project are supposed to provide an idea of what the class does in a nutshell.
        Always put them directly after __init__().
        """
        colorama.init(autoreset=True)
        self.__check_updates()
        self.__update_apps()
        input("Press Enter to continue...")

    def __check_updates(self):
        project_list = []
        for path in self.cfg_local:
            for list_item in self.cfg_local[path]:
                location_found = False
                for project in self.cfg_available["from_github"]:
                    if list_item == project["name"]:
                        location_found = True
                        native_path = os.path.join(*os.path.split(path))
                        github_project = GithubApp(project, native_path, self.__github_manager.get_headers)
                        project_list.append(github_project)
                        continue
                if location_found:
                    continue
                for project in self.cfg_available["from_html"]:
                    if list_item == project["name"]:
                        location_found = True
                        native_path = os.path.join(*os.path.split(path))
                        html_project = HTMLApp(project, native_path)
                        project_list.append(html_project)
                if location_found:
                    continue
        for project in project_list:
            project.execute()
            self.__github_manager.check_update(project)
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
    def project_status_report(project: GithubApp):
        color = ''
        message = ''
        if project.update_status == "no_update":
            color = colorama.Style.BRIGHT
            message = "No update available"
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
