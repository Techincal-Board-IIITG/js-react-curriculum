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


def run_page(code, steps="", files=None, ignore=""):
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
    import http.server
    import threading
    served = dict(files or {})
    served["index.html"] = code

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            name = self.path.split("?")[0].lstrip("/") or "index.html"
            if name not in served:
                self.send_response(404)
                self.end_headers()
                return
            kind = ("text/html" if name.endswith(".html") else
                    "text/css" if name.endswith(".css") else "text/javascript")
            data = served[name].encode()
            self.send_response(200)
            self.send_header("Content-Type", kind + "; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_address[1]}"
    page.goto(origin + "/index.html")
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
    server.shutdown()
    drop = [x for x in ignore.split(";") if x]
    return [l for l in logs if not any(x in l for x in drop)]


_MOCK = {}


def ensure_mock(source):
    """Start the sheet's own mock-server.mjs once (port 3001) and reset it before each use."""
    import atexit, socket, time, urllib.request
    if source is None:
        raise RuntimeError("block uses `mock` but the sheet has no mock-server.mjs block")
    if "proc" not in _MOCK:
        d = tempfile.mkdtemp()
        path = Path(d) / "mock-server.mjs"
        path.write_text(source)
        env = dict(__import__("os").environ, PORT="3001")
        _MOCK["proc"] = subprocess.Popen(["node", str(path)], env=env,
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        atexit.register(_MOCK["proc"].kill)
        for _ in range(50):
            try:
                socket.create_connection(("localhost", 3001), timeout=0.2).close()
                break
            except OSError:
                time.sleep(0.1)
    urllib.request.urlopen("http://localhost:3001/__reset", timeout=3).read()


def merged_bundle(bundles, name):
    """bundle="p1,net" merges the files of several bundles (first one wins on clashes)."""
    merged = {}
    for part in (name or "").split(","):
        for k, v in bundles.get(part.strip(), {}).items():
            merged.setdefault(k, v)
    return merged


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
            for _name in _b["attrs"]["bundle"].split(","):
                bundles.setdefault(_name.strip(), {})[_b["attrs"]["file"]] = _b["code"]

    mock_src = next((_b["code"] for _bs, _i, _b in sequence(flat)
                     if _b["t"] == "code" and _b["attrs"].get("file") == "mock-server.mjs"), None)
    sib = ROOT / "content" / "student" / Path(path).name
    if meta.get("kind") == "instructor" and sib.exists():
        # keys share the mock server and bundles (http.js, ...) defined in the student sheet
        _, st_text = load_source(sib)
        _, st_body = parse_front_matter(st_text)
        for _bs, _i, _b in sequence(parse_blocks(st_body)):
            if _b["t"] != "code":
                continue
            if "bundle" in _b["attrs"] and "file" in _b["attrs"]:
                for _name in _b["attrs"]["bundle"].split(","):
                    bundles.setdefault(_name.strip(), {}).setdefault(_b["attrs"]["file"], _b["code"])
            if mock_src is None and _b["attrs"].get("file") == "mock-server.mjs":
                mock_src = _b["code"]

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
                if "mock" in flags:
                    ensure_mock(mock_src)
                rc, out, err = run_node(code, merged_bundle(bundles, b["attrs"].get("bundle")))
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
                if "mock" in flags:
                    ensure_mock(mock_src)
                logs = run_page(code, b["attrs"].get("steps", ""),
                                merged_bundle(bundles, b["attrs"].get("bundle")),
                                b["attrs"].get("ignore", ""))
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
