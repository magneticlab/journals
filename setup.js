#!/usr/bin/env node
/**
 * Journals — Interactive Setup
 *
 * Run: node setup.js
 * Or:  npm run setup
 *
 * Checks prerequisites, walks you through configuration,
 * generates sample entries, and gets you ready to run.
 */

import { createInterface } from 'readline'
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'
import { execSync } from 'child_process'
import { homedir } from 'os'

const __dirname = dirname(fileURLToPath(import.meta.url))
const CONFIG_PATH = join(__dirname, 'journals.config.js')

const rl = createInterface({ input: process.stdin, output: process.stdout })
const ask = (q, fallback = '') => new Promise(resolve => {
  rl.question(`${q}${fallback ? ` (${fallback})` : ''}: `, answer => {
    resolve(answer.trim() || fallback)
  })
})

// ─── Pre-flight checks ────────────────────────────────────────────

function checkCommand(cmd, label) {
  try {
    const version = execSync(cmd, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] }).trim()
    return { ok: true, version }
  } catch {
    return { ok: false, version: null }
  }
}

function runPreflight() {
  console.log()
  console.log('  Journals — Setup Wizard')
  console.log('  ━━━━━━━━━━━━━━━━━━━━━━')
  console.log()
  console.log('  Checking prerequisites...')
  console.log()

  const checks = []
  let hasErrors = false
  let hasWarnings = false

  // 1. Python
  const py = checkCommand('python3 --version')
  if (py.ok) {
    const ver = py.version.replace('Python ', '')
    const [major, minor] = ver.split('.').map(Number)
    if (major >= 3 && minor >= 9) {
      checks.push({ icon: '✓', label: `Python ${ver}`, status: 'ok' })
    } else {
      checks.push({ icon: '✗', label: `Python ${ver} — need 3.9+`, status: 'error' })
      hasErrors = true
    }
  } else {
    checks.push({ icon: '✗', label: 'Python 3 — not found', status: 'error' })
    hasErrors = true
  }

  // 2. Node.js
  const node = checkCommand('node --version')
  if (node.ok) {
    const ver = node.version.replace('v', '')
    const major = parseInt(ver.split('.')[0])
    if (major >= 18) {
      checks.push({ icon: '✓', label: `Node.js ${ver}`, status: 'ok' })
    } else {
      checks.push({ icon: '✗', label: `Node.js ${ver} — need 18+`, status: 'error' })
      hasErrors = true
    }
  } else {
    checks.push({ icon: '✗', label: 'Node.js — not found', status: 'error' })
    hasErrors = true
  }

  // 3. Git
  const git = checkCommand('git --version')
  if (git.ok) {
    checks.push({ icon: '✓', label: git.version, status: 'ok' })
  } else {
    checks.push({ icon: '✗', label: 'Git — not found', status: 'error' })
    hasErrors = true
  }

  // 4. Git user config
  if (git.ok) {
    const userName = checkCommand('git config user.name')
    const userEmail = checkCommand('git config user.email')
    if (userName.ok && userEmail.ok) {
      checks.push({ icon: '✓', label: `Git user: ${userName.version} <${userEmail.version}>`, status: 'ok' })
    } else {
      checks.push({ icon: '!', label: 'Git user.name/email not set — needed for commits', status: 'warn' })
      hasWarnings = true
    }
  }

  // 5. Claude Code
  const claude = checkCommand('claude --version')
  if (claude.ok) {
    checks.push({ icon: '✓', label: `Claude Code ${claude.version}`, status: 'ok' })
  } else {
    checks.push({ icon: '!', label: 'Claude Code — not installed (work journal will be empty without it)', status: 'warn' })
    hasWarnings = true
  }

  // 6. Claude history file
  const historyPath = join(homedir(), '.claude', 'history.jsonl')
  if (existsSync(historyPath)) {
    checks.push({ icon: '✓', label: 'Claude Code history file found', status: 'ok' })
  } else if (claude.ok) {
    checks.push({ icon: '!', label: 'Claude Code history not found — it will be created after your first session', status: 'warn' })
    hasWarnings = true
  }

  // 7. SSH key (for multi-machine push)
  const sshDir = join(homedir(), '.ssh')
  const hasSSH = existsSync(join(sshDir, 'id_ed25519')) ||
                 existsSync(join(sshDir, 'id_rsa')) ||
                 existsSync(join(sshDir, 'id_ecdsa'))
  if (hasSSH) {
    checks.push({ icon: '✓', label: 'SSH key found', status: 'ok' })
  } else {
    checks.push({ icon: '!', label: 'No SSH key found — needed for git push (multi-machine sync)', status: 'warn' })
    hasWarnings = true
  }

  // 8. zsh (for daily journal)
  const zshHistory = existsSync(join(homedir(), '.zsh_history'))
  if (zshHistory) {
    checks.push({ icon: '✓', label: 'zsh history found', status: 'ok' })
  } else {
    checks.push({ icon: '!', label: 'No zsh history — daily journal uses zsh; bash users will see limited data', status: 'warn' })
    hasWarnings = true
  }

  // Print results
  for (const c of checks) {
    const color = c.status === 'ok' ? '\x1b[32m' : c.status === 'error' ? '\x1b[31m' : '\x1b[33m'
    console.log(`  ${color}${c.icon}\x1b[0m  ${c.label}`)
  }
  console.log()

  return { hasErrors, hasWarnings }
}

