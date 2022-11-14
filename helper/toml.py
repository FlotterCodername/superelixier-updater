from typing import IO, Any

import tomli
import tomli_w


def dumps(obj: Any) -> str:
    return ""


def loads(s: str | bytes) -> Any:
    pass


def dump(obj: Any, fp: IO[str]) -> None:
    pass


def load(fp) -> Any:
    pass
