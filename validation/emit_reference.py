#!/usr/bin/env python3
"""Write `emit`-flagged code blocks of instructor keys to real files.
Usage: python3 validation/emit_reference.py <instructor-dir> <out-dir> [student-dir-for-ask.mjs]
Code after the line '// --- self-test ---' is dropped."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine.parser import load_source, parse_blocks, parse_front_matter

def walk(bs):
    for b in bs:
        yield b
        if b["t"] == "container":
            yield from walk(b["children"])

def emit(src, out, only_flag="emit", name_attr="file"):
    _, text = load_source(src)
    _, body = parse_front_matter(text)
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for b in walk(parse_blocks(body)):
        if b["t"] == "code" and only_flag in b["flags"] and name_attr in b["attrs"]:
            code = b["code"].split("// --- self-test ---")[0].rstrip() + "\n"
            (out / b["attrs"][name_attr]).write_text(code)
            n += 1
    return n

if __name__ == "__main__":
    n = emit(Path(sys.argv[1]), Path(sys.argv[2]))
    if len(sys.argv) > 3:   # copy shared helper files from the student sheet
        _, text = load_source(Path(sys.argv[3]))
        _, body = parse_front_matter(text)
        for b in walk(parse_blocks(body)):
            if b["t"] == "code" and b["attrs"].get("file") == "ask.mjs":
                (Path(sys.argv[2]) / "ask.mjs").write_text(b["code"] + "\n"); n += 1
    print(f"emitted {n} files to {sys.argv[2]}")
