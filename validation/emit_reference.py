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
        elif b["t"] == "code" and "bundle" in b["attrs"] and "file" in b["attrs"]:
            folder = out / b["attrs"]["bundle"].split(",")[0].strip()
            folder.mkdir(parents=True, exist_ok=True)
            (folder / b["attrs"]["file"]).write_text(b["code"].rstrip() + "\n")
            (folder / "package.json").write_text('{"type": "module"}\n')
            n += 1
    return n


def emit_shared(student_dir, out):
    """Copy the student sheet's shared bundle `net` files and mock-server.mjs into every
    emitted project folder, so each folder runs as downloaded."""
    _, text = load_source(Path(student_dir))
    _, body = parse_front_matter(text)
    shared, mock = {}, None
    for b in walk(parse_blocks(body)):
        if b["t"] != "code":
            continue
        names = [x.strip() for x in b["attrs"].get("bundle", "").split(",")]
        if "net" in names and b["attrs"].get("file", "").endswith(".js") \
                and "run" not in b["flags"]:
            shared[b["attrs"]["file"]] = b["code"].rstrip() + "\n"
        if b["attrs"].get("file") == "mock-server.mjs":
            mock = b["code"].rstrip() + "\n"
    count = 0
    if mock:
        (out / "mock-server.mjs").write_text(mock)
        count += 1
    for folder in [p for p in out.iterdir() if p.is_dir()]:
        for name, code in shared.items():
            (folder / name).write_text(code)
            count += 1
    return count


if __name__ == "__main__":
    n = emit(Path(sys.argv[1]), Path(sys.argv[2]))
    if len(sys.argv) > 3:   # copy shared helper files from the student sheet
        _, text = load_source(Path(sys.argv[3]))
        _, body = parse_front_matter(text)
        for b in walk(parse_blocks(body)):
            if b["t"] == "code" and b["attrs"].get("file") == "ask.mjs":
                (Path(sys.argv[2]) / "ask.mjs").write_text(b["code"] + "\n"); n += 1
    if len(sys.argv) > 3 and any(p.is_dir() for p in Path(sys.argv[2]).iterdir()):
        n += emit_shared(Path(sys.argv[3]), Path(sys.argv[2]))
    print(f"emitted {n} files to {sys.argv[2]}")
