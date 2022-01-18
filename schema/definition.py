"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
import copy

import jsonschema

from helper.terminal import ERROR

INSTALLERS = {"enum": ["sfx", "innoextract"]}
REPOS = {"enum": ["appveyor", "github", "html"]}
VS_TYPES = {"enum": ["id", "integer", "tuple"]}

ARRAY = {"type": "array"}
BOOL = {"type": "boolean"}
INT = {"type": "integer"}
STRING = {"type": "string"}

INFO = {
    "type": "object",
    "required": ["gist", "category"],
    "properties": {
        "gist": {"anyOf": [STRING, ARRAY]},
        "category": {"type": "string"},
    },
    "additionalProperties": False,
}

PROPERTIES = {
    "appdatas": {"anyOf": [STRING, ARRAY]},
    "blob_re": STRING,
    "blob_permalink": STRING,
    "blob_unwanted": {"anyOf": [STRING, ARRAY]},
    "branch": STRING,
    "info": INFO,
    "installer": INSTALLERS,
    "name": STRING,
    "url": STRING,
    "user": STRING,
    "prerelease": BOOL,
    "project": STRING,
    "repo": REPOS,
    "ver_scheme_re": STRING,
    "ver_scheme_type": VS_TYPES,
    "ver_scheme_spec": INT,
}

DEFINITION_BASE = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "required": ["info", "url", "repo"],
    "properties": PROPERTIES,
    "additionalProperties": False,
}

DISALLOW_APIBASED = [
    "blob_permalink",
    "url",
    "ver_scheme_re",
    "ver_scheme_type",
    "ver_scheme_spec",
]
DISALLOW_APPVEYOR = [*DISALLOW_APIBASED, "prerelease"]
DISALLOW_GITHUB = [*DISALLOW_APIBASED, "branch"]
DISALLOW_HTML = ["branch", "user", "project", "prelease"]
REQUIRE_APPVEYOR = {"required": ["blob_re", "branch", "info", "name", "project", "repo", "user"]}
REQUIRE_GITHUB = {"required": ["blob_re", "info", "name", "project", "repo", "user"]}
REQUIRE_HTML = {
    "required": ["info", "url", "repo", "ver_scheme_type"],
    "oneOf": [
        {"required": ["blob_permalink", "ver_scheme_re"]},
        {"required": ["blob_re"]},
    ],
}


class JsonSchema:
    def __init__(self):
        self.__definition_appveyor = copy.deepcopy(DEFINITION_BASE)
        self.__definition_github = copy.deepcopy(DEFINITION_BASE)
        self.__definition_html = copy.deepcopy(DEFINITION_BASE)
        self.__apply_override()
        self.REPO_MAP = {
            "appveyor": self.__definition_appveyor,
            "github": self.__definition_github,
            "html": self.__definition_html,
        }

    def __apply_override(self):
        my_actions = (
            (self.__definition_appveyor, REQUIRE_APPVEYOR, DISALLOW_APPVEYOR),
            (self.__definition_github, REQUIRE_GITHUB, DISALLOW_GITHUB),
            (self.__definition_html, REQUIRE_HTML, DISALLOW_HTML),
        )
        for row in my_actions:
            row[0].update(row[1])
            for key in row[2]:
                if key in row[0]["properties"]:
                    row[0]["properties"].pop(key)

    def validate_definition(self, obj, filename):
        if "repo" not in obj:
            print('%sfile %s: Missing key "repo"!' % (ERROR, filename))
            return False
        if obj["repo"] not in REPOS["enum"]:
            print('%sfile %s: Unknown value for key "repo"!' % (ERROR, filename))
            return False
        model = self.REPO_MAP[obj["repo"]]
        try:
            jsonschema.validate(obj, model)
        except jsonschema.ValidationError:
            print("%sfile %s: ValidationError!" % (ERROR, filename))
            return False
        except jsonschema.SchemaError:
            print("%sfile %s: The app has a bug in its %s schema validation!" % (ERROR, filename, obj["repo"]))
            return False
        return True


if __name__ == "__main__":
    instance = JsonSchema()
    for key in instance.REPO_MAP:
        with open(key + ".schema.json", "w") as fd:
            import json

            json.dump(instance.REPO_MAP[key], fd, indent=2)
