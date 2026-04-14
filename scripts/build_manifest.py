#!/usr/bin/env python3
"""
Build a JSON manifest of all journal entries for the Vue app.
Also copies markdown files to the app's public directory.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

JOURNALS_DIR = Path(__file__).parent.parent
APP_PUBLIC = JOURNALS_DIR / "app" / "public" / "entries"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def read_summary(filepath: Path) -> str:
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if line.startswith(">"):
                    return line.lstrip("> ").strip()
        return ""
    except Exception:
        return ""


def build():
    manifest = {"work": [], "daily": []}

    for journal_type in ["work", "daily"]:
        entries_dir = JOURNALS_DIR / journal_type / "entries"
        public_dir = APP_PUBLIC / journal_type
        public_dir.mkdir(parents=True, exist_ok=True)

        if not entries_dir.exists():
            continue

        for f in sorted(entries_dir.glob("*.md"), reverse=True):
            date_str = f.stem
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue

            summary = read_summary(f)

            # Skip empty days
            if "No Claude Code sessions" in summary and journal_type == "work":
                continue
            if "0 terminal commands, 0 git commits" in summary and journal_type == "daily":
                continue

            manifest[journal_type].append({
                "date": date_str,
                "day": WEEKDAYS[dt.weekday()],
                "display": dt.strftime("%B %d, %Y"),
                "summary": summary,
            })

            # Copy md to public
            shutil.copy2(f, public_dir / f.name)

    output = JOURNALS_DIR / "app" / "public" / "manifest.json"
    output.write_text(json.dumps(manifest, indent=2))
    total = len(manifest["work"]) + len(manifest["daily"])
    print(f"Manifest built: {len(manifest['work'])} work + {len(manifest['daily'])} daily entries ({total} total)")


if __name__ == "__main__":
    build()
