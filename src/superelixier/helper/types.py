"""
Copyright © 2022 Fabian H. Schneider

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
If a copy of the MPL was not distributed with this file,
You can obtain one at https://mozilla.org/MPL/2.0/.
"""
from typing import Any

JsonObject = dict[str, Any]
JsonArray = list[list | JsonObject]
Json = JsonArray | JsonObject
JsonResponse = Json | None
