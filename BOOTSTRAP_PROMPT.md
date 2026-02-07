# ZDC Blender Tools — Claude Code Bootstrap Prompt

This is your one-time setup prompt for consolidating your four existing local project folders into a single unified workspace backed by a new GitHub repository, with full development environment setup including BlenderMCP.

## Before You Begin — Manual GitHub Steps

Claude Code can handle most of this process, but you need to do a couple things on GitHub's website first (Claude Code can't click buttons on web pages for you). These are one-time actions.

### Step A: Create the new repository on GitHub

1. Go to https://github.com/new
2. Repository name: `ZDC-Blender-Tools`
3. Description: "Unified Blender 5.0+ add-on development workspace for Ziti Design & Creative"
4. Set it to **Public** (your existing repos are public)
5. Do NOT initialize with a README, .gitignore, or license (Claude Code will handle all of this)
6. Click "Create repository"
7. Confirm the URL exists: `https://github.com/kenkoller/ZDC-Blender-Tools.git`

### Step B: Fork the Home Builder 4 repository (separate from the monorepo)

The Home Builder add-on is someone else's work that you're expanding for Blender 5.0. The proper way to handle this in open source is with a GitHub "fork," which creates a linked copy under your account with automatic attribution to the original author.

1. Find the original Home Builder 4 repository on GitHub (search for "home_builder_4" or the original author's name — you may need to identify the original repo URL from the add-on's documentation or `__init__.py`)
2. Click the **"Fork"** button in the top-right corner of the original repo's page
3. This creates `kenkoller/home_builder_4` (or whatever the repo name is) with a banner that reads "forked from [original-author]/[repo-name]"
4. In your fork's description, add something like: "Blender 5.0+ compatibility updates and expanded features by Ziti Design & Creative"
5. This is now a separate repository from ZDC-Blender-Tools — it stays independent because it's fundamentally a modification of someone else's project

