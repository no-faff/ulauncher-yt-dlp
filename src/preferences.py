from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.enums import Format


@dataclass
class YtDlpPreferences:
    download_dir: Path
    default_format: Format


def get_preferences(raw: dict[str, str]) -> YtDlpPreferences:
    return YtDlpPreferences(
        download_dir=Path(raw["download_dir"]).expanduser(),
        default_format=Format(int(raw["default_format"])),
    )


def validate_preferences(preferences: YtDlpPreferences) -> list[str]:
    errors = []
    if not preferences.download_dir.is_dir():
        errors.append(f"Download directory '{preferences.download_dir}' does not exist.")
    return errors
