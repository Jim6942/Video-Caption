from fastapi import FastAPI, UploadFile, File
from fastapi.responses import PlainTextResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

app.mount("/static", StaticFiles(directory="static"), name="static")

MAX_BYTES = int(os.getenv("MAX_UPLOAD_MB", "25")) * 1024 * 1024

@app.get("/")
async def home():
    return FileResponse("static/index.html")

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
        if os.path.getsize(in_p) > MAX_BYTES:
            return PlainTextResponse("file too large", status_code=413)
        transcribe_file_to_txt(in_p, out_p)
        with open(out_p, "r", encoding="utf-8") as f:
            return f.read()
