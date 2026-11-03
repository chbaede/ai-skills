import datetime
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import urllib.error

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.update_skills import (
    build_request,
    calculate_weekly_delta,
    estimate_cold_start_stars,
    fetch_repo_metadata,
    find_latest_prior_snapshot,
    format_iso_week,
    get_available_snapshots,
    load_history_stars_map,
    parse_args,
    update_skills,
)


class TestUpdaterCalculations(unittest.TestCase):
    def test_format_iso_week(self):
        dt = datetime.datetime(2026, 11, 3, 12, 0, 0, tzinfo=datetime.timezone.utc)
        self.assertEqual(format_iso_week(dt), "2026-W45")

        dt_jan = datetime.datetime(2026, 1, 15, tzinfo=datetime.timezone.utc)
        self.assertEqual(format_iso_week(dt_jan), "2026-W03")

    def test_estimate_cold_start_stars(self):
        self.assertEqual(estimate_cold_start_stars(0), 0)
        self.assertEqual(estimate_cold_start_stars(-10), 0)

        # Non-zero stars should return reasonable positive delta (> 0)
        delta_small = estimate_cold_start_stars(100)
        self.assertGreaterEqual(delta_small, 1)

        delta_large = estimate_cold_start_stars(10000)
        self.assertGreaterEqual(delta_large, 10)
        self.assertLessEqual(delta_large, 500)

    def test_calculate_weekly_delta_with_prior(self):
        # Normal growth
        delta = calculate_weekly_delta(current_stars=1500, prior_stars=1420)
        self.assertEqual(delta, 80)

        # Zero growth
        delta_zero = calculate_weekly_delta(current_stars=1500, prior_stars=1500)
        self.assertEqual(delta_zero, 0)

        # Negative delta protection (stars decreased)
        delta_negative = calculate_weekly_delta(current_stars=1490, prior_stars=1500)
        self.assertEqual(delta_negative, 0)

    def test_calculate_weekly_delta_cold_start(self):
        # When prior_stars is None, cold-start estimation should be used
        delta = calculate_weekly_delta(current_stars=5000, prior_stars=None)
        self.assertGreater(delta, 0)
        self.assertIsInstance(delta, int)

    def test_calculate_weekly_delta_prior_zero_or_negative(self):
        # When prior_stars <= 0, cold-start estimation should be used
        delta_zero = calculate_weekly_delta(current_stars=5000, prior_stars=0)
        self.assertEqual(delta_zero, estimate_cold_start_stars(5000))

        delta_neg = calculate_weekly_delta(current_stars=5000, prior_stars=-10)
        self.assertEqual(delta_neg, estimate_cold_start_stars(5000))


class TestSnapshotHistory(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.history_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_find_latest_prior_snapshot_empty(self):
        result = find_latest_prior_snapshot(self.history_dir, "2026-W45")
        self.assertIsNone(result)

    def test_find_latest_prior_snapshot_ignores_same_and_future_weeks(self):
        (self.history_dir / "2026-W45.json").write_text("{}", encoding="utf-8")
        (self.history_dir / "2026-W46.json").write_text("{}", encoding="utf-8")
        (self.history_dir / "notes.txt").write_text("ignore me", encoding="utf-8")

        result = find_latest_prior_snapshot(self.history_dir, "2026-W45")
        self.assertIsNone(result)

    def test_find_latest_prior_snapshot_picks_most_recent_prior(self):
        (self.history_dir / "2026-W42.json").write_text("{}", encoding="utf-8")
        (self.history_dir / "2026-W44.json").write_text("{}", encoding="utf-8")
        (self.history_dir / "2026-W45.json").write_text("{}", encoding="utf-8")

        result = find_latest_prior_snapshot(self.history_dir, "2026-W45")
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "2026-W44.json")

    def test_load_history_stars_map(self):
        snapshot_data = {
            "week": "2026-W44",
            "skills": [
                {"id": "s1", "repo": "owner/repo1", "stars": 1200},
                {"id": "s2", "repo": "owner/repo2", "stars": 3400},
            ],
        }
        snap_file = self.history_dir / "2026-W44.json"
        snap_file.write_text(json.dumps(snapshot_data), encoding="utf-8")

        stars_map = load_history_stars_map(snap_file)
        self.assertEqual(stars_map.get("owner/repo1"), 1200)
        self.assertEqual(stars_map.get("owner/repo2"), 3400)
        self.assertIsNone(stars_map.get("owner/nonexistent"))

    def test_get_available_snapshots_empty_dir(self):
        result = get_available_snapshots(self.history_dir)
        self.assertEqual(result, [])

    def test_get_available_snapshots_sorted_descending(self):
        (self.history_dir / "2026-W42.json").write_text("{}", encoding="utf-8")
        (self.history_dir / "2026-W45.json").write_text("{}", encoding="utf-8")
        (self.history_dir / "2026-W44.json").write_text("{}", encoding="utf-8")
        (self.history_dir / "readme.txt").write_text("ignore", encoding="utf-8")

        result = get_available_snapshots(self.history_dir)
        self.assertEqual(result, ["2026-W45", "2026-W44", "2026-W42"])


