# AI Skills Curation Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a minimalist, developer-centric GitHub Pages web platform that curates top AI Agent Skills and MCP servers ranked by total stars and 7-day weekly star growth, with automated weekly updates, historical snapshots, mobile responsiveness, and bilingual (EN/KO) support.

**Architecture:** Pure zero-dependency static web application (`index.html`, `css/style.css`, `js/app.js`) powered by flat JSON data files (`data/registry.json`, `data/skills.json`, `data/history/YYYY-WW.json`), accompanied by a standalone Python updater script and GitHub Actions cron/deploy pipelines.

**Tech Stack:** Native HTML5/CSS3/ES6 JavaScript, Python 3 (urllib/json standard library, zero pip dependencies), GitHub Actions, GitHub Pages.

**Spec:** [`docs/superpowers/specs/2026-11-03-ai-skills-curation-design.md`](file:///Users/CHANBAE/.gemini/antigravity/scratch/ai-skills/docs/superpowers/specs/2026-11-03-ai-skills-curation-design.md)

## Global Constraints

- Git author & committer: `Changhyeok Bae <changhyeok.bae@gmail.com>`
- Git commit message: Title <= 50 chars, body hard-wrapped <= 72 chars per line
- Target repository: `chbaede/ai-skills` (`git@github.com:chbaede/ai-skills.git`)
- Zero external runtime framework dependencies (pure static web)
- UI aesthetics: Developer minimalism (Geist / JetBrains Mono typography, high readability, no AI-slop)
- Mobile responsiveness: Clean cards/collapsible layout on screens <640px

## Review Focus

1. **GitHub API Unauthenticated Rate Limiting:** When `GITHUB_TOKEN` is unset in local environment, requests must handle 60 req/hr limits gracefully with clear error messages and cached fallbacks.
2. **First-Run Snapshot Absence (Cold Start):** When no historical snapshot exists in `data/history/`, weekly delta must compute via recent stargazer timestamps or sensible seed values rather than showing zero or NaN.
3. **Locale State Persistence:** Switching languages (KO/EN) must instantly re-render without reloading, update URL hash/query, and persist in `localStorage`.
4. **Historical Snapshot Switching:** Loading a past week snapshot must render cleanly, update the "Last Updated" badge to show the historical week, and allow one-click return to "Live".
5. **Mobile Viewport Overflow:** Long repository names or tags must not cause horizontal scrolling or break table alignment on small screens (320px - 480px).

---

### Task 1: Curated Registry Schema & Seed Data

**Files:**
- Create: `data/registry.json`
- Create: `tests/test_registry.py`

**Interfaces:**
- Produces: `data/registry.json` containing verified repository records with `id`, `repo`, `name`, `category`, `tags`, and bilingual `description` (`en`, `ko`).

- [ ] **Step 1: Write test for registry format and schema**
  Create `tests/test_registry.py` asserting all required fields exist, categories match allowed values, and descriptions exist in both Korean and English.

- [ ] **Step 2: Run test to verify failure**
  Run: `python3 tests/test_registry.py`
  Expected: FAIL with missing file.

- [ ] **Step 3: Create `data/registry.json` with 12 curated AI skills/tools**
  Populate with verified repositories: `modelcontextprotocol/servers`, `obra/superpowers`, `anthropics/claude-quickstarts`, `openinterpreter/open-interpreter`, `cline/cline`, `Roo-Code/Roo-Code`, `Aider-AI/aider`, `princeton-nlp/SWE-agent`, `microsoft/semantic-kernel`, `executeautomation/mcp-playwright`, `mark3labs/mcp-go`, `github/copilot-cli`.

- [ ] **Step 4: Run test to verify it passes**
  Run: `python3 tests/test_registry.py`
  Expected: PASS

- [ ] **Step 5: Commit**
  Run:
  ```bash
  git add data/registry.json tests/test_registry.py
  git commit -m "feat(data): add curated ai skills registry schema"
  ```

---

### Task 2: Python Data Updater & History Archiver

**Files:**
- Create: `scripts/update_skills.py`
- Create: `tests/test_updater.py`
- Produces: `data/skills.json`, `data/history/{year}-W{week}.json`

**Interfaces:**
- Consumes: `data/registry.json`
- Produces: `data/skills.json` and weekly snapshot in `data/history/` with updated `stars`, `weekly_stars`, `open_issues`, and `updated_at`.

- [ ] **Step 1: Write unit tests for updater calculations**
  Create `tests/test_updater.py` testing delta calculations between snapshots, ISO week formatting, and graceful rate-limit handling.

- [ ] **Step 2: Run test to verify failure**
  Run: `python3 tests/test_updater.py`
  Expected: FAIL with "module not found".

- [ ] **Step 3: Implement `scripts/update_skills.py`**
  Implement GitHub REST API fetcher using standard library `urllib.request`, rate limit token support (`GITHUB_TOKEN`), snapshot diffing, and fallback stargazer inspection.

- [ ] **Step 4: Execute updater and run tests**
  Run: `python3 tests/test_updater.py` and `python3 scripts/update_skills.py --dry-run`
  Expected: PASS

- [ ] **Step 5: Generate initial live dataset and first snapshot**
  Run: `python3 scripts/update_skills.py` to create `data/skills.json` and `data/history/2026-W45.json`.

- [ ] **Step 6: Commit**
  Run:
  ```bash
  git add scripts/update_skills.py tests/test_updater.py data/skills.json data/history/
  git commit -m "feat(collector): implement weekly skills updater"
  ```

---

### Task 3: Developer-Centric Frontend (HTML / CSS / JS)

**Files:**
- Create: `index.html`
- Create: `css/style.css`
- Create: `js/app.js`
- Create: `tests/test_frontend.py`

**Interfaces:**
- Consumes: `data/skills.json` and `data/history/*.json`
- Renders: Interactive responsive UI with search, filtering, language toggle (KO/EN), history selector, and sorting.

- [ ] **Step 1: Write automated tests for frontend assets and i18n keys**
  Create `tests/test_frontend.py` verifying HTML structure, CSS mobile media queries, and complete translation key parity in `js/app.js`.

- [ ] **Step 2: Implement `index.html`**
  Write semantically structured HTML layout with header (stats, updated date, locale switch, history dropdown), search/filter toolbar, results counter, data grid/table, and clean footer.

- [ ] **Step 3: Implement `css/style.css`**
  Write clean developer styling: dark-mode palette, Geist/JetBrains monospace typography, table layout for desktop, dense card view for mobile (<640px), badges for categories and `+Δ` weekly stars.

- [ ] **Step 4: Implement `js/app.js`**
  Implement client-side fetch, state management (language, selected week snapshot, search query, category filter, sort order), responsive rendering, and URL/localStorage persistence.

- [ ] **Step 5: Run tests and verify in browser**
  Run: `python3 tests/test_frontend.py`
  Expected: PASS

- [ ] **Step 6: Commit**
  Run:
  ```bash
  git add index.html css/style.css js/app.js tests/test_frontend.py
  git commit -m "feat(ui): build responsive bilingual developer ui"
  ```

---

### Task 4: GitHub Actions Automation & Pages Deployment

**Files:**
- Create: `.github/workflows/weekly-update.yml`
- Create: `.github/workflows/deploy-pages.yml`
- Create: `README.md`

**Interfaces:**
- GitHub Actions triggers: Weekly cron (Monday 00:00 UTC) + manual trigger (`workflow_dispatch`).
- Automatic deployment to GitHub Pages on `main` push.

- [ ] **Step 1: Create `.github/workflows/weekly-update.yml`**
  Configure cron job, checkout, python execution, git commit with user's author/committer settings, and push.

- [ ] **Step 2: Create `.github/workflows/deploy-pages.yml`**
  Configure standard `actions/deploy-pages` with `pages` permissions to serve repository root.

- [ ] **Step 3: Create bilingual `README.md`**
  Write clear Korean & English documentation explaining the platform, weekly update mechanism, how to submit new skills, and local preview.

- [ ] **Step 4: Commit**
  Run:
  ```bash
  git add .github/workflows/ README.md
  git commit -m "ci: add weekly update workflow and pages deploy"
  ```

---

### Task 5: End-to-End Verification & GitHub Push

**Files:**
- Verify entire repository state.

- [ ] **Step 1: Run all test suites**
  Run: `python3 -m unittest discover -s tests -p "test_*.py"`
  Expected: All tests PASS.

- [ ] **Step 2: Verify git author and committer configuration**
  Run: `git log -1 --pretty=fuller` and check author/committer is `Changhyeok Bae <changhyeok.bae@gmail.com>`.

- [ ] **Step 3: Push to remote repository**
  Run: `git push -u origin main`
  Expected: Pushed successfully to `git@github.com:chbaede/ai-skills.git`.
