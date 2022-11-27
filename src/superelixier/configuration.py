"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import os
import sys
import textwrap
from copy import deepcopy
from dataclasses import dataclass
from os.path import join as opj

from superelixier.definition import Definition
from superelixier.helper import toml
from superelixier.helper.environment import DIR_APP, DIR_CFG
from superelixier.helper.filesystem import make_path_native
from superelixier.helper.terminal import DENT, Ansi
from superelixier.helper.toml import TOMLDecodeError
from superelixier.helper.types import Json

__all__ = [
    "DirectoryConfig",
    "InvalidAuthException",
    "InvalidLocalException",
    "MissingAuthException",
    "MissingLocalException",
]

E_MISSING = Ansi.ERROR + "The file %s was not found." + Ansi.RESET
E_INVALID = Ansi.ERROR + "The file %s is not valid TOML." + Ansi.RESET

FN_AUTH = "auth.toml"
FN_LOCAL = "local.toml"
FN_LOCAL_EX = "local_example.toml"

UX_SAMPLE_LOCAL = f"""\
[[{Ansi.YELLOW}directory{Ansi.RESET}]]
{Ansi.YELLOW}default{Ansi.RESET} = true  {Ansi.DIM}# Optional. Only one default folder is possible!{Ansi.RESET}
{Ansi.YELLOW}path{Ansi.RESET} = {Ansi.GREEN}"C:/my cool directory/my apps"{Ansi.RESET}
{Ansi.YELLOW}apps{Ansi.RESET} = [
    {Ansi.GREEN}"app1"{Ansi.RESET},
    {Ansi.GREEN}"app2{Ansi.RESET},
]"""

AUTH_DEFAULT: dict[str, str] = {"appveyor_token": "", "github_token": ""}


@dataclass
class DirectoryConfig:
    path: str
    apps: list[str] | None = None
    default: bool = False

    def __post_init__(self):
        if self.path.startswith("/") or self.path.startswith("\\"):
            drive = os.path.splitdrive(sys.argv[0])[0]
            self.path = drive + self.path
            self.__volume_relative = True
        else:
            self.__volume_relative = False
        if self.apps is None:
            self.apps = []
        self.path = make_path_native(self.path)

    @property
    def volume_relative(self) -> bool:
        return self.__volume_relative


class InvalidLocalException(Exception):
    pass


class MissingLocalException(Exception):
    pass


class InvalidAuthException(Exception):
    pass


class MissingAuthException(Exception):
    pass


class ConfigHandler:
    __state = {}

    def __init__(self):
        self.__dict__ = self.__state
        if self.__state == {}:
            self.__auth = None
            self.__definitions = None
            self.__local = None

    @property
    def auth(self):
        if self.__auth is None:
            self.__auth = self._load_auth()
        return deepcopy(self.__auth)

    @property
    def definitions(self):
        if self.__definitions is None:
            self.__definitions = self.__load_definitions()
        return deepcopy(self.__definitions)

    @property
    def local(self) -> dict[str, DirectoryConfig]:
        if self.__local is None:
            self.__local = self._load_local()
        return deepcopy(self.__local)

    def _load_auth(self) -> Json:
        loc = opj(DIR_CFG, FN_AUTH)
        try:
            return self.__load_toml(loc)
        except OSError:
            print(f"Trying to create blank {FN_AUTH}...")
            try:
                with open(loc, "wb") as fd:
                    toml.dump(AUTH_DEFAULT, fd)
                return self.__load_toml(loc)
            except (OSError, TOMLDecodeError):
                raise MissingAuthException(f"Permanently failed to create an {FN_AUTH} file.")
        except TOMLDecodeError:
            raise InvalidAuthException(E_INVALID % FN_AUTH)

    def _load_local(self):
        msg_missing = E_MISSING % FN_LOCAL
        msg_missing += f"\n{DENT}You can use '{FN_LOCAL_EX}' in the application's 'config' directory as a blueprint."
        loc = opj(DIR_CFG, FN_LOCAL)
        try:
            unvalidated = self.__load_toml(loc)
            return ConfigHandler._validate_local(unvalidated)
        except TOMLDecodeError:
            raise InvalidLocalException(E_INVALID % FN_LOCAL)
        except OSError:
            raise MissingLocalException(msg_missing)

    @classmethod
    def __load_toml(cls, path: str) -> Json | None:
        with open(path, "rb") as fd:
            return toml.load(fd)

    def write_app_list(self):
        from superelixier.eula import TERMS

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
        default_directories = []
        try:
            assert isinstance(cfg_loaded["directory"], list)
            for item in cfg_loaded["directory"]:
                assert isinstance(item["path"], str)
                if "apps" in item:
                    assert isinstance(item["apps"], list)
                    for item2 in item["apps"]:
                        assert isinstance(item2, str)
                if "default" in item:
                    assert isinstance(item["default"], bool)
                    if item["default"]:
                        default_directories.append(item["path"])
                assert set(item.keys()).issubset({"path", "apps", "default"})
        except (AssertionError, KeyError):
            raise InvalidLocalException(
                textwrap.dedent(
                    """\
                    The file {} must have one of more "directory" entries, like so:

                    {}

                    Put the file into: {}"""
                ).format(FN_LOCAL, UX_SAMPLE_LOCAL, DIR_CFG)
            )
        if len(default_directories) > 1:
            bulleted = "- " + "\n- ".join(default_directories)
            raise InvalidLocalException(
                textwrap.dedent(
                    """\
                    Multiple folders are set as default (only one is allowed):
                    {}"""
                ).format(bulleted)
            )
        paths = [i["path"] for i in cfg_loaded["directory"]]
        if len(paths) != len(set(paths)):
            for p in set(paths):
                paths.remove(p)
            bulleted = "- " + "\n- ".join(set(paths))
            raise InvalidLocalException(
                textwrap.dedent(
                    """\
                    Duplicate values for directory.path (each value must be unique):
                    {}"""
                ).format(bulleted)
            )
        return {i.path: i for i in (DirectoryConfig(**j) for j in cfg_loaded["directory"])}


configuration = ConfigHandler()
