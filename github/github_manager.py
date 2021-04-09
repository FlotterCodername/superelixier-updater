"""
Copyright 2021 Fabian H. Schneider
"""
import colorama
import json
import os
from datetime import datetime
from github.github import HEADERS, GITHUB_DATE
from github.github_project import GithubProject


class GithubManager:

    def __init__(self, token):
        self.__headers = HEADERS
        self.__headers["Authorization"] = token

    def check_update(self, project: GithubProject):
        if project.update_status == "failed":
            print(colorama.Fore.RED + f"Failed to update {project.name}")
        else:
            if os.path.isfile(os.path.join(project.project_dir, "superelixier.json")):
                with open(os.path.join(project.project_dir, "superelixier.json"), 'r') as file:
                    date_installed = datetime.strptime(json.load(file), GITHUB_DATE)
                if project.date_latest == date_installed:
                    project.update_status = "no_update"
                elif project.date_latest > date_installed:
                    project.update_status = "update"
                else:
                    print(colorama.Fore.RED + f"{project.name}: Could not determine installed version")
                    raise ValueError
            else:
                print(
                    colorama.Fore.MAGENTA + f"{project.name}: Version info file not found -- assuming update is available")
                project.update_status = "update"
