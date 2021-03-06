"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import json
import os
import sys
import textwrap
import traceback
from json import JSONDecodeError
from os.path import join as opj
from typing import Optional

import settings
from config_handler import AUTH
from helper import DIR_APP
from helper.terminal import ERROR, WARNING, exit_app
from helper.types import Json, RealBool
from schema.definition import JsonSchema

E_MISSING = ERROR + "%s was not found but is required."
E_INVALID = ERROR + "%s is not valid JSON."
W_INVALID = WARNING + "%s is not valid JSON.%s"

FN_AUTH = "auth.json"
FN_LOCAL = "local.json"
FN_LOCAL_EX = "local_example.json"


class ConfigHandler:
    def __init__(self):
        self._cfg_dir: str = opj(DIR_APP, "config")
        self._schema: JsonSchema = JsonSchema()
        self._configuration: dict = {
            "auth": self._load_auth(),
            "available": self.__load_cfg_available(),
            "local": self._load_local(),
        }
        settings.app_config = self._configuration
        settings.appveyor_headers["Authorization"] = self._configuration["auth"]["appveyor_token"]
        settings.github_headers["Authorization"] = self._configuration["auth"]["github_token"]

    def _load_auth(self) -> Json:
        msg_invalid = E_INVALID % FN_AUTH
        loc = opj(self._cfg_dir, FN_AUTH)
        try:
            return self.__load_json(loc, msg_invalid)
        except FileNotFoundError:
            with open(loc, "w") as fd:
                json.dump(AUTH, fd)
            return self.__load_json(loc)
        except JSONDecodeError:
            exit_app()

    def _load_local(self):
        msg_invalid = E_INVALID % FN_LOCAL
        msg_missing = E_MISSING % FN_LOCAL
        msg_missing += f"You can use '{FN_LOCAL_EX}' in the application's 'config' directory as a blueprint."
        loc = opj(self._cfg_dir, FN_LOCAL)
        try:
            unvalidated = self.__load_json(loc, msg_invalid, msg_missing)
            return ConfigHandler._validate_paths(unvalidated)
        except (FileNotFoundError, JSONDecodeError):
            exit_app()

    @classmethod
    def __load_json(
        cls, path: str, msg_invalid: str = None, msg_missing: str = None, raising: RealBool = True
    ) -> Optional[Json]:
        loaded = None
        try:
            with open(opj(path), "r") as fd:
                loaded = json.load(fd)
        except (FileNotFoundError, JSONDecodeError) as e:
            msg = msg_missing if isinstance(e, FileNotFoundError) else msg_invalid
            print(msg)
            if raising:
                traceback.print_exc()
                raise e
        finally:
            return loaded

    def write_app_list(self):
        cfg = []
        for item in self._configuration["available"]:
            cfg.append(self._configuration["available"][item])
        markdown = [
            textwrap.dedent(
                """
                # Pre-configured Apps
                
                These apps are subject to their respective licenses as determined by _the proprietors of these apps_ 
                ('proprietors' hereafter). Inclusion in this list should not be seen as any indication of affiliation of
                proprietors with _the creator(s) of Superelixier Updater_ ('we' hereafter). We only provide automation
                routines for installing these apps on your local machine.
                
                It remains your responsibility as a user of our software to adhere to the terms and licenses proprietors
                have set for the software that you are asking our routines to access. 
                                
                As a practical example, you may be required to purchase a license from proprietors if using proprietors'
                software commercially. As a further practical example, if you create a modified version of proprietors'
                software, you may be required to disclose source code of your modified version."""
            )
        ]
        cats = []
        for app in cfg:
            if app["info"]["category"] not in cats:
                cats.append(app["info"]["category"])
        cats.sort(key=str.casefold)
        for cat in cats:  # meow
            markdown.append(
                textwrap.dedent(
                    f"""
                    ## {cat}
                    App | Description
                    --- | ---"""
                )
            )
            for app in cfg:
                if app["info"]["category"] == cat:
                    markdown.append(f"**{app['name']}** | {app['info']['gist'].replace('%name', app['name'])}")
        markdown = "\r\n".join(markdown)
        with open(opj(DIR_APP, "docs", "Available Apps.md"), "wb") as file:
            file.write(str.encode(markdown))

    def __load_cfg_available(self):
        definition_dir = opj(DIR_APP, "definitions")
        files = [f for f in os.listdir(definition_dir) if f != ".manifest.json"]
        cfg_available = {}
        for defi in files:
            if defi.endswith(".json"):
                try:
                    my_dict = json.load(open(opj(definition_dir, defi), "r"))
                    if not self._schema.validate_definition(my_dict, filename=defi):
                        raise ValueError
                    cfg_available[my_dict["name"].casefold()] = my_dict
                except ValueError:
                    print(f"{ERROR}Bad definition: {defi!r}")
        return cfg_available

    @classmethod
    def _validate_paths(cls, cfg_local: dict) -> dict:
        converted = {}
        for old, val in cfg_local.items():
            if old.startswith("/") or old.startswith("\\"):
                drive = os.path.splitdrive(sys.argv[0])[0]
                new = drive + old
                converted[new] = val
            else:
                converted[old] = val
        return converted

    @property
    def configuration(self):
        return self._configuration
