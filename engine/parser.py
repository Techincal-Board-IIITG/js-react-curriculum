"""Parser for the curriculum authoring format (a strict Markdown subset).

Blocks: headings (#..#####), paragraphs, lists (- / 1.), pipe tables,
fenced code (```lang key="v" flag), containers (::: kind args ... :::),
page break (---pagebreak---), horizontal rule (---).
"""
import re
import shlex
from pathlib import Path

FENCE_RE = re.compile(r"^```(\S*)\s*(.*)$")
CONT_RE = re.compile(r"^(:{3,})\s*(\w+)?\s*(.*)$")
LIST_RE = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")
HEAD_RE = re.compile(r"^(#{1,5})\s+(.*)$")


def parse_front_matter(text):
    meta, goals = {}, []
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return meta, text
    cur = None
    for ln in m.group(1).split("\n"):
        if re.match(r"^\s+-\s+", ln) and cur:
            meta.setdefault(cur, []).append(re.sub(r"^\s+-\s+", "", ln).strip())
        elif ":" in ln:
            k, _, v = ln.partition(":")
            cur = k.strip()
            if v.strip():
                meta[cur] = v.strip()
            else:
                meta[cur] = []
    return meta, text[m.end():]


def parse_attrs(s):
    attrs, flags = {}, set()
    if not s.strip():
        return attrs, flags
    for tok in shlex.split(s):
        if "=" in tok:
            k, _, v = tok.partition("=")
            attrs[k] = v
        else:
            flags.add(tok)
    return attrs, flags


def split_row(line):
    """Split a pipe-table row, ignoring pipes inside backticks and \\| escapes."""
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    cells, cur, in_code, i = [], "", False, 0
    while i < len(line):
        ch = line[i]
        if ch == "`":
            in_code = not in_code
            cur += ch
        elif ch == "\\" and i + 1 < len(line) and line[i + 1] == "|":
            cur += "|"
            i += 1
        elif ch == "|" and not in_code:
            cells.append(cur.strip())
            cur = ""
        else:
            cur += ch
        i += 1
    cells.append(cur.strip())
    return cells


def _starts_block(ln):
    s = ln.strip()
    return (not s or FENCE_RE.match(ln) or HEAD_RE.match(ln) or CONT_RE.match(ln)
            or s.startswith("|") or LIST_RE.match(ln) or s.startswith("---")
            or s.startswith("[[widths"))


def parse_blocks(text):
    lines = text.split("\n")
    i, out = 0, []
    pending_widths = None
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        if ln.strip() == "---pagebreak---":
            out.append({"t": "pagebreak"})
            i += 1
            continue
        if ln.strip() == "---":
            out.append({"t": "hr"})
            i += 1
            continue
        m = re.match(r"^\[\[widths\s+([\d.\s]+)\]\]$", ln.strip())
        if m:
            pending_widths = [float(x) for x in m.group(1).split()]
            i += 1
            continue
        m = FENCE_RE.match(ln)
        if m:
            lang, rest = m.group(1), m.group(2)
            attrs, flags = parse_attrs(rest)
            i += 1
            body = []
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(lines[i])
                i += 1
            i += 1
            out.append({"t": "code", "lang": lang, "attrs": attrs, "flags": flags,
                        "code": "\n".join(body), "line": i})
            continue
        m = CONT_RE.match(ln)
        if m and m.group(2):
            colons, kind, args = m.group(1), m.group(2), m.group(3).strip()
            i += 1
            inner = []
            while i < len(lines) and lines[i].strip() != colons:
                inner.append(lines[i])
                i += 1
            if i >= len(lines):
                raise ValueError(f"unclosed container '{kind}' ({colons})")
            i += 1
            out.append({"t": "container", "kind": kind, "args": args,
                        "children": parse_blocks("\n".join(inner))})
            continue
        m = HEAD_RE.match(ln)
        if m:
            out.append({"t": "h", "level": len(m.group(1)), "text": m.group(2).strip()})
            i += 1
            continue
        if ln.strip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            if len(rows) < 2 or not all(re.match(r"^:?-{2,}:?$", c) for c in rows[1]):
                raise ValueError(f"malformed table near: {rows[0]}")
            ncol = len(rows[0])
            body = rows[2:]
            for r in rows[:1] + body:
                if len(r) != ncol:
                    raise ValueError(f"table row has {len(r)} cells, header has {ncol}: {r}")
            out.append({"t": "table", "head": rows[0], "rows": body, "widths": pending_widths})
            pending_widths = None
            continue
        if LIST_RE.match(ln):
            items = []
            while i < len(lines):
                m = LIST_RE.match(lines[i])
                if m:
                    ind = len(m.group(1).replace("\t", "  "))
                    items.append({"level": ind // 2, "ordered": m.group(2)[0].isdigit(),
                                  "text": m.group(3).strip()})
                    i += 1
                elif (lines[i].strip() and lines[i].startswith("  ") and items
                      and not FENCE_RE.match(lines[i].lstrip())):
                    items[-1]["text"] += " " + lines[i].strip()
                    i += 1
                elif not lines[i].strip():
                    j = i
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    if j < len(lines) and LIST_RE.match(lines[j]) and lines[j].startswith(" "):
                        i = j
                    else:
                        break
                else:
                    break
            out.append({"t": "list", "items": items})
            continue
        para = [ln.strip()]
        i += 1
        while i < len(lines) and not _starts_block(lines[i]):
            para.append(lines[i].strip())
            i += 1
        out.append({"t": "para", "text": " ".join(para)})
    return out


def load_source(path_or_dir):
    """Load one .md file or every .md file (sorted) in a directory."""
    p = Path(path_or_dir)
    files = sorted(p.glob("*.md")) if p.is_dir() else [p]
    text = "\n".join(f.read_text(encoding="utf-8") for f in files)
    return files, text
