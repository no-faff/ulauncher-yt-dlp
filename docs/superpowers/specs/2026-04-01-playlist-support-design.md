# Playlist support

## Summary

Add playlist download support. Playlist URLs get a subfolder with numbered files. Single video behaviour is unchanged. `--no-playlist` is always passed so ambiguous URLs (video+list combo) download one video.

## Detection

Use yt-dlp's extractor registry to match the URL against known extractors via regex (no network call, ~0.3s). If the matching extractor is a playlist type (name contains "playlist", "album", "set", "collection", etc.), treat it as a playlist. This covers all yt-dlp-supported sites, not just YouTube.

This is the same mechanism yt-dlp itself uses internally to decide which extractor to run. The only difference vs calling `--flat-playlist` is that we skip the network request (which adds 3-4s latency).

## Output templates

- **Single video:** `<download_dir>/<filename_template>` (unchanged, uses existing preference)
- **Playlist:** `<download_dir>/%(playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s`

The playlist template is not configurable. The user's filename template preference only applies to single videos.

## Constraints

- Clips (timestamps) are incompatible with playlists. Show an error if both are provided.
- `--no-playlist` is always passed regardless of URL type.

## File changes

### main.py

- Add `_is_playlist_url(url: str) -> bool` using yt-dlp's extractor registry. Import `yt_dlp`, create a `YoutubeDL` instance, iterate `_ies` and regex-match. Check if the first matching extractor name suggests a playlist type.
- `_parse_query`: return a fourth value `is_playlist` based on detection. Reject timestamps + playlist URL combos.
- Update result item description: show "Playlist" when detected.
- Pass `is_playlist` in the `ExtensionCustomAction` data dict.
- Pass `is_playlist` through to `start_download`.

### download.py

- `_build_command`: accept `is_playlist: bool` parameter. When true, use the playlist output template. Always pass `--no-playlist`.
- `start_download`: accept and forward `is_playlist` parameter.

### No changes

- No new preferences, enums or manifest changes.
- `preferences.py` unchanged.
