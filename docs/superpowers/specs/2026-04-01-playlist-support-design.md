# Playlist support

## Summary

Add playlist download support. Playlist URLs get a subfolder with numbered files. Single video behaviour is unchanged. `--no-playlist` is always passed so ambiguous URLs (video+list combo) download one video.

## Detection

URL heuristic: check for `/playlist?` in the URL. Cheap, no network call, covers YouTube which is the primary use case. Non-YouTube playlist URLs that don't match the pattern still download fine but land flat in the download directory.

## Output templates

- **Single video:** `<download_dir>/<filename_template>` (unchanged, uses existing preference)
- **Playlist:** `<download_dir>/%(playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s`

The playlist template is not configurable. The user's filename template preference only applies to single videos.

## Constraints

- Clips (timestamps) are incompatible with playlists. Show an error if both are provided.
- `--no-playlist` is always passed regardless of URL type.

## File changes

### main.py

- Add `_is_playlist_url(url: str) -> bool` heuristic (checks for `/playlist?` in URL).
- `_parse_query`: return a fourth value `is_playlist` based on the heuristic. Reject timestamps + playlist URL combos.
- Update result item description: show "Playlist" when detected.
- Pass `is_playlist` in the `ExtensionCustomAction` data dict.
- Pass `is_playlist` through to `start_download`.

### download.py

- `_build_command`: accept `is_playlist: bool` parameter. When true, use the playlist output template. Always pass `--no-playlist`.
- `start_download`: accept and forward `is_playlist` parameter.

### No changes

- No new preferences, enums or manifest changes.
- `preferences.py` unchanged.