class TestGithubApiIntegration(unittest.TestCase):
    def test_build_request_without_token(self):
        req = build_request("https://api.github.com/repos/foo/bar", token=None)
        self.assertEqual(req.headers.get("User-agent"), "ai-skills-updater")
        self.assertNotIn("Authorization", req.headers)

    def test_build_request_with_token(self):
        req = build_request("https://api.github.com/repos/foo/bar", token="ghp_test123")
        self.assertEqual(req.headers.get("Authorization"), "Bearer ghp_test123")

        req_bearer = build_request("https://api.github.com/repos/foo/bar", token="Bearer custom_tok")
        self.assertEqual(req_bearer.headers.get("Authorization"), "Bearer custom_tok")

    @patch("urllib.request.urlopen")
    def test_fetch_repo_metadata_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "full_name": "foo/bar",
            "stargazers_count": 2500,
            "open_issues_count": 42,
            "html_url": "https://github.com/foo/bar",
        }).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        meta = fetch_repo_metadata("foo/bar", token="ghp_test")
        self.assertIsNotNone(meta)
        self.assertEqual(meta["stars"], 2500)
        self.assertEqual(meta["open_issues"], 42)
        self.assertEqual(meta["url"], "https://github.com/foo/bar")

    @patch("urllib.request.urlopen")
    def test_fetch_repo_metadata_resolves_repo_aliases(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "full_name": "RooCodeInc/Roo-Code",
            "stargazers_count": 24000,
            "open_issues_count": 999,
            "html_url": "https://github.com/RooCodeInc/Roo-Code",
        }).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        meta = fetch_repo_metadata("Roo-Code/Roo-Code", token=None)
        self.assertIsNotNone(meta)
        self.assertEqual(meta["stars"], 24000)
        # Check that the request was made to the aliased URL
        called_req = mock_urlopen.call_args[0][0]
        self.assertIn("RooCodeInc/Roo-Code", called_req.full_url)

    @patch("urllib.request.urlopen")
    def test_fetch_repo_metadata_handles_rate_limit_403(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://api.github.com/repos/foo/bar",
            code=403,
            msg="rate limit exceeded",
            hdrs={},
            fp=None,
        )
        with patch("scripts.update_skills.logger.warning") as mock_warn:
            meta = fetch_repo_metadata("foo/bar", token=None)
            # Should gracefully return None without raising exception
            self.assertIsNone(meta)
            mock_warn.assert_called_once()

    @patch("urllib.request.urlopen")
    def test_fetch_repo_metadata_handles_network_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError(reason="Name resolution failure")
        with patch("scripts.update_skills.logger.warning") as mock_warn:
            meta = fetch_repo_metadata("foo/bar", token=None)
            # Should gracefully return None without raising exception
            self.assertIsNone(meta)
            mock_warn.assert_called_once()


