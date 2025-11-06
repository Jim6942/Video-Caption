import os
from pathlib import Path
from typing import List
import argparse
from dotenv import load_dotenv
from tenacity import retry, wait_exponential_jitter, stop_after_attempt, retry_if_exception_type

import assemblyai as aai
from srt_utils import Word, words_to_srt

load_dotenv()
AAI_KEY = os.getenv("ASSEMBLYAI_API_KEY")
if not AAI_KEY:
    raise RuntimeError("ASSEMBLYAI_API_KEY not set")
aai.settings.api_key = AAI_KEY

transcriber = aai.Transcriber()

@retry(wait=wait_exponential_jitter(initial=1, max=10),
       stop=stop_after_attempt(6),
       retry=retry_if_exception_type(Exception))
def _transcribe_with_words(source: str) -> aai.Transcript:
    cfg = aai.TranscriptionConfig(
        punctuate=True,
        format_text=True,
        disfluencies=False,
        speech_model="best",
    )
    return transcriber.transcribe(source, config=cfg)

def _words_from_transcript(t: aai.Transcript) -> List[Word]:
    if not getattr(t, "words", None):
        raise RuntimeError("Word timestamps missing; cannot build SRT.")
    out: List[Word] = []
    for w in t.words:
        s = int(round(getattr(w, "start", 0)))
        e = int(round(getattr(w, "end", 0)))
        if s < 10000 and e < 10000:
            s, e = s * 1000, e * 1000
        out.append(Word(w.text, s, e))
    return out

def transcribe_to_txt(source: str, dst_txt: str) -> None:
    t = _transcribe_with_words(source)
    Path(dst_txt).parent.mkdir(parents=True, exist_ok=True)
    Path(dst_txt).write_text(t.text or "", encoding="utf-8")

def transcribe_to_srt(source: str, dst_srt: str) -> None:
    t = _transcribe_with_words(source)
    try:
        srt = words_to_srt(_words_from_transcript(t))
    except Exception:
        srt = getattr(t, "export_subtitles_srt", lambda: None)()
        if not srt:
            raise
    Path(dst_srt).parent.mkdir(parents=True, exist_ok=True)
    Path(dst_srt).write_text(srt, encoding="utf-8")

def batch_transcribe_dir(in_dir: str, out_dir: str, fmt: str = "txt") -> int:
    in_p, out_p = Path(in_dir), Path(out_dir)
    out_p.mkdir(parents=True, exist_ok=True)
    done = 0
    for p in sorted(in_p.iterdir()):
        if not p.is_file(): continue
        if p.suffix.lower() not in {".mp3", ".mp4", ".wav", ".m4a"}: continue
        dst = out_p / (p.stem + (".srt" if fmt == "srt" else ".txt"))
        if dst.exists(): continue
        (transcribe_to_srt if fmt == "srt" else transcribe_to_txt)(str(p), str(dst))
        done += 1
    return done

def is_url(s: str) -> bool:
    return s.startswith("http://") or s.startswith("https://")

def main():
    ap = argparse.ArgumentParser(description="Video-Caption CLI (file or direct URL)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--file", help="Local media file (.mp3/.mp4/.wav/.m4a)")
    g.add_argument("--url", help="Direct media URL (e.g., https://.../audio.mp3)")
    g.add_argument("--folder", help="Folder of media files")
    ap.add_argument("--out", default="out", help="Output path (file or folder)")
    ap.add_argument("--format", choices=["txt", "srt"], default="txt")
    a = ap.parse_args()

    if a.file or a.url:
        source = a.url if a.url else a.file
        dst = Path(a.out)
        if dst.is_dir():
            stem = "download" if is_url(source) else Path(source).stem
            dst = dst / (stem + (".srt" if a.format == "srt" else ".txt"))
        (transcribe_to_srt if a.format == "srt" else transcribe_to_txt)(source, str(dst))
        print(f"Wrote {dst}")
    else:
        n = batch_transcribe_dir(a.folder, a.out, fmt=a.format)
        print("Captioning Successful :D")
        print("Total files converted -", n)

if __name__ == "__main__":
    main()
