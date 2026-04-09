# dotenv-schema-validator

Validate `.env` files against a declarative `.schema.env` schema file.

---

## Installation

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv tool install .
```

This installs the `dotenv-validate` command globally.

---

## Usage

```bash
dotenv-validate --schema <schema_file> <env_file> [<env_file> ...]
```

### Flags

| Flag | Required | Description |
|------|----------|-------------|
| `--schema` / `-s` | Yes | Path to the `.schema.env` file |
| `env_files` | Yes | One or more `.env` files to validate |

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All env files passed validation |
| `1` | One or more env files failed validation, or a file could not be read |

### Examples

```bash
# Validate a single file
dotenv-validate --schema .schema.env .env

# Validate multiple files
dotenv-validate --schema .schema.env .env.staging .env.production

# Short flag
dotenv-validate -s .schema.env .env
```

---

## Output

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

All errors for a file are reported together. When validating multiple files, validation continues even if one fails.

---

## Schema Format

Create a `.schema.env` file declaring the expected keys and their types:

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

### Supported Types

| Type | Constraints | Description |
|------|-------------|-------------|
| `string` | `min=N`, `max=N` | Any string value. Constraints check character length. |
| `int` | `min=N`, `max=N` | Must be a valid integer. Constraints are inclusive bounds. |
| `float` | `min=N`, `max=N` | Must be a valid float. Constraints are inclusive bounds. |
| `bool` | none | Accepted values (case-insensitive): `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off` |
| `url` | none | Must be a valid URL with scheme `http` or `https`. |
| `email` | none | Must match `^[^@\s]+@[^@\s]+\.[^@\s]+$` |
| `enum` | values listed in parentheses | Value must exactly match one of the listed options. Case-sensitive. |

### Optional Fields

Prefix any rule with `optional|` to mark a key as not required:

```bash
DEBUG=optional|bool
ADMIN_EMAIL=optional|email
```

- If the key is absent from the `.env` file, no error is raised
- If the key is present but empty, no error is raised
- If the key is present and non-empty, it is still validated against the type

### Key Format

All keys in both `.env` and `.schema.env` files must be uppercase and match `^[A-Z0-9_]+$`. Keys containing lowercase letters are a parse error.

---

## .env Format

Standard `.env` format is supported:

```bash
API_URL=https://api.example.com
API_KEY="my-super-secret-key-that-is-long-enough!!"
APP_ENV=production
PORT=8080
TIMEOUT_MS=3000
# DEBUG is optional, omitting it is fine
ADMIN_EMAIL=admin@example.com
```

- Lines beginning with `#` are treated as comments and ignored
- Blank lines are ignored
- Values may be wrapped in single or double quotes — they are stripped automatically
- Keys and values are stripped of surrounding whitespace

---

## Development

### Setup

```bash
uv add click
uv add --dev pytest mypy ruff
```

### Run Tests

```bash
uv run pytest
```

### Type Checking

```bash
uv run mypy dotenv_schema_validator
```

### Formatting

```bash
# Check
uv run ruff format --check dotenv_schema_validator tests

# Apply
uv run ruff format dotenv_schema_validator tests
```
