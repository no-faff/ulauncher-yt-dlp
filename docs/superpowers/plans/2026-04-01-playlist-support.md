# Playlist support implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Support playlist downloads with automatic subfolder organisation and numbered filenames.

**Architecture:** Add playlist detection using yt-dlp's extractor registry (no network call). Pass detection result through the existing action data flow. Adjust the output template in `_build_command` when a playlist is detected. Always pass `--no-playlist` so ambiguous URLs download a single video.

**Tech Stack:** Python, yt-dlp (extractor API + CLI flags)

---

### Task 1: Add playlist detection module

**Files:**
- Create: `src/playlist.py`
- Create: `tests/test_playlist.py`

This module wraps yt-dlp's extractor registry to determine whether a URL points to a playlist. The extractor list is cached after first load (~0.19s cold, <1ms warm).

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_playlist.py
from src.playlist import is_playlist_url


def test_youtube_playlist():
    assert is_playlist_url("https://www.youtube.com/playlist?list=PLRqwX-V7Uu6ZiZxtDDRCi6uhfTH4FilpH") is True


def test_youtube_single_video():
    assert is_playlist_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is False


def test_youtube_ambiguous_video_with_list_param():
    """watch?v=...&list=... is ambiguous. --no-playlist forces single video, so treat as non-playlist."""
    assert is_playlist_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLxxx") is False


def test_soundcloud_set():
    assert is_playlist_url("https://soundcloud.com/artist/sets/my-set") is True


def test_soundcloud_track():
    assert is_playlist_url("https://soundcloud.com/artist/track") is False


def test_bandcamp_album():
    assert is_playlist_url("https://artist.bandcamp.com/album/my-album") is True


def test_bandcamp_track():
    assert is_playlist_url("https://artist.bandcamp.com/track/my-track") is False


def test_vimeo_showcase():
    assert is_playlist_url("https://vimeo.com/showcase/123456") is True


def test_vimeo_single():
    assert is_playlist_url("https://vimeo.com/123456789") is False


def test_dailymotion_playlist():
    assert is_playlist_url("https://www.dailymotion.com/playlist/x5nmbq") is True


def test_dailymotion_video():
    assert is_playlist_url("https://www.dailymotion.com/video/x5e9eog") is False


def test_empty_string():
    assert is_playlist_url("") is False


def test_nonsense_string():
    assert is_playlist_url("not a url at all") is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/fred/projects/ulauncher-yt-dlp && python -m pytest tests/test_playlist.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.playlist'`

- [ ] **Step 3: Write the implementation**

```python
# src/playlist.py
from __future__ import annotations

from urllib.parse import parse_qs, urlparse

_PLAYLIST_KEYWORDS = frozenset({
    "album", "channel", "collection", "favorites", "list", "playlist", "set", "tab",
})

_extractors: list | None = None


def _get_extractors() -> list:
    global _extractors
    if _extractors is None:
        import yt_dlp.extractor
        _extractors = list(yt_dlp.extractor.gen_extractors())
    return _extractors


def is_playlist_url(url: str) -> bool:
    """Check whether a URL points to a playlist using yt-dlp's extractor registry.

    Uses cached regex matching only (no network call). Returns False for
    ambiguous URLs that contain both a video ID and a playlist parameter.
    """
    if not url:
        return False

    # Ambiguous YouTube URL: has both v= and list=. --no-playlist will
    # force single-video behaviour, so report it as non-playlist.
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    if qs.get("v") and qs.get("list"):
        return False

    for ie in _get_extractors():
        if ie.suitable(url):
            if ie.IE_NAME == "generic":
                return False
            name = ie.IE_NAME.lower()
            cls_name = ie.__class__.__name__.lower()
            return any(kw in name for kw in _PLAYLIST_KEYWORDS) or any(
                kw in cls_name for kw in _PLAYLIST_KEYWORDS
            )

    return False
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/fred/projects/ulauncher-yt-dlp && python -m pytest tests/test_playlist.py -v`
Expected: All 13 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/playlist.py tests/test_playlist.py
git commit -m "feat: add playlist URL detection via yt-dlp extractors"
```

---

### Task 2: Update input parsing to handle playlists

**Files:**
- Modify: `main.py:44-51` (`_parse_query`)
- Create: `tests/test_parse_query.py`

`_parse_query` currently returns `(url, start, end)`. Add a fourth value `is_playlist`. Reject the combination of timestamps + playlist URL.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_parse_query.py
from unittest.mock import patch

from main import _parse_query


@patch("main.is_playlist_url", return_value=False)
def test_single_video_url(mock_pl):
    url, start, end, is_playlist = _parse_query("https://youtube.com/watch?v=abc")
    assert url == "https://youtube.com/watch?v=abc"
    assert start is None
    assert end is None
    assert is_playlist is False


@patch("main.is_playlist_url", return_value=False)
def test_clip_with_timestamps(mock_pl):
    url, start, end, is_playlist = _parse_query("https://youtube.com/watch?v=abc 1:30 3:45")
    assert url == "https://youtube.com/watch?v=abc"
    assert start == "1:30"
    assert end == "3:45"
    assert is_playlist is False


@patch("main.is_playlist_url", return_value=True)
def test_playlist_url(mock_pl):
    url, start, end, is_playlist = _parse_query("https://youtube.com/playlist?list=PLxxx")
    assert url == "https://youtube.com/playlist?list=PLxxx"
    assert start is None
    assert end is None
    assert is_playlist is True


@patch("main.is_playlist_url", return_value=True)
def test_playlist_with_timestamps_rejected(mock_pl):
    """Timestamps are incompatible with playlists."""
    url, start, end, is_playlist = _parse_query("https://youtube.com/playlist?list=PLxxx 1:30 3:45")
    assert url is None


@patch("main.is_playlist_url", return_value=False)
def test_invalid_input(mock_pl):
    url, start, end, is_playlist = _parse_query("url arg1")
    assert url is None


@patch("main.is_playlist_url", return_value=False)
def test_empty_input(mock_pl):
    url, start, end, is_playlist = _parse_query("")
    assert url is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/fred/projects/ulauncher-yt-dlp && python -m pytest tests/test_parse_query.py -v`
