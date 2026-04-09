from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

_VALID_KEY_RE = re.compile(r"^[A-Z0-9_]+$")


@dataclass
class FieldSchema:
    key: str
    type: str
    optional: bool = False
    constraints: dict[str, str] = field(default_factory=dict)
    enum_values: list[str] = field(default_factory=list)


def parse_env_file(path: str | Path) -> dict[str, str]:
    """Parse a .env file and return a dict of key/value pairs."""
    result: dict[str, str] = {}
    with open(path) as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(
                    f"Line {lineno}: invalid syntax (no '=' found): {raw.rstrip()}"
                )
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if not _VALID_KEY_RE.match(key):
                raise ValueError(
                    f"Line {lineno}: key '{key}' must be uppercase (A-Z, 0-9, _)"
                )
            if len(value) >= 2 and (
                (value.startswith('"') and value.endswith('"'))
                or (value.startswith("'") and value.endswith("'"))
            ):
                value = value[1:-1]
            result[key] = value
    return result
