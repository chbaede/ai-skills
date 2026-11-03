"""Tests for CI workflows and documentation.

Validates GitHub Actions workflow configurations (weekly updater and Pages deployment)
and bilingual README documentation.
"""

from pathlib import Path
import re
import unittest

try:
    import yaml
except ImportError:
    yaml = None

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = PROJECT_ROOT / ".github" / "workflows"
WEEKLY_UPDATE_YML = WORKFLOWS_DIR / "weekly-update.yml"
DEPLOY_PAGES_YML = WORKFLOWS_DIR / "deploy-pages.yml"
README_MD = PROJECT_ROOT / "README.md"


class TestWeeklyUpdateWorkflow(unittest.TestCase):
    """Validate .github/workflows/weekly-update.yml configuration."""

    def setUp(self):
        self.assertTrue(
            WEEKLY_UPDATE_YML.exists(),
            f"Missing weekly update workflow at {WEEKLY_UPDATE_YML}",
        )
        with open(WEEKLY_UPDATE_YML, "r", encoding="utf-8") as f:
            self.raw_content = f.read()

        if yaml is not None:
            self.workflow_data = yaml.safe_load(self.raw_content)
        else:
            self.workflow_data = None

    def _get_on_section(self):
        """Helper to safely extract the 'on' trigger section in PyYAML (which may parse 'on' as True)."""
        if self.workflow_data:
            return self.workflow_data.get("on") or self.workflow_data.get(True)
        return None

    def test_yaml_syntax_valid(self):
        """Workflow must be valid YAML."""
        if yaml is not None:
            self.assertIsNotNone(self.workflow_data)

    def test_triggers_schedule_and_dispatch(self):
        """Must trigger on weekly schedule (Monday 00:00 UTC) and workflow_dispatch."""
        on_data = self._get_on_section()
        if on_data:
            self.assertIn("schedule", on_data)
            schedules = on_data["schedule"]
            cron_values = [s.get("cron") for s in schedules if isinstance(s, dict)]
            self.assertIn("0 0 * * 1", cron_values)
            self.assertIn("workflow_dispatch", on_data)
        else:
            self.assertIn("cron: '0 0 * * 1'", self.raw_content)
            self.assertIn("workflow_dispatch:", self.raw_content)

    def test_permissions_contents_write(self):
        """Must have permissions: contents: write to push updates."""
        if self.workflow_data:
            permissions = self.workflow_data.get("permissions", {})
            self.assertEqual(permissions.get("contents"), "write")
        else:
            self.assertRegex(self.raw_content, r"permissions:[\s\S]*contents:\s*write")

    def test_steps_checkout_and_python_setup(self):
        """Must checkout repo and configure Python 3.11."""
        self.assertIn("actions/checkout@v4", self.raw_content)
        self.assertIn("actions/setup-python@v5", self.raw_content)
        self.assertRegex(self.raw_content, r"python-version:\s*['\"]?3\.11['\"]?")

    def test_execution_with_github_token(self):
        """Must execute python3 scripts/update_skills.py with GITHUB_TOKEN secret."""
        self.assertIn("python3 scripts/update_skills.py", self.raw_content)
        self.assertRegex(
            self.raw_content,
            r"GITHUB_TOKEN:\s*\$\{\{\s*secrets\.GITHUB_TOKEN\s*\}\}",
        )

    def test_git_committer_and_message_constraints(self):
        """Must configure author Changhyeok Bae, email changhyeok.bae@gmail.com, and conform to commit limits."""
        self.assertIn('git config user.name "Changhyeok Bae"', self.raw_content)
        self.assertIn('git config user.email "changhyeok.bae@gmail.com"', self.raw_content)

        # Subject length check <= 50 chars
        subject_match = re.search(r'chore\(data\):[^\n"\']+', self.raw_content)
        self.assertIsNotNone(subject_match, "Commit subject starting with chore(data): required")
        subject = subject_match.group(0).strip()
        self.assertLessEqual(
            len(subject),
            50,
            f"Commit subject '{subject}' exceeds 50 characters (len={len(subject)})",
        )

        # Check commit body hard-wrapped <= 72 chars
        body_match = re.search(r'-m\s+"([^"\n]+)"\s+-m\s+"([^"\n]+)"', self.raw_content)
        if body_match:
            body = body_match.group(2)
            self.assertLessEqual(
                len(body),
                72,
                f"Commit body '{body}' exceeds 72 characters (len={len(body)})",
            )

    def test_git_push_target_refspec(self):
        """Must push explicitly using HEAD:main for detached HEAD compatibility in CI."""
        self.assertIn("git push origin HEAD:main", self.raw_content)


