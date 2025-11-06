const $ = (id) => document.getElementById(id);

const f = $('file'), drop = $('drop'), pick = $('pick'), go = $('go');
const out = $('out'), meta = $('filemeta'), bar = $('bar'), statusEl = $('status');
const copyBtn = $('copy'), dlBtn = $('dl'), vid = $('vid'), aud = $('aud'), yt = $('yt');
const urlInput = $('url'), goUrl = $('goUrl'), fmtSel = $('format');

const MAX_MB = 25;

const setStatus = (t, cls='pill muted') => { statusEl.className = cls; statusEl.textContent = t; }
const fmtBytes = (b)=>{ const u=['B','KB','MB','GB']; let i=0; while(b>=1024 && i<u.length-1){b/=1024;i++} return b.toFixed(1)+' '+u[i]; }
const extOf = (name)=> (name.split('.').pop()||'').toLowerCase();

pick.onclick = () => f.click();

/* ---------- YouTube helpers & player control ---------- */
function isYouTubeURL(u) {
  if (!u) return false;
  return /(?:youtube\.com\/watch\?v=|youtu\.be\/)/i.test(u);
}
function extractYTID(u) {
  // supports watch?v=, youtu.be/, and keeps only the 11-char id
  const m = u.match(/(?:v=|youtu\.be\/)([0-9A-Za-z_-]{11})/);
  return m ? m[1] : null;
}
function showYouTubeEmbed(u) {
  const id = extractYTID(u);
  if (!id) { hideAllPlayers(); return; }
  const src = `https://www.youtube.com/embed/${id}`;
  yt.src = src;
  yt.classList.remove('hidden');
  vid.classList.add('hidden'); aud.classList.add('hidden');
}
function hideAllPlayers() {
  yt.classList.add('hidden'); yt.src = '';
  vid.classList.add('hidden'); aud.classList.add('hidden');
}

/* ---------- Local file preview ---------- */
function loadPlayerFromFile(file) {
  hideAllPlayers();
  const url = URL.createObjectURL(file);
  const ext = extOf(file.name);
  if (['mp4','webm','mov','m4v'].includes(ext)) {
    vid.src = url; vid.classList.remove('hidden'); vid.load();
  } else if (['mp3','wav','m4a','ogg'].includes(ext)) {
    aud.src = url; aud.classList.remove('hidden'); aud.load();
  }
}

f.onchange = () => {
  const file = f.files[0];
  meta.textContent = file ? `${file.name} • ${fmtBytes(file.size)}` : 'No file selected';
  meta.className = file ? 'pill ok' : 'pill muted';
  if (file) loadPlayerFromFile(file);
};

/* Live YouTube preview as the user pastes/edits URL */
urlInput.addEventListener('input', () => {
  const u = urlInput.value.trim();
  if (isYouTubeURL(u)) showYouTubeEmbed(u);
  else hideAllPlayers();
});

/* ---------- drag-n-drop ---------- */
['dragenter','dragover'].forEach(e => drop.addEventListener(e, ev => { ev.preventDefault(); drop.classList.add('drag'); }));
['dragleave','drop'].forEach(e => drop.addEventListener(e, ev => { ev.preventDefault(); drop.classList.remove('drag'); }));
drop.addEventListener('drop', ev => { f.files = ev.dataTransfer.files; f.onchange(); });

/* ---------- xhr helper ---------- */
function postForm(path, fd) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', path);
    xhr.upload.onprogress = (e) => { if (e.lengthComputable) bar.style.width = (e.loaded/e.total*100).toFixed(0)+'%'; };
    xhr.onload = () => (xhr.status>=200 && xhr.status<300) ? resolve(xhr.responseText) : reject(xhr.responseText||'Error');
    xhr.onerror = () => reject('Network error');
    xhr.send(fd);
  });
}

/* ---------- actions ---------- */
async function transcribeFile() {
  const file = f.files[0];
  if (!file) return setStatus('Pick a file', 'pill bad');
  if (file.size > MAX_MB*1024*1024) return setStatus('File too large', 'pill bad');

  go.disabled = true; copyBtn.disabled = true; dlBtn.disabled = true;
  out.value = ''; bar.style.width='0%'; setStatus('Uploading…', 'pill');

  const fd = new FormData(); fd.append('file', file); fd.append('format', fmtSel.value);
  try {
    const text = await postForm('/transcribe', fd);
    out.value = text; setStatus('Done', 'pill ok');
    copyBtn.disabled = false; dlBtn.disabled = false;
  } catch (e) {
    out.value = String(e); setStatus('Error', 'pill bad');
  } finally {
    go.disabled = false;
  }
}

async function transcribeURL() {
  const url = urlInput.value.trim();
  if (!url) return setStatus('Paste a URL', 'pill bad');

  // if it's YouTube, show the embed (nice for cross-checking)
  if (isYouTubeURL(url)) showYouTubeEmbed(url);

  goUrl.disabled = true; copyBtn.disabled = true; dlBtn.disabled = true;
  out.value = ''; bar.style.width='100%'; setStatus('Fetching…', 'pill');

  const fd = new FormData(); fd.append('url', url); fd.append('format', fmtSel.value);
  try {
    const text = await postForm('/transcribe_url', fd);
    out.value = text; setStatus('Done', 'pill ok');
    copyBtn.disabled = false; dlBtn.disabled = false;
  } catch (e) {
    out.value = String(e);
    setStatus('Could not process that URL', 'pill bad');
  } finally {
    goUrl.disabled = false;
  }
}

go.onclick = transcribeFile;
goUrl.onclick = transcribeURL;

/* utility actions */
copyBtn.onclick = async () => { await navigator.clipboard.writeText(out.value); setStatus('Copied', 'pill ok'); };
dlBtn.onclick = () => {
  const ext = fmtSel.value === 'srt' ? '.srt' : '.txt';
  const base = (f.files[0]?.name || 'transcript').replace(/\.[^.]+$/, '');
  const blob = new Blob([out.value], { type: 'text/plain;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = base + ext; a.click();
  URL.revokeObjectURL(a.href);
};
