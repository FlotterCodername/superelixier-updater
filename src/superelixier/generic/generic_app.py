"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import json
import os
import random
import string
from dataclasses import asdict, dataclass
from typing import Callable

from superelixier.definition import Definition
from superelixier.helper.types import UpdateStatus


@dataclass
class VersionInfo:
    version_id: str  #: such as a date, version tuple, commit id, ...
    blobs: list[str]  #: urls belonging to the versiond_id

    @property
    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class VersionInstalled(VersionInfo):
    repo: str
    spec: int = 1

    def __post_init__(self):
        if not isinstance(self.spec, int) or self.spec < 0:
            self.spec = 0


class GenericApp:
    execute: Callable

    def __init__(self, definition: Definition, target: str = None):
        """
        Do not instantiate this. Always use the child classes.
        """
        self._definition: Definition = definition
        self._version_installed: VersionInstalled | None = None
        self._version_latest: VersionInfo | None = None
        self._random_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=32))
        self._appdir: str | None = None
        self._target_dir: str | None = target
        # Update status managed by manager classes
        self.update_status: UpdateStatus = "unknown"
        self.__post_init()

    def __post_init(self):
        if self.target_dir:
            self._appdir = os.path.join(self.target_dir, self.name)
            installed_json = os.path.join(self._appdir, "superelixier.json")
            if os.path.isfile(installed_json):
                with open(installed_json, "r") as fdr:
                    loaded = json.load(fdr)
                try:
                    self._version_installed = VersionInstalled(**loaded)
                except (ValueError, TypeError):
                    os.unlink(installed_json)

    @property
    def name(self):
        return self.definition.info.name

    @property
    def versioning(self):
        raise NotImplementedError

    @property
    def versioning_spec(self):
        return None

    @property
    def appdir(self):
        return self._appdir

    @property
    def definition(self):
        return self._definition

    @property
    def target_dir(self):
        return self._target_dir

    @property
    def version_installed(self):
        return self._version_installed

    @property
    def version_latest(self):
        return self._version_latest

    @property
    def random_id(self):
        return self._random_id

    def __repr__(self):
        return f"{self.name} | {self.update_status}"
