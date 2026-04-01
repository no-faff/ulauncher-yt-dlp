from pathlib import Path

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
