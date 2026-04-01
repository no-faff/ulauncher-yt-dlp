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
