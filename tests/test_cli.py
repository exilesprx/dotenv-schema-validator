import pytest
from click.testing import CliRunner

from dotenv_schema_validator.cli import main


def test_empty_schema_warns_and_exits_zero(tmp_path: pytest.TempPathFactory) -> None:
    schema_file = tmp_path / ".schema.env"  # type: ignore[operator]
    schema_file.write_text("")
    env_file = tmp_path / ".env"  # type: ignore[operator]
    env_file.write_text("KEY=value\n")

    runner = CliRunner()
    result = runner.invoke(main, ["--schema", str(schema_file), str(env_file)])

    assert result.exit_code == 0
    assert "⚠" in result.output
    assert "empty" in result.output
