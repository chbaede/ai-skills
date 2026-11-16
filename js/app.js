/**
 * AI Skills Radar - Frontend Application
 * Zero external runtime dependencies (Native ES6+).
 */

const TRANSLATIONS = {
  en: {
    siteTitle: "AI Skills Radar",
    siteTagline: "Curated directory of top open-source AI agent skills, MCP servers, and tooling.",
    skillsCountSuffix: "skills",
    lastUpdatedPrefix: "Updated:",
    historyLabel: "Snapshot:",
    historyLatest: "Latest (Live)",
    searchPlaceholder: "Search by skill name, description, repo, or tags...",
    allCategories: "All",
    categoryMcpServer: "MCP Server",
    categoryAgentTool: "Agent Tool",
    categoryCodingAssistant: "Coding Assistant",
    categoryAgentPlugin: "Agent Plugin",
    categoryBenchmarkEval: "Benchmark / Eval",
    sortLabel: "Sort by:",
    sortTrending: "Trending (+Δ Weekly Stars)",
    sortTrendingDesc: "Trending (+Δ Weekly Stars ↓)",
    sortTrendingAsc: "Trending (+Δ Weekly Stars ↑)",
    sortStars: "Total Stars",
    sortStarsDesc: "Total Stars (High to Low ↓)",
    sortStarsAsc: "Total Stars (Low to High ↑)",
    sortCategoryAsc: "Category (A → Z, Grouped)",
    sortCategoryDesc: "Category (Z → A)",
    sortIssues: "Open Issues",
    sortIssuesDesc: "Open Issues (High to Low ↓)",
    sortIssuesAsc: "Open Issues (Low to High ↑)",
    sortNameAsc: "Skill Name (A → Z)",
    sortNameDesc: "Skill Name (Z → A)",
    filterByCategoryTip: "Click to filter by this category",
    showingResults: "Showing {count} of {total} skills",
    colName: "Skill / Tool",
    colCategory: "Category",
    colWeeklyDelta: "Weekly Trend",
    colStars: "Stars",
    colIssues: "Issues",
    colTags: "Tags",
    starsLabel: "stars",
    issuesLabel: "issues",
    weeklyDeltaLabel: "/wk",
    viewOnGithub: "View on GitHub",
    emptyTitle: "No skills found",
    emptyDescription: "Try adjusting your search query or filters.",
    footerCurated: "Curated open-source intelligence for AI agent engineers.",
    footerUpdatedWeekly: "Metrics refreshed weekly via GitHub API.",
    mainHub: "Main Hub",
    themeLight: "Light Mode",
    themeDark: "Dark Mode",
    curatorShelfTitle: "Recommended & In-Use",
    curatorShelfSubtitle: "Core tools and workflows actively used and personally recommended by the author.",
    filterCuratorPicks: "★ Curator's Picks",
    badgeInUse: "★ In Use",
    badgeCuratorPick: "★ Curator's Pick",
    adLabel: "Advertisement",
  },
  ko: {
    siteTitle: "AI Skills Radar",
    siteTagline: "최고 수준의 오픈소스 AI 에이전트 스킬, MCP 서버 및 도구 큐레이션 디렉토리입니다.",
    skillsCountSuffix: "개 스킬",
    lastUpdatedPrefix: "업데이트:",
    historyLabel: "스냅샷:",
    historyLatest: "최신 (라이브)",
    searchPlaceholder: "스킬 이름, 설명, 저장소 또는 태그로 검색...",
    allCategories: "전체",
    categoryMcpServer: "MCP Server",
    categoryAgentTool: "Agent Tool",
    categoryCodingAssistant: "Coding Assistant",
    categoryAgentPlugin: "Agent Plugin",
    categoryBenchmarkEval: "Benchmark / Eval",
    sortLabel: "정렬 기준:",
    sortTrending: "트렌딩 (+Δ 주간 스타)",
    sortTrendingDesc: "주간 트렌딩 높은순 (+Δ ↓)",
    sortTrendingAsc: "주간 트렌딩 낮은순 (+Δ ↑)",
    sortStars: "총 스타 수",
    sortStarsDesc: "스타 많은순 (★ 높은순 ↓)",
    sortStarsAsc: "스타 적은순 (★ 낮은순 ↑)",
    sortCategoryAsc: "카테고리순 (같은것 묶기 A→Z)",
    sortCategoryDesc: "카테고리 역순 (Z→A)",
    sortIssues: "오픈 이슈",
    sortIssuesDesc: "이슈 많은순 (이슈 높은순 ↓)",
    sortIssuesAsc: "이슈 적은순 (이슈 낮은순 ↑)",
    sortNameAsc: "이름순 (A → Z)",
    sortNameDesc: "이름 역순 (Z → A)",
    filterByCategoryTip: "클릭 시 이 카테고리만 필터링",
    showingResults: "{total}개 중 {count}개 표시",
    colName: "스킬 / 도구",
    colCategory: "카테고리",
    colWeeklyDelta: "주간 트렌드",
    colStars: "스타 수",
    colIssues: "이슈 수",
    colTags: "태그",
    starsLabel: "스타",
    issuesLabel: "이슈",
    weeklyDeltaLabel: "/주",
    viewOnGithub: "GitHub에서 보기",
    emptyTitle: "일치하는 스킬이 없습니다",
    emptyDescription: "검색어나 필터 조건을 변경해 보세요.",
    footerCurated: "AI 에이전트 엔지니어를 위해 엄선된 오픈소스 인텔리전스입니다.",
    footerUpdatedWeekly: "GitHub API를 통해 매주 메트릭이 업데이트됩니다.",
    mainHub: "메인 허브",
    themeLight: "라이트 모드",
    themeDark: "다크 모드",
    curatorShelfTitle: "큐레이터 실사용 추천",
    curatorShelfSubtitle: "작성자가 실제 업무에서 직접 사용하며 검증한 핵심 AI 스킬 및 도구입니다.",
    filterCuratorPicks: "★ 큐레이터 추천",
    badgeInUse: "★ 실사용",
    badgeCuratorPick: "★ 큐레이터 추천",
    adLabel: "스폰서 광고",
  }
};