Expected: FAIL — `_parse_query` returns 3 values, tests expect 4

- [ ] **Step 3: Update `_parse_query` in `main.py`**

Add the import at the top of `main.py`:

```python
from src.playlist import is_playlist_url
```

Replace `_parse_query` (lines 44-51) with:

```python
def _parse_query(query: str) -> tuple[str | None, str | None, str | None, bool]:
    """Parse query into (url, start, end, is_playlist). Returns (None, None, None, False) if invalid."""
    parts = query.strip().split()
    if not parts:
        return None, None, None, False
    url = parts[0]
    playlist = is_playlist_url(url)
    if len(parts) == 1:
        return url, None, None, playlist
    if len(parts) == 3 and _is_timestamp(parts[1]) and _is_timestamp(parts[2]):
        if playlist:
            return None, None, None, False
        return url, parts[1], parts[2], False
    return None, None, None, False
```

- [ ] **Step 4: Update callers of `_parse_query` in `KeywordQueryEventListener.on_event`**

Replace line 122:

```python
        url, start, end = _parse_query(query)
```

with:

```python
        url, start, end, is_playlist = _parse_query(query)
```

Replace the description block (lines 130-136):

```python
        if start and end:
            description = f"Clip {start} to {end}"
        elif audio_only:
            description = "MP3"
        else:
            description = "Full video"
```

with:

```python
        if start and end:
            description = f"Clip {start} to {end}"
        elif is_playlist:
            description = "Playlist"
        elif audio_only:
            description = "MP3"
        else:
            description = "Full video"
```

Update the action data dict (line 143):

```python
                    {"url": url, "start": start, "end": end, "audio": audio_only}
```

to:

```python
                    {"url": url, "start": start, "end": end, "audio": audio_only, "playlist": is_playlist}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /home/fred/projects/ulauncher-yt-dlp && python -m pytest tests/test_parse_query.py -v`
Expected: All 6 tests PASS

- [ ] **Step 6: Commit**

```bash
git add main.py tests/test_parse_query.py
git commit -m "feat: detect playlists in input parsing"
```

---

### Task 3: Update download command to support playlists

**Files:**
- Modify: `src/download.py:26-71` (`_build_command`), `src/download.py:150-165` (`start_download`)
- Create: `tests/test_download.py`

Add `is_playlist` parameter. When true, use the playlist output template and always pass `--no-playlist`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_download.py
from pathlib import Path
from unittest.mock import patch

from src.download import _build_command
from src.enums import Format, SponsorBlock, Subtitles
from src.preferences import YtDlpPreferences


def _default_prefs(**overrides) -> YtDlpPreferences:
    defaults = {
        "download_dir": Path("/tmp/downloads"),
        "default_format": Format.MP4,
        "max_resolution": 0,
        "subtitles": Subtitles.OFF,
        "sub_lang": "en",
        "sponsorblock": SponsorBlock.OFF,
        "embed_metadata": False,
        "filename_template": "%(title)s.%(ext)s",
        "cookies_browser": None,
    }
    defaults.update(overrides)
    return YtDlpPreferences(**defaults)


def test_single_video_has_no_playlist():
    cmd = _build_command("https://youtube.com/watch?v=abc", _default_prefs())
    assert "--no-playlist" in cmd
    output_arg = cmd[cmd.index("-o") + 1]
    assert "playlist_title" not in output_arg
    assert "playlist_index" not in output_arg


