"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
from dataclasses import dataclass
from typing import Optional

import jsonschema

from superelixier.helper.terminal import Ansi
from superelixier.helper.types import (
    DefinitionCategory,
    DefinitionInstaller,
    DefinitionRepo,
    DefinitionVersioning,
    JsonObject,
)
from superelixier.schema import BOOL, INT, NULL, STR, any_of, array_of, enum


@dataclass(frozen=True)
class DefinitionInfo:
    name: str
    category: DefinitionCategory = None
    gist: str = None

    @classmethod
    def from_dict(cls, obj: dict | None) -> "DefinitionInfo":
        key = "info"
        if isinstance(obj, dict):
            if key in obj:
                return cls(**obj[key])
            else:
                raise ValueError
        else:
            raise TypeError

    @classmethod
    def schema(cls):
        return {
            "properties": {"name": STR, "category": any_of(STR, NULL), "gist": any_of(STR, NULL)},
            "required": ["name"],
            "additionalProperties": False,
        }


@dataclass(frozen=True)
class DefinitionAppveyor:
    blob_re: str
    user: str
    project: str
    branch: str = None

    @classmethod
    def from_dict(cls, obj: dict | None) -> Optional["DefinitionAppveyor"]:
        key = "appveyor"
        if isinstance(obj, dict) and key in obj:
            return cls(**obj[key])

    @classmethod
    def schema(cls):
        return {
            "properties": {"blob_re": STR, "user": STR, "project": STR, "branch": any_of(STR, NULL)},
            "required": ["blob_re", "user", "project"],
            "additionalProperties": False,
        }


@dataclass(frozen=True)
class DefinitionGithub:
    blob_re: str
    user: str
    project: str
    prerelease: bool = None

    @classmethod
    def from_dict(cls, obj: dict | None) -> Optional["DefinitionGithub"]:
        key = "github"
        if isinstance(obj, dict) and key in obj:
            return cls(**obj[key])

    @classmethod
    def schema(cls):
        return {
            "properties": {"blob_re": STR, "user": STR, "project": STR, "prerelease": any_of(BOOL, NULL)},
            "required": ["blob_re", "user", "project"],
            "additionalProperties": False,
        }


@dataclass(frozen=True)
class DefinitionHTML:
    url: str
    versioning: DefinitionVersioning
    blob_re: str = None
    blob_permalink: str = None
    blob_permalink_re: DefinitionVersioning = None
    versioning_spec: int = None

    @classmethod
    def from_dict(cls, obj: dict | None) -> Optional["DefinitionHTML"]:
        key = "html"
        if isinstance(obj, dict) and key in obj:
            return cls(**obj[key])

    @classmethod
    def schema(cls):
        return {
            "properties": {
                "url": STR,
                "versioning": enum(DefinitionVersioning),
                "blob_re": STR,
                "blob_permalink": STR,
                "blob_permalink_re": STR,
                "versioning_spec": any_of(INT, NULL),
            },
            "required": ["url", "versioning"],
            "oneOf": [
                {"required": ["blob_re"]},
                {"required": ["blob_permalink", "blob_permalink_re"]},
            ],
            "additionalProperties": False,
        }


@dataclass(frozen=True)
class DefinitionLocal:
    appdata: list[str] = ""
    delete: list[str] = ""
    installer: DefinitionInstaller = None

    def __post_init__(self):
        if isinstance(self.appdata, str):
            object.__setattr__(self, "appdata", [self.appdata])
        if isinstance(self.delete, str):
            object.__setattr__(self, "delete", [self.delete])

    @classmethod
    def from_dict(cls, obj: dict | None) -> Optional["DefinitionLocal"]:
        key = "local"
        if isinstance(obj, dict):
            return cls(**obj[key]) if key in obj else cls()

    @classmethod
    def schema(cls):
        return {
            "properties": {
                "appdata": any_of(array_of(STR), STR, NULL),
                "delete": any_of(array_of(STR), STR, NULL),
                "installer": enum(DefinitionInstaller),
            },
            "required": [],
            "additionalProperties": False,
        }


@dataclass(frozen=True)
class Definition:
    info: DefinitionInfo
    appveyor: DefinitionAppveyor | None
    github: DefinitionGithub | None
    html: DefinitionHTML | None
    local: DefinitionLocal | None

    @property
    def repo_type(self) -> DefinitionRepo:
        if self.appveyor is not None:
            return "appveyor"
        elif self.github is not None:
            return "github"
        else:
            return "html"

    @property
    def repo(self) -> DefinitionAppveyor | DefinitionGithub | DefinitionHTML:
        for prop in (self.appveyor, self.github, self.html):
            if prop is not None:
                return prop
        raise RuntimeError

    @classmethod
    def from_dict(cls, obj: dict):
        assert Definition.validate_definition(obj, "", quiet=True)
        return Definition(
            info=DefinitionInfo.from_dict(obj),
            appveyor=DefinitionAppveyor.from_dict(obj),
            github=DefinitionGithub.from_dict(obj),
            html=DefinitionHTML.from_dict(obj),
            local=DefinitionLocal.from_dict(obj),
        )

    @classmethod
    def schema(cls):
        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "TODO",
            "title": "An app definition for the superelixier-updater application",
            "type": "object",
            "properties": {
                "info": DefinitionInfo.schema(),
                "appveyor": DefinitionAppveyor.schema(),
                "github": DefinitionGithub.schema(),
                "html": DefinitionHTML.schema(),
                "local": DefinitionLocal.schema(),
            },
            "required": ["info"],
            "oneOf": [{"required": ["appveyor"]}, {"required": ["github"]}, {"required": ["html"]}],
            "additionalProperties": False,
        }

    @classmethod
    def dump_schema(cls):
        import json

        print(json.dumps(cls.schema(), indent=2))

    @classmethod
    def validate_definition(cls, obj: JsonObject, filename: str, *, quiet: bool = False) -> bool:
        schema = cls.schema()
        try:
            jsonschema.validate(obj, schema)
        except jsonschema.ValidationError:
            if not quiet:
                print(f"{Ansi.ERROR}file {filename}: ValidationError!{Ansi.RESET}")
            return False
        except jsonschema.SchemaError:
            raise RuntimeError("The app has a bug in its definition schema validation!")
        return True
