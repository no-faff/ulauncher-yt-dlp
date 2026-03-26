# yt-dlp

A [Ulauncher](https://ulauncher.io/) extension for downloading videos with [yt-dlp](https://github.com/yt-dlp/yt-dlp). Supports full videos and clips with timestamps.

## Features

- Download any video yt-dlp supports (YouTube, Vimeo, hundreds more)
- Clip extraction with start and end timestamps
- Desktop notification on completion or failure
- Configurable download directory and format

## Requirements

- Ulauncher 6 (Extension API v2)
- yt-dlp
- notify-send (usually pre-installed on Linux desktops)

Install yt-dlp if you don't have it:

```bash
# Fedora
sudo dnf install yt-dlp

# Ubuntu/Debian
sudo apt install yt-dlp

# pip
pip install yt-dlp
```

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

Timestamps accept `m:ss`, `h:mm:ss` or plain seconds.

Downloads run in the background. A desktop notification appears when the download finishes (or fails).

## Settings

| Setting | Description | Default |
|---|---|---|
| Download directory | Where files are saved | `~/Downloads` |
| Default format | Best quality, MP4 or audio only | Best quality |

## Also by No Faff

- [Find](https://github.com/no-faff/ulauncher-find) - find files and directories by name

## Licence

MIT
