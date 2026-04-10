import pytest
from click.testing import CliRunner

from dotenv_schema_validator.generate_cli import main
from dotenv_schema_validator.generator import generate_schema

# ---------------------------------------------------------------------------
# generate_schema() unit tests
# ---------------------------------------------------------------------------


def test_non_empty_value_produces_string_rule() -> None:
    result = generate_schema({"API_KEY": "abc123"})
    assert "API_KEY=string" in result


def test_empty_value_produces_optional_string_rule() -> None:
    result = generate_schema({"DEBUG": ""})
    assert "DEBUG=optional|string" in result


def test_output_preserves_insertion_order() -> None:
    env = {"FIRST": "one", "SECOND": "two", "THIRD": "three"}
    result = generate_schema(env)
    lines = result.strip().splitlines()
    assert lines == ["FIRST=string", "SECOND=string", "THIRD=string"]


def test_multiple_keys_all_emitted() -> None:
    env = {"A": "val", "B": "", "C": "other"}
    result = generate_schema(env)
    assert "A=string" in result
    assert "B=optional|string" in result
    assert "C=string" in result


def test_output_ends_with_trailing_newline() -> None:
    result = generate_schema({"KEY": "value"})
    assert result.endswith("\n")


def test_empty_dict_produces_only_newline() -> None:
    result = generate_schema({})
    assert result == "\n"


# ---------------------------------------------------------------------------
# generate_cli (dotenv-schema-generate) CLI tests
# ---------------------------------------------------------------------------


def test_cli_writes_schema_file_on_success(tmp_path: pytest.TempPathFactory) -> None:
    env_file = tmp_path / ".env"  # type: ignore[operator]
    env_file.write_text("API_KEY=secret\nDEBUG=\n")
    output_file = tmp_path / ".schema.env"  # type: ignore[operator]

    runner = CliRunner()
    result = runner.invoke(main, [str(env_file), "--output", str(output_file)])

    assert result.exit_code == 0
    content = output_file.read_text()
    assert "API_KEY=string" in content
    assert "DEBUG=optional|string" in content


def test_cli_prints_success_message(tmp_path: pytest.TempPathFactory) -> None:
    env_file = tmp_path / ".env"  # type: ignore[operator]
    env_file.write_text("KEY=value\n")
    output_file = tmp_path / ".schema.env"  # type: ignore[operator]

    runner = CliRunner()
    result = runner.invoke(main, [str(env_file), "--output", str(output_file)])

    assert result.exit_code == 0
    assert f"✓ Schema written to {output_file}" in result.output


def test_cli_exits_with_code_1_when_env_file_missing(
    tmp_path: pytest.TempPathFactory,
) -> None:
    missing = tmp_path / "nonexistent.env"  # type: ignore[operator]
    output_file = tmp_path / ".schema.env"  # type: ignore[operator]

    runner = CliRunner()
    result = runner.invoke(main, [str(missing), "--output", str(output_file)])

    assert result.exit_code == 1
    assert "✗" in result.output


def test_cli_exits_with_code_1_when_env_file_malformed(
    tmp_path: pytest.TempPathFactory,
) -> None:
    env_file = tmp_path / ".env"  # type: ignore[operator]
    env_file.write_text("this-line-has-no-equals-sign\n")
    output_file = tmp_path / ".schema.env"  # type: ignore[operator]

    runner = CliRunner()
    result = runner.invoke(main, [str(env_file), "--output", str(output_file)])

    assert result.exit_code == 1
    assert "✗" in result.output
