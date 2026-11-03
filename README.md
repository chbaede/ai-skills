# AI Skills Radar

[![GitHub Pages](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-brightgreen)](https://chbaede.github.io/ai-skills/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Automated Weekly Updates](https://img.shields.io/badge/Updates-Automated%20Weekly-orange)](.github/workflows/weekly-update.yml)

> **Curated directory of top open-source AI agent skills, MCP servers, and tooling.**
>
> 🌐 **Live URL:** [https://chbaede.github.io/ai-skills/](https://chbaede.github.io/ai-skills/)

---

## English

### Overview

**AI Skills Radar** is a developer-focused, high-signal curation platform tracking open-source tooling, Model Context Protocol (MCP) servers, coding assistants, and agent extensions. It provides real-time visibility into the fast-evolving AI agent ecosystem with weekly momentum tracking (+Δ weekly stars) and historical archive snapshots.

### Key Features

- **⚡ Weekly Trending Momentum (+Δ Stars):** Highlights repositories with rapid weekly star velocity alongside total GitHub stars.
- **📜 Historical Snapshots & Archive:** Browse historical snapshots (e.g. `2026-W45`) or track current metrics with zero data loss.
- **🌐 Instant Bilingual Toggle (KO / EN):** Seamless language switching with URL query parameter (`?lang=ko` / `?lang=en`) and local persistence.
- **🎨 Developer Dark Aesthetic:** Clean, typography-first monospace layout optimized for fast scanning, filtering, and sorting.
- **⚡ Zero-Dependency Lightweight Architecture:**
  - Pure Python 3 standard library updater script (`scripts/update_skills.py`).
  - Vanilla JavaScript ES6+ frontend without bulky frameworks.
  - Zero server maintenance — 100% static hosting on GitHub Pages.

### Architecture & Automation

```
ai-skills/
├── index.html                   # Responsive bilingual single-page app
├── css/style.css                # Dark developer CSS design system
├── js/app.js                    # Vanilla ES6+ reactive renderer & filter
├── data/
│   ├── registry.json            # Curated catalog metadata & bilingual descriptions
│   ├── skills.json              # Latest live metrics (stars, weekly delta, open issues)
│   └── history/
│       └── 2026-W45.json        # Archived historical weekly snapshots
├── scripts/
│   └── update_skills.py         # Automated metrics updater (standard library only)
├── .github/workflows/
│   ├── weekly-update.yml        # Weekly automated cron fetch & git commit
│   └── deploy-pages.yml         # GitHub Pages automated deployment
└── tests/                       # Complete unit test suite
```

#### GitHub Actions Automation
- **Weekly Updater Workflow (`.github/workflows/weekly-update.yml`):**
  - Runs automatically every Monday at 00:00 UTC (`0 0 * * 1`) or manually via `workflow_dispatch`.
  - Executes `python3 scripts/update_skills.py` with GitHub API rate-limit resilience.
  - Automatically creates a new ISO week snapshot in `data/history/` and updates `data/skills.json`.
  - Commits and pushes changes directly back to `main`.
- **Pages Deployment Workflow (`.github/workflows/deploy-pages.yml`):**
  - Triggers on every push to `main` affecting web assets.
  - Deploys static files to GitHub Pages via official `actions/deploy-pages`.

### Local Development & Preview

Run a lightweight static HTTP server from the project root:

```bash
# Start local server
python3 -m http.server 8000

# Open in your browser
open http://localhost:8000
# or test Korean locale directly
open http://localhost:8000/?lang=ko
```

### Running Manual Updates

You can update metrics manually at any time:

```bash
# Dry-run update (fetches and displays stats without writing files)
python3 scripts/update_skills.py --dry-run

# Live update (optionally set GITHUB_TOKEN to avoid 60 req/hr rate limits)
export GITHUB_TOKEN="ghp_your_token_here"
python3 scripts/update_skills.py
```

### Running the Test Suite

The project includes an end-to-end unit test suite validating the registry schema, the updater pipeline, frontend DOM rendering logic, and CI workflows:

```bash
python3 -m unittest discover -s tests
```

### How to Propose a New Skill

Contributions to add high-quality open-source AI tools are warmly welcomed!

1. Fork this repository and create your feature branch:
   ```bash
   git checkout -b feat/add-my-tool
   ```
2. Add your repository entry into [`data/registry.json`](data/registry.json) following the schema:
   ```json
   {
     "id": "my-tool",
     "repo": "owner/my-tool",
     "name": "My Tool",
     "category": "Agent Tool",
     "url": "https://github.com/owner/my-tool",
     "tags": ["agent", "tool"],
     "description": {
       "en": "Concise English description of the tool.",
       "ko": "도구에 대한 명확하고 간결한 한국어 설명."
     }
   }
   ```
   *Allowed Categories:* `MCP Server`, `Agent Tool`, `Coding Assistant`, `Agent Plugin`, `Benchmark / Eval`.
3. Validate your changes against the test suite:
   ```bash
   python3 -m unittest discover -s tests
   ```
4. Open a Pull Request!

---

## 한국어

### 소개

**AI Skills Radar**는 전 세계 오픈소스 AI 에이전트 도구, Model Context Protocol (MCP) 서버, 코딩 어시스턴트, 에이전트 플러그인 생태계를 한눈에 파악할 수 있는 개발자 중심 큐레이션 플랫폼입니다.

주간 스타 성장량(+Δ Weekly Stars)을 추적하여 최근 가장 주목받는 기술 트렌드를 식별하고, 주간 스냅샷 아카이브를 통해 생태계의 성장 과정을 영구히 보존합니다.

### 주요 기능

- **⚡ 주간 트렌딩 모멘텀 (+Δ 스타):** 누적 스타 수와 함께 최근 7일간의 스타 증가량을 계산하여 급부상 중인 도구를 최상위에 노출합니다.
- **📜 과거 스냅샷 아카이브:** 과거 특정 주차(예: `2026-W45`)의 데이터를 즉시 조회하고 시간에 따른 성장을 비교 분석할 수 있습니다.
- **🌐 원클릭 한국어/영어 전환:** 상단 언어 토글 버튼 및 URL 쿼리 파라미터(`?lang=ko` / `?lang=en`)를 지원하며 브라우저 설정을 자동 기억합니다.
- **🎨 개발자 친화적 다크 모드 UI:** 불필요한 장식을 배제하고 모노스페이스 타이포그래피와 컴팩트한 그리드로 구성되어 빠른 탐색과 검색이 가능합니다.
- **⚡ 의존성 없는 가벼운 아키텍처:**
  - 파이썬 표준 라이브러리만을 사용하는 데이터 수집 스크립트 (`scripts/update_skills.py`).
  - 외부 프레임워크 없는 순수 Vanilla JS (ES6+) 프론트엔드.
  - 유지보수 비용 없는 100% GitHub Pages 정적 호스팅.

### 자동화 및 아키텍처

- **주간 데이터 갱신 (`.github/workflows/weekly-update.yml`):**
  - 매주 월요일 00:00 UTC (`0 0 * * 1`) 또는 수동 실행(`workflow_dispatch`)으로 트리거됩니다.
  - GitHub REST API를 통해 저장소 스타 수, 오픈 이슈 수를 수집하고 직전 주차와의 차이를 계산합니다.
  - `data/history/YYYY-Www.json` 스냅샷을 생성하고 `data/skills.json`을 갱신한 뒤 자동으로 `main` 브랜치에 커밋 및 푸시합니다.
- **GitHub Pages 자동 배포 (`.github/workflows/deploy-pages.yml`):**
  - 웹 자산 변경 시 자동으로 GitHub Pages에 최신 정적 사이트를 배포합니다.

### 로컬 실행 방법

별도의 빌드 과정 없이 로컬 웹 서버로 바로 확인하실 수 있습니다:

```bash
# 로컬 웹 서버 구동
python3 -m http.server 8000

# 브라우저에서 접속
open http://localhost:8000
# 한국어 버전 바로 열기
open http://localhost:8000/?lang=ko
```

### 수동 데이터 업데이트 실행

```bash
# 드라이 런 (파일 저장 없이 콘솔 출력)
python3 scripts/update_skills.py --dry-run

# 실제 업데이트 (API 호출 제한 방지를 위해 GITHUB_TOKEN 설정 권장)
export GITHUB_TOKEN="ghp_your_token_here"
python3 scripts/update_skills.py
```

### 테스트 실행

레지스트리 무결성, 주간 수집기 파이프라인, 프론트엔드 DOM 렌더링, CI 워크플로우를 검증하는 테스트 스위트입니다:

```bash
python3 -m unittest discover -s tests
```

### 신규 스킬 제안 및 기여 방법

우수한 오픈소스 AI 도구의 추가 기여를 언제나 환영합니다!

1. 저장소를 Fork하고 기능 브랜치를 생성합니다:
   ```bash
   git checkout -b feat/add-my-tool
   ```
2. [`data/registry.json`](data/registry.json) 파일에 새로운 도구 항목을 추가합니다:
   ```json
   {
     "id": "my-tool",
     "repo": "owner/my-tool",
     "name": "도구 이름",
     "category": "Agent Tool",
     "url": "https://github.com/owner/my-tool",
     "tags": ["agent", "tool"],
     "description": {
       "en": "Concise English description of the tool.",
       "ko": "도구에 대한 명확하고 간결한 한국어 설명."
     }
   }
   ```
   *지원 카테고리:* `MCP Server`, `Agent Tool`, `Coding Assistant`, `Agent Plugin`, `Benchmark / Eval`.
3. 테스트를 실행하여 데이터 정합성을 확인합니다:
   ```bash
   python3 -m unittest discover -s tests
   ```
4. Pull Request를 제출해 주세요!

---

## License

[MIT License](LICENSE)
