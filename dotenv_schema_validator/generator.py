def generate_schema(env: dict[str, str]) -> str:
    """Generate a .schema.env schema string from a parsed .env dict.

    For each key:
    - Non-empty value  -> KEY=string
    - Empty value      -> KEY=optional|string

    Keys are emitted in insertion order.
    """
    lines: list[str] = []
    for key, value in env.items():
        if value:
            lines.append(f"{key}=string")
        else:
            lines.append(f"{key}=optional|string")
    return "\n".join(lines) + "\n" if lines else "\n"
