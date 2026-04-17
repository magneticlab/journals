#!/usr/bin/env python3
"""
Build a JSON manifest from the generated JSON entry files.
"""

import json
from pathlib import Path

JOURNALS_DIR = Path(__file__).parent.parent
APP_PUBLIC = JOURNALS_DIR / "app" / "public"


def build():
    manifest = {"work": [], "daily": [], "narrative": []}

    for journal_type in ["work", "daily", "narrative"]:
        entries_dir = APP_PUBLIC / "entries" / journal_type
        if not entries_dir.exists():
            continue

        for f in sorted(entries_dir.glob("*.json"), reverse=True):
            try:
                data = json.loads(f.read_text())
                manifest[journal_type].append({
                    "date": data["date"],
                    "day": data["day"],
                    "display": data["display"],
                    "summary": data["summary"],
                    "stats": data.get("stats", {}),
                })
            except (json.JSONDecodeError, KeyError):
                continue

    (APP_PUBLIC / "manifest.json").write_text(json.dumps(manifest, indent=2))
    total = sum(len(v) for v in manifest.values())
    print(
        f"Manifest built: {len(manifest['work'])} work + "
        f"{len(manifest['daily'])} daily + "
        f"{len(manifest['narrative'])} narrative ({total} total)"
    )


if __name__ == "__main__":
    build()
