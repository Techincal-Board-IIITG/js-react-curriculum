#!/usr/bin/env python3
"""Check 'Line N' references in prose against the code block above them.
 1. flags references to blank or missing lines (definite errors)
 2. flags references where none of the `code tokens` mentioned right after the reference
    occur on the referenced line(s) (probable errors; review by hand)
Usage: python3 validation/check_line_refs.py <dir>... [--strict]"""
import re, sys
from pathlib import Path
REF = re.compile(r"\b[Ll]ines? (\d+)(?:(?: and | to |, )(\d+))?")
TOK = re.compile(r"`([^`]+)`")

def idents(token):
    return [w for w in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", token) if len(w) > 2]

def scan(path):
    text = path.read_text()
    out = []
    parts = re.split(r"(```[^\n]*\n.*?```\n)", text, flags=re.S)
    last, name = None, ""
    for part in parts:
        if part.startswith("```"):
            head = part.split("\n", 1)[0]
            body = part.split("\n", 1)[1].rsplit("```", 1)[0]
            lang = head[3:].split()[0] if head[3:].split() else ""
            if lang in ("output", "text", "tree", "diagram"):
                continue
            last = body.rstrip("\n").split("\n")
            mm = re.search(r'file="([^"]+)"', head)
            name = mm.group(1) if mm else lang
        elif last is not None:
            for m in REF.finditer(part):
                a = int(m.group(1)); b = int(m.group(2)) if m.group(2) else a
                lo, hi = min(a, b), max(a, b)
                if m.group(2) and (" and " in m.group(0) or ", " in m.group(0)):
                    wanted = [a, b]
                else:
                    wanted = list(range(lo, hi + 1))
                bad = [n for n in wanted if n < 1 or n > len(last) or last[n - 1].strip() == ""]
                if bad:
                    out.append(("DEFINITE", name, m.group(0), part[m.start():m.end() + 70].replace("\n", " ")))
                    continue
                # tokens in the next ~160 chars (to the end of the sentence)
                tail = part[m.end(): m.end() + 170]
                sentence = re.split(r"(?<=[.!?])\s", tail, maxsplit=1)[0]
                toks = [w for t in TOK.findall(sentence) for w in idents(t)]
                if not toks:
                    continue
                line_text = " ".join(last[n - 1] for n in wanted)
                if not any(w in line_text for w in toks):
                    out.append(("PROBABLE", name, m.group(0), sentence[:90].replace("\n", " ")))
            if re.search(r"^#{1,3} ", part, flags=re.M):
                last = None
    return out

args = [a for a in sys.argv[1:] if not a.startswith("--")]
strict = "--strict" in sys.argv
n_def = n_prob = 0
for d in args:
    for f in sorted(Path(d).rglob("*.md")):
        for kind, name, ref, ctx in scan(f):
            if kind == "PROBABLE" and not strict:
                n_prob += 1
                print(f"  ? {f.parent.name}/{f.name} [{name}] '{ref}' -> {ctx}")
            elif kind == "DEFINITE":
                n_def += 1
                print(f"  X {f.parent.name}/{f.name} [{name}] '{ref}' -> {ctx}")
print(f"definite: {n_def}, probable: {n_prob}")
