import json
from pathlib import Path
import unittest

REGISTRY_PATH = Path(__file__).resolve().parent.parent / "data" / "registry.json"

ALLOWED_CATEGORIES = {
    "MCP Server",
    "Agent Tool",
    "Coding Assistant",
    "Agent Plugin",
    "Benchmark / Eval",
}

EXPECTED_REPOS = [
    "modelcontextprotocol/servers",
    "obra/superpowers",
    "anthropics/claude-quickstarts",
    "openinterpreter/open-interpreter",
    "cline/cline",
    "Roo-Code/Roo-Code",
    "Aider-AI/aider",
    "princeton-nlp/SWE-agent",
    "microsoft/semantic-kernel",
    "executeautomation/mcp-playwright",
    "mark3labs/mcp-go",
    "github/copilot-cli",
    "multica-ai/andrej-karpathy-skills",
    "Egonex-AI/Understand-Anything",
    "hugohe3/ppt-master",
]

CURATOR_PICKS = [
    "obra/superpowers",
    "multica-ai/andrej-karpathy-skills",
    "Egonex-AI/Understand-Anything",
    "hugohe3/ppt-master",
]


class TestRegistrySchema(unittest.TestCase):
    def setUp(self):
        self.assertTrue(
            REGISTRY_PATH.exists(),
            f"Registry file not found at {REGISTRY_PATH}",
        )
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            self.registry = json.load(f)

    def test_registry_is_list(self):
        self.assertIsInstance(self.registry, list, "Registry root must be a list")

    def test_item_count(self):
        self.assertEqual(
            len(self.registry),
            15,
            f"Expected exactly 15 items in registry, found {len(self.registry)}",
        )

    def test_curator_picks_featured(self):
        """Verify the 4 curator-recommended skills have featured: true."""
        featured_repos = [item["repo"] for item in self.registry if item.get("featured")]
        for pick in CURATOR_PICKS:
            self.assertIn(pick, featured_repos, f"Expected {pick} to be marked as featured")

    def test_required_fields_and_types(self):
        required_fields = {
            "id": str,
            "repo": str,
            "name": str,
            "category": str,
            "url": str,
            "tags": list,
            "description": dict,
        }
        for item in self.registry:
            repo_name = item.get("repo", "unknown")
            for field, expected_type in required_fields.items():
                self.assertIn(
                    field,
                    item,
                    f"Item '{repo_name}' is missing required field '{field}'",
                )
                self.assertIsInstance(
                    item[field],
                    expected_type,
                    f"Field '{field}' in '{repo_name}' must be of type {expected_type.__name__}",
                )

    def test_categories_allowed(self):
        for item in self.registry:
            category = item["category"]
            self.assertIn(
                category,
                ALLOWED_CATEGORIES,
                f"Invalid category '{category}' in repo '{item.get('repo')}'. Allowed: {ALLOWED_CATEGORIES}",
            )

    def test_bilingual_descriptions(self):
        for item in self.registry:
            repo_name = item.get("repo", "unknown")
            desc = item.get("description", {})
            self.assertIn(
                "en",
                desc,
                f"Repo '{repo_name}' description missing 'en' key",
            )
            self.assertIn(
                "ko",
                desc,
                f"Repo '{repo_name}' description missing 'ko' key",
            )
            self.assertTrue(
                isinstance(desc["en"], str) and len(desc["en"].strip()) > 10,
                f"Repo '{repo_name}' 'en' description must be meaningful (>10 chars)",
            )
            self.assertTrue(
                isinstance(desc["ko"], str) and len(desc["ko"].strip()) > 10,
                f"Repo '{repo_name}' 'ko' description must be meaningful (>10 chars)",
            )

    def test_tags_format(self):
        for item in self.registry:
            repo_name = item.get("repo", "unknown")
            tags = item.get("tags", [])
            self.assertGreater(
                len(tags), 0, f"Repo '{repo_name}' must have at least one tag"
            )
            for tag in tags:
                self.assertIsInstance(
                    tag, str, f"Tag in '{repo_name}' must be a string"
                )
                self.assertGreater(
                    len(tag.strip()), 0, f"Tag in '{repo_name}' cannot be empty"
                )

    def test_uniqueness_of_ids_and_repos(self):
        ids = [item.get("id") for item in self.registry]
        repos = [item.get("repo") for item in self.registry]
        self.assertEqual(
            len(ids),
            len(set(ids)),
            f"Duplicate IDs found: {[x for x in ids if ids.count(x) > 1]}",
        )
        self.assertEqual(
            len(repos),
            len(set(repos)),
            f"Duplicate repos found: {[x for x in repos if repos.count(x) > 1]}",
        )

    def test_all_expected_repos_present(self):
        present_repos = {item.get("repo") for item in self.registry}
        for expected in EXPECTED_REPOS:
            self.assertIn(
                expected,
                present_repos,
                f"Expected repository '{expected}' not found in registry",
            )

    def test_urls_valid(self):
        for item in self.registry:
            repo = item.get("repo")
            url = item.get("url")
            expected_prefix = f"https://github.com/{repo}"
            self.assertTrue(
                url.startswith(expected_prefix),
                f"URL '{url}' does not match expected prefix '{expected_prefix}'",
            )


if __name__ == "__main__":
    unittest.main()
