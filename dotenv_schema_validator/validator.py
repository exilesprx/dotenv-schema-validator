from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from urllib.parse import urlparse

if TYPE_CHECKING:
    from dotenv_schema_validator.parser import FieldSchema

_BOOL_TRUE = frozenset({"true", "1", "yes", "on"})
_BOOL_FALSE = frozenset({"false", "0", "no", "off"})
_BOOL_VALUES = _BOOL_TRUE | _BOOL_FALSE

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class ValidationError:
    key: str
    message: str

    def __str__(self) -> str:
        return f"  - {self.key}: {self.message}"


@dataclass
class ValidationResult:
    errors: list[ValidationError] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0

    def __str__(self) -> str:
        if self.valid:
            return "valid"
        return "\n".join(str(e) for e in self.errors)


def _validate_string(
    key: str, value: str, schema: FieldSchema
) -> ValidationError | None:
    length = len(value)
    if "min" in schema.constraints:
        min_len = int(schema.constraints["min"])
        if length < min_len:
            return ValidationError(
                key, f"must be at least {min_len} characters (got {length})"
            )
    if "max" in schema.constraints:
        max_len = int(schema.constraints["max"])
        if length > max_len:
            return ValidationError(
                key, f"must be at most {max_len} characters (got {length})"
            )
    return None


def _validate_int(key: str, value: str, schema: FieldSchema) -> ValidationError | None:
    try:
        int_val = int(value)
    except ValueError:
        return ValidationError(key, f"must be an integer (got '{value}')")
    if "min" in schema.constraints:
        min_val = int(schema.constraints["min"])
        if int_val < min_val:
            return ValidationError(key, f"must be >= {min_val} (got {int_val})")
    if "max" in schema.constraints:
        max_val = int(schema.constraints["max"])
        if int_val > max_val:
            return ValidationError(key, f"must be <= {max_val} (got {int_val})")
    return None


def _validate_float(
    key: str, value: str, schema: FieldSchema
) -> ValidationError | None:
    try:
        float_val = float(value)
    except ValueError:
        return ValidationError(key, f"must be a float (got '{value}')")
    if "min" in schema.constraints:
        min_val = float(schema.constraints["min"])
        if float_val < min_val:
            return ValidationError(key, f"must be >= {min_val} (got {float_val})")
    if "max" in schema.constraints:
        max_val = float(schema.constraints["max"])
        if float_val > max_val:
            return ValidationError(key, f"must be <= {max_val} (got {float_val})")
    return None


def _validate_bool(key: str, value: str) -> ValidationError | None:
    if value.lower() not in _BOOL_VALUES:
        return ValidationError(
            key,
            f"must be a boolean (true/false, 1/0, yes/no) (got '{value}')",
        )
    return None


def _validate_url(key: str, value: str) -> ValidationError | None:
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return ValidationError(key, f"must be a valid http/https URL (got '{value}')")
    return None


def _validate_email(key: str, value: str) -> ValidationError | None:
    if not _EMAIL_RE.match(value):
        return ValidationError(key, f"must be a valid email address (got '{value}')")
    return None


def _validate_enum(key: str, value: str, schema: FieldSchema) -> ValidationError | None:
    if value not in schema.enum_values:
        options = ", ".join(schema.enum_values)
        return ValidationError(key, f"must be one of ({options}) (got '{value}')")
    return None


def _validate_value(
    key: str, value: str, schema: FieldSchema
) -> ValidationError | None:
    if schema.type in ("string", "int", "float", "enum"):
        dispatch = {
            "string": _validate_string,
            "int": _validate_int,
            "float": _validate_float,
            "enum": _validate_enum,
        }
        return dispatch[schema.type](key, value, schema)
    simple_dispatch = {
        "bool": _validate_bool,
        "url": _validate_url,
        "email": _validate_email,
    }
    if schema.type in simple_dispatch:
        return simple_dispatch[schema.type](key, value)
    return None  # unreachable given parser validation, but satisfies mypy


def validate(env: dict[str, str], schema: dict[str, FieldSchema]) -> ValidationResult:
    """Validate a parsed env dict against a parsed schema dict."""
    result = ValidationResult()

    for key, field_schema in schema.items():
        if key not in env:
            if not field_schema.optional:
                result.errors.append(ValidationError(key, "required key is missing"))
            continue

        value = env[key]

        if value == "":
            if not field_schema.optional:
                result.errors.append(
                    ValidationError(key, "required key has an empty value")
                )
            continue

        error = _validate_value(key, value, field_schema)
        if error is not None:
            result.errors.append(error)

    return result
