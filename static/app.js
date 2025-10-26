const f = document.getElementById('file');
const drop = document.getElementById('drop');
const pick = document.getElementById('pick');
const go = document.getElementById('go');
const out = document.getElementById('out');
const meta = document.getElementById('filemeta');
const bar = document.getElementById('bar');
const status = document.getElementById('status');
const copyBtn = document.getElementById('copy');
const dlBtn = document.getElementById('dl');
const vid = document.getElementById('vid');
const aud = document.getElementById('aud');

function setStatus(t, c = 'pill muted') { status.className = c; status.textContent = t }
function fmt(b) { const u = ['B', 'KB', 'MB', 'GB']; let i = 0; while (b >= 1024 && i < u.length - 1) { b /= 1024; i++ } return b.toFixed(1) + ' ' + u[i] }
function extOf(name) { return (name.split('.').pop() || '').toLowerCase() }

pick.onclick = () => f.click();

function loadPlayer(file) {
    const url = URL.createObjectURL(file);
    const ext = extOf(file.name);
    vid.classList.add('hidden'); aud.classList.add('hidden');
    if (['mp4', 'webm', 'mov', 'm4v'].includes(ext)) { vid.src = url; vid.classList.remove('hidden'); vid.load(); }
    else if (['mp3', 'wav', 'm4a', 'ogg'].includes(ext)) { aud.src = url; aud.classList.remove('hidden'); aud.load(); }
}

f.onchange = () => { const file = f.files[0]; meta.textContent = file ? `${file.name} • ${fmt(file.size)}` : 'No file selected'; meta.className = file ? 'pill ok' : 'pill muted'; if (file) loadPlayer(file); };

['dragenter', 'dragover'].forEach(e => drop.addEventListener(e, ev => { ev.preventDefault(); drop.classList.add('drag') }));
['dragleave', 'drop'].forEach(e => drop.addEventListener(e, ev => { ev.preventDefault(); drop.classList.remove('drag') }));
drop.addEventListener('drop', ev => { f.files = ev.dataTransfer.files; f.onchange() });

go.onclick = async () => {
    const file = f.files[0];
    if (!file) { setStatus('Pick a file', 'pill bad'); return }
    if (file.size > 25 * 1024 * 1024) { setStatus('File too large', 'pill bad'); return }
    go.disabled = true; copyBtn.disabled = true; dlBtn.disabled = true; out.value = ''; setStatus('Uploading…', 'pill'); bar.style.width = '0%';

    const fd = new FormData(); fd.append('file', file);
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/transcribe');
    xhr.upload.onprogress = (e) => { if (e.lengthComputable) { bar.style.width = (e.loaded / e.total * 100).toFixed(0) + '%' } };
    xhr.onload = () => {
        bar.style.width = '100%';
        if (xhr.status >= 200 && xhr.status < 300) { out.value = xhr.responseText; setStatus('Done', 'pill ok'); copyBtn.disabled = false; dlBtn.disabled = false }
        else { setStatus('Error', 'pill bad'); out.value = xhr.responseText || 'Something went wrong.' }
        go.disabled = false
    };
    xhr.onerror = () => { setStatus('Network error', 'pill bad'); go.disabled = false };
    xhr.send(fd);
};

copyBtn.onclick = async () => { await navigator.clipboard.writeText(out.value); setStatus('Copied', 'pill ok') };
dlBtn.onclick = () => { const b = new Blob([out.value], { type: 'text/plain' }); const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = (f.files[0]?.name || 'transcript').replace(/\.[^.]+$/, '') + '.txt'; a.click(); URL.revokeObjectURL(a.href) };
