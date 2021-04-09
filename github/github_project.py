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
