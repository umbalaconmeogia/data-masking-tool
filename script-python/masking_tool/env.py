"""Minimal .env parser.

Spec (kept intentionally small so the PHP port can implement it identically):
skip blank lines and lines starting with '#', split on the first '=',
trim whitespace around key and value, strip one pair of matching single or
double quotes around the value. No interpolation, no escapes, no multi-line.
"""


def load_env(path):
    values = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                value = value[1:-1]
            if key:
                values[key] = value
    return values