const KNOWN_SNAPSHOTS = ["2026-W45"];

const state = {
  lang: "en",
  theme: "dark",
  skillsData: null,
  rawSkills: [],
  selectedCategory: "all",
  searchQuery: "",
  sortBy: "trending",
  currentSnapshot: "latest",
};

// ============================================================================
// Utilities
// ============================================================================

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatNumber(num) {
  if (num === null || num === undefined || isNaN(num)) return "0";
  return Number(num).toLocaleString("en-US");
}

function formatTimestamp(isoStr) {
  if (!isoStr) return "";
  try {
    const d = new Date(isoStr);
    if (isNaN(d.getTime())) return isoStr;
    const year = d.getUTCFullYear();
    const month = String(d.getUTCMonth() + 1).padStart(2, "0");
    const day = String(d.getUTCDate()).padStart(2, "0");
    const hours = String(d.getUTCHours()).padStart(2, "0");
    const minutes = String(d.getUTCMinutes()).padStart(2, "0");
    return `${year}-${month}-${day} ${hours}:${minutes} UTC`;
  } catch (e) {
    return isoStr;
  }
}

function getCategoryBadgeClass(category) {
  const map = {
    "MCP Server": "badge-cat-mcp-server",
    "Agent Tool": "badge-cat-agent-tool",
    "Coding Assistant": "badge-cat-coding-assistant",
    "Agent Plugin": "badge-cat-agent-plugin",
    "Benchmark / Eval": "badge-cat-benchmark-eval",
  };
  return map[category] || "badge-cat-mcp-server";
}

// ============================================================================
// Theme Management (Dark / Light)
// ============================================================================

function initTheme() {
  let stored = null;
  try {
    stored = localStorage.getItem("ai_skills_theme");
  } catch (err) {
    // Ignore storage errors in restricted contexts
  }
  if (stored === "light" || stored === "dark") {
    state.theme = stored;
  } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches) {
    state.theme = "light";
  } else {
    state.theme = "dark";
  }
  applyTheme(state.theme);
}

