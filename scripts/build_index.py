#!/usr/bin/env python3
"""
Build index.html pages for both journals.
Scans entries/ directories and generates a navigable HTML page with a date table.
"""

import os
from pathlib import Path
from datetime import datetime

JOURNALS_DIR = Path(__file__).parent.parent
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def read_first_line(filepath: Path) -> str:
    """Read the first non-empty line from a markdown file (the title)."""
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if line and line.startswith("#"):
                    return line.lstrip("# ").strip()
        return ""
    except Exception:
        return ""


def read_summary_line(filepath: Path) -> str:
    """Read the blockquote summary line."""
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if line.startswith(">"):
                    return line.lstrip("> ").strip()
        return ""
    except Exception:
        return ""


def build_index(journal_name: str, title: str, description: str):
    """Build an index.html for a journal directory."""
    entries_dir = JOURNALS_DIR / journal_name / "entries"
    output_file = JOURNALS_DIR / journal_name / "index.html"

    if not entries_dir.exists():
        entries_dir.mkdir(parents=True, exist_ok=True)

    # Collect entries
    entries = []
    for f in sorted(entries_dir.glob("*.md"), reverse=True):
        date_str = f.stem  # e.g., 2026-04-14
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            day_name = WEEKDAYS[dt.weekday()]
            summary = read_summary_line(f)
            entries.append({
                "date": date_str,
                "day": day_name,
                "display": dt.strftime("%B %d, %Y"),
                "summary": summary,
                "file": f"entries/{f.name}",
            })
        except ValueError:
            continue

    # Generate HTML
    rows = ""
    for e in entries:
        summary_escaped = e["summary"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        rows += f"""
        <tr onclick="loadEntry('{e['file']}')" style="cursor:pointer">
          <td><strong>{e['date']}</strong></td>
          <td>{e['day']}</td>
          <td class="summary">{summary_escaped[:120]}{'...' if len(e['summary']) > 120 else ''}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #0a0a0a;
      color: #e5e5e5;
      min-height: 100vh;
    }}
    .container {{
      max-width: 960px;
      margin: 0 auto;
      padding: 2rem 1.5rem;
    }}
    h1 {{
      font-size: 1.75rem;
      font-weight: 600;
      margin-bottom: 0.25rem;
      color: #fff;
    }}
    .subtitle {{
      color: #737373;
      font-size: 0.875rem;
      margin-bottom: 2rem;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 2rem;
    }}
    th {{
      text-align: left;
      padding: 0.75rem 1rem;
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #737373;
      border-bottom: 1px solid #262626;
    }}
    td {{
      padding: 0.75rem 1rem;
      font-size: 0.875rem;
      border-bottom: 1px solid #171717;
    }}
    tr:hover td {{
      background: #171717;
    }}
    .summary {{
      color: #a3a3a3;
      max-width: 500px;
    }}
    #entry-viewer {{
      display: none;
      background: #111;
      border: 1px solid #262626;
      border-radius: 8px;
      padding: 2rem;
      margin-top: 1rem;
      line-height: 1.7;
      font-size: 0.9rem;
    }}
    #entry-viewer h1 {{ font-size: 1.5rem; margin-bottom: 1rem; }}
    #entry-viewer h2 {{ font-size: 1.2rem; margin: 1.5rem 0 0.75rem; color: #d4d4d4; }}
    #entry-viewer h3 {{ font-size: 1rem; margin: 1.25rem 0 0.5rem; color: #a3a3a3; }}
    #entry-viewer blockquote {{
      border-left: 3px solid #404040;
      padding-left: 1rem;
      color: #a3a3a3;
      margin: 1rem 0;
      font-style: italic;
    }}
    #entry-viewer table {{ margin: 1rem 0; }}
    #entry-viewer ul, #entry-viewer ol {{ padding-left: 1.5rem; margin: 0.5rem 0; }}
    #entry-viewer li {{ margin: 0.25rem 0; }}
    #entry-viewer code {{
      background: #1a1a1a;
      padding: 0.15rem 0.4rem;
      border-radius: 3px;
      font-size: 0.85em;
      color: #e5e5e5;
    }}
    #entry-viewer hr {{
      border: none;
      border-top: 1px solid #262626;
      margin: 2rem 0;
    }}
    #entry-viewer em {{ color: #737373; }}
    .back-btn {{
      display: inline-block;
      padding: 0.5rem 1rem;
      background: #171717;
      border: 1px solid #262626;
      border-radius: 6px;
      color: #a3a3a3;
      cursor: pointer;
      font-size: 0.8rem;
      margin-bottom: 1rem;
    }}
    .back-btn:hover {{ background: #262626; color: #fff; }}
    .empty {{
      text-align: center;
      color: #525252;
      padding: 3rem;
      font-style: italic;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>{title}</h1>
    <p class="subtitle">{description}</p>

    <div id="table-view">
      {'<table><thead><tr><th>Date</th><th>Day</th><th>Summary</th></tr></thead><tbody>' + rows + '</tbody></table>' if entries else '<p class="empty">No entries yet. Run the generator script to create your first entry.</p>'}
    </div>

    <div id="entry-viewer">
      <span class="back-btn" onclick="closeEntry()">Back to index</span>
      <div id="entry-content"></div>
    </div>
  </div>

  <script>
    function loadEntry(path) {{
      fetch(path)
        .then(r => r.text())
        .then(md => {{
          document.getElementById('entry-content').innerHTML = renderMarkdown(md);
          document.getElementById('table-view').style.display = 'none';
          document.getElementById('entry-viewer').style.display = 'block';
          window.scrollTo(0, 0);
        }})
        .catch(e => alert('Could not load entry: ' + e));
    }}

    function closeEntry() {{
      document.getElementById('table-view').style.display = 'block';
      document.getElementById('entry-viewer').style.display = 'none';
    }}

    function renderMarkdown(md) {{
      // Simple markdown renderer
      let html = md
        .replace(/^### (.+)$/gm, '<h3>$1</h3>')
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')
        .replace(/^# (.+)$/gm, '<h1>$1</h1>')
        .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
        .replace(/^---$/gm, '<hr>')
        .replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>')
        .replace(/\\*(.+?)\\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/^- (.+)$/gm, '<li>$1</li>')
        .replace(/^\\| (.+)$/gm, (match) => {{
          const cells = match.split('|').filter(c => c.trim());
          if (cells.some(c => /^[-:]+$/.test(c.trim()))) return '';
          const tag = 'td';
          return '<tr>' + cells.map(c => `<${{tag}}>${{c.trim()}}</${{tag}}>`).join('') + '</tr>';
        }});

      // Wrap consecutive <li> in <ul>
      html = html.replace(/((?:<li>.*<\\/li>\\n?)+)/g, '<ul>$1</ul>');
      // Wrap consecutive <tr> in <table>
      html = html.replace(/((?:<tr>.*<\\/tr>\\n?)+)/g, '<table>$1</table>');
      // Paragraphs for remaining text
      html = html.replace(/^(?!<[hublot]|<\\/|$)(.+)$/gm, '<p>$1</p>');

      return html;
    }}
  </script>
</body>
</html>"""

    output_file.write_text(html)
    print(f"Index built: {output_file} ({len(entries)} entries)")


def main():
    build_index(
        "work",
        "Work Journal — Claude Sessions",
        "Daily reports from Claude Code sessions, git activity, and project work."
    )
    build_index(
        "daily",
        "Daily Journal — Laptop Activity",
        "Daily summary of terminal commands, file changes, and development activity."
    )


if __name__ == "__main__":
    main()
