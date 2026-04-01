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