def test_single_video_uses_filename_template():
    cmd = _build_command("https://youtube.com/watch?v=abc", _default_prefs())
    output_arg = cmd[cmd.index("-o") + 1]
    assert output_arg == "/tmp/downloads/%(title)s.%(ext)s"


def test_playlist_uses_subfolder_template():
    cmd = _build_command("https://youtube.com/playlist?list=PLxxx", _default_prefs(), is_playlist=True)
    output_arg = cmd[cmd.index("-o") + 1]
    assert output_arg == "/tmp/downloads/%(playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s"


def test_playlist_has_no_playlist_flag():
    cmd = _build_command("https://youtube.com/playlist?list=PLxxx", _default_prefs(), is_playlist=True)
    assert "--no-playlist" in cmd


def test_clip_has_no_playlist():
    cmd = _build_command("https://youtube.com/watch?v=abc", _default_prefs(), start="1:30", end="3:45")
    assert "--no-playlist" in cmd
    assert "--download-sections" in cmd
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/fred/projects/ulauncher-yt-dlp && python -m pytest tests/test_download.py -v`
Expected: FAIL — `_build_command` does not accept `is_playlist`, and `--no-playlist` is not in the output

- [ ] **Step 3: Update `_build_command` in `src/download.py`**

Update the function signature (line 26-31):

```python
def _build_command(
    url: str,
    prefs: YtDlpPreferences,
    start: str | None = None,
    end: str | None = None,
    is_playlist: bool = False,
) -> list[str]:
```

Add `--no-playlist` after `cmd = ["yt-dlp"]` (after line 32):

```python
    cmd = ["yt-dlp", "--no-playlist"]
```

Replace the output template line (line 68):

```python
    cmd += ["-o", str(prefs.download_dir / prefs.filename_template)]
```

with:

```python
    if is_playlist:
        template = "%(playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s"
    else:
        template = prefs.filename_template
    cmd += ["-o", str(prefs.download_dir / template)]
```

- [ ] **Step 4: Update `start_download` in `src/download.py`**

Update the function signature (line 150-155):

```python
def start_download(
    url: str,
    prefs: YtDlpPreferences,
    start: str | None = None,
    end: str | None = None,
    is_playlist: bool = False,
) -> None:
```

Update the `_build_command` call (line 156):

```python
    cmd = _build_command(url, prefs, start, end, is_playlist=is_playlist)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /home/fred/projects/ulauncher-yt-dlp && python -m pytest tests/test_download.py -v`
Expected: All 5 tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/download.py tests/test_download.py
git commit -m "feat: playlist output template and --no-playlist flag"
```

---

### Task 4: Wire playlist flag through the event listener

**Files:**
- Modify: `main.py:149-161` (`ItemEnterEventListener`)

- [ ] **Step 1: Update `ItemEnterEventListener.on_event` in `main.py`**

Replace the `start_download` call (lines 155-160):

```python
        start_download(
            url=data["url"],
            prefs=prefs,
            start=data.get("start"),
            end=data.get("end"),
        )
```

with:

```python
        start_download(
            url=data["url"],
            prefs=prefs,
            start=data.get("start"),
            end=data.get("end"),
            is_playlist=data.get("playlist", False),
        )
```

- [ ] **Step 2: Update the hint text**

Replace the hint text (lines 115-119):

```python
                    name="yt <url> to download, or yt <url> 1:30 3:45 to grab a clip",
                    description="Timestamps: m:ss, h:mm:ss or plain seconds",
```

with:

```python
                    name="yt <url> to download, or yt <url> 1:30 3:45 to grab a clip",
                    description="Playlist URLs download into a subfolder. Timestamps: m:ss, h:mm:ss or plain seconds",
```

- [ ] **Step 3: Run all tests**

Run: `cd /home/fred/projects/ulauncher-yt-dlp && python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: wire playlist flag through event listener"
```

---

### Task 5: Manual smoke test

- [ ] **Step 1: Restart Ulauncher**

```bash
pkill ulauncher && ulauncher &
```

- [ ] **Step 2: Test single video**

Type `yt https://www.youtube.com/watch?v=dQw4w9WgXcQ` — should show "Full video" description, download a single file to the download directory.

- [ ] **Step 3: Test playlist**

Type `yt https://www.youtube.com/playlist?list=PLRqwX-V7Uu6ZiZxtDDRCi6uhfTH4FilpH` — should show "Playlist" description, download into a subfolder with numbered files.

- [ ] **Step 4: Test ambiguous URL**

Type `yt https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLRqwX-V7Uu6ZiZxtDDRCi6uhfTH4FilpH` — should show "Full video" (not "Playlist"), download a single file.

- [ ] **Step 5: Test playlist + timestamps rejected**

Type `yt https://www.youtube.com/playlist?list=PLxxx 1:30 3:45` — should show the "Invalid input" error.

- [ ] **Step 6: Commit any fixes, then final commit**

```bash
git add -A
git commit -m "feat: playlist download support with subfolder organisation"
```
