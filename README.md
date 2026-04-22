# Journals

A personal development journal that automatically captures your daily work from Claude Code sessions, git commits, and terminal history — displayed in a beautiful Vue 3 dashboard with animated backgrounds and multiple themes.

Works across multiple machines with automatic git-based sync.

![Vue 3](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vuedotjs&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-8-646CFF?logo=vite&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![Zero Dependencies](https://img.shields.io/badge/Python_deps-zero-green)

## What It Does

- **Work Journal** — Parses your [Claude Code](https://claude.ai/code) session history and git commits to generate structured daily reports with performance metrics (output volume, complexity, focus, depth, craft, momentum)
- **Daily Journal** — Captures terminal activity, command categories, and file changes
- **Narrative Journal** — Renders long-form markdown journal entries from Claude Code memory files (optional)
- **Multi-Machine Sync** — Entries from multiple computers merge automatically via git
- **AI Reflect** — Optional end-of-day reflection with Claude API analysis
- **6 Background Animations** — Ribbons, Amoeba, Stripes, Spikes, Borealis, Nebula (WebGL)
- **5 Themes** — Midnight, Dawn, Daylight, Dusk, Aurora (auto-switches by time of day)
- **Weather Widget** — Current conditions via Open-Meteo (no API key needed)

## Prerequisites

Before you start, make sure you have these installed:

### Required

| Tool | Why | Install |
|------|-----|---------|
| **Node.js 18+** | Runs the Vue frontend and setup wizard | [nodejs.org](https://nodejs.org) or `brew install node` |
| **Python 3.9+** | Runs the journal generators (zero pip deps) | [python.org](https://python.org) or `brew install python` |
| **Git** | Version control + multi-machine sync | `xcode-select --install` (macOS) or [git-scm.com](https://git-scm.com) |

### Required for Work Journal

| Tool | Why | Install |
|------|-----|---------|
| **Claude Code** | The Work Journal reads `~/.claude/history.jsonl` which is created by Claude Code. Without it, only the Daily Journal (terminal + git activity) will have data. | `npm install -g @anthropic-ai/claude-code` then run `claude` once to initialize |

### Required for Multi-Machine Sync

If you plan to sync entries between multiple computers:

| Tool | Why | Setup |
|------|-----|-------|
| **SSH key** | Git push/pull with GitHub requires SSH authentication | `ssh-keygen -t ed25519 -C "you@example.com"` then add `~/.ssh/id_ed25519.pub` at [github.com/settings/ssh/new](https://github.com/settings/ssh/new) |
| **Git identity** | Commits require a name and email | `git config --global user.name "Your Name"` and `git config --global user.email "you@example.com"` |
| **Your own fork/repo** | You need push access to a remote | Fork this repo or create a private repo, then update the remote (see [Quick Start](#quick-start)) |

### Optional

| Tool | Why |
|------|-----|
| **zsh** | Daily Journal reads `~/.zsh_history`. Bash users will see limited terminal data. macOS uses zsh by default. |
| **Anthropic API key** | Only needed for the AI Reflect feature (`app/.env`) |

### Verify Setup

Run the setup wizard — it checks all prerequisites and tells you what's missing:

```bash
node setup.js
```

## Quick Start

```bash
# 1. Fork this repo on GitHub, then clone your fork
git clone git@github.com:YOUR_USERNAME/journals.git
cd journals

# 2. Run the setup wizard (checks prerequisites + configures)
node setup.js

# 3. Generate today's entries
python3 scripts/generate_all.py

# 4. Start the dev server
cd app && npm run dev
```

Open [http://localhost:5173](http://localhost:5173) to see your journal.

> **Note:** If you cloned with HTTPS and want multi-machine sync, switch to SSH:
> ```bash
> git remote set-url origin git@github.com:YOUR_USERNAME/journals.git
> ```

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

| Source | Used By | Default Path | Notes |
|--------|---------|--------------|-------|
| Claude Code history | Work Journal | `~/.claude/history.jsonl` | Created by Claude Code after your first session |
| Git repos | Work + Daily | `~/GitHub/` | Any directory containing git repos |
| Terminal history | Daily Journal | `~/.zsh_history` | macOS zsh only |
| Claude memory files | Narrative | *(disabled by default)* | Set `narrativeDir` in config to enable |

## Configuration

All settings live in `journals.config.js` at the project root:

```js
export default {
  name: 'Your Name',
  siteTitle: 'Journals',

  weather: {
    enabled: true,
    latitude: 40.71,    // your coordinates (open-meteo.com)
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

Create `journals.config.local.js` (gitignored) to override any shared config value on a specific machine without affecting other machines:

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

### Prerequisites for Multi-Machine

Before setting up sync, make sure **each machine** has:

1. **Claude Code installed** — `npm install -g @anthropic-ai/claude-code`
2. **SSH key configured** with access to your GitHub repo — [GitHub SSH guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
3. **Git identity set** — `git config --global user.name` and `user.email`
4. **Push access** to the repo — use your own fork, not the upstream

Test SSH connectivity:
```bash
ssh -T git@github.com
# Should say: "Hi USERNAME! You've successfully authenticated"
```

### How It Works

1. **Machine ID** — Each computer is identified by a `machineId` (auto-detected from hostname, or set manually). Common hostnames like `MacBook-Pro.local` become `macbook`, `Mac-Studio.local` becomes `macstudio`.

2. **Merge on write** — When generating entries, the scripts check if a JSON file already exists for that date. If it does and contains data from a different machine, the new data is merged in:
   - Git commits are deduplicated by hash (shared across machines via git)
   - Claude Code sessions are additive (each machine has its own `~/.claude/history.jsonl`)
   - Shell commands are additive (each machine has its own `~/.zsh_history`)
   - Stats are aggregated across all machines

3. **Git as sync layer** — The repo itself is the sync mechanism:
   - `generate_all.py` pulls from remote before generating (picks up other machines' entries)
   - After generating, it commits and pushes (if `autoPush: true`)
   - No external services, databases, or sync tools needed

### Setup (Per Machine)

**Step 1 — Clone on each machine:**

```bash
git clone git@github.com:YOUR_USERNAME/journals.git
cd journals
```

> Use SSH (`git@github.com:...`), not HTTPS. Auto-push requires SSH authentication.

**Step 2 — Run setup on each machine:**

```bash
node setup.js
```

The wizard will detect your hostname, check prerequisites, and configure everything. Set `autoPush: true` when prompted.

**Step 3 — Generate on each machine:**

```bash
python3 scripts/generate_all.py
```

Each run will:
1. `git pull` — get latest entries from the other machine
2. Generate this machine's data for today
3. Merge with any existing data from other machines
4. `git commit` + `git push` — share with other machines

**Step 4 — Automate (optional):**

Set up a daily LaunchAgent or cron on each machine (see [Automation](#automate-with-cron--launchagent) below).

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

### Troubleshooting Multi-Machine

| Problem | Cause | Fix |
|---------|-------|-----|
| `Permission denied (publickey)` | SSH key not configured for GitHub | [Add your SSH key](https://github.com/settings/ssh/new) |
| `fatal: could not read Username` | Remote uses HTTPS, not SSH | `git remote set-url origin git@github.com:USER/journals.git` |
| Entries from other machine don't appear | `autoPush` is `false` | Set `autoPush: true` in `journals.config.js` |
| Merge conflicts on entries | Both machines pushed at the same time | `git pull --rebase` then re-run `python3 scripts/generate_all.py` |
| Work Journal is empty | Claude Code not installed or never used | Install Claude Code: `npm install -g @anthropic-ai/claude-code` |
| Daily Journal is empty | No zsh history found | Only zsh is supported; bash users see git-only data |

### Single Machine

If you only use one computer, multi-machine sync is transparent — everything works the same, entries just won't have the `_machines` metadata. No extra setup needed. You can leave `autoPush: false`.

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
├── journals.config.js         # Shared configuration
├── journals.config.local.js   # Per-machine overrides (gitignored)
├── setup.js                   # Interactive setup wizard with pre-flight checks
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
│   ├── generate_work_journal.py   # Claude Code sessions → metrics
│   ├── generate_daily_journal.py  # Shell history → activity
│   ├── generate_narrative.py      # Markdown → sections
│   ├── config.py              # Config loader (JS parser + machine ID)
│   ├── build_manifest.py      # JSON manifest builder
│   ├── build_index.py         # HTML index builder
│   └── backfill.py            # Bulk date generation
└── README.md
```

## License

MIT
