import assemblyai as aai
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
AAI_KEY = os.getenv("ASSEMBLYAI_API_KEY")
if not AAI_KEY:
    raise RuntimeError("ASSEMBLYAI_API_KEY not set")
aai.settings.api_key = AAI_KEY

transcriber = aai.Transcriber()

def transcribe_file_to_txt(src_path: str, dst_txt: str) -> None:
    t = transcriber.transcribe(src_path)
    text = t.text or ""
    Path(dst_txt).parent.mkdir(parents=True, exist_ok=True)
    with open(dst_txt, "w", encoding="utf-8") as f:
        f.write(text)

def batch_transcribe_dir(in_dir: str, out_dir: str) -> int:
    in_dir_p = Path(in_dir)
    out_dir_p = Path(out_dir)
    out_dir_p.mkdir(parents=True, exist_ok=True)
    done = 0
    for p in sorted(in_dir_p.iterdir()):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".mp3", ".mp4", ".wav", ".m4a"}:
            continue
        out_file = out_dir_p / (p.stem + ".txt")
        if out_file.exists():
            continue
        transcribe_file_to_txt(str(p), str(out_file))
        done += 1
    return done

if __name__ == "__main__":
    base = Path.cwd()
    in_folder = base / "pre caption"
    out_folder = base / "post caption"
    n = batch_transcribe_dir(str(in_folder), str(out_folder))
    print("Captioning Successful :D")
    print("Total files converted -", n)
