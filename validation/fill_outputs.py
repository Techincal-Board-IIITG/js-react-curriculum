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

path = Path(sys.argv[1])
# the mock server block may live in another file of the same sheet
_sheet_text = "\n".join(f.read_text() for f in sorted(path.parent.glob("*.md")))
_sib = ROOT / "content" / "student" / path.parent.name
if "instructor" in str(path) and _sib.exists():
    _sheet_text += "\n" + "\n".join(f.read_text() for f in sorted(_sib.glob("*.md")))
text = path.read_text()
_mock = re.search(r'```js file="mock-server\.mjs"[^\n]*\n((?:(?!```).)*)```', _sheet_text, re.S)
MOCK_SRC = _mock.group(1) if _mock else None
FENCE = re.compile(r"```(\w+)([^\n]*)\n(.*?)```\n", re.S)
bundles = {}
for m in FENCE.finditer(_sheet_text):
    attrs, flags = parse_attrs(m.group(2))
    if "bundle" in attrs and "file" in attrs:
        for _n in attrs["bundle"].split(","):
            bundles.setdefault(_n.strip(), {})[attrs["file"]] = m.group(3)

pat = re.compile(r"(```(js|html)([^\n]*)\n)((?:(?!```).)*)(```\n\n```output\n)TBD\n(```)", re.S)
def repl(m):
    head, lang, info, code, mid, end = m.groups()
    attrs, flags = parse_attrs(info)
    files = cc.merged_bundle(bundles, attrs.get("bundle"))
    name = attrs.get("file", "?")
    if "mock" in flags:
        cc.ensure_mock(MOCK_SRC)
    if lang == "js" and "run" in flags:
        rc, out, err = cc.run_node(code, files)
        out = out.rstrip("\n")
        print(f"--- {name} (node exit {rc})\n{out}" + (f"\nSTDERR: {err[:300]}" if rc else ""))
    elif lang == "html" and "page" in flags:
        logs = cc.run_page(code, attrs.get("steps", ""), files, attrs.get("ignore", ""))
        out = "\n".join(logs)
        print(f"--- {name} (page)\n{out}")
    else:
        return m.group(0)
    return head + code + mid + out + "\n" + end
path.write_text(pat.sub(repl, text))
