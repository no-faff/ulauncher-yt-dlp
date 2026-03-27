from __future__ import annotations

import logging
import os
import subprocess
import threading
from pathlib import Path

from src.enums import Format

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
    download_dir: Path,
    fmt: Format,
    start: str | None = None,
    end: str | None = None,
    cookies_browser: str | None = None,
) -> list[str]:
    cmd = ["yt-dlp"]

    if cookies_browser:
        cmd += ["--cookies-from-browser", cookies_browser]

    if fmt == Format.MP4:
        cmd += ["--merge-output-format", "mp4"]
    elif fmt == Format.AUDIO:
        cmd.append("-x")

    if start and end:
        cmd += ["--download-sections", f"*{start}-{end}"]

    cmd += ["-o", str(download_dir / "%(title)s.%(ext)s")]
    cmd.append(url)

    return cmd


def _notify(title: str, body: str, icon: str = "dialog-information") -> None:
    try:
        subprocess.run(
            ["notify-send", title, body, f"--icon={icon}"],
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        logger.warning("Could not send desktop notification")


def _run_download(cmd: list[str]) -> None:
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
            _notify("Download complete", "Video saved to downloads folder")
        else:
            stderr = result.stderr.strip()
            error = stderr.splitlines()[-1] if stderr else "Unknown error"
            _notify("Download failed", error, icon="dialog-error")
            logger.error("yt-dlp failed: %s", stderr)
    except subprocess.TimeoutExpired:
        _notify("Download failed", "Timed out after 10 minutes", icon="dialog-error")
        logger.error("yt-dlp timed out")


def start_download(
    url: str,
    download_dir: Path,
    fmt: Format,
    start: str | None = None,
    end: str | None = None,
    cookies_browser: str | None = None,
) -> None:
    cmd = _build_command(url, download_dir, fmt, start, end, cookies_browser)
    thread = threading.Thread(target=_run_download, args=(cmd,), daemon=True)
    thread.start()
