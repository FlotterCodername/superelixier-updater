"""
Copyright 2021 Fabian H. Schneider
"""
import colorama
import os
from config_loader.config_loader import ConfigLoader
from github.github_manager import GithubManager
from github.github_project import GithubProject


# TODO: Pre-Release version check
# TODO: Retention of old versions
# TODO: HTML Parse
# TODO: Buildbot, Appveyor, etc.

class Main:
    def __init__(self):
        # CFG
        configuration = ConfigLoader().configuration
        self.cfg_auth = configuration["auth"]
        self.cfg_available = configuration["available"]
        self.cfg_local = configuration["local"]
        # Helper objects
        self.job_list = []

    def execute(self):
        colorama.init(autoreset=True)
        self.__check_updates()
        self.__update_apps()
        # input("Press Enter to continue...")

    def __check_updates(self):
        github_token = self.cfg_auth["github_token"]
        project_list = []
        for path in self.cfg_local:
            for list_item in self.cfg_local[path]:
                location_found = False
                if not location_found:
                    for project in self.cfg_available["from_github"]:
                        if not location_found and list_item == project["name"]:
                            location_found = True
                            native_path = os.path.join(*os.path.split(path))
                            github_project = GithubProject(project, native_path, github_token)
                            project_list.append(github_project)
        my_github_manager = GithubManager()
        for project in project_list:
            project.execute()
            my_github_manager.check_update(project)
            self.project_status_report(project)
            if project.update_status in ["update", "update_noverfile", "not_installed"]:
                self.job_list.append(project)

    def __update_apps(self):
        for job in self.job_list:
            color = ''
            message = f'{job.name}: '
            if job.update_status == "update":
                color = colorama.Fore.GREEN
                message += "Updating"
            elif job.update_status == "update_noverfile":
                color = colorama.Fore.MAGENTA
                message += "Updating (forced)"
            elif job.update_status == "not_installed":
                color = colorama.Fore.BLUE
                message += "Installing"
            Main.print_header(message, color)

    @staticmethod
    def project_status_report(project: GithubProject):
        color = ''
        message = ''
        if project.update_status == "no_update":
            color = colorama.Style.BRIGHT
            message = "No update available"
        elif project.update_status == "update":
            color = colorama.Fore.GREEN
            message = "Update available"
        elif project.update_status == "update_noverfile":
            color = colorama.Fore.MAGENTA
            message = "Update forced (no valid version info found)"
        elif project.update_status == "not_installed":
            color = colorama.Fore.BLUE
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
