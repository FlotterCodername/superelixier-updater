"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import colorama
import json
import os
import re
import sys
from config_loader.defaults import AUTH


class ConfigLoader:

    def __init__(self):
        self._configuration = {}
        cfg_dir = os.path.join(os.path.dirname(sys.argv[0]), "config")
        for cfg in ["auth", "available", "local"]:
            try:
                self._configuration[cfg] = json.load(open(os.path.join(cfg_dir, f"{cfg}.json"), 'r'))
            except FileNotFoundError:
                if cfg == "auth":
                    with open(os.path.join(cfg_dir, f"{cfg}.json"), "w") as file:
                        json.dump(AUTH, file)
                    self._configuration[cfg] = json.load(open(os.path.join(cfg_dir, f"{cfg}.json"), 'r'))
                else:
                    print(f"{colorama.Fore.RED}Fatal error: {cfg}.json was not found but is required.")
                    if cfg == "local":
                        print(f"{colorama.Fore.RED}There is a {cfg}_example.json in the config directory that you can use as a blueprint.")
                    input("Press ENTER to exit.")
                    sys.exit()
            except json.JSONDecodeError:
                print(f"{colorama.Fore.RED}Fatal error: {cfg}.json is not a valid JSON file.")
                input("Press ENTER to exit.")
                sys.exit()
        tmp = self.__validate_paths()
        self._configuration["local"] = tmp

    def write_app_list(self):
        cfg = self._configuration["available"]
        app_list = []
        for app_location in cfg:
            for app in cfg[app_location]:
                app_list.append(app["name"])
        app_list.sort(key=str.casefold)
        markdown = ["# Pre-configured Apps\r\n",
                    "These apps are subject to their respective licenses as determined by _the proprietors of these apps_ ('proprietors' hereafter).",
                    "Inclusion in this list should not be seen as any indication of affiliation of proprietors with _the creator(s) of Superelixier Updater_ ('we' hereafter).",
                    "We only provide automation routines for installing these apps on your local machine.\r\n",
                    "It remains your responsibility as a user of our software to adhere to the terms and licenses proprietors have set for the software that you are asking our routines to access.\r\n",
                    "As a practical example, you may be required to purchase a license from proprietors if using proprietors' software commercially.",
                    "As a further practical example, if you create a modified version of proprietors' software, you may be required to disclose source code of your modified version."]
        for app in app_list:
            markdown.append(f"- {app}")
        markdown = "\r\n".join(markdown)
        with open(os.path.join(os.path.dirname(sys.argv[0]), "Available Apps.md"), "wb") as file:
            file.write(str.encode(markdown))

    def __validate_paths(self):
        cfg_local = self._configuration["local"].copy()
        for key in self._configuration["local"]:
            if re.match(r"^/", key):
                cwdrive = os.path.splitdrive(sys.argv[0])[0]
                key_new = cwdrive + key
                cfg_local[key_new] = cfg_local.pop(key)
        return cfg_local

    @property
    def configuration(self):
        return self._configuration
