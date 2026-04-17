# Journals

A personal development journal that automatically captures your daily work from Claude Code sessions, git commits, and terminal history — displayed in a beautiful Vue 3 dashboard with animated backgrounds and multiple themes.

![Vue 3](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vuedotjs&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-8-646CFF?logo=vite&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![Zero Dependencies](https://img.shields.io/badge/Python_deps-zero-green)

## What It Does

- **Work Journal** — Parses your Claude Code session history and git commits to generate structured daily reports with metrics (output volume, complexity, focus, depth, craft, momentum)
- **Daily Journal** — Captures terminal activity, command categories, and file changes
- **Narrative Journal** — Renders long-form markdown journal entries from Claude Code memory files (optional)
- **AI Reflect** — Optional end-of-day reflection with Claude API analysis
- **6 Background Animations** — Ribbons, Amoeba, Stripes, Spikes, Borealis, Nebula (WebGL)
- **5 Themes** — Midnight, Dawn, Daylight, Dusk, Aurora (auto-switches by time of day)
- **Weather Widget** — Current conditions via Open-Meteo (no API key needed)

## Quick Start

```bash
# Clone the repo
git clone https://github.com/magneticlab/journals.git
cd journals

# Run the interactive setup wizard
node setup.js

# Start the dev server
cd app && npm run dev
```

The setup wizard will:
1. Ask for your name, location, and preferences
2. Configure data source paths
3. Generate sample entries so you can see how it looks
4. Install dependencies

## Generate Real Entries

Once configured, generate journal entries from your actual data:

```bash
# Generate today's entries
python3 scripts/generate_all.py

# Generate for a specific date
python3 scripts/generate_all.py 2026-04-15

# Backfill the last 30 days
python3 scripts/backfill.py 30

# Rebuild the manifest index
python3 scripts/build_manifest.py
```

### Data Sources

The generators read from these local sources (all configurable in `journals.config.js`):

| Source | Used By | Default Path |
|--------|---------|--------------|
| Claude Code history | Work Journal | `~/.claude/history.jsonl` |
| Git repos | Work + Daily | `~/GitHub/` |
| Terminal history | Daily Journal | `~/.zsh_history` |
| Claude memory files | Narrative | *(disabled by default)* |

### Automate with Cron / LaunchAgent

To generate entries automatically every day:

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

Then load it:
```bash
launchctl load ~/Library/LaunchAgents/com.journals.generate.plist
```

**Linux (cron):**
```bash
# Run at 11:30 PM daily
30 23 * * * cd /path/to/journals && python3 scripts/generate_all.py
```

## Configuration

All settings live in `journals.config.js` at the project root:

```js
export default {
  name: 'Your Name',
  siteTitle: 'Journals',
  weather: {
    enabled: true,
    latitude: 40.71,
    longitude: -74.01,
  },
  sources: {
    claudeHistory: '.claude/history.jsonl',
    reposDir: 'GitHub',
    narrativeDir: null, // set to enable narrative journal
  },
  git: {
    autoPush: false,
    branch: 'main',
  },
  reflect: {
    enabled: false, // requires VITE_ANTHROPIC_API_KEY in app/.env
    model: 'claude-haiku-4-5-20251001',
  },
}
```

## Deploy to Your Domain

### Static Export (Netlify, Vercel, any host)

```bash
cd app && npm run build
# Upload the dist/ folder to your host
```

### Netlify

```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
cd app && npm run build && netlify deploy --prod --dir=dist
```

### Custom Domain with Subdirectory

If deploying under a subdirectory (e.g., `yourdomain.com/journals/`), update `app/vite.config.js`:

```js
base: '/journals/',
```

Then rebuild and deploy.

## Forking & Updates

Fork this repo to get your own copy. To pull in upstream improvements:

```bash
# Add upstream remote (one-time)
git remote add upstream https://github.com/magneticlab/journals.git

# Fetch and merge updates
git fetch upstream
git merge upstream/main
```

Your personal config and generated entries are gitignored, so merges should be clean.

## Project Structure

```
journals/
├── journals.config.js     # Your configuration
├── setup.js               # Interactive setup wizard
├── package.json           # Root scripts (setup, generate, dev)
├── app/                   # Vue 3 + Vite frontend
│   ├── src/
│   │   ├── pages/         # Home, Journal, Entry, AuroraPreview
│   │   ├── components/    # Animations, charts, modals, switchers
│   │   ├── composables/   # Theme and animation state
│   │   └── services/      # Claude API integration
│   └── public/
│       ├── manifest.json  # Entry index (auto-generated)
│       └── entries/       # Generated JSON entries
├── scripts/               # Python generators (zero pip deps)
│   ├── generate_all.py    # Master orchestrator
│   ├── generate_work_journal.py
│   ├── generate_daily_journal.py
│   ├── generate_narrative.py
│   ├── build_manifest.py
│   └── backfill.py
└── README.md
```

## Requirements

- **Node.js** 18+
- **Python** 3.9+ (no pip dependencies)
- **Claude Code** (for work journal data — optional, daily journal works without it)

## License

MIT
