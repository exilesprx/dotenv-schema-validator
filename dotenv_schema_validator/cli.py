from __future__ import annotations

import sys

import click

from dotenv_schema_validator.parser import parse_env_file, parse_schema_file
from dotenv_schema_validator.validator import validate


@click.command()
@click.option(
    "--schema",
    "-s",
    required=True,
    help="Path to the .schema.env file.",
)
@click.argument("env_files", nargs=-1, required=True)
def main(schema: str, env_files: tuple[str, ...]) -> None:
    """Validate one or more .env files against a .schema.env schema file."""
    try:
        parsed_schema = parse_schema_file(schema)
    except (ValueError, FileNotFoundError, OSError) as e:
        click.echo(f"❌ Failed to load schema '{schema}': {e}")
        sys.exit(1)

    if not parsed_schema:
        click.echo(
            "⚠️  Warning: schema file is empty — all keys will be ignored",
            err=True,
        )

    any_failed = False

    for env_file in env_files:
        try:
            env = parse_env_file(env_file)
        except (ValueError, FileNotFoundError, OSError) as e:
            click.echo(f"❌ Failed to load '{env_file}': {e}")
            any_failed = True
            continue

        result = validate(env, parsed_schema)

        if result.valid:
            click.echo(f"✅ {env_file} is valid")
        else:
            any_failed = True
            click.echo(f"❌ {env_file} failed validation:")
            for error in result.errors:
                click.echo(str(error))

    if any_failed:
        sys.exit(1)
