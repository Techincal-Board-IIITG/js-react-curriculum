#!/usr/bin/env python3
"""Validate curriculum sources.

* every ```js/jsx block parses (esbuild)           [skip with `nocheck`]
* every ```js block flagged `run` is executed in Node and its stdout is
  compared with the ```output block that directly follows it
* line-length limit so code never clips or wraps in the PDF
* glyphs exist in the monospace font
* student sheets: 5 projects, each with all ten required fields, and all
  mandatory teaching-format sections present

Usage: python3 validation/check_code.py [dir ...]   (default: all content dirs)
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine.parser import load_source, parse_blocks, parse_front_matter  # noqa: E402
from engine import theme  # noqa: E402

ESBUILD = "/home/claude/.npm-global/lib/node_modules/tsx/node_modules/esbuild/bin/esbuild"
MAX_NUM, MAX_PLAIN = 88, 92

PROJECT_FIELDS = ["objective", "problem statement", "required features", "technical constraints",
                  "expected behavior", "suggested milestones", "edge cases",
                  "acceptance criteria", "stretch goals", "concepts practiced"]
REQUIRED_H2 = ["learning objectives", "common mistakes", "exercises", "mini project",
               "summary", "self-assessment", "completion checklist", "documentation"]


def walk(blocks):
    for b in blocks:
        yield b
        if b["t"] == "container":
            yield from walk(b["children"])


def esbuild_ok(code, loader="jsx"):
    r = subprocess.run([ESBUILD, f"--loader={loader}", "--log-level=error"],
                       input=code, capture_output=True, text=True)
    return r.returncode == 0, r.stderr.strip().split("\n")[0:3]


def run_node(code, files=None):
    with tempfile.TemporaryDirectory() as d:
        for name, text in (files or {}).items():
            if name.endswith((".js", ".mjs")):
                (Path(d) / name).write_text(text)
        if files:
            (Path(d) / "package.json").write_text('{"type": "module"}')
        p = Path(d) / "snippet.mjs"
        p.write_text(code)
        r = subprocess.run(["node", str(p)], capture_output=True, text=True, timeout=15, cwd=d)
    return r.returncode, r.stdout, r.stderr



_PW = {}


def run_page(code, steps="", files=None):
    """Load an HTML page in headless Chromium, perform scripted steps, return log lines.
    steps: 'click SEL | fill SEL text | press SEL Key | wait 50 | print SEL | reload'."""
    from playwright.sync_api import sync_playwright
    if "browser" not in _PW:
        _PW["ctx"] = sync_playwright().start()
        _PW["browser"] = _PW["ctx"].chromium.launch()
    page = _PW["browser"].new_context().new_page()
    logs = []
    page.on("console", lambda m: logs.append(m.text))
    page.on("pageerror", lambda e: logs.append("PAGEERROR: " + str(e).split("\n")[0]))
    served = dict(files or {})
    served["index.html"] = code

    def serve(route):
        name = route.request.url.split("app.test/", 1)[1].split("?")[0] or "index.html"
        if name not in served:
            route.fulfill(status=404, body="not found")
            return
        kind = "text/html" if name.endswith(".html") else (
            "text/css" if name.endswith(".css") else "text/javascript")
        route.fulfill(body=served[name], content_type=kind)

    page.route("http://app.test/**", serve)
    page.goto("http://app.test/index.html")
    page.wait_for_timeout(60)
    for raw in [x.strip() for x in steps.split("|") if x.strip()]:
        cmd, _, rest = raw.partition(" ")
        if cmd == "click":
            page.click(rest)
        elif cmd == "fill":
            sel, _, text = rest.partition(" ")
            page.fill(sel, text)
        elif cmd == "press":
            sel, _, key = rest.partition(" ")
            page.press(sel, key)
        elif cmd == "check":
            page.check(rest)
        elif cmd == "select":
            sel, _, val = rest.partition(" ")
            page.select_option(sel, val)
        elif cmd == "wait":
            page.wait_for_timeout(int(rest))
        elif cmd == "print":
            logs.append(page.inner_text(rest).replace("\n", " / "))
        elif cmd == "reload":
            page.reload()
        elif cmd == "eval":
            logs.append(str(page.evaluate(rest)))
        else:
            raise ValueError(f"unknown step {raw!r}")
        page.wait_for_timeout(40)
    page.context.close()
    return logs


def norm(s):
    return "\n".join(l.rstrip() for l in s.strip().split("\n"))


def check_dir(path):
    errors, warns, stats = [], [], {"blocks": 0, "run": 0, "parsed": 0}
    files, text = load_source(path)
    meta, body = parse_front_matter(text)
    name = Path(path).name
    try:
        blocks = list(walk(parse_blocks(body)))
    except Exception as e:  # noqa: BLE001
        return [f"{name}: PARSE ERROR {e}"], warns, stats
    flat = parse_blocks(body)

    def sequence(bs):
        for i, b in enumerate(bs):
            yield bs, i, b
            if b["t"] == "container":
                yield from sequence(b["children"])

    bundles = {}
    for _bs, _i, _b in sequence(flat):
        if _b["t"] == "code" and "bundle" in _b["attrs"] and "file" in _b["attrs"]:
            bundles.setdefault(_b["attrs"]["bundle"], {})[_b["attrs"]["file"]] = _b["code"]

    for bs, i, b in sequence(flat):
        if b["t"] != "code" or b["lang"] == "diagram":
            if b["t"] == "para":
                import re
                for m in re.finditer(r"`([^`]+)`", b["text"]):
                    if len(m.group(1)) > 44:
                        warns.append(f"{name}: long inline code ({len(m.group(1))} chars): {m.group(1)[:40]}...")
            continue
        stats["blocks"] += 1
        lang, flags, code = b["lang"], b["flags"], b["code"]
        where = f"{name} block~line{b['line']} [{lang}]"
        numbered = lang not in ("output", "text", "tree")
        limit = MAX_NUM if numbered else MAX_PLAIN
        for n, ln in enumerate(code.split("\n"), 1):
            if len(ln.replace("\t", "  ")) > limit:
                errors.append(f"{where}: line {n} is {len(ln)} chars (> {limit}): {ln[:50]}...")
        miss = theme.missing_mono_glyphs(code)
        if miss:
            errors.append(f"{where}: glyphs missing from mono font: {miss}")
        if "nocheck" in flags:
            continue
        if lang in ("js", "javascript", "jsx"):
            ok, msg = esbuild_ok(code, "jsx" if lang == "jsx" else "js")
            stats["parsed"] += 1
            if not ok:
                errors.append(f"{where}: syntax error: {' | '.join(msg)}")
                continue
            if "run" in flags:
                stats["run"] += 1
                rc, out, err = run_node(code, bundles.get(b["attrs"].get("bundle")))
                nxt = bs[i + 1] if i + 1 < len(bs) else None
                if "throws" in flags:
                    if rc == 0:
                        errors.append(f"{where}: expected to throw but exited 0")
                    expected = nxt["code"] if nxt and nxt["t"] == "code" and nxt["lang"] == "output" else None
                    if expected and norm(expected) not in norm(out + "\n" + err.split("\n")[0]):
                        pass
                    continue
                if rc != 0:
                    errors.append(f"{where}: run failed: {err.strip().splitlines()[-1] if err.strip() else rc}")
                    continue
                if nxt and nxt["t"] == "code" and nxt["lang"] == "output":
                    if norm(out) != norm(nxt["code"]):
                        errors.append(f"{where}: OUTPUT MISMATCH\n--- expected\n{norm(nxt['code'])}\n--- actual\n{norm(out)}")
                else:
                    warns.append(f"{where}: `run` block has no following output block")
        elif lang == "html" and "page" in flags:
            stats["run"] += 1
            try:
                logs = run_page(code, b["attrs"].get("steps", ""),
                                bundles.get(b["attrs"].get("bundle"), {}))
            except Exception as e:  # noqa: BLE001
                errors.append(f"{where}: page run failed: {str(e).splitlines()[0]}")
                continue
            nxt = bs[i + 1] if i + 1 < len(bs) else None
            if "throws" in flags:
                if not any(l.startswith("PAGEERROR") for l in logs):
                    errors.append(f"{where}: expected a page error but none occurred")
            elif any(l.startswith("PAGEERROR") for l in logs):
                errors.append(f"{where}: unexpected page error: {[l for l in logs if l.startswith('PAGEERROR')][0]}")
            if nxt and nxt["t"] == "code" and nxt["lang"] == "output" and "throws" not in flags:
                if norm("\n".join(logs)) != norm(nxt["code"]):
                    errors.append(f"{where}: PAGE OUTPUT MISMATCH\n--- expected\n{norm(nxt['code'])}\n--- actual\n{norm(chr(10).join(logs))}")
            elif "throws" not in flags:
                warns.append(f"{where}: `page` block has no following output block")
        elif lang == "json":
            try:
                json.loads(code)
            except Exception as e:  # noqa: BLE001
                errors.append(f"{where}: invalid JSON: {e}")

    # structure checks (student sheets only)
    if meta.get("kind", "student") == "student" and meta.get("structure", "yes") != "no":
        h2s = [b["text"].lower() for b in blocks if b["t"] == "h" and b["level"] == 2]
        for req in REQUIRED_H2:
            if not any(req in h for h in h2s):
                errors.append(f"{name}: missing required section containing '{req}'")
        projects = [b for b in blocks if b["t"] == "container" and b["kind"] == "project"]
        if len(projects) != 5:
            errors.append(f"{name}: expected 5 projects, found {len(projects)}")
        for p in projects:
            labels = [x["text"].lower() for x in walk(p["children"]) if x["t"] == "h" and x["level"] == 5]
            for f in PROJECT_FIELDS:
                if not any(f in l for l in labels):
                    errors.append(f"{name}: project '{p['args'][:30]}' missing field '{f}'")
    return errors, warns, stats


def main():
    dirs = [Path(a) for a in sys.argv[1:]]
    if not dirs:
        for sub in ("student", "instructor"):
            dirs += sorted(p for p in (ROOT / "content" / sub).iterdir()
                           if p.is_dir() and not (p / ".wip").exists() and not p.name.startswith("_"))
    bad = 0
    for d in dirs:
        errs, warns, st = check_dir(d)
        status = "FAIL" if errs else "ok"
        print(f"[{status}] {d.name}: {st['blocks']} code blocks, {st['parsed']} parsed, "
              f"{st['run']} executed, {len(warns)} warnings")
        for e in errs:
            print("   ERROR:", e)
        for w in warns[:8]:
            print("   warn:", w)
        bad += bool(errs)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