function setTheme(theme) {
  if (theme !== "light" && theme !== "dark") return;
  state.theme = theme;
  try {
    localStorage.setItem("ai_skills_theme", theme);
  } catch (err) {
    // Ignore storage errors
  }
  applyTheme(theme);
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  updateThemeToggleUI();
}

function updateThemeToggleUI() {
  const toggleBtn = document.getElementById("theme-toggle");
  if (!toggleBtn) return;
  const isLight = state.theme === "light";
  const dict = TRANSLATIONS[state.lang] || TRANSLATIONS.en;
  const nextThemeLabel = isLight ? dict.themeDark : dict.themeLight;
  toggleBtn.setAttribute("aria-label", nextThemeLabel);
  toggleBtn.title = nextThemeLabel;
  toggleBtn.innerHTML = isLight
    ? `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg><span>${nextThemeLabel}</span>`
    : `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg><span>${nextThemeLabel}</span>`;
}

// ============================================================================
// Language & i18n
// ============================================================================

function initLanguage() {
  const params = new URLSearchParams(window.location.search);
  const urlLang = params.get("lang");
  if (urlLang === "ko" || urlLang === "en") {
    state.lang = urlLang;
  } else {
    let stored = null;
    try {
      stored = localStorage.getItem("ai_skills_lang");
    } catch (err) {
      // Ignore storage errors in restricted contexts (e.g. file://)
    }
    if (stored === "ko" || stored === "en") {
      state.lang = stored;
    } else if (navigator.language && navigator.language.toLowerCase().startsWith("ko")) {
      state.lang = "ko";
    } else {
      state.lang = "en";
    }
  }
  applyLanguage(state.lang);
}

function setLanguage(lang) {
  if (lang !== "en" && lang !== "ko") return;
  state.lang = lang;
  try {
    localStorage.setItem("ai_skills_lang", lang);
  } catch (err) {
    // Ignore storage errors in restricted contexts
  }

  // Sync URL query param
  try {
    const url = new URL(window.location);
    url.searchParams.set("lang", lang);
    window.history.replaceState({}, "", url);
  } catch (err) {
    // Ignore history replaceState restrictions (e.g. file:// origins)
  }

  applyLanguage(lang);
  renderCuratorShelf();
  renderSkills();
}

function applyLanguage(lang) {
  document.documentElement.lang = lang;
  const dict = TRANSLATIONS[lang] || TRANSLATIONS.en;

  // Toggle active button state
  const btnEn = document.getElementById("lang-en");
  const btnKo = document.getElementById("lang-ko");
  if (btnEn && btnKo) {
    btnEn.classList.toggle("active", lang === "en");
    btnKo.classList.toggle("active", lang === "ko");
  }

  // Update text elements with data-i18n
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) {
      el.textContent = dict[key];
    }
  });

  // Update attribute elements (e.g. placeholder)
  document.querySelectorAll("[data-i18n-attr]").forEach((el) => {
    const attrSpec = el.getAttribute("data-i18n-attr");
    const [attr, key] = attrSpec.split(":");
    if (attr && key && dict[key]) {
      el.setAttribute(attr, dict[key]);
    }
  });

  // Update last-updated prefix if already present
  if (state.skillsData && state.skillsData.updated_at) {
    updateMetaInfo(state.skillsData);
  }

  // Update theme toggle label for current language
  updateThemeToggleUI();
}

// ============================================================================
// Data Fetching & Snapshot History
// ============================================================================

async function fetchSnapshot(snapshot) {
  const url = snapshot === "latest" ? "data/skills.json" : `data/history/${snapshot}.json`;
  try {
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`Failed to load ${url} (${res.status})`);
    }
    const data = await res.json();
    state.skillsData = data;
    state.rawSkills = data.skills || [];
    state.currentSnapshot = snapshot;

    updateMetaInfo(data);
    updateHistoryOptions(data.available_snapshots, data.week);
    renderCuratorShelf();
    renderSkills();
  } catch (err) {
    console.error("Error loading snapshot:", err);
  }
}

