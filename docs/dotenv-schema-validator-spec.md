# dotenv-schema-validator — Implementation Spec

Build a Python CLI tool called `dotenv-schema-validator` that validates `.env` files against a declarative `.schema.env` schema file.

---

## Project Structure

```
dotenv-schema-validator/
├── .python-version
├── pyproject.toml
├── uv.lock
├── README.md
├── dotenv_schema_validator/
│   ├── __init__.py
│   ├── parser.py
│   ├── validator.py
│   └── cli.py
└── tests/
    ├── __init__.py
    ├── test_parser.py
    └── test_validator.py
```

> `main.py` created by `uv init` should be removed — it is not part of this project.

---

## Dependencies

- Python 3.13 (pinned via `.python-version`, managed by `uv`)
- `click` — CLI interface only (`uv add click`)
- No other third-party runtime dependencies
- `pytest` for tests (`uv add --dev pytest`)
- `mypy` for type checking (`uv add --dev mypy`)
- `ruff` for formatting (`uv add --dev ruff`)

---

## uv Workflow

This project uses [uv](https://docs.astral.sh/uv/) for dependency and environment management.

### Setup

```bash
uv add click
uv add --dev pytest
```

### Running Tests

```bash
uv run pytest
```

### Installing the CLI locally

```bash
uv tool install .
```

### Linting and Formatting

```bash
uv run mypy dotenv_schema_validator
uv run ruff format dotenv_schema_validator tests
```

---

## Implementation Phases

Build the project incrementally, completing and verifying each phase before moving to the next.

### Phase 1 — Project Scaffolding

- Update `pyproject.toml` with the correct name, build system, scripts, and dependencies
- Delete `main.py` (created by `uv init`, not part of this project)
- Create the package directory: `dotenv_schema_validator/` with `__init__.py`
- Create the test directory: `tests/` with `__init__.py`
- Add runtime and dev dependencies: `uv add click` and `uv add --dev pytest mypy ruff`
- Create empty `parser.py`, `validator.py`, and `cli.py` files
- **Verify:** `uv run pytest` runs successfully with 0 tests collected and no errors; `uv run mypy dotenv_schema_validator` passes; `uv run ruff format --check dotenv_schema_validator tests` reports no changes needed

### Phase 2 — `.env` File Parser + Tests

- Implement `FieldSchema` dataclass in `parser.py`
- Implement `parse_env_file()` in `parser.py`
- Write all `test_parser.py` tests covering `.env` parsing (basic parsing, quote stripping, comments, blank lines, parse errors)
- **Verify:** all `.env` parser tests pass; `uv run mypy dotenv_schema_validator` passes; `uv run ruff format --check dotenv_schema_validator tests` reports no changes needed

### Phase 3 — `.schema.env` File Parser + Tests

- Implement `parse_schema_file()` in `parser.py`
- Write all `test_parser.py` tests covering schema parsing (types, optional prefix, constraints, enums, error cases)
- **Verify:** all parser tests pass; `uv run mypy dotenv_schema_validator` passes; `uv run ruff format --check dotenv_schema_validator tests` reports no changes needed

### Phase 4 — Validator + Tests

- Implement `ValidationError` and `ValidationResult` dataclasses in `validator.py`
- Implement `validate()` with all type checks, constraint logic, and missing/empty key handling
- Write all `test_validator.py` tests
- **Verify:** all validator tests pass; `uv run mypy dotenv_schema_validator` passes; `uv run ruff format --check dotenv_schema_validator tests` reports no changes needed

### Phase 5 — CLI

- Implement `cli.py` using `click`
- **Verify:** `uv run dotenv-validate --help` shows correct usage; manual smoke test against sample `.env` and `.schema.env` files confirms correct output and exit codes; `uv run mypy dotenv_schema_validator` passes; `uv run ruff format --check dotenv_schema_validator tests` reports no changes needed

### Phase 6 — Final Verification

- Run the full test suite: `uv run pytest`
- Run type checking: `uv run mypy dotenv_schema_validator`
- Run formatter check: `uv run ruff format --check dotenv_schema_validator tests`
- Install as a tool: `uv tool install .`
- End-to-end test with a valid and an invalid `.env` file, confirming correct output and exit codes

---

## CLI Behaviour

### Command

```bash
dotenv-validate --schema <schema_file> <env_file> [<env_file> ...]
```

### Arguments & Flags

| Flag | Required | Description |
|------|----------|-------------|
| `--schema` / `-s` | Yes | Path to the `.schema.env` file |
| `env_files` | Yes | One or more `.env` files to validate |

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All env files passed validation |
| `1` | One or more env files failed validation, or a file could not be read |

### Output

On success:
```
✅ .env.production is valid
```

On failure:
```
❌ .env.staging failed validation:
  - API_KEY: must be at least 32 characters (got 12)
  - PORT: must be <= 65535 (got 99999)
  - APP_ENV: must be one of (development, staging, production) (got 'prod')
```

On unreadable file:
```
❌ Failed to load '.env.missing': [Errno 2] No such file or directory
```

- All errors for a file are reported together — do not stop at the first error
- If validating multiple files, continue validating remaining files even if one fails

---

## .env File Format

Standard `.env` format:

```bash
KEY=value
OTHER="quoted value"
ANOTHER='single quoted'
# This is a comment
```

### Parsing Rules

- Lines beginning with `#` are comments and must be ignored
- Blank lines must be ignored
- Values may optionally be wrapped in double or single quotes — strip them if present
- A line without `=` is a parse error: raise `ValueError` with the line number and content
- Keys and values must be stripped of surrounding whitespace
- Keys must match `^[A-Z0-9_]+$` (uppercase letters, digits, and underscores only); a key containing lowercase letters is a parse error: raise `ValueError` with the line number and key

---

## .schema.env File Format

```bash
# This is a comment
API_URL=url
API_KEY=string(min=32)
APP_ENV=enum(development,staging,production)
PORT=int(min=1,max=65535)
TIMEOUT_MS=int
DEBUG=optional|bool
ADMIN_EMAIL=optional|email
```

### Parsing Rules

- Lines beginning with `#` are comments and must be ignored
- Blank lines must be ignored
- Each line has the format `KEY=rule`
- A line without `=` is a parse error
- Keys and rules must be stripped of surrounding whitespace
- Keys must match `^[A-Z0-9_]+$` (uppercase letters, digits, and underscores only); a key containing lowercase letters is a parse error: raise `ValueError` with the key

### Rule Syntax

```
rule        := [optional_prefix] type [constraints]
optional    := "optional|"
type        := "string" | "int" | "float" | "bool" | "url" | "email" | "enum"
constraints := "(" args ")"
args        := key=value ["," key=value]*   # for string/int/float
             | value ["," value]*            # for enum
```

### Supported Types & Constraints

| Type | Constraints | Description |
|------|-------------|-------------|
| `string` | `min=N`, `max=N` | Any string value. Constraints check character length. |
| `int` | `min=N`, `max=N` | Must be a valid integer. Constraints are inclusive bounds. |
| `float` | `min=N`, `max=N` | Must be a valid float. Constraints are inclusive bounds. |
| `bool` | none | Accepted values (case-insensitive): `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off` |
| `url` | none | Must be a valid URL with scheme `http` or `https` and a non-empty netloc. Use `urllib.parse.urlparse` — no third-party libraries. |
| `email` | none | Must match the regex `^[^@\s]+@[^@\s]+\.[^@\s]+$` |
| `enum` | values listed in parentheses | Value must exactly match one of the listed options. Case-sensitive. |

### Optional Fields

Prefix any rule with `optional|` to mark the key as not required:

```bash
DEBUG=optional|bool
```

- If the key is absent from the `.env` file, no error is raised
- If the key is present but empty, no error is raised
- If the key is present and non-empty, its value is still validated against the type

---

## Module Responsibilities

### `parser.py`

Exports:
- `parse_env_file(path: str | Path) -> dict[str, str]`
- `parse_schema_file(path: str | Path) -> dict[str, FieldSchema]`
- `FieldSchema` dataclass with fields:
  - `key: str`
  - `type: str`
  - `optional: bool` (default `False`)
  - `constraints: dict[str, str]` (default empty dict)
  - `enum_values: list[str]` (default empty list)

### `validator.py`

Exports:
- `validate(env: dict[str, str], schema: dict[str, FieldSchema]) -> ValidationResult`
- `ValidationResult` dataclass with fields:
  - `errors: list[ValidationError]`
  - `valid: bool` property — `True` if errors is empty
  - `__str__` — returns human-readable summary
- `ValidationError` dataclass with fields:
  - `key: str`
  - `message: str`
  - `__str__` — returns `"  - {key}: {message}"`

### `cli.py`

- Uses `click` to define the CLI
- Installed as the command `dotenv-validate` via `pyproject.toml`
- Loads schema once, then iterates over each env file
- Catches `ValueError` and `FileNotFoundError` from the parser and prints a clean error message
- Exits with code `1` if any file fails

---

## Validation Rules

1. **Missing required key** — key is in schema, not optional, and absent from the env file → error
2. **Empty required value** — key is present but value is empty string and field is not optional → error
3. **Type mismatch** — value does not conform to the declared type → error with descriptive message
4. **Constraint violation** — value fails a min/max constraint → error stating the constraint and actual value
5. **Unknown keys** — keys present in the env file but not in the schema are silently ignored

---

## Error Message Format

Error messages must be specific and include the actual value where relevant:

| Scenario | Message format |
|----------|---------------|
| Missing required key | `required key is missing` |
| Empty required value | `required key has an empty value` |
| Not an integer | `must be an integer (got 'abc')` |
| Below min | `must be >= 1 (got 0)` |
| Above max | `must be <= 65535 (got 99999)` |
| Not a bool | `must be a boolean (true/false, 1/0, yes/no) (got 'enabled')` |
| Invalid URL | `must be a valid http/https URL (got 'not-a-url')` |
| Invalid email | `must be a valid email address (got 'notanemail')` |
| Enum mismatch | `must be one of (development, staging, production) (got 'prod')` |
| String too short | `must be at least 32 characters (got 12)` |
| String too long | `must be at most 10 characters (got 15)` |
| Lowercase key in `.env` | `Line N: key 'port' must be uppercase (A-Z, 0-9, _)` |
| Lowercase key in `.schema.env` | `key 'port' must be uppercase (A-Z, 0-9, _)` |

---

## pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "dotenv-schema-validator"
version = "0.1.0"
description = "Validate .env files against a .schema.env schema file"
readme = "README.md"
requires-python = ">=3.13"
license = { text = "MIT" }
dependencies = [
    "click>=8.0",
]

[project.scripts]
dotenv-validate = "dotenv_schema_validator.cli:main"

[dependency-groups]
dev = [
    "pytest>=8.0",
    "mypy>=1.0",
    "ruff>=0.4",
]

[tool.mypy]
strict = true

[tool.ruff]
line-length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
```

---

## Test Coverage Requirements

### `test_parser.py`

- Parses a basic `.env` file correctly
- Strips surrounding quotes from values
- Skips comments and blank lines
- Raises `ValueError` on a line with no `=`
- Raises `ValueError` when a `.env` key is not uppercase (e.g. `port=8080`)
- Parses a required `string` rule
- Parses an `optional|bool` rule
- Parses `string(min=32,max=64)` constraints correctly
- Parses `enum(development,staging,production)` values correctly
- Raises `ValueError` on an unrecognised type
- Raises `ValueError` on `enum` with no values
- Raises `ValueError` when a `.schema.env` key is not uppercase

### `test_validator.py`

- Missing required key produces an error
- Missing optional key produces no error
- Empty required value produces an error
- `string(min=N)` passes when length >= N
- `string(min=N)` fails when length < N
- `string(max=N)` fails when length > N
- `int` fails when value is not a number
- `int(min=N)` fails when value < N
- `int(max=N)` fails when value > N
- `float` fails when value is not a float
- `bool` passes for all of: `true`, `false`, `1`, `0`, `yes`, `no`, `True`, `FALSE`
- `bool` fails for non-boolean strings
- `url` passes for valid `https://` URL
- `url` fails for non-URL strings
- `url` fails for non-http/https schemes (e.g. `ftp://`)
- `email` passes for valid email
- `email` fails for invalid email
- `enum` passes when value is in the list
- `enum` fails when value is not in the list, and error message includes the actual value
- Multiple errors across keys are all reported in a single `ValidationResult`
