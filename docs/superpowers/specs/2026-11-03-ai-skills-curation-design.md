# AI Skills Curation Platform Design Document

**Date:** 2026-11-03  
**Repository:** [chbaede/ai-skills](https://github.com/chbaede/ai-skills)  
**Author/Committer:** Changhyeok Bae <changhyeok.bae@gmail.com>

---

## 1. Intent & Purpose

Provide a curated, developer-focused directory of the most useful **AI Skills, Agent Tools, and MCP (Model Context Protocol) Servers**, filtered by total GitHub stars, weekly star growth (Δ 7 days), and community engagement.

The goal is to cut through the noise of generic AI directories with an ultra-clean, high-readability developer UX (Hacker News / Linear aesthetic), fully responsive across desktop and mobile, with bilingual support (Korean & English), weekly automated updates, and historical snapshot tracking on GitHub Pages.

---

## 2. Goals, Non-Goals & Anti-Goals

### Goals
- **Curated Quality over Quantity**: Track only genuinely high-utility, actively maintained AI skills, tools, and MCP servers (not general ML frameworks).
- **Dual-Metric Ranking**: Showcase both total authority (Total Stars) and trending velocity (+Stars this week).
- **Developer-Native UI/UX**: Clean typography, high contrast, compact table/card hybrid, zero fluff, fast loading (<50KB).
- **Mobile Responsive**: Flawless layout without broken tables or overflowing tags on smartphones and tablets.
- **Bilingual Interface**: Full Korean (KO) and English (EN) toggle with instant switching and URL/localStorage persistence.
- **Historical Snapshots**: Archive weekly state into `data/history/YYYY-WW.json`, with a snapshot switcher on the UI.
- **Last Updated Badge**: Prominently display the exact last update timestamp.
- **Automated & On-Demand Updating**: Python updater script callable locally or scheduled via GitHub Actions cron, publishing to GitHub Pages.

### Non-Goals
- Tracking all machine learning libraries (e.g., PyTorch, Transformers, TensorFlow) or generic wrapper apps.
- Complex user accounts, backend databases, or dynamic SSR servers.

### Anti-Goals
- "AI-slop" design: No unnecessary glowing gradients, floating 3D spheres, animated marketing gimmicks, or low-density card grids.

---

## 3. Constraints & Commit Standards

- **Git Author & Committer**: `Changhyeok Bae <changhyeok.bae@gmail.com>`
- **Git Commit Convention**:
  - Title: 50 characters or fewer.
  - Body: Hard-wrapped at 72 characters per line.
- **Hosting**: GitHub Pages via GitHub Actions (`actions/deploy-pages`).

---

## 4. Approaches & Architecture Tradeoffs

### Chosen Approach: Zero-Dependency Static Web + Python Collector
- **Structure**: Native HTML5, modern CSS with CSS variables, vanilla ES6 JavaScript.
- **Data storage**: Flat JSON files (`data/registry.json`, `data/skills.json`, `data/history/YYYY-WW.json`).
- **Updater**: Standalone Python script (`scripts/update_skills.py`) utilizing GitHub API.
- **Why chosen**: Zero npm build dependencies, cannot break over time due to package deprecation, loads in single-digit milliseconds, perfectly auditable.

*(Alternative considered & discarded: Astro/Next.js SSG — discarded due to unnecessary dependency churn, heavier bundle sizes, and complexity for a data-driven static catalog).*

---

## 5. System Components & Settled Engineering Decisions

### 5.1 Architecture & Granularity (Settled Decision)
- **1:1 Repository Mapping**: Each tracked skill in `registry.json` strictly maps 1:1 to an independent GitHub repository (`owner/repo`).
- Monorepos (such as `modelcontextprotocol/servers`) are tracked as unified collections to avoid duplicating identical star counts across multiple sub-items. Sub-capabilities (e.g. Postgres, Filesystem, Memory, Git tools) are highlighted in the curated tags and descriptions.
- Standalone popular MCP tools (e.g. Playwright MCP, SQLite MCP) with their own repositories are tracked as individual entries.

### 5.2 Bilingual Content Management (Settled Decision)
- `data/registry.json` is the **permanent source of truth** for human-curated descriptions in both English (`en`) and Korean (`ko`), as well as curated category tags.
- The Python updater script **only** updates dynamic metrics (`stars`, `weekly_stars`, `open_issues`, `updated_at`). It does not overwrite human-curated descriptions with raw GitHub strings, eliminating translation drift.

### 5.3 Weekly Delta Calculation & Cold-Start Strategy (Settled Decision)
- **Snapshot Diffing**: `weekly_stars = current_stars - prior_snapshot_stars`.
- **Archive System**: Snapshots are saved immutably as `data/history/YYYY-WW.json` (ISO week format).
- **Cold-Start (Day 1 / New Repos)**:
  - If a prior snapshot exists in `data/history/`, the delta is calculated directly.
  - If no prior snapshot exists (Day 1 launch), the collector uses GitHub's Stargazers API with timestamp headers (`application/vnd.github.v3.star+json`) to inspect recent stargazers within the past 7 days, providing real trending numbers immediately on launch.
- **On-Demand vs. Weekly Runs**: On-demand updates refresh `data/skills.json` and update the current week's snapshot (`YYYY-WW.json`), keeping the history aligned per calendar week without fracturing.

### 5.4 Seed Repositories Disambiguation (Settled Decision)
Validated and curated initial repository list:
1. `modelcontextprotocol/servers` (MCP Official Servers: Postgres, Memory, Git, Filesystem, etc.)
2. `obra/superpowers` (Superpowers agent skills framework & tools)
3. `anthropics/claude-quickstarts` (Anthropic Computer Use demo & agent toolkits)
4. `openinterpreter/open-interpreter` (Open Interpreter local code & tool execution)
5. `cline/cline` (Autonomous coding agent with extensive MCP tool ecosystem)
6. `Roo-Code/Roo-Code` (AI coding assistant fork with multi-mode agent tools & MCP)
7. `Aider-AI/aider` (AI terminal pair programming & repository-level tool editing)
8. `princeton-nlp/SWE-agent` (Software engineering benchmark agent tools)
9. `microsoft/semantic-kernel` (Semantic Kernel agent plugins and connectors)
10. `executeautomation/mcp-playwright` (Playwright browser automation MCP skill)
11. `mark3labs/mcp-go` (Go-based MCP tool & server toolkit)
12. `github/copilot-cli` (GitHub Copilot CLI command assistant)


### 5.1 Data Structure & Schemas
- `data/registry.json`: List of curated repositories to track (repository name, category, EN/KO descriptions, primary tags, documentation links).
- `data/skills.json`: Generated live dataset with current metadata:
  ```json
  {
    "updated_at": "2026-11-03T10:00:00Z",
    "week": "2026-W45",
    "total_count": 25,
    "skills": [
      {
        "id": "modelcontextprotocol-servers",
        "repo": "modelcontextprotocol/servers",
        "name": "MCP Official Servers",
        "category": "MCP Server",
        "stars": 32150,
        "weekly_stars": 1420,
        "open_issues": 85,
        "description": {
          "en": "Official Model Context Protocol reference servers...",
          "ko": "공식 모델 컨텍스트 프로토콜(MCP) 참조 서버 모음..."
        },
        "url": "https://github.com/modelcontextprotocol/servers",
        "tags": ["mcp", "agent-tool", "official"]
      }
    ]
  }
  ```
- `data/history/YYYY-WW.json`: Immutable archive copy saved during each weekly run.

### 5.2 Python Collector (`scripts/update_skills.py`)
- Reads `data/registry.json`.
- Fetches GitHub REST / GraphQL API for stars, issues, description, and stargazer timestamps or calculates weekly delta against the prior snapshot.
- Writes to `data/skills.json` and copies to `data/history/{year}-W{week}.json`.
- Supports `GITHUB_TOKEN` environment variable if present.

### 5.3 Frontend Interface
- **Layout**: Header with title, live stats summary (Total skills tracked, Last updated timestamp), language switch (`EN` / `KO`), and history dropdown (`Live (Latest)` vs archived weeks).
- **Controls**:
  - Search input (instant fuzzy filtering by title, description, tags).
  - Category filters (`All`, `MCP Server`, `Agent Tool`, `Workflow Skill`, `Coding Assistant`).
  - Sort toggles (`Stars (Total)`, `Trending (+Δ Weekly)`, `Issues/Activity`).
- **Mobile Adaptations**: Responsive CSS Grid / Flexbox; collapses wide table columns into clean, dense cards with monospace metric badges on mobile viewports (<640px).

### 5.4 CI/CD & GitHub Pages
- `.github/workflows/weekly-update.yml`:
  - Triggers: Scheduled cron (every Monday at 00:00 UTC) + `workflow_dispatch`.
  - Action: Runs python updater, commits updated files with prescribed commit convention, pushes to `main`.
- `.github/workflows/deploy-pages.yml`:
  - Triggers on push to `main`.
  - Deploys repository root directly to GitHub Pages.

---

## 6. Curated Initial Seed List
Focused strictly on top-tier AI Agent Skills, MCP servers, and AI coding assistant tools:
1. `modelcontextprotocol/servers` (Official MCP servers collection)
2. `anthropics/anthropic-tools` / anthropic computer use tools
3. `superpowers/skills` / agent skills repository
4. `openinterpreter/open-interpreter` (Local code execution agent skill)
5. `cline/cline` / `Roo-Code/Roo-Code` MCP skill ecosystems
6. `microsoft/semantic-kernel` (Agent plugins & skills)
7. `princeton-nlp/SWE-agent` (Software engineering benchmark agent skill)
8. `Aider-AI/aider` (AI pair programming terminal skill)
9. Additional top verified MCP servers (PostgreSQL, Filesystem, Memory, Web Fetch, Git, Slack, Brave Search).