function updateMetaInfo(data) {
  const totalCountEl = document.getElementById("stats-total-count");
  if (totalCountEl) {
    totalCountEl.textContent = data.skills ? data.skills.length : data.total_count || "0";
  }

  const updatedValEl = document.getElementById("last-updated-val");
  if (updatedValEl && data.updated_at) {
    updatedValEl.textContent = formatTimestamp(data.updated_at);
  }
}

function updateHistoryOptions(availableSnapshots, currentWeek) {
  const select = document.getElementById("history-select");
  if (!select) return;

  let snapshotsList = [];
  if (Array.isArray(availableSnapshots) && availableSnapshots.length > 0) {
    snapshotsList = availableSnapshots;
  } else if (typeof availableSnapshots === "string") {
    currentWeek = availableSnapshots;
    snapshotsList = KNOWN_SNAPSHOTS;
  } else {
    snapshotsList = KNOWN_SNAPSHOTS;
  }

  const snapshots = new Set(snapshotsList);
  if (currentWeek && typeof currentWeek === "string") {
    snapshots.add(currentWeek);
  }

  const existingVals = Array.from(select.options || []).map((o) => o.value);
  const sorted = Array.from(snapshots).sort().reverse();
  sorted.forEach((snap) => {
    if (!existingVals.includes(snap)) {
      const opt = document.createElement("option");
      opt.value = snap;
      opt.textContent = snap;
      select.appendChild(opt);
      if (select.options && Array.isArray(select.options)) {
        select.options.push(opt);
      }
    }
  });
}

// ============================================================================
// Filter, Search, Sort & Rendering
// ============================================================================

function getFilteredAndSortedSkills() {
  let list = [...state.rawSkills];

  // 1. Category Filter
  if (state.selectedCategory === "featured") {
    list = list.filter((s) => Boolean(s.featured));
  } else if (state.selectedCategory !== "all") {
    list = list.filter((s) => s.category === state.selectedCategory);
  }

  // 2. Search Query Filter
  if (state.searchQuery) {
    const q = state.searchQuery.toLowerCase();
    list = list.filter((s) => {
      const nameMatch = s.name && s.name.toLowerCase().includes(q);
      const repoMatch = s.repo && s.repo.toLowerCase().includes(q);
      const descEn = s.description && s.description.en && s.description.en.toLowerCase().includes(q);
      const descKo = s.description && s.description.ko && s.description.ko.toLowerCase().includes(q);
      const tagMatch = s.tags && s.tags.some((t) => t.toLowerCase().includes(q));
      return nameMatch || repoMatch || descEn || descKo || tagMatch;
    });
  }

  // 3. Sorting
  list.sort((a, b) => {
    const mode = state.sortBy || "trending";

    // Weekly Trend (+Δ Weekly Stars)
    if (mode === "trending" || mode === "trending-desc") {
      const deltaA = a.weekly_stars !== undefined && a.weekly_stars !== null ? a.weekly_stars : (a.weekly_delta || 0);
      const deltaB = b.weekly_stars !== undefined && b.weekly_stars !== null ? b.weekly_stars : (b.weekly_delta || 0);
      if (deltaB !== deltaA) return deltaB - deltaA;
      return (b.stars || 0) - (a.stars || 0);
    }
    if (mode === "trending-asc") {
      const deltaA = a.weekly_stars !== undefined && a.weekly_stars !== null ? a.weekly_stars : (a.weekly_delta || 0);
      const deltaB = b.weekly_stars !== undefined && b.weekly_stars !== null ? b.weekly_stars : (b.weekly_delta || 0);
      if (deltaA !== deltaB) return deltaA - deltaB;
      return (a.stars || 0) - (b.stars || 0);
    }

    // Total Stars
    if (mode === "stars" || mode === "stars-desc") {
      return (b.stars || 0) - (a.stars || 0);
    }
    if (mode === "stars-asc") {
      return (a.stars || 0) - (b.stars || 0);
    }

    // Category: Group identical categories together, sub-sort by stars descending
    if (mode === "category" || mode === "category-asc") {
      const catA = (a.category || "").toLowerCase();
      const catB = (b.category || "").toLowerCase();
      if (catA !== catB) return catA.localeCompare(catB);
      return (b.stars || 0) - (a.stars || 0);
    }
    if (mode === "category-desc") {
      const catA = (a.category || "").toLowerCase();
      const catB = (b.category || "").toLowerCase();
      if (catA !== catB) return catB.localeCompare(catA);
      return (b.stars || 0) - (a.stars || 0);
    }

    // Open Issues
    if (mode === "issues" || mode === "issues-desc") {
      return (b.open_issues || 0) - (a.open_issues || 0);
    }
    if (mode === "issues-asc") {
      return (a.open_issues || 0) - (b.open_issues || 0);
    }

    // Skill Name
    if (mode === "name" || mode === "name-asc") {
      const nameA = (a.name || "").toLowerCase();
      const nameB = (b.name || "").toLowerCase();
      return nameA.localeCompare(nameB);
    }
    if (mode === "name-desc") {
      const nameA = (a.name || "").toLowerCase();
      const nameB = (b.name || "").toLowerCase();
      return nameB.localeCompare(nameA);
    }

    return 0;
  });

  return list;
}

