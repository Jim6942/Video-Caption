import os, tempfile, shutil
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from main import transcribe_to_txt, transcribe_to_srt
from utils_media import is_youtube_url, ensure_youtube_wav

load_dotenv()
MAX_BYTES = int(os.getenv("MAX_UPLOAD_MB", "25")) * 1024 * 1024

app = FastAPI(title="Video-Caption")

if os.getenv("CORS_ALLOW_ALL", "0") == "1":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def home():
    return FileResponse("static/index.html")

def _transcribe_common(source: str, out_fmt: str) -> str:
    with tempfile.TemporaryDirectory() as td:
        out_p = os.path.join(td, "out.srt" if out_fmt == "srt" else "out.txt")
        (transcribe_to_srt if out_fmt == "srt" else transcribe_to_txt)(source, out_p)
        with open(out_p, "r", encoding="utf-8") as f:
            return f.read()

@app.post("/transcribe", response_class=PlainTextResponse)
async def transcribe(file: UploadFile = File(...), format: str = Form(default="txt")):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in {".mp3", ".mp4", ".wav", ".m4a"}:
        return PlainTextResponse("unsupported file type", status_code=400)

    td = tempfile.mkdtemp(prefix="vc_")
    try:
        in_p = os.path.join(td, file.filename)
        with open(in_p, "wb") as f:
            shutil.copyfileobj(file.file, f)
        if os.path.getsize(in_p) > MAX_BYTES:
            return PlainTextResponse("file too large", status_code=413)

        text = _transcribe_common(in_p, format.lower())
        return PlainTextResponse(text)
    except Exception as e:
        return PlainTextResponse(f"error: {e}", status_code=500)
    finally:
        shutil.rmtree(td, ignore_errors=True)

@app.post("/transcribe_url", response_class=PlainTextResponse)
async def transcribe_url(url: str = Form(...), format: str = Form(default="txt")):
    fmt = format.lower()
    if is_youtube_url(url):
        wav = None
        tmpd = None
        try:
            wav, tmpd = ensure_youtube_wav(url)
            return PlainTextResponse(_transcribe_common(wav, fmt))
        except Exception as e:
            raise HTTPException(status_code=424, detail=str(e))
        finally:
            if tmpd: shutil.rmtree(tmpd, ignore_errors=True)
    else:
        # Non-YouTube direct media URL: let AssemblyAI fetch it directly
        if not (url.startswith("http://") or url.startswith("https://")):
            raise HTTPException(status_code=422, detail="Provide a valid http(s) URL")
        try:
            return PlainTextResponse(_transcribe_common(url, fmt))
        except Exception as e:
            raise HTTPException(status_code=424, detail=f"Could not fetch that URL as media. ({e})")
