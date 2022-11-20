"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import os
import sys
import traceback
from copy import deepcopy
from os.path import join as opj

from superelixier.config_handler.eula import TERMS
from superelixier.definition import Definition
from superelixier.helper import toml
from superelixier.helper.filesystem import DIR_APP, DIR_CFG
from superelixier.helper.terminal import Ansi, exit_app
from superelixier.helper.toml import TOMLDecodeError
from superelixier.helper.types import Json

E_MISSING = Ansi.ERROR + "%s was not found but is required."
E_INVALID = Ansi.ERROR + "%s is not valid TOML."
W_INVALID = Ansi.WARNING + "%s is not valid TOML.%s"

FN_AUTH = "auth.toml"
FN_LOCAL = "local.toml"
FN_LOCAL_EX = "local_example.toml"

UX_MISSING_LOCAL = f"""\
The file {FN_LOCAL} must have one of more "directory" entries, like so:

[[{Ansi.YELLOW}directory{Ansi.RESET}]]
{Ansi.YELLOW}path{Ansi.RESET} = {Ansi.GREEN}"C:/my cool directory/my apps"{Ansi.RESET}
{Ansi.YELLOW}apps{Ansi.RESET} = [
    {Ansi.GREEN}"app1"{Ansi.RESET},
    {Ansi.GREEN}"app2{Ansi.RESET},
]

Put the file into: {DIR_APP}"""

AUTH_DEFAULT: dict[str, str] = {"appveyor_token": "", "github_token": ""}

__all__ = []


class ConfigHandler:
    __state = {}

    def __init__(self):
        self.__dict__ = self.__state
        if self.__state == {}:
            self.__auth = self._load_auth()
            self.__definitions = self.__load_definitions()
            self.__local = self._load_local()

    @property
    def auth(self):
        return deepcopy(self.__auth)

    @property
    def definitions(self):
        return deepcopy(self.__definitions)

    @property
    def local(self):
        return deepcopy(self.__local)

    def _load_auth(self) -> Json:
        msg_invalid = E_INVALID % FN_AUTH
        loc = opj(DIR_CFG, FN_AUTH)
        try:
            return self.__load_toml(loc, msg_invalid)
        except FileNotFoundError:
            with open(loc, "wb") as fd:
                toml.dump(AUTH_DEFAULT, fd)
            return self.__load_toml(loc)
        except TOMLDecodeError:
            exit_app()

    def _load_local(self):
        msg_invalid = E_INVALID % FN_LOCAL
        msg_missing = E_MISSING % FN_LOCAL
        msg_missing += f"You can use '{FN_LOCAL_EX}' in the application's 'config' directory as a blueprint."
        loc = opj(DIR_CFG, FN_LOCAL)
        try:
            unvalidated = self.__load_toml(loc, msg_invalid, msg_missing)
            return ConfigHandler._validate_local(unvalidated)
        except (FileNotFoundError, TOMLDecodeError):
            exit_app()

    @classmethod
    def __load_toml(
        cls, path: str, msg_invalid: str = None, msg_missing: str = None, raising: bool = True
    ) -> Json | None:
        loaded = None
        try:
            with open(opj(path), "rb") as fd:
                loaded = toml.load(fd)
        except (FileNotFoundError, TOMLDecodeError) as e:
            msg = msg_missing if isinstance(e, FileNotFoundError) else msg_invalid
            print(msg)
            if raising:
                traceback.print_exc()
                raise e
        finally:
            return loaded

    def write_app_list(self):
        cfg = []
        for item in self.definitions:
            cfg.append(self.definitions[item])
        markdown = [TERMS]
        cats = []
        for app in cfg:
            if app.info.category not in cats:
                cats.append(app.info.category)
        cats.sort(key=str.casefold)
        for cat in cats:  # meow
            markdown.append(f"## {cat}\r\n| App | Description |\r\n| --- | --- |")
            for app in cfg:
                if app.info.category == cat:
                    markdown.append(f"| **{app.info.name}** | {app.info.gist.replace('%name', app.info.name)} |")
        markdown = "\r\n".join(markdown)
        with open(opj(DIR_APP, "docs", "Available Apps.md"), "wb") as file:
            file.write(str.encode(markdown))

    @classmethod
    def __load_definitions(cls):
        definition_dir = opj(DIR_APP, "definitions")
        files = [f for f in os.listdir(definition_dir) if f.endswith(".toml")]
        cfg_available = {}
        for defi in files:
            try:
                with open(opj(definition_dir, defi), "rb") as fd:
                    my_dict = toml.load(fd)
                if not Definition.validate_definition(my_dict, filename=defi):
                    raise ValueError
                cfg_available[my_dict["info"]["name"].casefold()] = Definition.from_dict(my_dict)
            except TOMLDecodeError:
                print(f"{Ansi.ERROR}Bad TOML file: {defi!r}")
            except ValueError:
                print(f"{Ansi.ERROR}Bad definition: {defi!r}")
        return cfg_available

    @classmethod
    def _validate_local(cls, cfg_loaded: dict) -> dict:
        try:
            assert isinstance(cfg_loaded["directory"], list)
            for item in cfg_loaded["directory"]:
                assert isinstance(item["path"], str)
                if "apps" in item:
                    assert isinstance(item["apps"], list)
                    for item2 in item["apps"]:
                        assert isinstance(item2, str)
        except (AssertionError, KeyError):
            print(UX_MISSING_LOCAL)
            exit_app()

        cfg_local = {entry["path"]: entry["apps"] for entry in cfg_loaded["directory"]}
        converted = {}
        for old, val in cfg_local.items():
            if old.startswith("/") or old.startswith("\\"):
                drive = os.path.splitdrive(sys.argv[0])[0]
                new = drive + old
                converted[new] = val
            else:
                converted[old] = val
        return converted


configuration = ConfigHandler()
