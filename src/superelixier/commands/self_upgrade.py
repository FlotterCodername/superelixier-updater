"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import json
import os.path
import textwrap
from typing import Optional
from zipfile import ZipFile

import requests as rest
from cleo.commands.command import Command
from dateutil import parser
from packaging import version
from packaging.version import Version
from requests import RequestException
from urllib3.exceptions import HTTPError

from superelixier import __version_obj__
from superelixier.file_handler import Downloader
from superelixier.github import GITHUB_API
from superelixier.helper.environment import DIR_APP
from superelixier.helper.terminal import DENT, Ansi, clear

USER = "FlotterCodername"
REPO = "superelixier-updater"
HEADERS = {"Accept": "application/vnd.github.v3+json", "User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"}
PRERELEASES = False  # Make configurable later


class SelfUpgrade(Command):
    # cleo
    name = "self upgrade"
    description = f'Upgrade the current installation of superelixier that is located at "{DIR_APP}".'

    def handle(self) -> int:
        return self.ask_update()

    def ask_update(self):
        check = self.check_update()
        if None in check:
            self.line("No update found!")
            return -1
        release, asset, description = check
        clear()
        self.line(
            Ansi.BRIGHT
            + f"A new version of superelixier is available{': ' + release['name'] if 'name' in release else '.'}"
            + ("\nDetails:" if description else "")
            + Ansi.RESET
        )
        if description:
            self.line(textwrap.indent(description, DENT) + "\n")
        inp = ""
        while inp.casefold() not in ("y", "n"):
            inp = input("Download and install now? [y/n]: ")
        if inp.casefold() == "y":
            return self.do_self_update(asset)
        else:
            return -2

    def do_self_update(self, asset):
        executable = os.path.join(DIR_APP, "superelixier.exe")
        executable_bak = os.path.join(DIR_APP, "superelixier.exe.bak")
        location = os.path.join(DIR_APP, "update.zip")
        if os.path.isfile(location):
            os.unlink(location)
        download = Downloader(asset["browser_download_url"], location)
        if download.file != "update.zip":
            os.rename(os.path.join(DIR_APP, download.file), location)
        with ZipFile(location) as update_zip:
            if error := ZipFile.testzip(update_zip):
                self.line(Ansi.ERROR + f"Self update check: Bad Zip File, {error}" + Ansi.RESET)
                return -1
            if os.path.isfile(executable_bak):
                os.unlink(executable_bak)
            if os.path.isfile(executable):
                os.rename(executable, executable_bak)
            self.write("Extracting... ")
            update_zip.extractall(DIR_APP)
        self.write(Ansi.GREEN + "Self upgrade successful!\n" + Ansi.RESET)
        return 0

    def notify_update(self: Optional["SelfUpgrade"], *, command: Command = None):
        if command is None:
            command = self
        check = SelfUpgrade.check_update(None, command=command)
        if None in check:
            return
        release, asset, description = check
        command.line(
            textwrap.dedent(
                f"""\
            {Ansi.BRIGHT}
            A new version of superelixier is available{': ' + release['name'] if 'name' in release else '.'}{Ansi.RESET}
            >>> Run "superelixier self upgrade" to install it."""
            )
        )

    def check_update(self: Optional["SelfUpgrade"], *, command: Command = None):
        if command is None:
            command = self
        NOTHING = (None, None, None)
        try:
            releases_api = rest.get(f"{GITHUB_API}/repos/{USER}/{REPO}/releases", headers=HEADERS)
            releases = json.loads(releases_api.text)
            if releases_api.status_code != 200:
                command.line(
                    Ansi.ERROR
                    + f"Self update check: HTTP Status {releases_api.status_code}: {releases['message']}"
                    + Ansi.RESET
                )
                return (*NOTHING,)
        except (json.JSONDecodeError, RequestException, HTTPError) as e:
            command.line(Ansi.ERROR + f"Self update check: {e.__class__.__name__}" + Ansi.RESET)
            return (*NOTHING,)
        if not PRERELEASES:
            releases = [i for i in releases if "prerelease" not in i or not i["prerelease"]]
        releases = {parser.parse(i["published_at"]): i for i in releases if "published_at" in i and i["published_at"]}
        releases = {
            k: v for k, v in releases.items() if "assets" in v and isinstance(v["assets"], list) and v["assets"]
        }
        if not releases.keys():
            return (*NOTHING,)
        latest_release = releases[max(releases.keys())]
        if "tag_name" in latest_release and latest_release["tag_name"]:
            try:
                package_version = version.parse(latest_release["tag_name"])
                assert isinstance(package_version, Version)
                if package_version <= __version_obj__:
                    return (*NOTHING,)
            except (AssertionError, TypeError, ValueError):
                pass
        asset = None
        if len(latest_release["assets"]) > 1:
            for i in latest_release["assets"]:
                if "name" in i and i["name"] == "update.zip":
                    asset = i
                    break
            if asset is None:
                return command.line(
                    Ansi.ERROR + "Self update check: No update file found for the version!" + Ansi.RESET
                )
        else:
            asset = latest_release["assets"][0]
        if asset and "browser_download_url" not in asset:
            asset = None
        description = ""
        if "body" in latest_release and latest_release["body"].strip():
            description = latest_release["body"].strip().replace("\r\n", "\n")
            while "\n\n" in description:
                description = description.replace("\n\n", "\n")
        return latest_release, asset, description
