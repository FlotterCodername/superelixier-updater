"""
Copyright 2021 Fabian H. Schneider
"""
import colorama
import json
import os
from datetime import datetime
from github.github import GITHUB_DATE
from github.github_project import GithubProject


class GithubManager:

    def __init__(self):
        pass

    @staticmethod
    def check_update(project: GithubProject):
        if project.update_status == "failed":
            print(colorama.Fore.RED + f"Failed to update {project.name}")
        else:
            ver_info_file = os.path.join(project.target_dir, project.name, "superelixier.json")
            if os.path.isfile(ver_info_file):
                with open(ver_info_file, 'r') as file:
                    date_installed = datetime.strptime(json.load(file), GITHUB_DATE)
                if project.date_latest == date_installed:
                    project.update_status = "no_update"
                elif project.date_latest > date_installed:
                    project.update_status = "update"
                else:
                    project.update_status = "error"
            else:
                project.update_status = "update_noverfile"
