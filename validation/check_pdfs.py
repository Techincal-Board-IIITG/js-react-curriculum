#!/usr/bin/env python3
"""Layout checks on built PDFs: pages, text, margins, tiny fonts, tofu glyphs.
Usage: python3 validation/check_pdfs.py dist/student/*.pdf"""
import sys
import pdfplumber

W = 595.28
LEFT, RIGHT = 50, W - 50      # content is 56pt margins; allow 6pt tolerance
BAD_CHARS = {"\u25a0", "\ufffd", "\x00"}

def check(path):
    issues, nchars = [], 0
    with pdfplumber.open(path) as pdf:
        n = len(pdf.pages)
        for i, page in enumerate(pdf.pages, 1):
            if i == 1:
                continue  # cover is drawn full-bleed by design
            chars = page.chars
            nchars += len(chars)
            if not chars:
                issues.append(f"p{i}: empty page")
                continue
            for ch in chars:
                if ch["text"] in BAD_CHARS:
                    issues.append(f"p{i}: bad glyph {ch['text']!r}"); break
            body = [c for c in chars if 50 < c["top"] < 790]
            over = [c for c in body if c["x1"] > RIGHT or c["x0"] < LEFT]
            if over:
                issues.append(f"p{i}: {len(over)} chars outside margins, e.g. {''.join(c['text'] for c in over[:20])!r}")
            small = [c for c in body if c["size"] < 6.4 and c["text"].strip()]
            if small:
                issues.append(f"p{i}: {len(small)} chars under 6.4pt")
            if len(chars) < 120 and i != n:
                issues.append(f"p{i}: nearly empty page ({len(chars)} chars)")
    return n, nchars, issues

bad = 0
for p in sys.argv[1:]:
    n, nchars, issues = check(p)
    print(f"[{'FAIL' if issues else 'ok'}] {p}: {n} pages, {nchars:,} characters")
    for x in issues[:15]:
        print("   ", x)
    bad += bool(issues)
sys.exit(1 if bad else 0)