// ─── Main ──────────────────────────────────────────────────────────

async function main() {
  const { hasErrors, hasWarnings } = runPreflight()

  if (hasErrors) {
    console.log('  \x1b[31mSome required tools are missing. Install them before continuing:\x1b[0m')
    console.log()
    console.log('    Python 3.9+  →  https://python.org or: brew install python')
    console.log('    Node.js 18+  →  https://nodejs.org or: brew install node')
    console.log('    Git          →  https://git-scm.com or: xcode-select --install')
    console.log()
    const cont = (await ask('  Continue anyway? (y/n)', 'n')).toLowerCase() === 'y'
    if (!cont) {
      rl.close()
      return
    }
  }

  if (hasWarnings) {
    console.log('  \x1b[33mSome optional tools are missing. Here\'s how to set them up:\x1b[0m')
    console.log()
    console.log('    Claude Code   →  npm install -g @anthropic-ai/claude-code')
    console.log('                     Required for the Work Journal. Without it, only the')
    console.log('                     Daily Journal (terminal + git activity) will have data.')
    console.log()
    console.log('    Git identity  →  git config --global user.name "Your Name"')
    console.log('                     git config --global user.email "you@example.com"')
    console.log()
    console.log('    SSH key       →  ssh-keygen -t ed25519 -C "you@example.com"')
    console.log('                     Then add ~/.ssh/id_ed25519.pub to GitHub:')
    console.log('                     https://github.com/settings/ssh/new')
    console.log('                     Required for auto-push (multi-machine sync).')
    console.log()
    await ask('  Press Enter to continue')
  }

  // 1. Basic info
  console.log()
  console.log('  Configuration')
  console.log('  ─────────────')
  const name = await ask('  Your name', 'User')
  const siteTitle = await ask('  Site title', 'Journals')

  // 2. Weather
  console.log()
  const weatherEnabled = (await ask('  Enable weather widget? (y/n)', 'y')).toLowerCase() === 'y'
  let lat = '40.71', lon = '-74.01', weatherLabel = 'New York'
  if (weatherEnabled) {
    console.log('  Find your coordinates at https://open-meteo.com')
    lat = await ask('  Latitude', '40.71')
    lon = await ask('  Longitude', '-74.01')
    weatherLabel = await ask('  Location name (for your reference)', 'New York')
  }

  // 3. Data sources
  console.log()
  console.log('  Data Sources')
  console.log('  ────────────')
  console.log('  Paths are relative to your home directory (~).')
  const reposDir = await ask('  Git repos directory', 'GitHub')

  // Verify the repos dir exists
  const reposDirFull = join(homedir(), reposDir)
  if (!existsSync(reposDirFull)) {
    console.log(`  \x1b[33m!\x1b[0m  ${reposDirFull} does not exist.`)
    console.log(`     Create it, or check the path. Git activity won't be tracked without it.`)
  }

  const claudeHistory = await ask('  Claude Code history path', '.claude/history.jsonl')
  const narrativeInput = await ask('  Narrative journal dir (or "skip" to disable)', 'skip')
  const narrativeDir = narrativeInput === 'skip' ? null : narrativeInput

  // 4. Multi-machine
  console.log()
  console.log('  Multi-Machine Sync')
  console.log('  ──────────────────')
  console.log('  If you use multiple computers, Journals can merge entries from all of them.')
  console.log('  Each machine gets a unique ID (auto-detected from hostname by default).')
  console.log()

  // Show detected hostname
  let detectedId = 'unknown'
  try {
    const hostname = execSync('hostname', { encoding: 'utf-8' }).trim().toLowerCase().replace('.local', '').replace(/ /g, '-')
    if (hostname.includes('macbook')) detectedId = 'macbook'
    else if (hostname.includes('mac-studio') || hostname.includes('macstudio')) detectedId = 'macstudio'
    else if (hostname.includes('imac')) detectedId = 'imac'
    else detectedId = hostname
    console.log(`  Detected machine ID: ${detectedId}`)
  } catch {}

  const machineIdInput = await ask('  Machine ID (press Enter to use detected, or type custom)', detectedId)
  const machineId = machineIdInput === detectedId ? null : machineIdInput

  // 5. Git auto-push
  console.log()
  console.log('  Git Auto-Push')
  console.log('  ─────────────')
  console.log('  When enabled, entries are committed and pushed to your remote after generation.')
  console.log('  This is required for multi-machine sync — other machines pull your entries.')
  console.log()

  if (!existsSync(join(homedir(), '.ssh', 'id_ed25519')) &&
      !existsSync(join(homedir(), '.ssh', 'id_rsa')) &&
      !existsSync(join(homedir(), '.ssh', 'id_ecdsa'))) {
    console.log('  \x1b[33m!\x1b[0m  No SSH key detected. Auto-push requires SSH authentication with GitHub.')
    console.log('     Set up an SSH key first:')
    console.log('       ssh-keygen -t ed25519 -C "you@example.com"')
    console.log('       Then add the public key to https://github.com/settings/ssh/new')
    console.log()
  }

  const autoPush = (await ask('  Enable auto-push? (y/n)', 'n')).toLowerCase() === 'y'
  const branch = autoPush ? await ask('  Push branch', 'main') : 'main'

  if (autoPush) {
    // Verify remote is configured
    try {
      const remote = execSync('git remote get-url origin', { encoding: 'utf-8', cwd: __dirname }).trim()
      console.log(`  Remote: ${remote}`)
      if (remote.startsWith('https://github.com/magneticlab/journals')) {
        console.log('  \x1b[33m!\x1b[0m  You\'re using the upstream remote. Fork the repo first, then update:')
        console.log(`     git remote set-url origin git@github.com:YOUR_USERNAME/journals.git`)
      }
    } catch {
      console.log('  \x1b[33m!\x1b[0m  No git remote configured. Add one:')
      console.log('     git remote add origin git@github.com:YOUR_USERNAME/journals.git')
    }

    // Test SSH connectivity
    console.log()
    console.log('  Testing GitHub SSH connection...')
    try {
      execSync('ssh -T git@github.com', { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'], timeout: 10000 })
    } catch (e) {
      const stderr = e.stderr || ''
      if (stderr.includes('successfully authenticated')) {
        console.log('  \x1b[32m✓\x1b[0m  GitHub SSH authentication successful')
      } else {
        console.log('  \x1b[31m✗\x1b[0m  GitHub SSH connection failed')
        console.log('     Auto-push won\'t work until SSH is configured.')
        console.log('     Guide: https://docs.github.com/en/authentication/connecting-to-github-with-ssh')
      }
    }
  }

  // 6. Claude API (for Reflect feature)
  console.log()
  const reflectEnabled = (await ask('  Enable AI Reflect feature? Requires Claude API key (y/n)', 'n')).toLowerCase() === 'y'

  // Write config
  const config = `/**
 * Journals — User Configuration
 * Generated by setup wizard on ${new Date().toISOString().slice(0, 10)}
 */

export default {
  name: '${name}',
  siteTitle: '${siteTitle}',${machineId ? `\n  machineId: '${machineId}',` : '\n  // machineId: auto-detected from hostname'}

  weather: {
    enabled: ${weatherEnabled},
    latitude: ${lat},
    longitude: ${lon},
    label: '${weatherLabel}',
  },

  sources: {
    claudeHistory: '${claudeHistory}',
    reposDir: '${reposDir}',
    narrativeDir: ${narrativeDir ? `'${narrativeDir}'` : 'null'},
  },

  git: {
    autoPush: ${autoPush},
    branch: '${branch}',
  },

  reflect: {
    enabled: ${reflectEnabled},
    model: 'claude-haiku-4-5-20251001',
  },
}
`
  writeFileSync(CONFIG_PATH, config)
  console.log()
  console.log('  \x1b[32m✓\x1b[0m  Config saved to journals.config.js')

  // Create .env if reflect enabled
  if (reflectEnabled) {
    const envPath = join(__dirname, 'app', '.env')
    if (!existsSync(envPath)) {
      const apiKey = await ask('  Your Anthropic API key (sk-ant-...)', '')
      if (apiKey) {
        writeFileSync(envPath, `VITE_ANTHROPIC_API_KEY=${apiKey}\n`)
        console.log('  API key saved to app/.env')
      } else {
        console.log('  Skipped — add your key to app/.env later')
      }
    }
  }

  // Generate sample entries
  console.log()
  const genSample = (await ask('  Generate sample entries to see how it looks? (y/n)', 'y')).toLowerCase() === 'y'
  if (genSample) {
    generateSampleEntries()
    console.log('  \x1b[32m✓\x1b[0m  Sample entries generated')
  }

  // Install dependencies
  console.log()
  console.log('  Installing dependencies...')
  try {
    execSync('npm install', { cwd: join(__dirname, 'app'), stdio: 'inherit' })
    console.log()
    console.log('  \x1b[32m✓\x1b[0m  Dependencies installed')
  } catch {
    console.log('  npm install failed — run it manually: cd app && npm install')
  }

  // Done
  console.log()
  console.log('  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log('  Setup complete!')
  console.log('  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
  console.log()
  console.log('  Next steps:')
  console.log()
  console.log('    1. Start the dev server:')
  console.log('       cd app && npm run dev')
  console.log()
  console.log('    2. Generate real entries from your data:')
  console.log('       python3 scripts/generate_all.py')
  console.log()
  if (autoPush) {
    console.log('    3. On your other machine(s):')
    console.log('       git clone git@github.com:YOU/journals.git')
    console.log('       node setup.js')
    console.log()
  }
  console.log('  For daily automation, see the README.')
  console.log()

  rl.close()
}

function generateSampleEntries() {
  const today = new Date().toISOString().slice(0, 10)
  const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10)
  const dayBefore = new Date(Date.now() - 86400000 * 2).toISOString().slice(0, 10)

  const days = [
    { date: dayBefore, dayName: getDayName(dayBefore) },
    { date: yesterday, dayName: getDayName(yesterday) },
    { date: today, dayName: getDayName(today) },
  ]

  const workDir = join(__dirname, 'app', 'public', 'entries', 'work')
  const dailyDir = join(__dirname, 'app', 'public', 'entries', 'daily')
  const narrativeDir = join(__dirname, 'app', 'public', 'entries', 'narrative')
  mkdirSync(workDir, { recursive: true })
  mkdirSync(dailyDir, { recursive: true })
  mkdirSync(narrativeDir, { recursive: true })

  for (const { date, dayName } of days) {
    const dt = new Date(date + 'T12:00:00')
    const display = dt.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })

    // Work entry
    const sessions = 1 + Math.floor(Math.random() * 4)
    const commits = 2 + Math.floor(Math.random() * 8)
    const messages = sessions * (10 + Math.floor(Math.random() * 20))
    writeFileSync(join(workDir, `${date}.json`), JSON.stringify({
      date, day: dayName, display,
      generatedAt: new Date().toISOString(),
      metrics: {
        volume: { score: 40 + Math.floor(Math.random() * 40), label: 'Output Volume' },
        complexity: { score: 30 + Math.floor(Math.random() * 40), label: 'Complexity' },
        focus: { score: 50 + Math.floor(Math.random() * 30), label: 'Focus' },
        depth: { score: 40 + Math.floor(Math.random() * 40), label: 'Depth' },
        craft: { score: 50 + Math.floor(Math.random() * 30), label: 'Craft' },
        momentum: { score: 30 + Math.floor(Math.random() * 50), label: 'Momentum' },
      },
      stats: { sessions, messages, commits, repos: 1, timeRange: '09:00–17:30', linesAdded: commits * 45, linesRemoved: commits * 12, filesChanged: commits * 3 },
      whatIDid: ['Set up Journals project and configured local environment', 'Explored the codebase and customized themes'],
      activityTimeline: ['Project setup and configuration', 'Theme customization'],
      insights: ['Getting familiar with the workflow — momentum will build as the habit forms.'],
      continuedFromYesterday: [],
      roadblocks: [],
      themes: { 'General Development': 3, 'Page Building': 2 },
      projectsWip: ['journals — sample data'],
      gitActivity: [{ repo: 'journals', commits: [{ hash: 'abc1234', author: 'You', message: 'Initial setup', time: '10:00' }], stat: `${commits * 3} files changed, ${commits * 45} insertions(+)` }],
      summary: `${sessions} session(s), ${messages} msgs, ${commits} commit(s) across 1 repo(s)`,
    }, null, 2))

    // Daily entry
    const commands = 20 + Math.floor(Math.random() * 60)
    writeFileSync(join(dailyDir, `${date}.json`), JSON.stringify({
      date, day: dayName, display,
      generatedAt: new Date().toISOString(),
      summary: `${commands} terminal commands, ${commits} commits across 1 repos, 0 files modified.`,
      stats: { commands, commits, repos: 1, filesModified: 0 },
      categories: { Git: Math.floor(commands * 0.3), Navigation: Math.floor(commands * 0.2), 'Claude Code': Math.floor(commands * 0.15), Other: Math.floor(commands * 0.35) },
      activityByHour: { '09': 5, '10': 8, '11': 12, '14': 10, '15': 7, '16': 5 },
      notableCommands: [{ time: '10:00', command: 'npm run dev' }, { time: '14:30', command: 'git log --oneline -10' }],
      gitActivity: [],
      fileGroups: {},
    }, null, 2))
  }

  // Build manifest
  const manifest = { work: [], daily: [], narrative: [] }
  for (const { date, dayName } of days) {
    const dt = new Date(date + 'T12:00:00')
    const display = dt.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
    const workData = JSON.parse(readFileSync(join(workDir, `${date}.json`), 'utf-8'))
    const dailyData = JSON.parse(readFileSync(join(dailyDir, `${date}.json`), 'utf-8'))
    manifest.work.push({ date, day: dayName, display, summary: workData.summary, stats: workData.stats })
    manifest.daily.push({ date, day: dayName, display, summary: dailyData.summary, stats: dailyData.stats })
  }
  writeFileSync(join(__dirname, 'app', 'public', 'manifest.json'), JSON.stringify(manifest, null, 2))
}

function getDayName(dateStr) {
  return new Date(dateStr + 'T12:00:00').toLocaleDateString('en-US', { weekday: 'long' })
}

main().catch(console.error)