function renderCuratorShelf() {
  const container = document.getElementById("curator-cards");
  if (!container) return;
  const dict = TRANSLATIONS[state.lang] || TRANSLATIONS.en;
  const featuredSkills = state.rawSkills.filter((s) => Boolean(s.featured));

  if (!featuredSkills.length) {
    const shelf = document.getElementById("curator-shelf");
    if (shelf) shelf.style.display = "none";
    return;
  }

  const shelf = document.getElementById("curator-shelf");
  if (shelf) shelf.style.display = "";

  const html = featuredSkills
    .map((skill) => {
      const desc =
        (skill.description && skill.description[state.lang]) ||
        (skill.description && skill.description.en) ||
        "";
      const catBadgeClass = getCategoryBadgeClass(skill.category);
      const delta = skill.weekly_stars !== undefined && skill.weekly_stars !== null ? skill.weekly_stars : 0;
      const tagsHtml = (skill.tags || [])
        .slice(0, 3)
        .map((t) => `<span class="tag-pill">#${escapeHtml(t)}</span>`)
        .join(" ");

      return `
        <div class="curator-card">
          <div class="curator-card-top">
            <div class="curator-card-name-group">
              <a href="${escapeHtml(skill.url)}" target="_blank" rel="noopener noreferrer" class="curator-card-title">
                ${escapeHtml(skill.name)}
              </a>
              <span class="curator-card-repo">${escapeHtml(skill.repo)}</span>
            </div>
            <div class="curator-card-badges">
              <span class="badge-in-use">${escapeHtml(dict.badgeInUse)}</span>
              <span class="badge ${catBadgeClass} badge-clickable" data-filter-category="${escapeHtml(skill.category)}" title="${escapeHtml(dict.filterByCategoryTip)}">${escapeHtml(skill.category)}</span>
            </div>
          </div>
          <p class="curator-card-desc">${escapeHtml(desc)}</p>
          <div class="curator-card-footer">
            <div class="curator-card-stats">
              <span><span class="stars-icon">★</span>${formatNumber(skill.stars)}</span>
              <span class="badge badge-delta"><span class="delta-symbol">+Δ</span> ${formatNumber(delta)} ${dict.weeklyDeltaLabel}</span>
            </div>
            <div class="card-tags">${tagsHtml}</div>
          </div>
        </div>
      `;
    })
    .join("");

  container.innerHTML = html;
}

