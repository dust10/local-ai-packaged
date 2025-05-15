import os
import toml
import re

PLACEHOLDER_PATTERN = re.compile(r"\$\{([^}]+)\}")

def resolve_placeholders(value):
    if isinstance(value, str):
        return PLACEHOLDER_PATTERN.sub(lambda m: os.getenv(m.group(1), m.group(0)), value)
    elif isinstance(value, dict):
        return {k: resolve_placeholders(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [resolve_placeholders(item) for item in value]
    return value

def main():
    secrets_path = ".streamlit/secrets.toml"  # Change path as needed
    with open(secrets_path, "r") as f:
        secrets = toml.load(f)

    resolved_secrets = resolve_placeholders(secrets)

    with open(secrets_path, "w") as f:
        toml.dump(resolved_secrets, f)

    print("Resolved and saved secrets.toml")

if __name__ == "__main__":
    main()
