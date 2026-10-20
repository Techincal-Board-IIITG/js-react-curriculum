#!/usr/bin/env python3
"""Replace the output block after each `run` block whose output is exactly TBD
with the real Node output, and print every filled block for human review.
Usage: python3 validation/fill_outputs.py <file.md>"""
import re, subprocess, sys, tempfile
from pathlib import Path
path = Path(sys.argv[1]); text = path.read_text()
pat = re.compile(r"(```js[^\n]*\brun\b[^\n]*\n)(.*?)(```\n\n```output\n)TBD\n(```)", re.S)
def repl(m):
    head, code, mid, end = m.groups()
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "s.mjs"; f.write_text(code)
        r = subprocess.run(["node", str(f)], capture_output=True, text=True, timeout=20, cwd=d)
    out = r.stdout.rstrip("\n")
    fn = re.search(r'file="([^"]+)"', head)
    print(f"--- {fn.group(1) if fn else '?'} (exit {r.returncode})\n{out}" + (f"\nSTDERR: {r.stderr[:200]}" if r.returncode else ""))
    return head + code + mid + out + "\n" + end
path.write_text(pat.sub(repl, text))
