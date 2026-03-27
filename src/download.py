from __future__ import annotations

import logging
import os
import subprocess
import threading
from pathlib import Path

from src.enums import Format, SponsorBlock, Subtitles
from src.preferences import YtDlpPreferences

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 600


def _get_env() -> dict[str, str]:
    """Return a copy of the environment with ~/.deno/bin on PATH."""
    env = os.environ.copy()
    deno_bin = str(Path.home() / ".deno" / "bin")
    if deno_bin not in env.get("PATH", ""):
        env["PATH"] = deno_bin + ":" + env.get("PATH", "")
    return env


def _build_command(
    url: str,
    prefs: YtDlpPreferences,
    start: str | None = None,
    end: str | None = None,
) -> list[str]:
    cmd = ["yt-dlp"]

    if prefs.cookies_browser:
        cmd += ["--cookies-from-browser", prefs.cookies_browser]

    # Format
    if prefs.default_format == Format.MP4:
        cmd += ["--merge-output-format", "mp4"]
    elif prefs.default_format == Format.AUDIO:
        cmd += ["-x", "--audio-format", "mp3"]

    # Resolution limit
    if prefs.max_resolution:
        cmd += ["-S", f"res:{prefs.max_resolution}"]

    # Clip
    if start and end:
        cmd += ["--download-sections", f"*{start}-{end}", "--force-keyframes-at-cuts"]

    # Subtitles
    if prefs.subtitles != Subtitles.OFF:
        cmd += ["--sub-langs", prefs.sub_lang, "--write-subs", "--write-auto-subs",
                "--sub-format", "srt", "--convert-subs", "srt"]
        if prefs.subtitles == Subtitles.EMBED:
            cmd.append("--embed-subs")

    # SponsorBlock
    if prefs.sponsorblock == SponsorBlock.REMOVE:
        cmd += ["--sponsorblock-remove", "all"]
    elif prefs.sponsorblock == SponsorBlock.MARK:
        cmd += ["--sponsorblock-mark", "all"]

    # Metadata
    if prefs.embed_metadata:
        cmd += ["--embed-metadata", "--embed-thumbnail"]

    cmd += ["-o", str(prefs.download_dir / prefs.filename_template)]
    cmd.append(url)

    return cmd


def _notify(title: str, body: str, icon: str = "dialog-information", folder: str | None = None) -> None:
    def _do_notify() -> None:
        try:
            cmd = ["notify-send", title, body, f"--icon={icon}"]
            if folder:
                cmd += ["--action", "default=Open folder"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if folder and result.stdout.strip() == "default":
                subprocess.Popen(["xdg-open", folder])
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("Could not send desktop notification")

    # Run in its own thread so the action listener doesn't block
    threading.Thread(target=_do_notify, daemon=True).start()


def _run_download(cmd: list[str], download_dir: str, txt_mode: str = "none") -> None:
    logger.info("Running: %s", cmd)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            env=_get_env(),
        )
        if result.returncode == 0:
            if txt_mode == "txt_only":
                _handle_txt_subs(download_dir, copy=False)
            elif txt_mode == "srt_and_txt":
                _handle_txt_subs(download_dir, copy=True)
            _notify("Download complete", f"Saved to {download_dir}", folder=download_dir)
        else:
            stderr = result.stderr.strip()
            error = stderr.splitlines()[-1] if stderr else "Unknown error"
            _notify("Download failed", error, icon="dialog-error")
            logger.error("yt-dlp failed: %s", stderr)
    except subprocess.TimeoutExpired:
        _notify("Download failed", "Timed out after 10 minutes", icon="dialog-error")
        logger.error("yt-dlp timed out")


def _handle_txt_subs(download_dir: str, copy: bool = False) -> None:
    """Convert or copy SRT files to TXT. If copy=True, keeps the SRT."""
    import glob
    import shutil
    for srt_file in glob.glob(os.path.join(download_dir, "*.srt")):
        txt_file = srt_file.rsplit(".", 1)[0] + ".txt"
        if os.path.exists(txt_file):
            continue
        try:
            if copy:
                shutil.copy2(srt_file, txt_file)
            else:
                os.rename(srt_file, txt_file)
        except OSError:
            logger.warning("Could not create .txt from %s", srt_file)


def start_download(
    url: str,
    prefs: YtDlpPreferences,
    start: str | None = None,
    end: str | None = None,
) -> None:
    cmd = _build_command(url, prefs, start, end)
    download_dir = str(prefs.download_dir)
    if prefs.subtitles == Subtitles.TXT:
        txt_mode = "txt_only"
    elif prefs.subtitles == Subtitles.SRT_AND_TXT:
        txt_mode = "srt_and_txt"
    else:
        txt_mode = "none"
    thread = threading.Thread(target=_run_download, args=(cmd, download_dir, txt_mode), daemon=True)
    thread.start()
