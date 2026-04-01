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