function renderSkills() {
  const skills = getFilteredAndSortedSkills();
  const totalRaw = state.rawSkills.length;
  const count = skills.length;
  const dict = TRANSLATIONS[state.lang] || TRANSLATIONS.en;

  // Results count
  const resultsCountEl = document.getElementById("results-count");
  if (resultsCountEl) {
    const template = dict.showingResults || "Showing {count} of {total} skills";
    resultsCountEl.textContent = template
      .replace("{count}", count)
      .replace("{total}", totalRaw);
  }

  const tableBody = document.getElementById("skills-tbody");
  const cardsContainer = document.getElementById("skills-cards");
  const emptyState = document.getElementById("empty-state");
  const table = document.getElementById("skills-table");

  if (count === 0) {
    if (table) table.style.display = "none";
    if (cardsContainer) cardsContainer.style.display = "none";
    if (emptyState) emptyState.style.display = "block";
    return;
  }

  if (table) table.style.display = "";
  if (cardsContainer) cardsContainer.style.display = "";
  if (emptyState) emptyState.style.display = "none";

  // Render Desktop Table Rows
  if (tableBody) {
    tableBody.innerHTML = skills.map((skill) => renderTableRow(skill)).join("");
  }

  // Render Mobile Cards
  if (cardsContainer) {
    cardsContainer.innerHTML = skills.map((skill) => renderCard(skill)).join("");
  }

  // Update Table Header Sort Indicators
  updateTableHeaderSortIndicators();
}

function updateTableHeaderSortIndicators() {
  const table = document.getElementById("skills-table");
  if (!table || typeof table.querySelectorAll !== "function") return;

  const currentSort = state.sortBy || "trending";
  const headers = table.querySelectorAll("th.th-sortable");
  if (!headers || !headers.length) return;

  headers.forEach((th) => {
    const key = th.getAttribute("data-sort-key");
    const icon = th.querySelector(".sort-icon");
    if (!key || !icon) return;

    let isAsc = false;
    let isDesc = false;

    if (key === "trending") {
      if (currentSort === "trending" || currentSort === "trending-desc") isDesc = true;
      else if (currentSort === "trending-asc") isAsc = true;
    } else if (key === "stars") {
      if (currentSort === "stars" || currentSort === "stars-desc") isDesc = true;
      else if (currentSort === "stars-asc") isAsc = true;
    } else if (key === "category") {
      if (currentSort === "category" || currentSort === "category-asc") isAsc = true;
      else if (currentSort === "category-desc") isDesc = true;
    } else if (key === "issues") {
      if (currentSort === "issues" || currentSort === "issues-desc") isDesc = true;
      else if (currentSort === "issues-asc") isAsc = true;
    } else if (key === "name") {
      if (currentSort === "name" || currentSort === "name-asc") isAsc = true;
      else if (currentSort === "name-desc") isDesc = true;
    }

    if (isAsc) {
      th.setAttribute("aria-sort", "ascending");
      icon.textContent = "▲";
    } else if (isDesc) {
      th.setAttribute("aria-sort", "descending");
      icon.textContent = "▼";
    } else {
      th.setAttribute("aria-sort", "none");
      icon.textContent = "⇅";
    }
  });

  const sortSelect = document.getElementById("sort-select");
  if (sortSelect && sortSelect.value !== currentSort) {
    const opts = Array.from(sortSelect.options || []).map((o) => o.value);
    if (opts.includes(currentSort)) {
      sortSelect.value = currentSort;
    }
  }
}

function handleSortToggle(key) {
  const current = state.sortBy || "trending";

  if (key === "trending") {
    state.sortBy = (current === "trending" || current === "trending-desc") ? "trending-asc" : "trending";
  } else if (key === "stars") {
    state.sortBy = (current === "stars" || current === "stars-desc") ? "stars-asc" : "stars";
  } else if (key === "category") {
    state.sortBy = (current === "category" || current === "category-asc") ? "category-desc" : "category-asc";
  } else if (key === "issues") {
    state.sortBy = (current === "issues" || current === "issues-desc") ? "issues-asc" : "issues";
  } else if (key === "name") {
    state.sortBy = (current === "name" || current === "name-asc") ? "name-desc" : "name-asc";
  }

  const sortSelect = document.getElementById("sort-select");
  if (sortSelect) {
    sortSelect.value = state.sortBy;
  }

  renderSkills();
}

