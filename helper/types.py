from typing import Any

JsonObject = dict[str, Any]
JsonArray = list[JsonObject]
Json = JsonArray | JsonObject
JsonResponse = Json | None
FlakyBool = bool | None
