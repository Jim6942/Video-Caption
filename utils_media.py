import os, re, tempfile, shutil, subprocess
from pathlib import Path
from typing import Optional, Tuple

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
import imageio_ffmpeg

_YT_ID_RE = re.compile(r'(?:v=|/)([0-9A-Za-z_-]{11})')

def is_youtube_url(url: str) -> bool:
    return "youtube.com/watch?" in url or "youtu.be/" in url

def _ffmpeg_bin() -> str:
    # Portable ffmpeg path — no system install needed
    return imageio_ffmpeg.get_ffmpeg_exe()

def _run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{p.stdout}")

def _download_audio_best(url: str, workdir: str, client: str) -> Path:
    """
    Download best *audio only* (no postprocessors). We convert to WAV ourselves.
    """
    Path(workdir).mkdir(parents=True, exist_ok=True)
    out = str(Path(workdir) / "audio.%(ext)s")
    ffmpeg_path = _ffmpeg_bin()

    ydl_opts = {
        "outtmpl": out,
        "format": "bestaudio/best",          # audio only (avoids SABR video headaches)
        "noplaylist": True,
        "quiet": True,
        "prefer_ffmpeg": True,
        "ffmpeg_location": os.path.dirname(ffmpeg_path) or ffmpeg_path,
        # Try specific player_client; some expose better direct audio URLs
        "extractor_args": {"youtube": {"player_client": [client]}},
        "http_headers": {"User-Agent": "Mozilla/5.0"},
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Resolve actual downloaded filename by glob
        for p in Path(workdir).glob("audio.*"):
            if p.is_file():
                return p
        # fallback: derive from reported extension
        ext = info.get("ext", "m4a")
        candidate = Path(workdir) / f"audio.{ext}"
        if candidate.exists():
            return candidate
        raise RuntimeError("Audio file not found after download.")

def _convert_to_wav(src_audio: Path, dst_wav: Path) -> None:
    ffmpeg_path = _ffmpeg_bin()
    _run([
        ffmpeg_path, "-y",
        "-i", str(src_audio),
        "-ac", "1",
        "-ar", "16000",
        str(dst_wav),
    ])

def ensure_youtube_wav(url: str) -> Tuple[str, str]:
    """
    Download YouTube audio and convert to 16k mono WAV (no cookies).
    Returns (wav_path, tempdir) — caller must cleanup tempdir.
    Raises with a clear message if blocked.
    """
    td = tempfile.mkdtemp(prefix="vcap_")
    last_err: Optional[Exception] = None
    for client in ["web", "tv", "ios", "android"]:
        try:
            audio_file = _download_audio_best(url, td, client)
            wav_path = Path(td) / "audio.wav"
            _convert_to_wav(audio_file, wav_path)
            return str(wav_path), td
        except DownloadError as e:
            last_err = e
        except Exception as e:
            last_err = e

    # Cleanup on failure and raise a simple, user-facing reason
    shutil.rmtree(td, ignore_errors=True)
    msg = "This video appears to be age- or region-gated (or otherwise blocked). Try another YouTube link."
    if last_err:
        msg += f" [yt-dlp: {last_err}]"
    raise RuntimeError(msg)
