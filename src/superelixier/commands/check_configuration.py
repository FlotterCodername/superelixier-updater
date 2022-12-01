"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import textwrap

from cleo.commands.command import Command

from superelixier import configuration
from superelixier.commands.self_upgrade import SelfUpgrade
from superelixier.configuration import (
    InvalidAuthException,
    InvalidLocalException,
    MissingAuthException,
    MissingLocalException,
)
from superelixier.helper.terminal import DENT


class CheckConfiguration(Command):
    # cleo
    name = "check configuration"
    description = "Inspect the local.toml and auth.toml files"

    def handle(self) -> int:
        ret_code, auth, local = 0, None, None
        self.line("auth.toml")
        try:
            auth = configuration.auth
        except (InvalidAuthException, MissingAuthException) as e:
            ret_code = -2
            self.line_error("- Problem with the file.")
            for arg in e.args:
                self.line(textwrap.indent(arg, DENT))
        if auth is not None:
            if "appveyor_token" in auth and auth["appveyor_token"].strip():
                self.line("- AppVeyor API token is there")
            else:
                self.line("- AppVeyor token is not there (optional)")
            if "github_token" in auth and auth["github_token"].strip():
                self.line("- GitHub API token is there")
            else:
                self.line("- GitHub token is not there (optional)")
        self.line("")
        self.line("local.toml")
        try:
            local = configuration.local
        except (InvalidLocalException, MissingLocalException) as e:
            ret_code = -2
            self.line_error("- Problem with the file.")
            for arg in e.args:
                self.line(textwrap.indent(arg, DENT))
        if local is not None:
            self.line("- Valid.")
        self.line("")
        if ret_code == 0:
            self.line("Everything is in order!")
        else:
            self.line_error("Some problems detected!")
        SelfUpgrade.notify_update(None, command=self)
        return ret_code
