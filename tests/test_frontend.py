import os
from pathlib import Path
import re
import subprocess
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = PROJECT_ROOT / "index.html"
STYLE_CSS = PROJECT_ROOT / "css" / "style.css"
APP_JS = PROJECT_ROOT / "js" / "app.js"


class TestFrontendFiles(unittest.TestCase):
    """Test that all required frontend files exist."""

    def test_index_html_exists(self):
        self.assertTrue(INDEX_HTML.exists(), f"Missing index.html at {INDEX_HTML}")

    def test_style_css_exists(self):
        self.assertTrue(STYLE_CSS.exists(), f"Missing css/style.css at {STYLE_CSS}")

    def test_app_js_exists(self):
        self.assertTrue(APP_JS.exists(), f"Missing js/app.js at {APP_JS}")


class TestHtmlStructure(unittest.TestCase):
    """Test semantic structure, meta tags, and critical elements in index.html."""

    def setUp(self):
        if not INDEX_HTML.exists():
            self.skipTest("index.html not created yet")
        with open(INDEX_HTML, "r", encoding="utf-8") as f:
            self.html = f.read()

    def test_viewport_meta_tag(self):
        self.assertRegex(
            self.html,
            r'<meta\s+name=["\']viewport["\']\s+content=["\'][^"\']*width=device-width[^"\']*["\']',
            "index.html must contain a viewport meta tag with width=device-width",
        )

    def test_doctype_and_html_tag(self):
        self.assertIn("<!DOCTYPE html>", self.html, "HTML must start with <!DOCTYPE html>")
        self.assertRegex(self.html, r'<html[^>]*lang=["\'][a-z]{2}["\']')

    def test_stylesheet_link(self):
        self.assertRegex(
            self.html,
            r'<link[^>]*rel=["\']stylesheet["\'][^>]*href=["\']css/style\.css["\']',
            "index.html must link to css/style.css",
        )

    def test_script_tag(self):
        self.assertRegex(
            self.html,
            r'<script[^>]*src=["\']js/app\.js["\']',
            "index.html must load js/app.js via script tag",
        )

    def test_header_and_brand_elements(self):
        self.assertIn("<header", self.html, "Missing <header> landmark element")
        self.assertIn("id=\"last-updated\"", self.html, "Missing last-updated element")
        self.assertIn("id=\"history-select\"", self.html, "Missing history snapshot selector")

    def test_language_switcher_present(self):
        self.assertRegex(
            self.html,
            r'id=["\']lang-(?:en|ko|toggle)["\']|class=["\'][^"\']*lang-switcher[^"\']*["\']',
            "index.html must include language switch controls",
        )

    def test_search_and_filter_controls(self):
        self.assertIn("id=\"search-input\"", self.html, "Missing search input element")
        self.assertIn("id=\"category-filters\"", self.html, "Missing category filters container")
        self.assertIn("id=\"sort-select\"", self.html, "Missing sort selector")
        self.assertIn("id=\"results-count\"", self.html, "Missing results counter element")
        expected_categories = [
            "all",
            "MCP Server",
            "Agent Tool",
            "Coding Assistant",
            "Agent Plugin",
            "Benchmark / Eval",
        ]
        for cat in expected_categories:
            self.assertIn(
                f'data-category="{cat}"',
                self.html,
                f"Missing category filter button for '{cat}'",
            )

    def test_results_and_empty_state_containers(self):
        self.assertRegex(
            self.html,
            r'id=["\']skills-(?:container|table|list)["\']',
            "Missing skills container or table",
        )
        self.assertIn("id=\"empty-state\"", self.html, "Missing empty state container")

    def test_footer_present(self):
        self.assertIn("<footer", self.html, "Missing <footer> landmark element")
        self.assertIn('href="https://github.com/chbaede/ai-skills"', self.html)


