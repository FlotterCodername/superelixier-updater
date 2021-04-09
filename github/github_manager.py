"""
Copyright 2021 Fabian H. Schneider
"""
import json
import os
from datetime import datetime
from github.github import GITHUB_DATE
from github.github_app import GithubApp


class GithubManager:

    def __init__(self):
        pass

    @staticmethod
    def check_update(app: GithubApp):
        if not os.path.isdir(app.appdir):
            app.update_status = "not_installed"
        elif not app.update_status == "failed":
            ver_info_file = os.path.join(app.target_dir, app.name, "superelixier.json")
            if os.path.isfile(ver_info_file):
                with open(ver_info_file, 'r') as file:
                    date_installed = datetime.strptime(json.load(file), GITHUB_DATE)
                if app.date_latest == date_installed:
                    app.update_status = "no_update"
                elif app.date_latest > date_installed:
                    app.update_status = "update"
                else:
                    app.update_status = "error"
            else:
                app.update_status = "no_version_file"