If you cannot find the original repository (some Blender add-ons aren't on GitHub), you can create a fresh repo and add proper attribution in the README and `__init__.py` instead. Claude Code can help you write that attribution when you get to it.

This step can be done later if you want to focus on the main workspace first.

### Step C: You're ready

Once the empty `ZDC-Blender-Tools` repo exists on GitHub, come back here and proceed with the Claude Code prompt below.

---

## How to Use the Bootstrap Prompt

1. Open a terminal on whichever machine you're starting with (Mac or PC)
2. Navigate to where you want the project to live (e.g., `cd ~/Projects` or `cd C:\Projects`)
3. Run `claude` to start Claude Code
4. Copy everything below the final `---` separator and paste it in
5. Claude Code will ask you questions as it goes — answer them when prompted

**Important note about the .gitignore file:** If Windows wouldn't let you rename it to `.gitignore` in File Explorer, that's fine — just leave it as `gitignore` without the dot. When you tell Claude Code where the starter files are, mention that the gitignore file needs to be renamed to `.gitignore`. Claude Code can do this easily from the terminal.

---

## Bootstrap Prompt (paste everything below this line into Claude Code)

```
I'm consolidating four existing Blender add-on projects into a single unified workspace backed by a new GitHub repository. Read the CLAUDE.md file after we set it up — it has all the project conventions.

Here's the situation:
- I have a new empty GitHub repo ready: kenkoller/ZDC-Blender-Tools
- I have four existing add-on projects as LOCAL FOLDERS on this machine (the local files are more up-to-date than what's on my old GitHub repos — always use the local folders as the source of truth)
- I also have four older GitHub repos (kenkoller/cabinet-generator, kenkoller/metallic-flake-shader, kenkoller/auto-batch-renderer, kenkoller/kitchen-generator) that will be archived after consolidation — do NOT clone from these
- I develop on both macOS and Windows
- All tools target Blender 5.0+ exclusively
- IMPORTANT: This is a public repository. No client names, proprietary color values, or confidential business information should appear in any committed files. There is a CLAUDE.local.md file (gitignored) for private context.

I have starter files ready (CLAUDE.md, CLAUDE.local.md, .gitignore, and this BOOTSTRAP_PROMPT.md). Ask me where they are and where my four existing project folders are located before proceeding.

Execute all phases below in order. Ask me for clarification when needed.

---

### Phase 1: Initialize the workspace from the GitHub repo

1. Clone the empty ZDC-Blender-Tools repo:
   ```
   git clone https://github.com/kenkoller/ZDC-Blender-Tools.git
   cd ZDC-Blender-Tools
   ```

2. Ask me where the starter files are (CLAUDE.md, CLAUDE.local.md, .gitignore, BOOTSTRAP_PROMPT.md). Copy them into the project root. If the .gitignore file doesn't have the leading dot, rename it to `.gitignore`.

3. Verify the .gitignore includes all of the following:
   - Private files: `CLAUDE.local.md`, `reference/` (entire directory)
   - Python: `__pycache__/`, `*.py[cod]`, `*$py.class`, `*.so`, `*.egg-info/`, `dist/`, `build/`
   - Blender: `*.blend1` through `*.blend5`
   - OS: `.DS_Store`, `Thumbs.db`, `Desktop.ini`, `._*`
   - IDE: `.vscode/`, `.idea/`, `*.swp`, `*.swo`
   - Environments: `.env`, `.venv/`, `env/`, `venv/`
   - Test artifacts: `test_log.json`, `test_report.json`, `*.log`

4. Create the full directory structure:
   ```
   addons/
   common/__init__.py
   scripts/
   tests/test_scenes/
   mcp/
   ```

5. Initial commit and push:
   ```
   git add -A
   git commit -m "[workspace] Initial project scaffolding with conventions"
   git push origin main
   ```

---

### Phase 2: Import and reorganize existing add-ons from local folders

Ask me for the local file paths to each of my four existing project folders. These are the authoritative, most up-to-date versions of the code — do NOT clone from GitHub.

Copy each project's files into the correct location under addons/, stripping all __pycache__ directories and .pyc files during import.

Process each add-on one at a time:

**auto-batch-renderer → addons/auto-batch-renderer/**
- Copy from my local folder (ask me for the path)
- Analyze the code and refactor into the standard structure: separate operators.py, panels.py, properties.py, move core logic into src/
- Update bl_info to ZDC conventions (name "ZDC - Auto Batch Renderer", blender (5, 0, 0), category "ZDC Tools")
- Rename operator/panel/property group classes to ZDC_ prefix convention
- Scrub any client-specific references (replace company/brand names with generic terms like "production client" or "client presets")
- Add a README.md describing the add-on
- Commit and push: `[auto-batch-renderer] Import and restructure to ZDC conventions`

**metallic-flake-shader → addons/metallic-flake-shader/**
- Copy from my local folder (ask me for the path)
- Analyze whether metallic_flake_shader.py and universal_pbr_shader.py should be one add-on or two — recommend based on code coupling
- Refactor into standard structure with ZDC_ naming
- Scrub any client-specific references
- Add a README.md
- Commit and push: `[metallic-flake-shader] Import and restructure to ZDC conventions`

**cabinet-generator → addons/cabinet-generator/**
- Copy from my local folder (ask me for the path)
- Already well-structured — preserve its internal organization (atomic/, systems/, nodes/, src/)
- If it has its own CLAUDE.md, review it: merge any useful project-level insights into the root CLAUDE.md (keeping it client-name-free), move addon-specific details into the addon's README.md, then delete the addon-level CLAUDE.md
- Normalize the outer layer: verify bl_info matches ZDC conventions, verify class naming
- Scrub any client-specific references (product names, company names, proprietary specs)
- Remove test artifacts (test_log.json, test_report.json) from tracked files
- Commit and push: `[cabinet-generator] Import and normalize to ZDC conventions`

**kitchen-generator → addons/kitchen-generator/**
- Copy from my local folder (ask me for the path)
- Analyze code structure and bring into compliance with standard structure
- Scrub any client-specific references
- Add a README.md
- Commit and push: `[kitchen-generator] Import and restructure to ZDC conventions`

After all four imports, provide a summary of findings: any incomplete/experimental code, any Blender 4.x API usage needing migration, any duplicated logic across add-ons, any client-specific references you found and scrubbed, and any concerns.

---

### Phase 3: Extract common utilities

Analyze all imported add-ons for genuinely shared patterns. Only extract code that is used in 2+ add-ons — don't force abstractions that don't exist yet.

Look for: node tree creation/manipulation helpers, shared material setup patterns, naming convention utilities, and any duplicated logic.

For color_standards.py in common/: create the module structure but keep it generic (e.g., a framework for defining calibrated color profiles with example entries). Actual client-specific color values belong only in CLAUDE.local.md and should be populated locally, never committed.

If nothing is genuinely shared yet, say so. An empty common/ with just __init__.py is fine — it'll get populated as the codebase grows.

Commit and push if extractions were made: `[common] Extract shared utilities`

---

### Phase 4: Create project README and utility scripts

**README.md (project root):**
- Project title: "ZDC Blender Tools"
- Brief description of ZDC and the purpose of this workspace
- List all add-ons with one-line descriptions
- "Getting Started" section: clone the repo, install uv, set up BlenderMCP (link to mcp/README.md), install add-ons into Blender
- Note Blender 5.0+ requirement prominently
- Note cross-platform support (macOS and Windows)
- Include a "Contributing" note (even if it's just me for now — it's good practice)
- Include a license section (ask me what license I want to use if not already decided)

**scripts/install_addons.py:**
- Creates symlinks from each addon directory into Blender's add-ons path
- Auto-detects platform (macOS vs Windows) and uses the correct Blender paths
- Accepts --blender-path override for non-standard installations
- Handles existing symlinks (offers to replace)
- Clear terminal output about what was linked where

**scripts/validate_bl_info.py:**
- Walks addons/ and validates every __init__.py has proper bl_info
- Checks: name starts with "ZDC - ", blender is (5, 0, 0)+, category is "ZDC Tools"
- Checks for ZDC_ prefix on operator/panel/property group class names
- Scans for potential client-name leaks (flag any occurrence of strings that look like company names — ask me to provide a list of terms to flag)
- Reports issues with file path and line numbers

Commit and push: `[workspace] Add README, install script, and validation tools`

---

### Phase 5: Set up BlenderMCP

This phase connects Claude Desktop to Blender for interactive development. Handle as much as possible automatically.

**Step 1 — Install the uv package manager.**

Detect my platform and run the appropriate command:

macOS:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows PowerShell:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify with: `uv --version`

If on Windows and uv isn't found, add to PATH:
```powershell
$localBin = "$env:USERPROFILE\.local\bin"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$userPath;$localBin", "User")
```

**Step 2 — Download the BlenderMCP addon.py:**

```bash
curl -L -o /tmp/blender_mcp_addon.py https://raw.githubusercontent.com/ahujasid/blender-mcp/main/addon.py
```

Tell me exactly where the file was saved.

**Step 3 — Write the Claude Desktop configuration:**

The config file is at:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Read the existing file first (if any) and MERGE — don't overwrite other MCP servers that might be configured.

macOS config entry:
```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"],
      "env": { "DISABLE_TELEMETRY": "true" }
    }
  }
}
```

Windows config entry:
```json
{
  "mcpServers": {
    "blender": {
      "command": "cmd",
      "args": ["/c", "uvx", "blender-mcp"],
      "env": { "DISABLE_TELEMETRY": "true" }
    }
  }
}
```

**Step 4 — Walk me through the manual steps:**

Tell me exactly what to do:
1. Open Blender → Edit → Preferences → Add-ons → Install from Disk → navigate to [exact path of downloaded addon.py] → Install → enable "Interface: Blender MCP"
2. In Blender 3D Viewport, press N → sidebar → Blender MCP tab → Start MCP Server → confirm "MCP Server started on port 9876"
3. Fully quit Claude Desktop (not just close window — Quit from dock/taskbar) and relaunch
4. Look for hammer icon (🔨) in Claude Desktop → test with: "What objects are currently in my Blender scene?"

**Step 5 — Save reference documentation in the project:**

Create mcp/README.md with complete standalone setup instructions covering everything from Steps 1–4 above, written for either platform (so I can set up my other machine later). Include a troubleshooting section covering: no hammer icon, first command fails, connection timeouts, uvx not found, and the warning about not running uvx manually in a terminal.

Create mcp/claude_desktop_config_mac.json and mcp/claude_desktop_config_win.json as reference copies.

Commit and push: `[mcp] Set up BlenderMCP integration with setup documentation`

---

### Phase 6: Archive old repositories

Now that everything is consolidated, I need to archive the four original GitHub repos so they don't cause confusion. Claude Code can't do this directly (it requires GitHub web UI), so give me clear step-by-step instructions for archiving each one:

- kenkoller/cabinet-generator
- kenkoller/metallic-flake-shader
- kenkoller/auto-batch-renderer
- kenkoller/kitchen-generator

For each repo, walk me through: how to update the repo description to say "⚠️ Archived — consolidated into kenkoller/ZDC-Blender-Tools", and then how to go to Settings → Danger Zone → Archive this repository. Explain that archiving makes the repo read-only but doesn't delete anything — it's reversible if I ever need to un-archive.

---

### Phase 7: Final review

Run a complete pass over the workspace:

1. Run scripts/validate_bl_info.py and fix any issues
2. Verify no __pycache__ or .pyc files are tracked: `git ls-files | grep -E "__pycache__|\.pyc$"` should return nothing
3. Verify no client-specific names appear in any tracked files: `git grep -i "rev.a.shelf"` should return nothing (ask me for additional terms to check)
4. Verify CLAUDE.local.md is NOT tracked: `git ls-files | grep CLAUDE.local` should return nothing
5. Verify every add-on has a README.md
6. Verify the reference/ directory is NOT tracked (it's gitignored for privacy)
7. Do a final `git status` — should be clean

Provide a final summary:
- What was reorganized and the key decisions made
- Any code flagged as incomplete, experimental, or broken
- Any Blender 4.x API usage that needs 5.0 migration
- Any shared patterns found (or not found) across add-ons
- The full directory tree of the final workspace
- Recommendations for what to work on next
- Reminder of the manual steps I still need to complete (archiving old repos, Home Builder fork)
```