class TestCssStyling(unittest.TestCase):
    """Test developer aesthetic, mobile responsiveness, and dark mode palette."""

    def setUp(self):
        if not STYLE_CSS.exists():
            self.skipTest("css/style.css not created yet")
        with open(STYLE_CSS, "r", encoding="utf-8") as f:
            self.css = f.read()

    def test_dark_palette_colors_present(self):
        # Developer aesthetic colors: #09090b, #18181b, #27272a, #fafafa, #a1a1aa
        self.assertTrue(
            "#09090b" in self.css.lower() or "#18181b" in self.css.lower(),
            "Dark theme background color (#09090b or #18181b) missing in css/style.css",
        )
        self.assertIn(
            "#27272a",
            self.css.lower(),
            "Border color #27272a missing in css/style.css",
        )
        self.assertTrue(
            "#fafafa" in self.css.lower() or "#ffffff" in self.css.lower(),
            "High contrast text color missing in css/style.css",
        )

    def test_monospace_font_stack(self):
        font_check = any(
            mono in self.css.lower()
            for mono in ["jetbrains mono", "geist", "monospace", "courier"]
        )
        self.assertTrue(font_check, "CSS must define developer typography with monospace/system fallback")

    def test_mobile_media_query_present(self):
        self.assertRegex(
            self.css,
            r'@media\s*\(\s*max-width:\s*(?:640|768)px\s*\)',
            "CSS must include mobile media query for max-width 640px or 768px",
        )

    def test_mobile_overflow_prevention(self):
        self.assertTrue(
            "overflow-x" in self.css or "overflow: hidden" in self.css,
            "CSS should guard against horizontal overflow",
        )

    def test_badge_and_card_styles(self):
        self.assertIn(".badge", self.css, "CSS must contain badge styling")
        self.assertTrue(
            "badge-delta" in self.css or "delta" in self.css,
            "CSS should style trend / delta indicators",
        )


