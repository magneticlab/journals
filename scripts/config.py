"""
Load user config from journals.config.js + optional journals.config.local.js.
The local config overrides the shared config for machine-specific values.
"""

import json
import re
import socket
from pathlib import Path

CONFIG_FILE = Path(__file__).parent.parent / "journals.config.js"
LOCAL_CONFIG_FILE = Path(__file__).parent.parent / "journals.config.local.js"


def _parse_js_config(filepath):
    """Parse a JS config file into a Python dict."""
    if not filepath.exists():
        return {}

    text = filepath.read_text()

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
        return {}

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
        print(f"Warning: Could not parse {filepath}, using defaults")
        return {}


def _deep_merge(base, override):
    """Recursively merge override into base."""
    merged = dict(base)
    for k, v in override.items():
        if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
            merged[k] = _deep_merge(merged[k], v)
        else:
            merged[k] = v
    return merged


def _auto_machine_id():
    """Derive a machine ID from the hostname."""
    hostname = socket.gethostname().lower().replace(".local", "").replace(" ", "-")
    # Common patterns
    if "macbook" in hostname:
        return "macbook"
    if "mac-studio" in hostname or "macstudio" in hostname:
        return "macstudio"
    if "imac" in hostname:
        return "imac"
    return hostname


def _defaults():
    return {
        "name": "User",
        "siteTitle": "Journals",
        "machineId": _auto_machine_id(),
        "weather": {"enabled": True, "latitude": 40.71, "longitude": -74.01},
        "sources": {
            "claudeHistory": ".claude/history.jsonl",
            "reposDir": "GitHub",
            "narrativeDir": None,
        },
        "git": {"autoPush": False, "branch": "main"},
    }


def load_config():
    """Load shared config, overlay local overrides, apply defaults."""
    cfg = _defaults()
    shared = _parse_js_config(CONFIG_FILE)
    cfg = _deep_merge(cfg, shared)
    local = _parse_js_config(LOCAL_CONFIG_FILE)
    cfg = _deep_merge(cfg, local)
    return cfg


# Convenience accessors
_cfg = None


def get():
    global _cfg
    if _cfg is None:
        _cfg = load_config()
    return _cfg
