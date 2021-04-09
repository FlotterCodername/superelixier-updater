"""
Copyright 2021 Fabian H. Schneider
"""


class GithubProject:

    def __init__(self, name, user, project, blob_re, blob_unwanted, appdatas):
        self._name = name
        self._user = user
        self._project = project
        self._blob_re = blob_re
        self._blob_unwanted = blob_unwanted
        self._appdatas = appdatas

    @property
    def name(self):
        return self._name

    @property
    def user(self):
        return self._user

    @property
    def project(self):
        return self._project

    @property
    def blob_re(self):
        return self._blob_re

    @property
    def blob_unwanted(self):
        return self._blob_unwanted

    @property
    def appdatas(self):
        return self._appdatas
