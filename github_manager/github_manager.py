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

    def __init__(self, name, user, project, blob_re, blob_unwanted, appdatas):
        self.__name = name
        self.__user = user
        self.__project = project
        self.__blob_re = blob_re
        self.__blob_unwanted = blob_unwanted
        self.__appdatas = appdatas
        self.__headers = self.HEADERS
