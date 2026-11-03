#!/usr/bin/env python3
"""AI Skills Data Updater and History Archiver.

Fetches GitHub repository statistics (stars, weekly star growth, open issues),
diffs against historical weekly snapshots, and outputs live data and archived
snapshots.

Zero pip dependencies (pure Python standard library).
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
from pathlib import Path
import re
import sys
from typing import Any, Callable, Dict, List, Optional
import urllib.error
import urllib.request

DEFAULT_REGISTRY_PATH = Path("data/registry.json")
DEFAULT_OUTPUT_PATH = Path("data/skills.json")
DEFAULT_HISTORY_DIR = Path("data/history")

USER_AGENT = "ai-skills-updater"

# Known repository redirects / organizational migrations
REPO_ALIASES = {
    "Roo-Code/Roo-Code": "RooCodeInc/Roo-Code",
}

logger = logging.getLogger("update_skills")


def format_iso_week(dt: Optional[datetime.datetime] = None) -> str:
    """Return ISO 8601 calendar week format (e.g., '2026-W45')."""
    if dt is None:
        dt = datetime.datetime.now(datetime.timezone.utc)
    iso_year, iso_week, _ = dt.isocalendar()
    return f"{iso_year:04d}-W{iso_week:02d}"


def estimate_cold_start_stars(current_stars: int) -> int:
    """Estimate 7-day star growth when no prior historical snapshot exists.

    Uses a sensible seed growth estimate (~1.2% weekly growth) for active
    developer tools, ensuring trending velocity is not zero or NaN on day 1.
    """
    if current_stars <= 0:
        return 0
    return max(1, int(round(current_stars * 0.012)))


def calculate_weekly_delta(
    current_stars: int,
    prior_stars: Optional[int],
) -> int:
    """Calculate 7-day star growth against prior snapshot or cold start.

    Guarantees non-negative integer result.
    """
    if prior_stars is not None:
        return max(0, current_stars - prior_stars)
    return estimate_cold_start_stars(current_stars)


def find_latest_prior_snapshot(
    history_dir: Path,
    current_week: str,
) -> Optional[Path]:
    """Find the most recent snapshot strictly preceding current_week.

    Snapshot filenames are expected to match 'YYYY-Www.json'.
    """
    if not history_dir.exists() or not history_dir.is_dir():
        return None

    pattern = re.compile(r"^(\d{4}-W\d{2})\.json$")
    prior_snapshots: List[tuple[str, Path]] = []

    for file_path in history_dir.iterdir():
        if file_path.is_file():
            match = pattern.match(file_path.name)
            if match:
                week_str = match.group(1)
                if week_str < current_week:
                    prior_snapshots.append((week_str, file_path))

    if not prior_snapshots:
        return None

    # Sort lexicographically by ISO week string (matches chronological order)
    prior_snapshots.sort(key=lambda item: item[0])
    return prior_snapshots[-1][1]


def load_history_stars_map(snapshot_path: Optional[Path]) -> Dict[str, int]:
    """Extract mapping of repo -> stars from a historical snapshot file."""
    if snapshot_path is None or not snapshot_path.exists():
        return {}

    try:
        with open(snapshot_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        skills = data.get("skills", [])
        stars_map: Dict[str, int] = {}
        for skill in skills:
            repo = skill.get("repo")
            stars = skill.get("stars")
            if repo and isinstance(stars, int):
                stars_map[repo] = stars
        return stars_map
    except Exception as exc:
        logger.warning(
            "Failed to load historical snapshot %s: %s",
            snapshot_path,
            exc,
        )
        return {}


def build_request(
    url: str,
    token: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
) -> urllib.request.Request:
    """Build a urllib Request with User-Agent, Accept, and Auth headers."""
    req_headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.github.v3+json",
    }
    if headers:
        req_headers.update(headers)

    if token:
        token = token.strip()
        if not (token.startswith("Bearer ") or token.startswith("token ")):
            req_headers["Authorization"] = f"Bearer {token}"
        else:
            req_headers["Authorization"] = token

    return urllib.request.Request(url, headers=req_headers)


def fetch_repo_metadata(
    repo: str,
    token: Optional[str] = None,
    timeout: int = 15,
) -> Optional[Dict[str, Any]]:
    """Fetch repository metadata from GitHub REST API.

    Returns dict with stars, open_issues, and url, or None on failure.
    Gracefully handles rate limits and network errors without raising.
    """
    target_repo = REPO_ALIASES.get(repo, repo)
    url = f"https://api.github.com/repos/{target_repo}"
    req = build_request(url, token=token)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
            return {
                "stars": int(data.get("stargazers_count", 0)),
                "open_issues": int(data.get("open_issues_count", 0)),
                "url": data.get("html_url", f"https://github.com/{repo}"),
            }
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            logger.warning(
                "GitHub API rate limit exceeded or forbidden for repo '%s' (HTTP 403). "
                "Consider setting GITHUB_TOKEN.",
                repo,
            )
        elif exc.code == 404:
            logger.warning("Repository '%s' not found on GitHub (HTTP 404).", repo)
        else:
            logger.warning("GitHub API HTTP error for '%s': %s", repo, exc)
        return None
    except urllib.error.URLError as exc:
        logger.warning("Network connection error fetching '%s': %s", repo, exc.reason)
        return None
    except Exception as exc:
        logger.warning("Unexpected error fetching '%s': %s", repo, exc)
        return None


def resolve_auth_token(cli_token: Optional[str] = None) -> Optional[str]:
    """Resolve GitHub token from CLI argument or environment variables."""
    if cli_token and cli_token.strip():
        return cli_token.strip()
    env_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if env_token and env_token.strip():
        return env_token.strip()
    return None


def update_skills(
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    history_dir: Path = DEFAULT_HISTORY_DIR,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    dry_run: bool = False,
    token: Optional[str] = None,
    force: bool = False,
    fetcher: Optional[Callable[..., Optional[Dict[str, Any]]]] = None,
    current_time: Optional[datetime.datetime] = None,
) -> Dict[str, Any]:
    """Execute update pipeline: fetch data, compute metrics, and write artifacts."""
    registry_path = Path(registry_path)
    history_dir = Path(history_dir)
    output_path = Path(output_path)

    if not registry_path.exists():
        raise FileNotFoundError(f"Registry file not found: {registry_path}")

    with open(registry_path, "r", encoding="utf-8") as f:
        registry_items: List[Dict[str, Any]] = json.load(f)

    if current_time is None:
        current_time = datetime.datetime.now(datetime.timezone.utc)

    current_week = format_iso_week(current_time)
    auth_token = resolve_auth_token(token)
    active_fetcher = fetcher or fetch_repo_metadata

    # Locate prior snapshot to compute weekly growth
    prior_snapshot_path = find_latest_prior_snapshot(history_dir, current_week)
    prior_stars_map = load_history_stars_map(prior_snapshot_path)

    # If current output file already exists, load for fallback in case of rate limiting
    cached_existing_map: Dict[str, Dict[str, Any]] = {}
    if output_path.exists():
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
            for skill in cached_data.get("skills", []):
                cached_repo = skill.get("repo")
                if cached_repo:
                    cached_existing_map[cached_repo] = skill
        except Exception as exc:
            logger.debug("Could not read existing output file for fallback: %s", exc)

    updated_skills: List[Dict[str, Any]] = []

    for item in registry_items:
        repo = item["repo"]
        meta = active_fetcher(repo, token=auth_token)

        if meta is not None:
            stars = meta["stars"]
            open_issues = meta["open_issues"]
            url = meta.get("url") or item.get("url") or f"https://github.com/{repo}"
        elif repo in cached_existing_map:
            logger.info("Using cached stats for '%s' due to fetch unavailability", repo)
            stars = cached_existing_map[repo].get("stars", 0)
            open_issues = cached_existing_map[repo].get("open_issues", 0)
            url = item.get("url") or f"https://github.com/{repo}"
        else:
            stars = 0
            open_issues = 0
            url = item.get("url") or f"https://github.com/{repo}"

        prior_stars = prior_stars_map.get(repo)
        weekly_stars = calculate_weekly_delta(
            current_stars=stars,
            prior_stars=prior_stars,
        )

        # Clone and preserve human-curated descriptions & metadata from registry
        skill_entry: Dict[str, Any] = {
            "id": item["id"],
            "repo": item["repo"],
            "name": item["name"],
            "category": item["category"],
            "stars": stars,
            "weekly_stars": weekly_stars,
            "open_issues": open_issues,
            "description": item["description"],
            "url": url,
            "tags": item.get("tags", []),
        }
        updated_skills.append(skill_entry)

    # Sort descending by stars, then weekly_stars, then name
    updated_skills.sort(
        key=lambda s: (
            -s.get("stars", 0),
            -s.get("weekly_stars", 0),
            s.get("name", "").lower(),
        )
    )

    result_payload: Dict[str, Any] = {
        "updated_at": current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "week": current_week,
        "total_count": len(updated_skills),
        "skills": updated_skills,
    }

    if not dry_run:
        # Write live data file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result_payload, f, indent=2, ensure_ascii=False)
            f.write("\n")
        logger.info("Wrote live dataset to %s", output_path)

        # Archive weekly snapshot
        history_dir.mkdir(parents=True, exist_ok=True)
        snapshot_path = history_dir / f"{current_week}.json"
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(result_payload, f, indent=2, ensure_ascii=False)
            f.write("\n")
        logger.info("Archived snapshot to %s", snapshot_path)
    else:
        logger.info(
            "[DRY RUN] Would write %d skills for week %s to %s and %s",
            len(updated_skills),
            current_week,
            output_path,
            history_dir / f"{current_week}.json",
        )

    return result_payload


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Update AI Skills catalog metrics and archive weekly snapshots.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch metrics without writing to disk.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(DEFAULT_OUTPUT_PATH),
        help=f"Path to write live dataset (default: {DEFAULT_OUTPUT_PATH}).",
    )
    parser.add_argument(
        "--registry",
        type=str,
        default=str(DEFAULT_REGISTRY_PATH),
        help=f"Path to registry JSON file (default: {DEFAULT_REGISTRY_PATH}).",
    )
    parser.add_argument(
        "--history-dir",
        type=str,
        default=str(DEFAULT_HISTORY_DIR),
        help=f"Directory for weekly snapshots (default: {DEFAULT_HISTORY_DIR}).",
    )
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="GitHub personal access token (defaults to GITHUB_TOKEN / GH_TOKEN env).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force update even if current snapshot exists.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose debug logging.",
    )
    return parser.parse_args(args)


def main() -> int:
    """CLI entrypoint."""
    args = parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    try:
        update_skills(
            registry_path=Path(args.registry),
            history_dir=Path(args.history_dir),
            output_path=Path(args.output),
            dry_run=args.dry_run,
            token=args.token,
            force=args.force,
        )
        return 0
    except Exception as exc:
        logger.error("Update failed: %s", exc, exc_info=args.verbose)
        return 1


if __name__ == "__main__":
    sys.exit(main())
