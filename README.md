# Journals

A personal development journal that automatically captures your daily work from Claude Code sessions, git commits, and terminal history — displayed in a beautiful Vue 3 dashboard with animated backgrounds and multiple themes.

Works across multiple machines with automatic git-based sync.

![Vue 3](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vuedotjs&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-8-646CFF?logo=vite&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![Zero Dependencies](https://img.shields.io/badge/Python_deps-zero-green)

## What It Does

- **Work Journal** — Parses your Claude Code session history and git commits to generate structured daily reports with metrics (output volume, complexity, focus, depth, craft, momentum)
- **Daily Journal** — Captures terminal activity, command categories, and file changes
- **Narrative Journal** — Renders long-form markdown journal entries from Claude Code memory files (optional)
- **Multi-Machine Sync** — Entries from multiple computers merge automatically via git
- **AI Reflect** — Optional end-of-day reflection with Claude API analysis
- **6 Background Animations** — Ribbons, Amoeba, Stripes, Spikes, Borealis, Nebula (WebGL)
- **5 Themes** — Midnight, Dawn, Daylight, Dusk, Aurora (auto-switches by time of day)
- **Weather Widget** — Current conditions via Open-Meteo (no API key needed)

## Quick Start

```bash
# Clone the repo
git clone https://github.com/magneticlab/journals.git
cd journals

# Edit the config
nano journals.config.js

# Install frontend dependencies
cd app && npm install && cd ..

# Generate today's entries
python3 scripts/generate_all.py

# Start the dev server
cd app && npm run dev
```

Open [http://localhost:5173](http://localhost:5173) to see your journal.

## Generate Entries

```bash
# Generate today's entries
python3 scripts/generate_all.py

# Generate for a specific date
python3 scripts/generate_all.py 2026-04-15

# Backfill the last 30 days
python3 scripts/backfill.py 30

# Backfill a date range
python3 scripts/backfill.py 2026-03-01 2026-04-14

# Rebuild the manifest index
python3 scripts/build_manifest.py
```

### Data Sources

The generators read from local sources (all configurable in `journals.config.js`):

| Source | Used By | Default Path |
|--------|---------|--------------|
| Claude Code history | Work Journal | `~/.claude/history.jsonl` |
| Git repos | Work + Daily | `~/GitHub/` |
| Terminal history | Daily Journal | `~/.zsh_history` |
| Claude memory files | Narrative | *(disabled by default)* |

## Configuration

All settings live in `journals.config.js` at the project root:

```js
export default {
  name: 'Your Name',
  siteTitle: 'Journals',

  weather: {
    enabled: true,
    latitude: 40.71,    // your coordinates
    longitude: -74.01,
  },

  sources: {
    claudeHistory: '.claude/history.jsonl',
    reposDir: 'GitHub',       // resolved relative to $HOME
    narrativeDir: null,       // set path to enable narrative journal
  },

  git: {
    autoPush: false,          // set to true for multi-machine sync
    branch: 'main',
  },

  reflect: {
    enabled: false,           // requires VITE_ANTHROPIC_API_KEY in app/.env
    model: 'claude-haiku-4-5-20251001',
  },
}
```

### Per-Machine Overrides

Create `journals.config.local.js` (gitignored) to override any shared config value on a specific machine:

```js
export default {
  machineId: 'work-laptop',    // override auto-detected ID
  sources: {
    reposDir: 'Projects',      // different repo directory on this machine
  },
}
```

## Multi-Machine Sync

If you use multiple computers, Journals can merge entries from all of them into a single unified timeline. Each machine contributes its own Claude Code sessions, terminal history, and git activity — deduplicated and aggregated automatically.

### How It Works

1. **Machine ID** — Each computer is identified by a `machineId` (auto-detected from hostname, or set manually). Common hostnames like `MacBook-Pro.local` become `macbook`, `Mac-Studio.local` becomes `macstudio`.

2. **Merge on write** — When generating entries, the scripts check if a JSON file already exists for that date. If it does and contains data from a different machine, the new data is merged in:
   - Git commits are deduplicated by hash (shared across machines)
   - Claude Code sessions are additive (each machine has its own)
   - Shell commands are additive
   - Stats are aggregated across all machines

3. **Git as sync layer** — The repo itself is the sync mechanism:
   - `generate_all.py` pulls from remote before generating (picks up other machines' entries)
   - After generating, it commits and pushes (if `autoPush: true`)
   - No external services, databases, or sync tools needed

### Setup

**Step 1 — Clone on each machine:**

```bash
git clone https://github.com/you/your-journals-fork.git journals
cd journals
```

**Step 2 — Configure each machine:**

Edit `journals.config.js` (shared settings):

```js
export default {
  name: 'Your Name',
  git: { autoPush: true, branch: 'main' },
  // ...
}
```

Optionally create `journals.config.local.js` on machines that need overrides:

```js
// Only needed if auto-detection doesn't work or repos are in a different location
export default {
  machineId: 'office-desktop',
  sources: { reposDir: 'Projects' },
}
```

**Step 3 — Generate on each machine:**

```bash
python3 scripts/generate_all.py
```

Each machine will:
1. Pull latest entries from remote
2. Generate this machine's data for today
3. Merge with any existing data from other machines
4. Commit and push

**Step 4 — Automate (optional):**

Set up a daily cron or LaunchAgent on each machine (see [Automation](#automate-with-cron--launchagent) below).

### Entry Structure

Multi-machine entries store per-machine snapshots for future merges:

```json
{
  "date": "2026-04-18",
  "machineId": "macbook",
  "stats": { "sessions": 6, "commits": 15 },
  "_machines": {
    "macbook": { "stats": { "sessions": 4, "commits": 15 } },
    "macstudio": { "stats": { "sessions": 2, "commits": 15 } }
  }
}
```

Top-level `stats` are aggregated. The `_machines` object preserves each machine's contribution so subsequent runs can re-merge cleanly.

### Single Machine

If you only use one computer, multi-machine sync is transparent — everything works the same, entries just won't have the `_machines` metadata. No extra setup needed.

## Automate with Cron / LaunchAgent

Generate entries automatically every day:

**macOS (LaunchAgent):**

```xml
<!-- Save as ~/Library/LaunchAgents/com.journals.generate.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.journals.generate</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/journals/scripts/generate_all.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>23</integer>
        <key>Minute</key>
        <integer>30</integer>
    </dict>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.journals.generate.plist
```

**Linux (cron):**

```bash
# Run at 11:30 PM daily
30 23 * * * cd /path/to/journals && python3 scripts/generate_all.py
```

## Deploy

### Static Export

```bash
cd app && npm run build
# Upload dist/ to any static host
```

### Subdirectory Deploy

If deploying under a path like `yourdomain.com/journals/`, set the base in `app/vite.config.js`:

```js
base: '/journals/',
```

Then rebuild and upload `dist/`.

### Netlify

```bash
npm i -g netlify-cli
cd app && npm run build && netlify deploy --prod --dir=dist
```

## Forking & Updates

Fork this repo to get your own copy. To pull upstream improvements:

```bash
# Add upstream remote (one-time)
git remote add upstream https://github.com/magneticlab/journals.git

# Fetch and merge updates
git fetch upstream
git merge upstream/main
```

Your `journals.config.local.js` is gitignored, so merges should be clean.

## Project Structure

```
journals/
├── journals.config.js        # Shared configuration
├── journals.config.local.js   # Per-machine overrides (gitignored)
├── app/                       # Vue 3 + Vite frontend
│   ├── src/
│   │   ├── pages/             # Home, Journal, Entry
│   │   ├── components/        # Animations, charts, modals
│   │   ├── composables/       # Theme and animation state
│   │   └── services/          # Claude API integration
│   └── public/
│       ├── manifest.json      # Entry index (auto-generated)
│       └── entries/           # Generated JSON entries
│           ├── work/          # Claude Code session reports
│           ├── daily/         # Terminal activity logs
│           └── narrative/     # Long-form journal entries
├── scripts/                   # Python generators (zero pip deps)
│   ├── generate_all.py        # Master orchestrator (pull → generate → push)
│   ├── generate_work_journal.py   # Claude sessions → metrics
│   ├── generate_daily_journal.py  # Shell history → activity
│   ├── generate_narrative.py      # Markdown → sections
│   ├── config.py              # Config loader (JS parser + machine ID)
│   ├── build_manifest.py      # JSON manifest builder
│   ├── build_index.py         # HTML index builder
│   └── backfill.py            # Bulk date generation
└── README.md
```

## Requirements

- **Node.js** 18+
- **Python** 3.9+ (no pip dependencies)
- **Claude Code** for work journal data (optional — daily journal works without it)
- **Git** for multi-machine sync

## License

MIT