function setCategory(cat) {
  state.selectedCategory = cat;
  const categoryFilters = document.getElementById("category-filters");
  if (categoryFilters) {
    categoryFilters.querySelectorAll(".category-pill").forEach((p) => {
      p.classList.toggle("active", p.getAttribute("data-category") === cat);
    });
  }
  renderSkills();
}

function renderTableRow(skill) {
  const lang = state.lang;
  const desc = (skill.description && skill.description[lang]) || (skill.description && skill.description.en) || "";
  const catBadgeClass = getCategoryBadgeClass(skill.category);
  const weeklyDelta = skill.weekly_stars !== undefined && skill.weekly_stars !== null ? skill.weekly_stars : 0;
  const dict = TRANSLATIONS[lang] || TRANSLATIONS.en;
  const featuredBadge = skill.featured
    ? `<span class="badge-featured" title="${escapeHtml(dict.badgeCuratorPick)}">${escapeHtml(dict.badgeInUse)}</span>`
    : "";

  const tagsHtml = (skill.tags || [])
    .slice(0, 4)
    .map((tag) => `<span class="tag-pill">${escapeHtml(tag)}</span>`)
    .join("");

  return `
    <tr>
      <td>
        <div class="skill-primary-cell">
          <div class="skill-title-row">
            <a href="${escapeHtml(skill.url)}" target="_blank" rel="noopener noreferrer" class="skill-name">
              ${escapeHtml(skill.name)}
            </a>
            ${featuredBadge}
            <a href="${escapeHtml(skill.url)}" target="_blank" rel="noopener noreferrer" class="skill-repo">
              ${escapeHtml(skill.repo)}
            </a>
          </div>
          <p class="skill-desc">${escapeHtml(desc)}</p>
        </div>
      </td>
      <td>
        <span class="badge ${catBadgeClass} badge-clickable" data-filter-category="${escapeHtml(skill.category)}" title="${escapeHtml(dict.filterByCategoryTip)}">${escapeHtml(skill.category)}</span>
      </td>
      <td class="td-delta">
        <span class="badge badge-delta">
          <span class="delta-symbol">+Δ</span> ${formatNumber(weeklyDelta)} ${dict.weeklyDeltaLabel}
        </span>
      </td>
      <td class="td-stars">
        <span class="stars-val"><span class="stars-icon">★</span>${formatNumber(skill.stars)}</span>
      </td>
      <td class="td-issues">
        <span class="issues-val">${formatNumber(skill.open_issues)}</span>
      </td>
      <td>
        <div class="tags-cell">${tagsHtml}</div>
      </td>
    </tr>
  `;
}

function renderCard(skill) {
  const lang = state.lang;
  const desc = (skill.description && skill.description[lang]) || (skill.description && skill.description.en) || "";
  const catBadgeClass = getCategoryBadgeClass(skill.category);
  const weeklyDelta = skill.weekly_stars !== undefined && skill.weekly_stars !== null ? skill.weekly_stars : 0;
  const dict = TRANSLATIONS[lang] || TRANSLATIONS.en;
  const featuredBadge = skill.featured
    ? `<span class="badge-featured" title="${escapeHtml(dict.badgeCuratorPick)}">${escapeHtml(dict.badgeInUse)}</span>`
    : "";

  const tagsHtml = (skill.tags || [])
    .map((tag) => `<span class="tag-pill">${escapeHtml(tag)}</span>`)
    .join("");

  return `
    <article class="skill-card">
      <div class="card-top">
        <div class="card-title-group">
          <div style="display: flex; align-items: center; gap: 6px;">
            <a href="${escapeHtml(skill.url)}" target="_blank" rel="noopener noreferrer" class="card-name">
              ${escapeHtml(skill.name)}
            </a>
            ${featuredBadge}
          </div>
          <a href="${escapeHtml(skill.url)}" target="_blank" rel="noopener noreferrer" class="card-repo">
            ${escapeHtml(skill.repo)}
          </a>
        </div>
        <span class="badge ${catBadgeClass} badge-clickable" data-filter-category="${escapeHtml(skill.category)}" title="${escapeHtml(dict.filterByCategoryTip)}">${escapeHtml(skill.category)}</span>
      </div>

      <p class="card-desc">${escapeHtml(desc)}</p>

      <div class="card-stats">
        <span class="badge badge-delta">
          <span class="delta-symbol">+Δ</span> ${formatNumber(weeklyDelta)} ${dict.weeklyDeltaLabel}
        </span>
        <div class="card-stat-item">
          <span class="stars-icon">★</span>
          <strong>${formatNumber(skill.stars)}</strong>
          <span>${dict.starsLabel}</span>
        </div>
        <div class="card-stat-item">
          <strong>${formatNumber(skill.open_issues)}</strong>
          <span>${dict.issuesLabel}</span>
        </div>
      </div>

      <div class="card-tags">${tagsHtml}</div>
    </article>
  `;
}

