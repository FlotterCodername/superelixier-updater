"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import json
import os.path
import sys
import textwrap

import requests as rest
from dateutil import parser
from requests import RequestException
from urllib3.exceptions import HTTPError

from superelixier.file_handler import Downloader
from superelixier.github import GITHUB_API
from superelixier.helper.terminal import DENT, Ansi, clear


class SelfUpdater:
    user = "FlotterCodername"
    project = "superelixier-updater"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)",
    }
    prereleases = True  # Make configurable later

    @classmethod
    def ask_update(cls):
        check = cls.check_update()
        if None in check:
            return
        release, asset, description = check
        print(
            Ansi.BRIGHT
            + f"A new version of superelixier is available.{' Details:' if description else ''}"
            + Ansi.RESET
        )
        if description:
            print(textwrap.indent(description, DENT) + "\n")
        inp = ""
        while inp.casefold() not in ("y", "n"):
            inp = input("\rDownload and install now [y/n]?")
        if inp.casefold() == "y":
            cls.do_self_update(asset)
        clear()

    @classmethod
    def check_update(cls):
        try:
            releases_api = rest.get(f"{GITHUB_API}/repos/{cls.user}/{cls.project}/releases", headers=cls.headers)
            releases = json.loads(releases_api.text)
            if releases_api.status_code != 200:
                print(Ansi.ERROR + f"Self update check: HTTP Status {releases_api.status_code}: {releases['message']}")
                return None
        except (json.JSONDecodeError, RequestException, HTTPError) as e:
            return print(Ansi.ERROR + f"Self update check: {e.__class__.__name__}")
        if not cls.prereleases:
            releases = [i for i in releases if "prerelease" not in i or not i["prerelease"]]
        releases = {parser.parse(i["published_at"]): i for i in releases if "published_at" in i and i["published_at"]}
        releases = {
            k: v for k, v in releases.items() if "assets" in v and isinstance(v["assets"], list) and v["assets"]
        }
        latest_release = releases[max(releases.keys())]
        asset = None
        if len(latest_release["assets"]) > 1:
            for i in latest_release["assets"]:
                if "name" in i and i["name"] == "update.zip":
                    asset = i
                    break
            if asset is None:
                return print(Ansi.ERROR + "Self update check: No update file found for the version!")
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

    @classmethod
    def do_self_update(cls, asset):
        target = os.path.expanduser("~/Downloads/update.zip")  # TODO bad target
        _ = Downloader(asset["browser_download_url"], target)


if __name__ == "__main__":
    SelfUpdater.ask_update()
    sys.exit()
