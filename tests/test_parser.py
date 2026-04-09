import pytest

from dotenv_schema_validator.parser import parse_env_file, parse_schema_file


def test_parse_env_basic(tmp_path: pytest.TempPathFactory) -> None:
    env = tmp_path / ".env"  # type: ignore[operator]
    env.write_text("KEY=value\nOTHER=hello\n")
    result = parse_env_file(env)
    assert result == {"KEY": "value", "OTHER": "hello"}


def test_parse_env_strips_double_quotes(tmp_path: pytest.TempPathFactory) -> None:
    env = tmp_path / ".env"  # type: ignore[operator]
    env.write_text('KEY="quoted value"\n')
    result = parse_env_file(env)
    assert result == {"KEY": "quoted value"}


def test_parse_env_strips_single_quotes(tmp_path: pytest.TempPathFactory) -> None:
    env = tmp_path / ".env"  # type: ignore[operator]
    env.write_text("KEY='single quoted'\n")
    result = parse_env_file(env)
    assert result == {"KEY": "single quoted"}


def test_parse_env_skips_comments(tmp_path: pytest.TempPathFactory) -> None:
    env = tmp_path / ".env"  # type: ignore[operator]
    env.write_text("# this is a comment\nKEY=value\n")
    result = parse_env_file(env)
    assert result == {"KEY": "value"}


def test_parse_env_skips_blank_lines(tmp_path: pytest.TempPathFactory) -> None:
    env = tmp_path / ".env"  # type: ignore[operator]
    env.write_text("\n\nKEY=value\n\n")
    result = parse_env_file(env)
    assert result == {"KEY": "value"}


def test_parse_env_strips_whitespace(tmp_path: pytest.TempPathFactory) -> None:
    env = tmp_path / ".env"  # type: ignore[operator]
    env.write_text("  KEY  =  value  \n")
    result = parse_env_file(env)
    assert result == {"KEY": "value"}


def test_parse_env_empty_value(tmp_path: pytest.TempPathFactory) -> None:
    env = tmp_path / ".env"  # type: ignore[operator]
    env.write_text("KEY=\n")
    result = parse_env_file(env)
    assert result == {"KEY": ""}


def test_parse_env_value_with_equals(tmp_path: pytest.TempPathFactory) -> None:
    env = tmp_path / ".env"  # type: ignore[operator]
    env.write_text("KEY=foo=bar\n")
    result = parse_env_file(env)
    assert result == {"KEY": "foo=bar"}


def test_parse_env_raises_on_missing_equals(tmp_path: pytest.TempPathFactory) -> None:
    env = tmp_path / ".env"  # type: ignore[operator]
    env.write_text("INVALID_LINE\n")
    with pytest.raises(ValueError, match="Line 1"):
        parse_env_file(env)


def test_parse_env_raises_on_lowercase_key(tmp_path: pytest.TempPathFactory) -> None:
    env = tmp_path / ".env"  # type: ignore[operator]
    env.write_text("port=8080\n")
    with pytest.raises(ValueError, match="key 'port' must be uppercase"):
        parse_env_file(env)


# --- parse_schema_file tests ---


def test_parse_schema_required_string(tmp_path: pytest.TempPathFactory) -> None:
    schema = tmp_path / ".schema.env"  # type: ignore[operator]
    schema.write_text("API_KEY=string\n")
    result = parse_schema_file(schema)
    assert result["API_KEY"].key == "API_KEY"
    assert result["API_KEY"].type == "string"
    assert result["API_KEY"].optional is False
    assert result["API_KEY"].constraints == {}
    assert result["API_KEY"].enum_values == []


def test_parse_schema_optional_bool(tmp_path: pytest.TempPathFactory) -> None:
    schema = tmp_path / ".schema.env"  # type: ignore[operator]
    schema.write_text("DEBUG=optional|bool\n")
    result = parse_schema_file(schema)
    assert result["DEBUG"].type == "bool"
    assert result["DEBUG"].optional is True


def test_parse_schema_string_constraints(tmp_path: pytest.TempPathFactory) -> None:
    schema = tmp_path / ".schema.env"  # type: ignore[operator]
    schema.write_text("API_KEY=string(min=32,max=64)\n")
    result = parse_schema_file(schema)
    assert result["API_KEY"].type == "string"
    assert result["API_KEY"].constraints == {"min": "32", "max": "64"}


def test_parse_schema_enum_values(tmp_path: pytest.TempPathFactory) -> None:
    schema = tmp_path / ".schema.env"  # type: ignore[operator]
    schema.write_text("APP_ENV=enum(development,staging,production)\n")
    result = parse_schema_file(schema)
    assert result["APP_ENV"].type == "enum"
    assert result["APP_ENV"].enum_values == ["development", "staging", "production"]


def test_parse_schema_skips_comments_and_blanks(
    tmp_path: pytest.TempPathFactory,
) -> None:
    schema = tmp_path / ".schema.env"  # type: ignore[operator]
    schema.write_text("# comment\n\nKEY=string\n")
    result = parse_schema_file(schema)
    assert list(result.keys()) == ["KEY"]


def test_parse_schema_raises_on_unrecognised_type(
    tmp_path: pytest.TempPathFactory,
) -> None:
    schema = tmp_path / ".schema.env"  # type: ignore[operator]
    schema.write_text("KEY=uuid\n")
    with pytest.raises(ValueError, match="unrecognised type"):
        parse_schema_file(schema)


def test_parse_schema_raises_on_enum_no_values(
    tmp_path: pytest.TempPathFactory,
) -> None:
    schema = tmp_path / ".schema.env"  # type: ignore[operator]
    schema.write_text("KEY=enum()\n")
    with pytest.raises(ValueError, match="enum must have at least one value"):
        parse_schema_file(schema)


def test_parse_schema_raises_on_lowercase_key(
    tmp_path: pytest.TempPathFactory,
) -> None:
    schema = tmp_path / ".schema.env"  # type: ignore[operator]
    schema.write_text("port=int\n")
    with pytest.raises(ValueError, match="key 'port' must be uppercase"):
        parse_schema_file(schema)