class TestJsApplication(unittest.TestCase):
    """Test pure JS logic, i18n parity, data fetch, and syntax."""

    def setUp(self):
        if not APP_JS.exists():
            self.skipTest("js/app.js not created yet")
        with open(APP_JS, "r", encoding="utf-8") as f:
            self.js = f.read()

    def test_js_syntax_valid(self):
        # Validate syntax via node --check
        res = subprocess.run(
            ["node", "--check", str(APP_JS)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"js/app.js syntax error:\n{res.stderr}")

    def test_data_skills_json_referenced(self):
        self.assertIn(
            "data/skills.json",
            self.js,
            "js/app.js must fetch data/skills.json",
        )

    def test_i18n_translation_keys_parity(self):
        """Verify that en and ko have identical translation keys."""
        # Extract translations using node or regex
        node_script = """
        const fs = require('fs');
        const code = fs.readFileSync(process.argv[1], 'utf8');
        // Extract TRANSLATIONS object
        const match = code.match(/(?:const|let|var)\\s+TRANSLATIONS\\s*=\\s*({[\\s\\S]*?\\n};)/);
        if (!match) {
            console.error("TRANSLATIONS object not found");
            process.exit(1);
        }
        const fn = new Function(match[0] + '; return TRANSLATIONS;');
        const t = fn();
        console.log(JSON.stringify({
            en: Object.keys(t.en),
            ko: Object.keys(t.ko)
        }));
        """
        res = subprocess.run(
            ["node", "-e", node_script, str(APP_JS)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"Failed to extract TRANSLATIONS: {res.stderr}")
        import json
        keys = json.loads(res.stdout)
        en_keys = set(keys["en"])
        ko_keys = set(keys["ko"])
        self.assertGreater(len(en_keys), 10, "Expected at least 10 translation keys")
        missing_in_ko = en_keys - ko_keys
        missing_in_en = ko_keys - en_keys
        self.assertEqual(
            missing_in_ko,
            set(),
            f"Keys missing in KO translation: {missing_in_ko}",
        )
        self.assertEqual(
            missing_in_en,
            set(),
            f"Keys missing in EN translation: {missing_in_en}",
        )

    def test_localstorage_and_url_query_sync(self):
        self.assertIn("localStorage", self.js, "Language should be persisted in localStorage")
        self.assertTrue(
            "searchParams" in self.js or "URLSearchParams" in self.js or "location.search" in self.js,
            "Language should be synced with URL query parameter ?lang=",
        )

    def test_sort_modes_present(self):
        self.assertTrue(
            "weekly_stars" in self.js,
            "Must support sorting by weekly stars (trending)",
        )
        self.assertTrue(
            "stars" in self.js,
            "Must support sorting by stars",
        )
        self.assertTrue(
            "open_issues" in self.js,
            "Must support sorting by open issues",
        )

    def test_js_runtime_execution(self):
        """Simulate JS runtime execution in Node to verify filtering, sorting, and i18n."""
        node_script = """
        const fs = require('fs');
        const vm = require('vm');
        const appCode = fs.readFileSync(process.argv[1], 'utf8');
        const skillsData = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

        const mockElements = {
          "site-title": { textContent: "", getAttribute: () => "siteTitle", setAttribute: () => {} },
          "site-tagline": { textContent: "", getAttribute: () => "siteTagline", setAttribute: () => {} },
          "lang-en": { classList: { toggle: () => {} }, addEventListener: () => {} },
          "lang-ko": { classList: { toggle: () => {} }, addEventListener: () => {} },
          "category-filters": { addEventListener: () => {}, querySelectorAll: () => [] },
          "search-input": { addEventListener: () => {}, value: "", getAttribute: () => "placeholder:searchPlaceholder", setAttribute: () => {} },
          "search-clear": { style: {}, addEventListener: () => {} },
          "sort-select": { addEventListener: () => {}, value: "trending" },
          "history-select": { addEventListener: () => {}, options: [{ value: "latest" }], appendChild: () => {} },
          "stats-total-count": { textContent: "" },
          "last-updated-val": { textContent: "" },
          "results-count": { textContent: "" },
          "skills-table": { style: {} },
          "skills-tbody": { innerHTML: "" },
          "skills-cards": { innerHTML: "", style: {} },
          "empty-state": { style: {} }
        };

        const sandbox = {
          document: {
            documentElement: { lang: "en" },
            getElementById: (id) => mockElements[id] || { textContent: "", style: {}, setAttribute: () => {}, getAttribute: () => null, addEventListener: () => {} },
            querySelectorAll: () => [],
            addEventListener: () => {}
          },
          window: {
            location: { search: "" },
            history: { replaceState: () => {} }
          },
          localStorage: {
            getItem: () => null,
            setItem: () => {}
          },
          navigator: { language: "en-US" },
          URL: function(url) { return { searchParams: { set: () => {} } }; },
          URLSearchParams: function(s) { return { get: () => null }; },
          skillsData: skillsData,
          mockElements: mockElements,
          console: console
        };

        vm.createContext(sandbox);
        vm.runInContext(appCode + `
          state.skillsData = skillsData;
          state.rawSkills = skillsData.skills;
          renderSkills();
          setLanguage("ko");
          state.selectedCategory = "MCP Server";
          let list = getFilteredAndSortedSkills();
          if (list.length === 0) throw new Error("Filter returned 0 items");
          state.sortBy = "stars";
          let sorted = getFilteredAndSortedSkills();
          if (sorted[0].stars < sorted[sorted.length - 1].stars) throw new Error("Sort failed");
        `, sandbox);
        """
        data_skills = PROJECT_ROOT / "data" / "skills.json"
        res = subprocess.run(
            ["node", "-e", node_script, str(APP_JS), str(data_skills)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"JS execution error:\n{res.stderr}")

    def test_app_js_graceful_on_storage_and_history_errors(self):
        """Verify app handles SecurityError / throwing localStorage and replaceState gracefully."""
        node_script = """
        const fs = require('fs');
        const vm = require('vm');

        const appCode = fs.readFileSync(process.argv[1], 'utf-8');
        const skillsData = JSON.parse(fs.readFileSync(process.argv[2], 'utf-8'));

        const mockElements = {
          "lang-en": { classList: { toggle: () => {} }, addEventListener: () => {} },
          "lang-ko": { classList: { toggle: () => {} }, addEventListener: () => {} },
          "skills-container": { innerHTML: "", style: {} },
          "empty-state": { style: {} }
        };

        const sandbox = {
          document: {
            documentElement: { lang: "en" },
            getElementById: (id) => mockElements[id] || { textContent: "", style: {}, setAttribute: () => {}, getAttribute: () => null, addEventListener: () => {}, classList: { toggle: () => {} } },
            querySelectorAll: () => [],
            addEventListener: () => {}
          },
          window: {
            location: { search: "" },
            history: {
              replaceState: () => { throw new Error("SecurityError: replaceState blocked"); }
            }
          },
          localStorage: {
            getItem: () => { throw new Error("SecurityError: localStorage blocked"); },
            setItem: () => { throw new Error("SecurityError: localStorage blocked"); }
          },
          navigator: { language: "ko-KR" },
          URL: function(url) { return { searchParams: { set: () => {} } }; },
          URLSearchParams: function(s) { return { get: () => null }; },
          skillsData: skillsData,
          mockElements: mockElements,
          console: console
        };

        vm.createContext(sandbox);
        vm.runInContext(appCode + `
          initLanguage();
          setLanguage("en");
        `, sandbox);
        """
        data_skills = PROJECT_ROOT / "data" / "skills.json"
        res = subprocess.run(
            ["node", "-e", node_script, str(APP_JS), str(data_skills)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"JS execution error when storage throws:\n{res.stderr}")

    def test_dynamic_snapshot_history_discovery(self):
        """Verify updateHistoryOptions dynamically populates snapshot options from data."""
        node_script = """
        const fs = require('fs');
        const vm = require('vm');
        const appCode = fs.readFileSync(process.argv[1], 'utf8');

        const appendedOptions = [];
        const mockSelect = {
          options: [{ value: "latest" }],
          appendChild: (opt) => {
            appendedOptions.push(opt.value);
            mockSelect.options.push(opt);
          }
        };

        const sandbox = {
          document: {
            getElementById: (id) => (id === "history-select" ? mockSelect : null),
            documentElement: { lang: "en" },
            createElement: (tag) => ({ value: "", textContent: "", setAttribute: () => {} }),
            querySelectorAll: () => [],
            addEventListener: () => {}
          },
          appendedOptions: appendedOptions,
          window: { location: { search: "" } },
          localStorage: { getItem: () => null, setItem: () => {} },
          navigator: { language: "en-US" },
          console: console
        };

        vm.createContext(sandbox);
        vm.runInContext(appCode + `
          // Test dynamic population from available_snapshots array
          updateHistoryOptions(["2026-W47", "2026-W46", "2026-W45"], "2026-W47");
          if (!appendedOptions.includes("2026-W47") || !appendedOptions.includes("2026-W46")) {
            throw new Error("Failed dynamic snapshot population: " + JSON.stringify(appendedOptions));
          }
          // Test graceful fallback when available_snapshots is null/empty
          updateHistoryOptions(null, "2026-W48");
          if (!appendedOptions.includes("2026-W48")) {
            throw new Error("Failed fallback snapshot population: " + JSON.stringify(appendedOptions));
          }
        `, sandbox);
        """
        res = subprocess.run(
            ["node", "-e", node_script, str(APP_JS)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"Dynamic snapshot JS test failed:\n{res.stderr}")

    def test_main_hub_links_present(self):
        """Must ensure link to https://main.yocto.co.kr/ exists in index.html."""
        with open(INDEX_HTML, "r", encoding="utf-8") as f:
            html = f.read()
        self.assertIn("https://main.yocto.co.kr/", html, "Main Hub link missing in index.html")
        self.assertRegex(html, r'href=["\']https://main\.yocto\.co\.kr/["\']')

    def test_theme_toggle_and_light_mode_styles(self):
        """Must ensure theme toggle button exists in HTML and [data-theme="light"] exists in CSS."""
        with open(INDEX_HTML, "r", encoding="utf-8") as f:
            html = f.read()
        self.assertIn('id="theme-toggle"', html, "Theme toggle button missing in index.html")

        with open(STYLE_CSS, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn('[data-theme="light"]', css, "Light theme variables missing in CSS")
        self.assertIn('--color-gold: #92400e', css, "High-contrast amber gold variable missing in light mode")
        self.assertIn('.theme-toggle-btn', css, "Theme toggle styling missing in CSS")
        self.assertIn('.main-hub-btn', css, "Main Hub button styling missing in CSS")

    def test_curator_shelf_present(self):
        """Must ensure curator shelf section, cards container, and styles exist."""
        with open(INDEX_HTML, "r", encoding="utf-8") as f:
            html = f.read()
        self.assertIn('id="curator-shelf"', html, "Curator shelf missing in index.html")
        self.assertIn('id="curator-cards"', html, "Curator cards container missing in index.html")
        self.assertIn('data-category="featured"', html, "Curator's picks category filter pill missing")

        with open(STYLE_CSS, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn('.curator-shelf', css, "Curator shelf styling missing in CSS")
        self.assertIn('.curator-card', css, "Curator card styling missing in CSS")
        self.assertIn('.badge-in-use', css, "Badge in-use styling missing in CSS")


if __name__ == "__main__":
    unittest.main()
