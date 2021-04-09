"""
Copyright 2021 Fabian H. Schneider
"""


class GithubManager:
    GITHUB_DATE = f"%Y-%m-%dT%H:%M:%SZ"
    HEADERS = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "",
        "User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"
    }

    def __init__(self, project, target, auth_token=""):
        self.__headers = self.HEADERS
        self.__project = project

    def execute(self):
        pass
