# Video-Caption — Audio/Video → Transcript (.txt)

**Live demo:** <https://video-caption-shgi.onrender.com>  
**Code:** this repo

Small student project that turns `.mp3/.mp4/.wav/.m4a` into a plain-text transcript.  
The web UI has drag-and-drop upload, a progress bar, an inline media player, and Copy / Download buttons.

**The site may load for around 30 seconds as it's hosted on a free provider.**

---

## Features
- Drag & drop upload (default limit: 25 MB)
- Inline **audio/video player** to cross-check the transcript
- One-click **Copy** and **Download .txt**
- Simple **CLI** for single file or whole folder
- FastAPI backend + AssemblyAI transcription
- No secrets in repo (uses `.env` locally and server env vars in production)

---

## Stack
Python • FastAPI • AssemblyAI SDK • HTML/CSS/JS

---

## Quickstart (Local)

1) Clone & enter
```bash
git clone https://github.com/Jim6942/Video-Caption.git
cd Video-Caption
```

2) Python env + deps

Windows (PowerShell)
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3) Environment
```bash
cp .env.example .env
# open .env and paste your AssemblyAI key
```

4) Run the site
```bash
python -m uvicorn api:app --reload
# open http://127.0.0.1:8000/
```

Upload an audio/video file → the transcript appears. The inline player lets you play/pause to verify lines.

--- 