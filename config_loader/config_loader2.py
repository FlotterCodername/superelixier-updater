"""
Copyright 2021 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
from json import JSONDecodeError

import json
import re
from os.path import join as opj

import helper.terminal
from config_loader.defaults import AUTH
from helper import *
E_MISSING = ERROR + '%s was not found but is required.'
E_INVALID = ERROR + '%s is not valid JSON.'
W_INVALID = WARNING + '%s is not valid JSON.%s'

FN_AUTH = 'auth.json'
FN_LOCAL = 'local.json'
FN_LOCAL_EX = 'local_example.json'

class ConfigHandler:

    def __init__(self):
        self._cfg_dir = opj(DIR_APP, "config")
        self._configuration = {"auth": self._load_auth(), "available": self.__load_cfg_available(), "local": self._load_local()}

    def _load_auth(self):
        msg_invalid = E_INVALID % FN_AUTH
        loc = opj(self._cfg_dir, FN_AUTH)
        try:
            return self.__load_json(loc, msg_invalid)
        except FileNotFoundError:
            with open(loc, "w") as fd:
                json.dump(AUTH, fd)
            return self.__load_json(loc)
        except JSONDecodeError:
            helper.terminal.exit_app()

    def _load_local(self):
        msg_invalid = E_INVALID % FN_LOCAL
        msg_missing = E_MISSING % FN_LOCAL
        msg_missing += "You can use '%s' in the application's 'config' directory as a blueprint." % FN_LOCAL_EX
        loc = opj(self._cfg_dir, FN_LOCAL)
        try:
            return self.__load_json(loc, msg_invalid, msg_missing)
        except (FileNotFoundError, JSONDecodeError):
            helper.terminal.exit_app()

    @staticmethod
    def __load_json(path: str, msg_invalid=None, msg_missing=None, raising=True):
        e_map = {FileNotFoundError: msg_missing, JSONDecodeError: msg_invalid}
        loaded = None
        try:
            with open(opj(path), 'r') as fd:
                loaded = json.load(fd)
        except (FileNotFoundError, JSONDecodeError) as e:
            if error := e_map[type(e)]:
                print(error)
            if raising:
                raise e
        return loaded

    def write_app_list(self):
        cfg = []
        for item in self._configuration["available"]:
            cfg.append(self._configuration["available"][item])
        markdown = ["# Pre-configured Apps\r\n",
                    "These apps are subject to their respective licenses as determined by _the proprietors of these apps_ ('proprietors' hereafter).",
                    "Inclusion in this list should not be seen as any indication of affiliation of proprietors with _the creator(s) of Superelixier Updater_ ('we' hereafter).",
                    "We only provide automation routines for installing these apps on your local machine.\r\n",
                    "It remains your responsibility as a user of our software to adhere to the terms and licenses proprietors have set for the software that you are asking our routines to access.\r\n",
                    "As a practical example, you may be required to purchase a license from proprietors if using proprietors' software commercially.",
                    "As a further practical example, if you create a modified version of proprietors' software, you may be required to disclose source code of your modified version.\r\n"]
        cats = []
        for app in cfg:
            if app['info']['category'] not in cats:
                cats.append(app['info']['category'])
        cats.sort(key=str.casefold)
        for cat in cats:
            markdown.append(f"## {cat}\r\nApp | Description\r\n--- | ---")
            for app in cfg:
                if app["info"]["category"] == cat:
                    markdown.append(f"**{app['name']}** | {app['info']['gist'].replace('%name', app['name'])}")
        markdown = "\r\n".join(markdown)
        with open(opj(DIR_APP, "docs", "Available Apps.md"), "wb") as file:
            file.write(str.encode(markdown))

    @staticmethod
    def __load_cfg_available():
        definition_dir = opj(DIR_APP, "definitions")
        files = [f for f in os.listdir(definition_dir) if f != '.manifest.json']
        cfg_available = {}
        for defi in files:
            if defi.endswith('.json'):
                try:
                    my_dict = json.load(open(opj(definition_dir, defi), 'r'))
                    cfg_available[my_dict["name"].casefold()] = my_dict
                except json.JSONDecodeError:
                    pass
        return cfg_available

    def __validate_paths(self):
        cfg_local = self._configuration["local"].copy()
        for key in self._configuration["local"]:
            if key.startswith('/'):
                cwdrive = os.path.splitdrive(sys.argv[0])[0]
                key_new = cwdrive + key
                cfg_local[key_new] = cfg_local.pop(key)
        return cfg_local

    @property
    def configuration(self):
        return self._configuration
