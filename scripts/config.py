"""
Load user config from journals.config.js.
Parses the JS config file and returns a Python dict.
"""

import json
import re
from pathlib import Path

CONFIG_FILE = Path(__file__).parent.parent / "journals.config.js"


def load_config():
    """Parse journals.config.js into a Python dict."""
    if not CONFIG_FILE.exists():
        return _defaults()

    text = CONFIG_FILE.read_text()

    # Strip JS export wrapper and comments, extract the object literal
    # Remove single-line comments (but not URLs with //)
    lines = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*") or stripped.startswith("/**"):
            continue
        if stripped.startswith("export default"):
            line = line.replace("export default", "")
        lines.append(line)

    body = "\n".join(lines)

    # Remove trailing commas (JS allows, JSON doesn't)
    body = re.sub(r",\s*([}\]])", r"\1", body)
    # Remove inline comments
    body = re.sub(r"//[^\n]*", "", body)
    # Convert JS null/true/false (already valid JSON)
    # Find the object
    match = re.search(r"\{", body)
    if not match:
        return _defaults()

    # Find matching closing brace
    depth = 0
    start = match.start()
    for i, ch in enumerate(body[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                obj_str = body[start : i + 1]
                break
    else:
        return _defaults()

    # Convert single-quoted strings to double-quoted
    obj_str = re.sub(r"'([^']*)'", r'"\1"', obj_str)
    # Quote unquoted JS object keys (word characters before colon)
    obj_str = re.sub(r'(?<=[{,\n])\s*(\w+)\s*:', r' "\1":', obj_str)

    try:
        return json.loads(obj_str)
    except json.JSONDecodeError:
        print(f"Warning: Could not parse {CONFIG_FILE}, using defaults")
        return _defaults()


def _defaults():
    return {
        "name": "User",
        "siteTitle": "Journals",
        "weather": {"enabled": True, "latitude": 40.71, "longitude": -74.01},
        "sources": {
            "claudeHistory": ".claude/history.jsonl",
            "reposDir": "GitHub",
            "narrativeDir": None,
        },
        "git": {"autoPush": False, "branch": "main"},
    }


# Convenience accessors
_cfg = None


def get():
    global _cfg
    if _cfg is None:
        _cfg = load_config()
    return _cfg
