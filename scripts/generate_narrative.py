#!/usr/bin/env python3
"""
Generate narrative journal entries from Claude memory markdown.

Source:  Configured via journals.config.js (sources.narrativeDir)
Output:  app/public/entries/narrative/YYYY-MM-DD.json

A single date can have multiple source files (e.g. 2026-04-16.md,
2026-04-16-hospital.md, 2026-04-16-report.md). They are merged into one
entry, each as its own labeled "section".

Zero pip dependencies — frontmatter parser and markdown→HTML renderer are
hand-rolled here. Good enough for the markdown style used in memory journals.
"""

import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from config import get as get_config

REPO_ROOT = Path(__file__).parent.parent
_cfg = get_config()
_narrative_dir = _cfg["sources"].get("narrativeDir")
SOURCE_DIR = Path.home() / _narrative_dir if _narrative_dir else None
OUTPUT_DIR = REPO_ROOT / "app" / "public" / "entries" / "narrative"

DATE_FROM_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:-(.+))?$")


def parse_frontmatter(text):
    """Return (frontmatter_dict, body_text). Frontmatter is YAML-lite: key: value."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5:]
    fm = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        val = val.strip().strip('"').strip("'")
        fm[key.strip()] = val
    return fm, body


def escape_html(s):
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
    )


def render_inline(text):
    """Inline markdown: code, bold, italic, links."""
    out = escape_html(text)
    # inline code first (so its content isn't touched by the rest)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    # links [text](url)
    out = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}</a>',
        out,
    )
    # bold **text**
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    # italic *text* (avoid matching inside ** which is already replaced)
    out = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", out)
    return out


def render_markdown(md):
    """Block-level markdown → HTML. Supports headings, lists, paragraphs, code blocks, hr."""
    lines = md.split("\n")
    out = []
    i = 0
    n = len(lines)

    def flush_paragraph(buf):
        if buf:
            text = " ".join(s.strip() for s in buf if s.strip())
            if text:
                out.append(f"<p>{render_inline(text)}</p>")
            buf.clear()

    para = []

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Code block fenced ```
        if stripped.startswith("```"):
            flush_paragraph(para)
            i += 1
            code = []
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            out.append("<pre><code>" + escape_html("\n".join(code)) + "</code></pre>")
            continue

        # Horizontal rule
        if stripped in ("---", "***", "___"):
            flush_paragraph(para)
            out.append("<hr />")
            i += 1
            continue

        # Headings
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            flush_paragraph(para)
            level = len(m.group(1))
            out.append(f"<h{level}>{render_inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # Unordered list
        if re.match(r"^[-*]\s+", stripped):
            flush_paragraph(para)
            items = []
            while i < n and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*]\s+", "", lines[i].strip()))
                i += 1
            out.append("<ul>" + "".join(f"<li>{render_inline(it)}</li>" for it in items) + "</ul>")
            continue

        # Ordered list
        if re.match(r"^\d+\.\s+", stripped):
            flush_paragraph(para)
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            out.append("<ol>" + "".join(f"<li>{render_inline(it)}</li>" for it in items) + "</ol>")
            continue

        # Blank line ends paragraph
        if stripped == "":
            flush_paragraph(para)
            i += 1
            continue

        # Default: paragraph line
        para.append(line)
        i += 1

    flush_paragraph(para)
    return "\n".join(out)


def first_paragraph_text(html, max_len=200):
    """Strip HTML tags from the first <p>, truncate. Used as summary."""
    m = re.search(r"<p>(.*?)</p>", html, re.DOTALL)
    if not m:
        return ""
    text = re.sub(r"<[^>]+>", "", m.group(1))
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_len:
        text = text[: max_len - 1].rstrip() + "…"
    return text


def section_title_for(filename, frontmatter):
    """Pick a human title for this file's section."""
    if frontmatter.get("name"):
        return frontmatter["name"]
    base = Path(filename).stem  # e.g. 2026-04-16-hospital
    m = DATE_FROM_NAME.match(base)
    if m and m.group(2):
        return m.group(2).replace("-", " ").replace("_", " ").title()
    return "Notes"


def collect_by_date():
    """Walk source dir, group files by date prefix in filename."""
    by_date = defaultdict(list)
    if SOURCE_DIR is None or not SOURCE_DIR.exists():
        return by_date

    for path in sorted(SOURCE_DIR.glob("*.md")):
        m = DATE_FROM_NAME.match(path.stem)
        if not m:
            continue
        date = m.group(1)
        by_date[date].append(path)
    return by_date


def build_entry(date, paths):
    sections = []
    for p in paths:
        text = p.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        html = render_markdown(body.strip())
        sections.append({
            "title": section_title_for(p.name, fm),
            "description": fm.get("description", ""),
            "source": p.name,
            "html": html,
        })

    dt = datetime.strptime(date, "%Y-%m-%d")
    summary = ""
    if sections:
        # Prefer an explicit description from the first file; fall back to first <p>.
        if sections[0]["description"]:
            summary = sections[0]["description"]
        else:
            summary = first_paragraph_text(sections[0]["html"])
    if not summary:
        summary = f"{len(sections)} entry/entries from memory journal."

    return {
        "date": date,
        "day": dt.strftime("%A"),
        "display": dt.strftime("%B %-d, %Y"),
        "generatedAt": datetime.now().isoformat(),
        "summary": summary,
        "stats": {
            "sections": len(sections),
            "sourceFiles": [s["source"] for s in sections],
        },
        "sections": sections,
    }


def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else None
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    by_date = collect_by_date()

    if not by_date:
        print(f"No narrative source files found at {SOURCE_DIR}")
        return

    if target_date:
        if target_date not in by_date:
            print(f"No narrative entries for {target_date}, skipping.")
            return
        dates = [target_date]
    else:
        dates = sorted(by_date.keys())

    for date in dates:
        entry = build_entry(date, by_date[date])
        out_path = OUTPUT_DIR / f"{date}.json"
        out_path.write_text(json.dumps(entry, indent=2, ensure_ascii=False))
        print(f"Narrative written: {date} ({len(entry['sections'])} section(s))")


if __name__ == "__main__":
    main()
