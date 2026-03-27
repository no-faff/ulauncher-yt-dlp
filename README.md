# Ulauncher yt-dlp

A [Ulauncher](https://ulauncher.io/) extension for downloading videos with [yt-dlp](https://github.com/yt-dlp/yt-dlp). Supports full videos and clips with timestamps.

## Features

- Download any video yt-dlp supports (YouTube, Vimeo, hundreds more)
- Clip extraction with start and end timestamps
- Desktop notification on completion or failure
- Configurable download directory and format

## Requirements

- Ulauncher 6 (Extension API v2)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [ffmpeg](https://ffmpeg.org/) (needed for merging video and audio, clips and audio extraction)
- [Deno](https://deno.land/) (needed by yt-dlp for YouTube and other sites)
- notify-send (usually already installed on Linux desktops)

### Installing yt-dlp and ffmpeg

```bash
# Fedora
sudo dnf install yt-dlp ffmpeg

# Ubuntu/Debian
sudo apt install yt-dlp ffmpeg

# Arch
sudo pacman -S yt-dlp ffmpeg

# Or with pip (yt-dlp only, install ffmpeg separately through your package manager)
pip install yt-dlp
```

### Installing Deno

yt-dlp needs Deno to download from YouTube and some other sites. Run this in a terminal:

```bash
curl -fsSL https://deno.land/install.sh | sh
```

The installer will ask two questions:

1. **"Edit shell configs to add deno to the PATH?"** - type **Y** and press Enter. This is required.
2. **"Set up completions?"** - just press Enter to skip. You don't need this.

Then close and reopen your terminal so the PATH change takes effect.

## Install

Open Ulauncher preferences, go to Extensions, click "Add extension" and paste:

```
https://github.com/no-faff/ulauncher-yt-dlp
```

## Usage

| Command | What it does |
|---|---|
| `yt <url>` | Download full video |
| `yt <url> 1:30 3:45` | Download clip from 1:30 to 3:45 |
| `yta <url>` | Download as MP3 |
| `yta <url> 1:30 3:45` | Download clip as MP3 |

Timestamps accept `m:ss`, `h:mm:ss` or plain seconds.

Downloads run in the background. A desktop notification appears when the download finishes (or fails).

## Settings

| Setting | Description | Default |
|---|---|---|
| Download directory | Where files are saved | `~/Downloads` |
| Default format | Best quality, MP4 or audio only | MP4 |
| Max resolution | Limit video resolution to save bandwidth and disk space | Best available |
| Subtitles | Off, embed in video, save as SRT, save as TXT, or both SRT and TXT | Off |
| Subtitle language | Language code (e.g. en, fr, de, es) | `en` |
| SponsorBlock | Remove or mark sponsor segments in YouTube videos | Off |
| Embed metadata | Embed title, uploader, thumbnail in the file | No |
| Filename template | yt-dlp [output template](https://github.com/yt-dlp/yt-dlp#output-template) | `%(title)s.%(ext)s` |
| Browser cookies | For private or restricted videos. Set to the browser where you're logged in | None |

## Also by No Faff

- [Find](https://github.com/no-faff/ulauncher-find) - find files and directories by name

## Licence

MIT
