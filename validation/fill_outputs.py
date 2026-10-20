#!/usr/bin/env python3
"""Fill `TBD` output blocks with REAL results (Node for js `run` blocks, Chromium for
html `page` blocks, honouring steps= and bundle=) and print every result for review.
Usage: python3 validation/fill_outputs.py <file.md>"""
import re, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "validation"))
from engine.parser import parse_attrs
import check_code as cc

path = Path(sys.argv[1]); text = path.read_text()
FENCE = re.compile(r"```(\w+)([^\n]*)\n(.*?)```\n", re.S)
bundles = {}
for m in FENCE.finditer(text):
    attrs, flags = parse_attrs(m.group(2))
    if "bundle" in attrs and "file" in attrs:
        bundles.setdefault(attrs["bundle"], {})[attrs["file"]] = m.group(3)

pat = re.compile(r"(```(js|html)([^\n]*)\n)((?:(?!```).)*)(```\n\n```output\n)TBD\n(```)", re.S)
def repl(m):
    head, lang, info, code, mid, end = m.groups()
    attrs, flags = parse_attrs(info)
    files = bundles.get(attrs.get("bundle"), {})
    name = attrs.get("file", "?")
    if lang == "js" and "run" in flags:
        rc, out, err = cc.run_node(code, files)
        out = out.rstrip("\n")
        print(f"--- {name} (node exit {rc})\n{out}" + (f"\nSTDERR: {err[:300]}" if rc else ""))
    elif lang == "html" and "page" in flags:
        logs = cc.run_page(code, attrs.get("steps", ""), files)
        out = "\n".join(logs)
        print(f"--- {name} (page)\n{out}")
    else:
        return m.group(0)
    return head + code + mid + out + "\n" + end
path.write_text(pat.sub(repl, text))
