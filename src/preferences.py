from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from src.enums import Format, SponsorBlock, Subtitles

logger = logging.getLogger(__name__)

PREFS_FILE = Path.home() / ".config" / "ulauncher" / "ext_preferences" / "com.github.no-faff.ulauncher-yt-dlp.json"


COOKIES_BROWSERS = {0: None, 1: "firefox", 2: "chrome", 3: "brave", 4: "edge", 5: "chromium"}


@dataclass
class YtDlpPreferences:
    download_dir: Path
    default_format: Format
    max_resolution: int
    subtitles: Subtitles
    sub_lang: str
    sponsorblock: SponsorBlock
    embed_metadata: bool
    filename_template: str
    cookies_browser: str | None


def get_preferences(raw: dict[str, str]) -> YtDlpPreferences:
    return YtDlpPreferences(
        download_dir=Path(raw["download_dir"]).expanduser(),
        default_format=Format(int(raw["default_format"])),
        max_resolution=int(raw.get("max_resolution", "0")),
        subtitles=Subtitles(int(raw.get("subtitles", "0"))),
        sub_lang=raw.get("sub_lang", "en").strip() or "en",
        sponsorblock=SponsorBlock(int(raw.get("sponsorblock", "0"))),
        embed_metadata=bool(int(raw.get("embed_metadata", "0"))),
        filename_template=raw.get("filename_template", "%(title)s.%(ext)s").strip() or "%(title)s.%(ext)s",
        cookies_browser=COOKIES_BROWSERS.get(int(raw.get("cookies_browser", "0"))),
    )


def load_preferences() -> YtDlpPreferences:
    """Read preferences directly from disk to ensure saved values are used."""
    try:
        data = json.loads(PREFS_FILE.read_text())
        return get_preferences(data["preferences"])
    except (OSError, json.JSONDecodeError, KeyError):
        logger.warning("Could not read preferences file, using defaults")
        return get_preferences({
            "download_dir": "~/Downloads", "default_format": "1",
            "max_resolution": "0", "subtitles": "0", "sub_lang": "en",
            "sponsorblock": "0", "embed_metadata": "0",
            "filename_template": "%(title)s.%(ext)s", "cookies_browser": "0",
        })


def validate_preferences(preferences: YtDlpPreferences) -> list[str]:
    errors = []
    if not preferences.download_dir.is_dir():
        errors.append(f"Download directory '{preferences.download_dir}' does not exist.")
    return errors
