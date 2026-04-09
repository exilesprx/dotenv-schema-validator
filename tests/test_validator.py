import pytest

from dotenv_schema_validator.parser import FieldSchema
from dotenv_schema_validator.validator import (
    ValidationError,
    ValidationResult,
    validate,
)


def make_schema(**fields: FieldSchema) -> dict[str, FieldSchema]:
    return dict(fields)


def required(type: str, **constraints: str) -> FieldSchema:
    return FieldSchema(key="", type=type, optional=False, constraints=constraints)


def optional(type: str) -> FieldSchema:
    return FieldSchema(key="", type=type, optional=True)


def enum_schema(*values: str) -> FieldSchema:
    return FieldSchema(key="", type="enum", optional=False, enum_values=list(values))


# --- Missing / empty key tests ---


def test_missing_required_key_produces_error() -> None:
    schema = make_schema(API_KEY=required("string"))
    result = validate({}, schema)
    assert not result.valid
    assert len(result.errors) == 1
    assert result.errors[0].key == "API_KEY"
    assert result.errors[0].message == "required key is missing"


def test_missing_optional_key_produces_no_error() -> None:
    schema = make_schema(DEBUG=optional("bool"))
    result = validate({}, schema)
    assert result.valid


def test_empty_required_value_produces_error() -> None:
    schema = make_schema(API_KEY=required("string"))
    result = validate({"API_KEY": ""}, schema)
    assert not result.valid
    assert result.errors[0].message == "required key has an empty value"


def test_empty_optional_value_produces_no_error() -> None:
    schema = make_schema(DEBUG=optional("bool"))
    result = validate({"DEBUG": ""}, schema)
    assert result.valid


# --- string tests ---


def test_string_min_passes_when_length_gte_min() -> None:
    schema = make_schema(KEY=required("string", min="5"))
    result = validate({"KEY": "hello"}, schema)
    assert result.valid


def test_string_min_fails_when_length_lt_min() -> None:
    schema = make_schema(KEY=required("string", min="10"))
    result = validate({"KEY": "short"}, schema)
    assert not result.valid
    assert "must be at least 10 characters" in result.errors[0].message
    assert "got 5" in result.errors[0].message


def test_string_max_fails_when_length_gt_max() -> None:
    schema = make_schema(KEY=required("string", max="3"))
    result = validate({"KEY": "toolong"}, schema)
    assert not result.valid
    assert "must be at most 3 characters" in result.errors[0].message
    assert "got 7" in result.errors[0].message


# --- int tests ---


def test_int_fails_when_not_a_number() -> None:
    schema = make_schema(PORT=required("int"))
    result = validate({"PORT": "abc"}, schema)
    assert not result.valid
    assert "must be an integer" in result.errors[0].message
    assert "got 'abc'" in result.errors[0].message


def test_int_min_fails_when_value_lt_min() -> None:
    schema = make_schema(PORT=required("int", min="1"))
    result = validate({"PORT": "0"}, schema)
    assert not result.valid
    assert "must be >= 1" in result.errors[0].message
    assert "got 0" in result.errors[0].message


def test_int_max_fails_when_value_gt_max() -> None:
    schema = make_schema(PORT=required("int", max="65535"))
    result = validate({"PORT": "99999"}, schema)
    assert not result.valid
    assert "must be <= 65535" in result.errors[0].message
    assert "got 99999" in result.errors[0].message


def test_int_passes_valid_value() -> None:
    schema = make_schema(PORT=required("int", min="1", max="65535"))
    result = validate({"PORT": "8080"}, schema)
    assert result.valid


# --- float tests ---


def test_float_fails_when_not_a_float() -> None:
    schema = make_schema(RATIO=required("float"))
    result = validate({"RATIO": "abc"}, schema)
    assert not result.valid
    assert "must be a float" in result.errors[0].message


def test_float_passes_valid_value() -> None:
    schema = make_schema(RATIO=required("float"))
    result = validate({"RATIO": "3.14"}, schema)
    assert result.valid


# --- bool tests ---


@pytest.mark.parametrize(
    "value", ["true", "false", "1", "0", "yes", "no", "True", "FALSE"]
)
def test_bool_passes_for_valid_values(value: str) -> None:
    schema = make_schema(FLAG=required("bool"))
    result = validate({"FLAG": value}, schema)
    assert result.valid


def test_bool_fails_for_invalid_value() -> None:
    schema = make_schema(FLAG=required("bool"))
    result = validate({"FLAG": "enabled"}, schema)
    assert not result.valid
    assert "must be a boolean" in result.errors[0].message
    assert "got 'enabled'" in result.errors[0].message


# --- url tests ---


def test_url_passes_for_valid_https_url() -> None:
    schema = make_schema(API_URL=required("url"))
    result = validate({"API_URL": "https://example.com"}, schema)
    assert result.valid


def test_url_fails_for_non_url_string() -> None:
    schema = make_schema(API_URL=required("url"))
    result = validate({"API_URL": "not-a-url"}, schema)
    assert not result.valid
    assert "must be a valid http/https URL" in result.errors[0].message


def test_url_fails_for_non_http_scheme() -> None:
    schema = make_schema(API_URL=required("url"))
    result = validate({"API_URL": "ftp://example.com"}, schema)
    assert not result.valid
    assert "must be a valid http/https URL" in result.errors[0].message


# --- email tests ---


def test_email_passes_for_valid_email() -> None:
    schema = make_schema(ADMIN_EMAIL=required("email"))
    result = validate({"ADMIN_EMAIL": "user@example.com"}, schema)
    assert result.valid


def test_email_fails_for_invalid_email() -> None:
    schema = make_schema(ADMIN_EMAIL=required("email"))
    result = validate({"ADMIN_EMAIL": "notanemail"}, schema)
    assert not result.valid
    assert "must be a valid email address" in result.errors[0].message


# --- enum tests ---


def test_enum_passes_when_value_in_list() -> None:
    schema = make_schema(APP_ENV=enum_schema("development", "staging", "production"))
    result = validate({"APP_ENV": "staging"}, schema)
    assert result.valid


def test_enum_fails_when_value_not_in_list() -> None:
    schema = make_schema(APP_ENV=enum_schema("development", "staging", "production"))
    result = validate({"APP_ENV": "prod"}, schema)
    assert not result.valid
    assert "must be one of" in result.errors[0].message
    assert "got 'prod'" in result.errors[0].message


# --- ValidationError / ValidationResult str tests ---


def test_validation_error_str() -> None:
    error = ValidationError(key="PORT", message="must be an integer (got 'abc')")
    assert str(error) == "  - PORT: must be an integer (got 'abc')"


def test_validation_result_valid_property() -> None:
    result = ValidationResult()
    assert result.valid
    result.errors.append(ValidationError("KEY", "required key is missing"))
    assert not result.valid


# --- Multiple errors reported together ---


def test_multiple_errors_reported_in_single_result() -> None:
    schema = make_schema(
        API_KEY=required("string", min="32"),
        PORT=required("int", max="65535"),
        APP_ENV=enum_schema("development", "staging", "production"),
    )
    env = {"API_KEY": "short", "PORT": "99999", "APP_ENV": "prod"}
    result = validate(env, schema)
    assert not result.valid
    assert len(result.errors) == 3
    keys = {e.key for e in result.errors}
    assert keys == {"API_KEY", "PORT", "APP_ENV"}
