"""
Copyright 2021 Fabian H. Schneider
"""
import colorama

from config_loader.config_loader import ConfigLoader
from github.github_project import GithubProject

colorama.init(autoreset=True)


class Main:
    def __init__(self):
        # CFG
        configuration = ConfigLoader().configuration
        self.cfg_auth = configuration["auth"]
        self.cfg_available = configuration["available"]
        self.cfg_local = configuration["local"]
        # Helper objects

    def execute(self):
        github_token = self.cfg_auth["github_token"]
        project_list = []

        for path in self.cfg_local:
            for list_item in self.cfg_local[path]:
                location_found = False
                if not location_found:
                    for project in self.cfg_available["from_github"]:
                        if not location_found and list_item == project["name"]:
                            location_found = True
                            github_project = GithubProject(project, path, github_token)
                            project_list.append(github_project)


    @staticmethod
    def print_header(string, color=''):
        bar = (len(string) + 4) * "#"
        print(color + bar + "\n# " + string + " #\n" + bar)


if __name__ == '__main__':
    superelixier_updater = Main()
    superelixier_updater.execute()
