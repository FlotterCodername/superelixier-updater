"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import os
import random
import string
from typing import Callable, List, Union


class GenericApp:
    execute: Callable

    def __init__(
        self,
        target: str,
        *,
        appdatas: Union[str, List[str]] = None,
        blob_re: str = None,
        blob_permalink: str = None,
        blob_unwanted: Union[str, List[str]] = None,
        branch: str = None,
        info: dict = None,
        installer: str = None,
        name: str = None,
        url: str = None,
        user: str = None,
        prerelease: bool = None,
        project: str = None,
        repo: str = None,
        ver_scheme_re: str = None,
        ver_scheme_type: str = None,
        ver_scheme_spec: int = None,
    ):
        """
        Do not instantiate this. Always use the child classes.
        """
        # Props from JSON
        self._appdatas = appdatas
        self._blob_re = blob_re
        self._blob_re = blob_re
        self._blob_permalink = blob_permalink
        self._blob_unwanted = blob_unwanted
        self._branch = branch
        self._info = info
        self._installer = installer
        self._name = name
        self._url = url
        self._user = user
        self._prerelease = prerelease
        self._project = project
        self._repo = repo
        self._ver_scheme_re = ver_scheme_re
        self._ver_scheme_type = ver_scheme_type
        self._ver_scheme_spec = ver_scheme_spec
        # Runtime props
        self._appdir = os.path.join(target, self._name)
        self._target_dir = target
        self._version_latest = {}
        self._random_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=32))
        # Update status managed by manager classes
        self.update_status = "unknown"

    @property
    def appdatas(self):
        return self._appdatas

    @property
    def blob_re(self):
        return self._blob_re

    @property
    def blob_permalink(self):
        return self._blob_permalink

    @property
    def blob_unwanted(self):
        return self._blob_unwanted

    @property
    def branch(self):
        return self._branch

    @property
    def info(self):
        return self._info

    @property
    def installer(self):
        return self._installer

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return self._url

    @property
    def user(self):
        return self._user

    @property
    def prerelease(self):
        return self._prerelease

    @property
    def project(self):
        return self._project

    @property
    def repo(self):
        return self._repo

    @property
    def ver_scheme_re(self):
        return self._ver_scheme_re

    @property
    def ver_scheme_type(self):
        return self._ver_scheme_type

    @property
    def ver_scheme_spec(self):
        return self._ver_scheme_spec

    @property
    def appdir(self):
        return self._appdir

    @property
    def target_dir(self):
        return self._target_dir

    @property
    def version_latest(self):
        return self._version_latest

    @property
    def random_id(self):
        return self._random_id