---

## After Setup: Quick Reference for Common Tasks

### Starting a new add-on
```
I want to create a new add-on called [name] that [description].
Create it under addons/ following our ZDC conventions.
```

### Before a major refactor
```
Commit the current state as a checkpoint: "[addon-name] Pre-refactor checkpoint"
Then proceed with [changes].
```

### Pushing changes to GitHub
If Claude Code doesn't push automatically, or you want to push manually:
```bash
git add -A
git commit -m "[addon-name] Description of changes"
git push origin main
```

### Creating a feature branch (for bigger changes)
```bash
git checkout -b feature/addon-name/description
# ... make changes, commit ...
git push origin feature/addon-name/description
# When done, merge on GitHub via Pull Request, or:
git checkout main
git merge feature/addon-name/description
git push origin main
```

### Checking what's different from GitHub
```bash
git status          # What's changed locally
git diff            # See the actual changes
git log --oneline   # See recent commits
```

### Setting up a second machine
1. Install Claude Code (`npm install -g @anthropic-ai/claude-code`)
2. Clone the repo: `git clone https://github.com/kenkoller/ZDC-Blender-Tools.git`
3. Copy your CLAUDE.local.md into the project root (this file doesn't sync through GitHub — transfer it manually via USB drive, private cloud storage, or similar)
4. Create a local reference/ directory if you need one for private documents
5. Follow the MCP setup instructions in mcp/README.md
