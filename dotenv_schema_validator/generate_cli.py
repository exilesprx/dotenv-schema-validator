from __future__ import annotations

import sys

import click

from dotenv_schema_validator.generator import generate_schema
from dotenv_schema_validator.parser import parse_env_file


@click.command()
@click.option(
    "--output",
    "-o",
    required=True,
    help="Path to write the generated .schema.env file.",
)
@click.argument("env_file")
def main(output: str, env_file: str) -> None:
    """Generate a .schema.env schema file from a .env file."""
    try:
        env = parse_env_file(env_file)
    except (ValueError, OSError) as e:
        click.echo(f"✗ Failed to load '{env_file}': {e}")
        sys.exit(1)

    schema_content = generate_schema(env)

    try:
        with open(output, "w") as f:
            f.write(schema_content)
    except OSError as e:
        click.echo(f"✗ Failed to write '{output}': {e}")
        sys.exit(1)

    click.echo(f"✓ Schema written to {output}")
