from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

_VALID_KEY_RE = re.compile(r"^[A-Z0-9_]+$")
_MIN_QUOTED_LEN = 2


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
    with Path(path).open() as f:
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
            if len(value) >= _MIN_QUOTED_LEN and (
                (value.startswith('"') and value.endswith('"'))
                or (value.startswith("'") and value.endswith("'"))
            ):
                value = value[1:-1]
            result[key] = value
    return result


_VALID_TYPES = frozenset({"string", "int", "float", "bool", "url", "email", "enum"})


def _parse_rule(key: str, raw_rule: str) -> FieldSchema:
    """Parse a single schema rule string into a FieldSchema."""
    rule = raw_rule.strip()
    optional = False

    if rule.startswith("optional|"):
        optional = True
        rule = rule[len("optional|") :]

    # Split type from constraints: e.g. "string(min=32,max=64)" or "enum(a,b,c)"
    paren_open = rule.find("(")
    if paren_open == -1:
        type_name = rule.strip()
        args_str = ""
    else:
        if not rule.endswith(")"):
            raise ValueError(
                f"key '{key}': malformed rule, missing closing ')': {raw_rule!r}"
            )
        type_name = rule[:paren_open].strip()
        args_str = rule[paren_open + 1 : -1]

    if type_name not in _VALID_TYPES:
        raise ValueError(f"key '{key}': unrecognised type '{type_name}'")

    constraints: dict[str, str] = {}
    enum_values: list[str] = []

    if args_str:
        if type_name == "enum":
            enum_values = [v.strip() for v in args_str.split(",")]
            if not enum_values or all(v == "" for v in enum_values):
                raise ValueError(f"key '{key}': enum must have at least one value")
        else:
            for part in args_str.split(","):
                stripped = part.strip()
                if "=" not in stripped:
                    raise ValueError(f"key '{key}': malformed constraint '{stripped}'")
                cname, _, cval = stripped.partition("=")
                constraints[cname.strip()] = cval.strip()
    elif type_name == "enum":
        raise ValueError(f"key '{key}': enum must have at least one value")

    return FieldSchema(
        key=key,
        type=type_name,
        optional=optional,
        constraints=constraints,
        enum_values=enum_values,
    )


def parse_schema_file(path: str | Path) -> dict[str, FieldSchema]:
    """Parse a .schema.env file and return a dict of key to FieldSchema."""
    result: dict[str, FieldSchema] = {}
    with Path(path).open() as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(
                    f"Line {lineno}: invalid syntax (no '=' found): {raw.rstrip()}"
                )
            key, _, rule = line.partition("=")
            key = key.strip()
            if not _VALID_KEY_RE.match(key):
                raise ValueError(f"key '{key}' must be uppercase (A-Z, 0-9, _)")
            result[key] = _parse_rule(key, rule)
    return result
