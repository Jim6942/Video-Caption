from dataclasses import dataclass
from typing import List
import math

@dataclass
class Word:
    text: str
    start_ms: int
    end_ms: int

def _ms_to_ts(ms: int) -> str:
    s, ms = divmod(ms, 1000)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def _wrap_line(words: List[str], max_len: int = 38) -> List[str]:
    lines, cur = [], ""
    for w in words:
        if not cur: cur = w
        elif len(cur) + 1 + len(w) <= max_len: cur += " " + w
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    if len(lines) > 2:
        mid = math.ceil(len(words) / 2)
        return [" ".join(words[:mid]), " ".join(words[mid:])]
    return lines

def _segment(words: List[Word], max_dur_ms: int = 6000, max_words: int = 18):
    segs, cur = [], []
    if not words: return segs
    start = words[0].start_ms
    for w in words:
        cur.append(w)
        over_time = (w.end_ms - start) >= max_dur_ms
        over_ct = len(cur) >= max_words
        punct_break = w.text.endswith((".", "?", "!", ","))
        if over_time or over_ct or punct_break:
            segs.append(cur); cur = []; start = w.end_ms + 1
    if cur: segs.append(cur)
    return segs

def words_to_srt(words: List[Word]) -> str:
    out, idx = [], 1
    for seg in _segment(words):
        out.append(str(idx))
        out.append(f"{_ms_to_ts(seg[0].start_ms)} --> {_ms_to_ts(seg[-1].end_ms)}")
        out.extend(_wrap_line([w.text for w in seg]))
        out.append("")
        idx += 1
    return "\n".join(out)
