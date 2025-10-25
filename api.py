from fastapi import FastAPI, UploadFile, File
from fastapi.responses import PlainTextResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile, shutil, os
from dotenv import load_dotenv
from main import transcribe_file_to_txt

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
<!doctype html>
<html>
  <head><meta charset="utf-8"><title>Audio → Transcript</title></head>
  <body style="font-family:system-ui;margin:40px;max-width:680px">
    <h2>Upload audio/video → get transcript (.txt)</h2>
    <form id="f">
      <input type="file" id="file" name="file" accept=".mp3,.mp4,.wav,.m4a" required />
      <button type="submit">Transcribe</button>
    </form>
    <pre id="out" style="white-space:pre-wrap;margin-top:20px;"></pre>
    <script>
      const form = document.getElementById('f');
      const out = document.getElementById('out');
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        out.textContent = 'Working...';
        const fd = new FormData();
        const file = document.getElementById('file').files[0];
        fd.append('file', file);
        const r = await fetch('/transcribe', { method: 'POST', body: fd });
        out.textContent = await r.text();
      });
    </script>
  </body>
</html>
"""

@app.post("/transcribe", response_class=PlainTextResponse)
async def transcribe(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in {".mp3", ".mp4", ".wav", ".m4a"}:
        return PlainTextResponse("unsupported file type", status_code=400)
    with tempfile.TemporaryDirectory() as td:
        in_p = os.path.join(td, file.filename)
        out_p = os.path.join(td, "out.txt")
        with open(in_p, "wb") as f:
            shutil.copyfileobj(file.file, f)
        transcribe_file_to_txt(in_p, out_p)
        with open(out_p, "r", encoding="utf-8") as f:
            return f.read()