class TestUpdaterPipeline(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.history_dir = self.base_dir / "history"
        self.history_dir.mkdir(parents=True)
        self.registry_file = self.base_dir / "registry.json"
        self.output_file = self.base_dir / "skills.json"

        # Mock sample registry
        self.sample_registry = [
            {
                "id": "repo-alpha",
                "repo": "test/alpha",
                "name": "Alpha Tool",
                "category": "Agent Tool",
                "url": "https://github.com/test/alpha",
                "tags": ["agent", "alpha"],
                "description": {
                    "en": "Alpha english description.",
                    "ko": "알파 한국어 설명입니다.",
                },
            },
            {
                "id": "repo-beta",
                "repo": "test/beta",
                "name": "Beta Server",
                "category": "MCP Server",
                "url": "https://github.com/test/beta",
                "tags": ["mcp", "beta"],
                "description": {
                    "en": "Beta english description.",
                    "ko": "베타 한국어 설명입니다.",
                },
            },
        ]
        self.registry_file.write_text(json.dumps(self.sample_registry), encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def mock_fetcher(self, repo, token=None):
        if repo == "test/alpha":
            return {"stars": 500, "open_issues": 10, "url": "https://github.com/test/alpha"}
        elif repo == "test/beta":
            return {"stars": 2000, "open_issues": 25, "url": "https://github.com/test/beta"}
        return None

    def test_update_skills_dry_run_does_not_write_files(self):
        result = update_skills(
            registry_path=self.registry_file,
            history_dir=self.history_dir,
            output_path=self.output_file,
            dry_run=True,
            fetcher=self.mock_fetcher,
            current_time=datetime.datetime(2026, 11, 3, 10, 0, 0, tzinfo=datetime.timezone.utc),
        )

        self.assertFalse(self.output_file.exists())
        self.assertEqual(len(list(self.history_dir.glob("*.json"))), 0)
        self.assertEqual(result["total_count"], 2)
        self.assertEqual(result["week"], "2026-W45")

    def test_update_skills_writes_output_and_snapshot(self):
        result = update_skills(
            registry_path=self.registry_file,
            history_dir=self.history_dir,
            output_path=self.output_file,
            dry_run=False,
            fetcher=self.mock_fetcher,
            current_time=datetime.datetime(2026, 11, 3, 10, 0, 0, tzinfo=datetime.timezone.utc),
        )

        self.assertTrue(self.output_file.exists())
        snapshot_file = self.history_dir / "2026-W45.json"
        self.assertTrue(snapshot_file.exists())

        with open(self.output_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["week"], "2026-W45")
        self.assertEqual(data["total_count"], 2)
        self.assertEqual(data["available_snapshots"], ["2026-W45"])
        # Verify sorting: Beta (2000 stars) should come before Alpha (500 stars)
        self.assertEqual(data["skills"][0]["id"], "repo-beta")
        self.assertEqual(data["skills"][0]["stars"], 2000)
        self.assertEqual(data["skills"][1]["id"], "repo-alpha")
        self.assertEqual(data["skills"][1]["stars"], 500)

        # Verify preservation of bilingual descriptions
        self.assertEqual(data["skills"][0]["description"]["ko"], "베타 한국어 설명입니다.")
        self.assertEqual(data["skills"][1]["description"]["en"], "Alpha english description.")

    def test_update_skills_with_prior_snapshot_computes_delta(self):
        # Create prior snapshot 2026-W44.json
        prior_snapshot = {
            "week": "2026-W44",
            "skills": [
                {"repo": "test/alpha", "stars": 450},
                {"repo": "test/beta", "stars": 1900},
            ],
        }
        (self.history_dir / "2026-W44.json").write_text(json.dumps(prior_snapshot), encoding="utf-8")

        result = update_skills(
            registry_path=self.registry_file,
            history_dir=self.history_dir,
            output_path=self.output_file,
            dry_run=True,
            fetcher=self.mock_fetcher,
            current_time=datetime.datetime(2026, 11, 3, 10, 0, 0, tzinfo=datetime.timezone.utc),
        )

        skills_by_id = {s["id"]: s for s in result["skills"]}
        # Beta: 2000 current - 1900 prior = 100 delta
        self.assertEqual(skills_by_id["repo-beta"]["weekly_stars"], 100)
        # Alpha: 500 current - 450 prior = 50 delta
        self.assertEqual(skills_by_id["repo-alpha"]["weekly_stars"], 50)

    def test_update_skills_graceful_fallback_when_fetcher_returns_none(self):
        # Fetcher fails for all repos (e.g. rate-limit or offline)
        failing_fetcher = lambda repo, token=None: None

        result = update_skills(
            registry_path=self.registry_file,
            history_dir=self.history_dir,
            output_path=self.output_file,
            dry_run=True,
            fetcher=failing_fetcher,
            current_time=datetime.datetime(2026, 11, 3, 10, 0, 0, tzinfo=datetime.timezone.utc),
        )

        self.assertEqual(result["total_count"], 2)
        for s in result["skills"]:
            self.assertEqual(s["stars"], 0)
            self.assertEqual(s["weekly_stars"], 0)


class TestCliArgs(unittest.TestCase):
    def test_parse_args_defaults(self):
        args = parse_args([])
        self.assertFalse(args.dry_run)
        self.assertIn("skills.json", args.output)

    def test_parse_args_flags(self):
        args = parse_args(["--dry-run", "--output", "custom.json"])
        self.assertTrue(args.dry_run)
        self.assertEqual(args.output, "custom.json")


if __name__ == "__main__":
    unittest.main()