class TestDeployPagesWorkflow(unittest.TestCase):
    """Validate .github/workflows/deploy-pages.yml configuration."""

    def setUp(self):
        self.assertTrue(
            DEPLOY_PAGES_YML.exists(),
            f"Missing pages deployment workflow at {DEPLOY_PAGES_YML}",
        )
        with open(DEPLOY_PAGES_YML, "r", encoding="utf-8") as f:
            self.raw_content = f.read()

        if yaml is not None:
            self.workflow_data = yaml.safe_load(self.raw_content)
        else:
            self.workflow_data = None

    def _get_on_section(self):
        if self.workflow_data:
            return self.workflow_data.get("on") or self.workflow_data.get(True)
        return None

    def test_yaml_syntax_valid(self):
        """Workflow must be valid YAML."""
        if yaml is not None:
            self.assertIsNotNone(self.workflow_data)

    def test_triggers_push_main_paths(self):
        """Must trigger on push to main with web paths and workflow_dispatch."""
        on_data = self._get_on_section()
        if on_data:
            self.assertIn("push", on_data)
            push = on_data["push"]
            self.assertIn("main", push.get("branches", []))
            paths = push.get("paths", [])
            for required_path in ["index.html", "css/**", "js/**", "data/**"]:
                self.assertIn(required_path, paths)
            self.assertIn("workflow_dispatch", on_data)
        else:
            self.assertIn("branches:", self.raw_content)
            self.assertIn("- main", self.raw_content)
            self.assertIn("workflow_dispatch:", self.raw_content)

    def test_permissions(self):
        """Must configure pages deployment permissions: contents: read, pages: write, id-token: write."""
        if self.workflow_data:
            perms = self.workflow_data.get("permissions", {})
            self.assertEqual(perms.get("contents"), "read")
            self.assertEqual(perms.get("pages"), "write")
            self.assertEqual(perms.get("id-token"), "write")
        else:
            self.assertIn("contents: read", self.raw_content)
            self.assertIn("pages: write", self.raw_content)
            self.assertIn("id-token: write", self.raw_content)

    def test_concurrency(self):
        """Must set concurrency group 'pages' and cancel-in-progress: false."""
        if self.workflow_data:
            concurrency = self.workflow_data.get("concurrency", {})
            self.assertEqual(concurrency.get("group"), "pages")
            self.assertFalse(concurrency.get("cancel-in-progress"))
        else:
            self.assertIn("group: \"pages\"", self.raw_content)
            self.assertIn("cancel-in-progress: false", self.raw_content)

    def test_actions_steps(self):
        """Must use official Pages actions."""
        self.assertIn("actions/checkout@v4", self.raw_content)
        self.assertIn("actions/configure-pages@v5", self.raw_content)
        self.assertIn("actions/upload-pages-artifact@v3", self.raw_content)
        self.assertIn("actions/deploy-pages@v4", self.raw_content)


class TestDocumentation(unittest.TestCase):
    """Validate README.md bilingual content, links, and operational guides."""

    def setUp(self):
        self.assertTrue(README_MD.exists(), f"Missing README.md at {README_MD}")
        with open(README_MD, "r", encoding="utf-8") as f:
            self.content = f.read()

    def test_readme_length_and_structure(self):
        """README must be substantial and properly structured."""
        self.assertGreater(len(self.content), 500, "README.md should contain detailed documentation")

    def test_live_url_present(self):
        """Must contain live GitHub Pages URL."""
        self.assertIn("https://chbaede.github.io/ai-skills/", self.content)

    def test_bilingual_sections(self):
        """Must contain distinct Korean and English documentation sections."""
        # Check Korean characters (Hangul Unicode range AC00-D7A3)
        hangul_matches = re.findall(r"[\uac00-\ud7a3]+", self.content)
        self.assertGreater(len(hangul_matches), 30, "README must contain extensive Korean documentation")

        # Check English section headings or keywords
        self.assertIn("AI Skills Radar", self.content)
        self.assertRegex(self.content, r"(#|##)\s*(English|Overview|Features)")

    def test_features_documented(self):
        """Must document key features: weekly trend delta, snapshots, dark UI, bilingual toggle."""
        self.assertIn("Δ", self.content)
        self.assertRegex(self.content, r"(Snapshot|스냅샷|Weekly|주간)")

    def test_automation_and_commands_documented(self):
        """Must document cron schedule and update command."""
        self.assertIn("python3 scripts/update_skills.py", self.content)
        self.assertIn("0 0 * * 1", self.content)

    def test_contribution_guide_documented(self):
        """Must document how to propose a new skill in data/registry.json."""
        self.assertIn("data/registry.json", self.content)

    def test_local_dev_and_test_suite_documented(self):
        """Must document how to preview locally and run tests."""
        self.assertIn("python3 -m unittest discover -s tests", self.content)


if __name__ == "__main__":
    unittest.main()
