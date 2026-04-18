/**
 * Journals — User Configuration
 *
 * Edit this file to personalize your journal instance.
 * Run `npm run setup` for an interactive setup wizard,
 * or edit these values directly.
 */

export default {
  // Display name shown in the greeting ("Good morning, {name}.")
  name: 'User',

  // Machine identifier — auto-detected from hostname.
  // Override per-machine in journals.config.local.js if needed.
  // machineId: 'macstudio',

  // Site title shown in the browser tab and nav
  siteTitle: 'Journals',

  // Weather location (Open-Meteo, no API key needed)
  // Find your coordinates at https://open-meteo.com
  weather: {
    enabled: true,
    latitude: 40.71,
    longitude: -74.01,
    // Label shown in config only (not displayed in UI)
    label: 'New York',
  },

  // Paths where the Python generators look for data
  // These are resolved relative to $HOME
  sources: {
    // Claude Code history file (JSONL)
    claudeHistory: '.claude/history.jsonl',

    // Directory containing your git repos
    reposDir: 'GitHub',

    // Claude memory journal directory (for narrative entries)
    // Set to null to disable narrative generation
    narrativeDir: null,
  },

  // Git auto-publish after generation
  git: {
    autoPush: true,
    // Branch to push to (set to your deploy branch if using CI/CD)
    branch: 'main',
  },

  // Claude API for the Reflect feature (optional)
  // Set your key in app/.env as VITE_ANTHROPIC_API_KEY
  reflect: {
    enabled: false,
    model: 'claude-haiku-4-5-20251001',
  },
}
