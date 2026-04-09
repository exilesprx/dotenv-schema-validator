import pytest

from dotenv_schema_validator.parser import parse_env_file


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