// ============================================================================
// Event Listeners & Initialization
// ============================================================================

function setupEventListeners() {
  // Language toggle buttons
  const btnEn = document.getElementById("lang-en");
  const btnKo = document.getElementById("lang-ko");
  if (btnEn) btnEn.addEventListener("click", () => setLanguage("en"));
  if (btnKo) btnKo.addEventListener("click", () => setLanguage("ko"));

  // Category filter pills
  const categoryFilters = document.getElementById("category-filters");
  if (categoryFilters) {
    categoryFilters.addEventListener("click", (e) => {
      const pill = e.target.closest(".category-pill");
      if (!pill) return;
      const cat = pill.getAttribute("data-category");
      state.selectedCategory = cat;

      categoryFilters.querySelectorAll(".category-pill").forEach((p) => {
        p.classList.toggle("active", p === pill);
      });

      renderSkills();
    });
  }

  // Search input
  const searchInput = document.getElementById("search-input");
  const searchClear = document.getElementById("search-clear");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      state.searchQuery = e.target.value.trim();
      if (searchClear) {
        searchClear.style.display = state.searchQuery ? "block" : "none";
      }
      renderSkills();
    });
  }

  if (searchClear && searchInput) {
    searchClear.addEventListener("click", () => {
      searchInput.value = "";
      state.searchQuery = "";
      searchClear.style.display = "none";
      searchInput.focus();
      renderSkills();
    });
  }

  // Sort select
  const sortSelect = document.getElementById("sort-select");
  if (sortSelect) {
    sortSelect.addEventListener("change", (e) => {
      state.sortBy = e.target.value;
      renderSkills();
    });
  }

  // Interactive Table Header Sorting
  const skillsTable = document.getElementById("skills-table");
  if (skillsTable) {
    skillsTable.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-sort-key]");
      if (btn) {
        const key = btn.getAttribute("data-sort-key");
        if (key) {
          handleSortToggle(key);
        }
      }
    });
  }

  // Clickable Category Badges to instantly filter by category
  const handleCategoryBadgeClick = (e) => {
    const badge = e.target.closest("[data-filter-category]");
    if (badge) {
      const cat = badge.getAttribute("data-filter-category");
      if (cat) {
        if (state.selectedCategory === cat) {
          setCategory("all");
        } else {
          setCategory(cat);
        }
      }
    }
  };

  const skillsContainer = document.getElementById("skills-container");
  if (skillsContainer) {
    skillsContainer.addEventListener("click", handleCategoryBadgeClick);
  }
  const curatorCards = document.getElementById("curator-cards");
  if (curatorCards) {
    curatorCards.addEventListener("click", handleCategoryBadgeClick);
  }

  // History snapshot select
  const historySelect = document.getElementById("history-select");
  if (historySelect) {
    historySelect.addEventListener("change", (e) => {
      const snap = e.target.value;
      fetchSnapshot(snap);
    });
  }

  // Theme toggle
  const themeToggle = document.getElementById("theme-toggle");
  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const nextTheme = state.theme === "light" ? "dark" : "light";
      setTheme(nextTheme);
    });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initLanguage();
  initTheme();
  setupEventListeners();
  fetchSnapshot("latest");
});
