"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
from typing import Any, Literal

DefinitionCategory = Literal[
    "Audio & Video", "Developer Tools", "Emulators", "Gaming", "Network Tools", "Security", "Utilities", "Other"
]
DefinitionInstaller = Literal["innoextract", "sfx"]
DefinitionRepo = Literal["appveyor", "github", "html"]
DefinitionVersioning = Literal["id", "integer", "tuple"]

JsonObject = dict[str, Any]
JsonArray = list[list | JsonObject]
Json = JsonArray | JsonObject
JsonResponse = Json | None

UpdateStatus = Literal[
    "no_update", "installed_newer", "update", "no_version_file", "not_installed", "error", "failed", "unknown"
]
