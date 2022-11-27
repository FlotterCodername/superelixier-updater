"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import textwrap
from concurrent.futures import ThreadPoolExecutor

from cleo.commands.command import Command
from cleo.helpers import argument, option
from requests import RequestException
from urllib3.exceptions import HTTPError

from superelixier import configuration
from superelixier.configuration import InvalidLocalException
from superelixier.file_handler import FileHandler
from superelixier.generic.generic_manager import GenericManager
from superelixier.helper.converters import create_app_jobs
from superelixier.helper.terminal import Ansi, DENT, print_header
from superelixier.helper.types import UpdateStatus


class Install(Command):
    # cleo
    name = "install"
    description = "Install apps"
    arguments = [argument(name="apps", description="Which apps install", multiple=True)]
    options = [
        option(
            "destination",
            "D",
            "Directory where the apps should be installed.",
            flag=False,
            value_required=True,
            default=None,
        ),
        option("upgrade", "u", "Update the apps if they are already installed"),
        option("force", "f", "Do not warn about already-existing folders or missing version info, just upgrade apps"),
        option("dry-run", "d", "Do not actually download and write files, just show what would happen"),
    ]

    def handle(self) -> int:
        arg_apps = self.argument("apps")
        op_de = self.option("destination")
        op_u = self.option("upgrade")
        op_f = self.option("force")
        op_d = self.option("dry-run")
        if op_de is None:
            try:
                for item in configuration.local.values():
                    if item.default:
                        op_de = item.path
            except InvalidLocalException as e:
                self.line_error("If the --destination option is not used, a valid local.toml is required.")
                self.line(e.args[0])
                return -100
        if op_de is None:
            self.line_error("If the \"--destination\" option is not used, you must set a folder as default.")
            self.line(textwrap.dedent(f"""\

            [[{Ansi.YELLOW}directory{Ansi.RESET}]]
            {Ansi.YELLOW}default{Ansi.RESET} = true
            {Ansi.YELLOW}path{Ansi.RESET} = {Ansi.GREEN}"C:/my cool directory/my apps"{Ansi.RESET}
            {Ansi.YELLOW}apps{Ansi.RESET} = [ ... ]
            """))
            self.line("Only one default folder is possible!")
            return -100
        app_jobs = create_app_jobs(arg_apps, op_de, self)
        with ThreadPoolExecutor(max_workers=8) as executor:
            for project in app_jobs:
                executor.submit(self.__check_update_status, project)
        should_update: set[UpdateStatus]
        match op_u, op_f:
            case _, True:
                should_update = {"no_update", "installed_newer", "update", "no_version_file", "not_installed"}
            case True, _:
                should_update = {"update", "not_installed"}
            case _:  # False, False
                should_update = {"not_installed"}

        is_installed_newer_case = False
        for app in (*app_jobs,):
            if app.update_status == "installed_newer":
                is_installed_newer_case = True
            if app.update_status in {"error", "failed", "unknown"}:
                app_jobs.remove(app)
                self.line_error(f"{app.name}: Something went wrong")
                continue
            if app.update_status not in should_update:
                app_jobs.remove(app)
                if not (op_u or op_f):
                    msg = f"{app.name}: Already installed"
                    if app.update_status == "update":
                        msg += f" (update available)"
                    elif app.update_status == "installed_newer":
                        msg += f" (installed newer)"
                    elif app.update_status == "no_version_file":
                        msg += f" (no version info)"
                    self.line(f"{app.name}: Already installed")
                    continue
                if op_u and not op_f:
                    match app.update_status:
                        case "no_update":
                            self.line(f"{app.name}: Already up-to-date")
                        case "installed_newer":
                            self.line_error(f"{app.name}: [!] Skipping: Installed is newer")
                        case "no_version_file":
                            self.line_error(f"{app.name}: [!] Skipping: No valid version info")
                    if app.update_status in {"installed_newer", "no_version_file"}:
                        self.line(DENT + "To upgrade anyway, re-run this command with the --force option.")
            else:
                match app.update_status:
                    case "no_update":
                        self.line(f"{app.name}: [!] Upgrade: Re-downloading the release")
                    case "installed_newer":
                        self.line(f"{app.name}: [!] Upgrade: Installed version appears newer")
                    case "no_version_file":
                        self.line(f"{app.name}: [!] Upgrade: No valid version info")
                    case "update":
                        self.line(f"{app.name}: Upgrade")
                    case _:  # "not_installed"
                        self.line(f"{app.name}: Installing")
        if is_installed_newer_case:
            self.line_error("One or more apps appeared to be ahead of the latest version!")
            self.line(textwrap.indent(textwrap.dedent(f"""\
            Maybe the release was removed... but it's more likely our app definition is outdated.
            Tech-savvy? Find out how to update/create app definitions here:
            {DENT}https://github.com/FlotterCodername/superelixier-updater/blob/main/docs/Adding%20Apps.md"""), DENT))

        for app in app_jobs:
            if not app.version_latest.blobs:
                print_header(app.name, Ansi.RED)
                self.line_error(f"Definition problem: no matching downloads for version ID {app.version_latest.version_id}")
            elif op_d:
                for blob in app.version_latest.blobs:
                    print_header(app.name, Ansi.MAGENTA)
                    self.line(f"Would download: {blob}")
            else:
                my_fh = FileHandler(app)
                if app.update_status == "not_installed":
                    print_header(app.name, Ansi.GREEN)
                    my_fh.project_install()
                else:
                    print_header(app.name, Ansi.CYAN)
                    my_fh.project_update()
        return 0

    @classmethod
    def __check_update_status(cls, project):
        # TODO: Duplicate code, refactor
        try:
            project.execute()
            GenericManager.check_update(project)
        except (RequestException, HTTPError):
            project.update_status = "failed"
