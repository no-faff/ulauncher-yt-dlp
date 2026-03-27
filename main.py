from __future__ import annotations

import logging
import re
import shutil
from pathlib import Path

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import (
    ItemEnterEvent,
    KeywordQueryEvent,
    PreferencesEvent,
    PreferencesUpdateEvent,
)
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

from src.download import start_download
from src.preferences import YtDlpPreferences, get_preferences, validate_preferences

logger = logging.getLogger(__name__)

TIMESTAMP_RE = re.compile(r"^\d+(?::\d{1,2}){0,2}$")
_DENO_PATHS = [Path.home() / ".deno" / "bin", Path("/usr/local/bin"), Path("/usr/bin")]


def _find_deno() -> bool:
    """Check for deno on PATH and in common install locations."""
    if shutil.which("deno"):
        return True
    return any((p / "deno").is_file() for p in _DENO_PATHS)


def _is_timestamp(value: str) -> bool:
    return bool(TIMESTAMP_RE.match(value))


def _parse_query(query: str) -> tuple[str | None, str | None, str | None]:
    """Parse query into (url, start, end). Returns (None, None, None) if invalid."""
    parts = query.strip().split()
    if len(parts) == 1:
        return parts[0], None, None
    if len(parts) == 3 and _is_timestamp(parts[1]) and _is_timestamp(parts[2]):
        return parts[0], parts[1], parts[2]
    return None, None, None


def _message(msg: str, icon: str = "icon") -> RenderResultListAction:
    return RenderResultListAction([
        ExtensionResultItem(
            icon=f"images/{icon}.png",
            name=msg,
            on_enter=DoNothingAction(),
        )
    ])


class YtDlpExtension(Extension):
    typed_preferences: YtDlpPreferences

    def __init__(self) -> None:
        super().__init__()
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class PreferencesEventListener(EventListener):
    def on_event(self, event: PreferencesEvent, extension: YtDlpExtension) -> None:
        extension.typed_preferences = get_preferences(event.preferences)


class PreferencesUpdateEventListener(EventListener):
    def on_event(
        self, event: PreferencesUpdateEvent, extension: YtDlpExtension
    ) -> None:
        preferences = extension.preferences
        preferences[event.id] = event.new_value
        extension.typed_preferences = get_preferences(preferences)


class KeywordQueryEventListener(EventListener):
    def on_event(
        self, event: KeywordQueryEvent, extension: YtDlpExtension
    ) -> RenderResultListAction:
        if not shutil.which("yt-dlp"):
            return _message("yt-dlp is not installed", "error")

        if not _find_deno():
            return RenderResultListAction([
                ExtensionResultItem(
                    icon="images/error.png",
                    name="deno is not installed (required by yt-dlp for YouTube)",
                    description="Press Enter to copy install command. Say yes to add to PATH, then restart Ulauncher.",
                    on_enter=CopyToClipboardAction("curl -fsSL https://deno.land/install.sh | sh"),
                )
            ])

        errors = validate_preferences(extension.typed_preferences)
        if errors:
            return _message(errors[0], "error")

        query = event.get_argument()
        if not query:
            return _message("Usage: yt <url> or yt <url> 1:30 3:45")

        url, start, end = _parse_query(query)
        if url is None:
            return _message("Invalid input. Use: yt <url> or yt <url> start end", "error")

        if start and end:
            description = f"Clip {start} to {end}"
        else:
            description = "Full video"

        return RenderResultListAction([
            ExtensionResultItem(
                icon="images/icon.png",
                name=f"Download: {url}",
                description=description,
                on_enter=ExtensionCustomAction(
                    {"url": url, "start": start, "end": end}
                ),
            )
        ])


class ItemEnterEventListener(EventListener):
    def on_event(self, event: ItemEnterEvent, extension: YtDlpExtension) -> HideWindowAction:
        data = event.get_data()
        prefs = extension.typed_preferences
        start_download(
            url=data["url"],
            download_dir=prefs.download_dir,
            fmt=prefs.default_format,
            start=data.get("start"),
            end=data.get("end"),
            cookies_browser=prefs.cookies_browser,
        )
        return HideWindowAction()


if __name__ == "__main__":
    YtDlpExtension().run()
