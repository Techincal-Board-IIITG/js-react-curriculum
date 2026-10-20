"""Custom ReportLab flowables: code blocks, headings, and diagrams."""
from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.lexers.special import TextLexer
from pygments.token import Token
from reportlab.lib.colors import white, HexColor
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Flowable, Paragraph

from . import theme as T

# ------------------------------------------------------------------ code
LEXER_ALIASES = {"js": "javascript", "jsx": "jsx", "javascript": "javascript",
                 "json": "json", "html": "html", "css": "css", "bash": "bash",
                 "sh": "bash", "shell": "bash", "diff": "diff", "ini": "ini",
                 "md": "markdown", "yaml": "yaml", "text": None, "tree": None,
                 "output": None, "": None, "env": "ini"}


def _color_for(ttype):
    C = T.CODE_COLORS
    if ttype in Token.Comment:
        return C["comment"]
    if ttype in Token.Keyword:
        return C["keyword"]
    if ttype in Token.Literal.String:
        return C["string"]
    if ttype in Token.Literal.Number:
        return C["number"]
    if ttype in Token.Name.Function or ttype in Token.Name.Function.Magic:
        return C["func"]
    if ttype in Token.Name.Tag:
        return C["tag"]
    if ttype in Token.Name.Attribute:
        return C["attr"]
    if ttype in Token.Name.Builtin or ttype in Token.Name.Class:
        return C["builtin"]
    if ttype in Token.Operator:
        return C["op"]
    if ttype in Token.Punctuation:
        return C["punct"]
    return C["fg"]


def highlight_lines(code: str, lang: str, plain_color=None):
    """Return list of lines; each line is list of (text, color)."""
    code = code.replace("\t", "  ").rstrip("\n")
    name = LEXER_ALIASES.get(lang, lang)
    if plain_color is not None or not name:
        return [[(ln, plain_color or T.CODE_FG)] if ln else [] for ln in code.split("\n")]
    try:
        lexer = get_lexer_by_name(name)
    except Exception:
        lexer = TextLexer()
    lines, cur = [], []
    for ttype, value in lex(code, lexer):
        col = _color_for(ttype)
        parts = value.split("\n")
        for i, part in enumerate(parts):
            if i > 0:
                lines.append(cur)
                cur = []
            if part:
                cur.append((part, col))
    lines.append(cur)
    while len(lines) > 1 and not lines[-1]:
        lines.pop()
    return lines


class CodeBlock(Flowable):
    FS = 8.2
    LEAD = 11.7
    PAD = 7
    HEAD = 17
    MIN_SPLIT = 4

    def __init__(self, lines, label="", kind="code", numbered=True, start=1,
                 first=True, accent=None):
        super().__init__()
        self.lines = lines          # list[list[(text,color)]]
        self.label = label
        self.kind = kind            # code | bad | good | output | plain
        self.numbered = numbered
        self.start = start          # first logical line number in this fragment
        self.first = first
        self.accent = accent
        self.spaceBefore = 5 if first else 0
        self.spaceAfter = 9
        self.charw = stringWidth("M", "Mono", self.FS)

    # layout ---------------------------------------------------------
    def _gutter(self, total_lines):
        if not self.numbered:
            return 0
        digits = len(str(self.start + total_lines))
        return digits * self.charw + 12

    def _layout(self, aw):
        g = self._gutter(len(self.lines))
        maxc = max(10, int((aw - 2 * self.PAD - g) / self.charw))
        rows = []  # (lineno or None, runs)
        per_line = []
        for i, runs in enumerate(self.lines):
            text_len = sum(len(t) for t, _ in runs)
            if text_len <= maxc:
                rows.append((self.start + i, runs))
                per_line.append(1)
                continue
            # defensive hard wrap (validator should prevent this)
            chunks, cur, n = [], [], 0
            for t, col in runs:
                while t:
                    room = maxc - n
                    cur.append((t[:room], col))
                    n += len(t[:room])
                    t = t[room:]
                    if n >= maxc:
                        chunks.append(cur)
                        cur, n = [], 0
            if cur:
                chunks.append(cur)
            for j, ch in enumerate(chunks):
                rows.append((self.start + i if j == 0 else None, ch))
            per_line.append(len(chunks))
        return rows, per_line, g

    def _head_h(self):
        return self.HEAD if (self.first and self.label) else 0

    def wrap(self, aw, ah):
        self._aw = aw
        self._rows, self._per_line, self._g = self._layout(aw)
        self._h = self._head_h() + 2 * self.PAD + len(self._rows) * self.LEAD
        return aw, self._h

    def split(self, aw, ah):
        self.wrap(aw, ah)
        if self._h <= ah:
            return [self]
        avail_rows = int((ah - self._head_h() - 2 * self.PAD) // self.LEAD)
        used = k = 0
        for n in self._per_line:
            if used + n > avail_rows:
                break
            used += n
            k += 1
        if k < min(self.MIN_SPLIT, len(self.lines)):
            return []
        a = CodeBlock(self.lines[:k], self.label, self.kind, self.numbered,
                      self.start, self.first, self.accent)
        b = CodeBlock(self.lines[k:], self.label, self.kind, self.numbered,
                      self.start + k, False, self.accent)
        return [a, b]

    # drawing --------------------------------------------------------
    def draw(self):
        c, w, h = self.canv, self._aw, self._h
        light = self.kind in ("output",)
        bg = T.OUT_BG if light else T.CODE_BG
        c.saveState()
        c.setFillColor(bg)
        c.roundRect(0, 0, w, h, 4, fill=1, stroke=0)
        head = self._head_h()
        if head:
            hc = {"bad": T.BAD_COLOR, "good": T.GOOD_COLOR}.get(self.kind)
            c.setFillColor(hc or (T.OUT_BG if light else T.CODE_HEAD))
            c.roundRect(0, h - head, w, head, 4, fill=1, stroke=0)
            c.rect(0, h - head, w, head / 2, fill=1, stroke=0)
            lab = self.label
            if self.kind == "bad":
                lab = "\u2717  INCORRECT  \u00b7  " + lab if lab else "\u2717  INCORRECT"
            elif self.kind == "good":
                lab = "\u2713  CORRECTED  \u00b7  " + lab if lab else "\u2713  CORRECTED"
            c.setFillColor(white if (hc or not light) else T.MUTED)
            c.setFont("Sym-Bold", 6.8)
            c.drawString(self.PAD + 1, h - head + 5.6, lab[:120])
            if self.accent is not None and not hc and not light:
                c.setFillColor(self.accent)
                c.rect(0, h - head, 3, head, fill=1, stroke=0)
        if self.numbered and self._g:
            c.setStrokeColor(HexColor("#2a3656"))
            c.setLineWidth(0.5)
            c.line(self.PAD + self._g - 6, 3, self.PAD + self._g - 6, h - head - 3)
        c.setFont("Mono", self.FS)
        top = h - head - self.PAD
        x0 = self.PAD + self._g
        for i, (no, runs) in enumerate(self._rows):
            y = top - (i + 1) * self.LEAD + 3.2
            if no is not None and self.numbered:
                c.setFillColor(T.CODE_GUTTER)
                c.drawRightString(self.PAD + self._g - 11, y, str(no))
            x = x0
            for text, col in runs:
                c.setFillColor(T.OUT_FG if light else col)
                c.drawString(x, y, text)
                x += self.charw * len(text)
        c.restoreState()


# -------------------------------------------------------------- headings
class H1(Paragraph):
    """Section heading: small label, big serif title, accent rule."""

    def __init__(self, text, label, style, accent):
        super().__init__(text, style)
        self.label = label
        self.accent = accent
        self.toc_level = 0
        self.toc_text = None

    def wrap(self, aw, ah):
        self._w = aw
        w, h = super().wrap(aw, ah)
        return w, h + 30

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(self.accent)
        c.setFont("Sans-Bold", 8.5)
        c.drawString(0, self.height + 17, self.label.upper())
        c.restoreState()
        c.saveState()
        c.translate(0, 8)
        super().draw()
        c.restoreState()
        c.saveState()
        c.setStrokeColor(self.accent)
        c.setLineWidth(1.6)
        c.line(0, 1, self._w, 1)
        c.restoreState()


class H2(Paragraph):
    def __init__(self, text, style, accent):
        super().__init__(text, style)
        self.accent = accent
        self.toc_level = 1
        self.toc_text = None

    def wrap(self, aw, ah):
        w, h = super().wrap(aw, ah)
        return w, h + 7

    def draw(self):
        c = self.canv
        c.saveState()
        c.translate(0, 7)
        super().draw()
        c.restoreState()
        c.saveState()
        c.setStrokeColor(self.accent)
        c.setLineWidth(2)
        c.line(0, 2, 34, 2)
        c.restoreState()


# -------------------------------------------------------------- diagrams
def _arrow(c, x1, y1, x2, y2, color, dashed=False, head=4.2):
    import math
    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1)
    if dashed:
        c.setDash(3, 2)
    ang = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * math.cos(ang), y2 - head * math.sin(ang)
    c.line(x1, y1, bx, by)
    c.setDash()
    p = c.beginPath()
    p.moveTo(x2, y2)
    p.lineTo(bx + head * 0.55 * math.sin(ang), by - head * 0.55 * math.cos(ang))
    p.lineTo(bx - head * 0.55 * math.sin(ang), by + head * 0.55 * math.cos(ang))
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


def _box(c, x, y, w, h, lines, accent, strong=False, fs=8.2):
    c.saveState()
    c.setLineWidth(1)
    c.setStrokeColor(accent)
    c.setFillColor(accent if strong else HexColor("#f4f6fa"))
    c.roundRect(x, y, w, h, 4, fill=1, stroke=1)
    n = len(lines)
    lead = fs + 2.4
    ty = y + h / 2 + (n - 1) * lead / 2 - fs * 0.33
    for i, ln in enumerate(lines):
        bold = i == 0
        c.setFillColor(white if strong else T.INK)
        c.setFont("Sans-Bold" if bold else "Sans", fs if bold else fs - 0.8)
        c.drawCentredString(x + w / 2, ty - i * lead, ln)
    c.restoreState()


def _wrap_label(text, width, fs=8.2):
    out = []
    for part in text.split("|"):
        part = part.strip()
        font = "Sans-Bold" if not out else "Sans"
        out.extend(simpleSplit(part, font, fs if not out else fs - 0.8, width) or [""])
    return out


class FlowDiagram(Flowable):
    """Chain of boxes: 'A -> B -> C'. A leading * marks a highlighted box."""

    def __init__(self, text, accent):
        super().__init__()
        items = [s.strip() for s in text.replace("\n", " ").split("->") if s.strip()]
        self.items = items
        self.accent = accent
        self.spaceBefore, self.spaceAfter = 4, 10

    def wrap(self, aw, ah):
        n = len(self.items)
        per = min(n, 4 if aw > 400 else 3)
        gap = 26
        bw = min(118, (aw - gap * (per - 1)) / per)
        self.per, self.gap, self.bw, self.aw = per, gap, bw, aw
        self.labels = [_wrap_label(i.lstrip("*").strip(), bw - 10) for i in self.items]
        rows = [self.labels[i:i + per] for i in range(0, n, per)]
        self.rowh = [max(len(l) for l in r) * 10.4 + 14 for r in rows]
        self.vgap = 26
        self.h = sum(self.rowh) + self.vgap * (len(rows) - 1) + 4
        return aw, self.h

    def draw(self):
        c = self.canv
        n = len(self.items)
        y_top = self.h - 2
        pos = []
        for r in range(0, n, self.per):
            ri = r // self.per
            rh = self.rowh[ri]
            cnt = min(self.per, n - r)
            total = cnt * self.bw + (cnt - 1) * self.gap
            x0 = (self.aw - total) / 2 if ri == 0 or cnt == self.per else (self.aw - total) / 2
            y = y_top - rh
            for k in range(cnt):
                idx = r + k
                x = x0 + k * (self.bw + self.gap)
                _box(c, x, y, self.bw, rh, self.labels[idx], self.accent,
                     strong=self.items[idx].startswith("*"))
                pos.append((x, y, rh))
            y_top = y - self.vgap
        for i in range(n - 1):
            x, y, rh = pos[i]
            nx, ny, nrh = pos[i + 1]
            if abs(y - ny) < 1:
                _arrow(c, x + self.bw, y + rh / 2, nx, ny + nrh / 2, self.accent)
            else:  # elbow down to the next row
                mid = y - self.vgap / 2
                c.saveState()
                c.setStrokeColor(self.accent)
                c.setLineWidth(1)
                c.line(x + self.bw / 2, y, x + self.bw / 2, mid)
                c.line(x + self.bw / 2, mid, nx + self.bw / 2, mid)
                c.restoreState()
                _arrow(c, nx + self.bw / 2, mid, nx + self.bw / 2, ny + nrh, self.accent)


class TreeDiagram(Flowable):
    """Indented list -> top-down tree of boxes (component trees, call trees)."""

    def __init__(self, text, accent):
        super().__init__()
        self.accent = accent
        self.root = None
        stack = []
        for raw in text.split("\n"):
            if not raw.strip():
                continue
            depth = (len(raw) - len(raw.lstrip(" "))) // 2
            node = {"text": raw.strip(), "kids": []}
            if depth == 0 and self.root is None:
                self.root = node
                stack = [node]
                continue
            while len(stack) > depth:
                stack.pop()
            stack[-1]["kids"].append(node)
            stack.append(node)
        self.spaceBefore, self.spaceAfter = 4, 10

    FS = 8.0

    def _measure(self, node):
        lines = _wrap_label(node["text"], 120, self.FS)
        w = max(stringWidth(l, "Sans-Bold" if i == 0 else "Sans", self.FS) for i, l in enumerate(lines)) + 14
        node["lines"], node["bw"] = lines, max(w, 64)
        node["bh"] = len(lines) * 10 + 11
        for k in node["kids"]:
            self._measure(k)
        kids_w = sum(k["sw"] for k in node["kids"]) + 10 * max(0, len(node["kids"]) - 1)
        node["sw"] = max(node["bw"], kids_w)

    def _depth(self, n):
        return 1 + max([self._depth(k) for k in n["kids"]] or [0])

    def wrap(self, aw, ah):
        self._measure(self.root)
        self.scale = min(1.0, aw / self.root["sw"])
        self.vgap = 22
        self.levels = self._depth(self.root)
        self.bh = max(self._maxh(self.root), 22)
        self.h = (self.levels * self.bh + (self.levels - 1) * self.vgap) * self.scale + 2
        self.aw = aw
        return aw, self.h

    def _maxh(self, n):
        return max([n["bh"]] + [self._maxh(k) for k in n["kids"]])

    def draw(self):
        c = self.canv
        c.saveState()
        c.scale(self.scale, self.scale)
        top = self.h / self.scale - 1
        x0 = (self.aw / self.scale - self.root["sw"]) / 2
        self._draw(c, self.root, x0, top, 0)
        c.restoreState()

    def _draw(self, c, n, x, top, depth):
        bx = x + (n["sw"] - n["bw"]) / 2
        by = top - n["bh"]
        _box(c, bx, by, n["bw"], n["bh"], n["lines"], self.accent,
             strong=(depth == 0), fs=self.FS)
        cx = x + (n["sw"] - sum(k["sw"] for k in n["kids"]) - 10 * max(0, len(n["kids"]) - 1)) / 2
        childtop = top - self.bh - self.vgap
        for k in n["kids"]:
            kx = cx + (k["sw"] - k["bw"]) / 2
            c.saveState()
            c.setStrokeColor(self.accent)
            c.setLineWidth(1)
            mid = by - (self.vgap + self.bh - n["bh"]) / 2
            c.line(bx + n["bw"] / 2, by, bx + n["bw"] / 2, mid)
            c.line(bx + n["bw"] / 2, mid, kx + k["bw"] / 2, mid)
            c.line(kx + k["bw"] / 2, mid, kx + k["bw"] / 2, childtop)
            c.restoreState()
            self._draw(c, k, cx, childtop, depth + 1)
            cx += k["sw"] + 10


class SequenceDiagram(Flowable):
    """actors: A | B | C   then   'A -> B: text', 'B --> A: text', 'note: text'."""

    FS = 7.8

    def __init__(self, text, accent):
        super().__init__()
        self.accent = accent
        self.actors, self.msgs = [], []
        for raw in text.split("\n"):
            ln = raw.strip()
            if not ln:
                continue
            if ln.lower().startswith("actors:"):
                self.actors = [a.strip() for a in ln[7:].split("|")]
            elif ln.lower().startswith("note:"):
                self.msgs.append(("note", None, None, ln[5:].strip()))
            else:
                head, _, label = ln.partition(":")
                dashed = "-->" in head
                a, _, b = head.replace("-->", "->").partition("->")
                self.msgs.append(("msg" if not dashed else "dash", a.strip(), b.strip(), label.strip()))
        self.spaceBefore, self.spaceAfter = 4, 10

    def wrap(self, aw, ah):
        self.aw = aw
        n = len(self.actors)
        self.colw = aw / n
        self.rows = []
        for kind, a, b, label in self.msgs:
            if kind == "note":
                lines = simpleSplit(label, "Sans-Italic", self.FS, aw - 40)
            else:
                span = max(abs(self.actors.index(a) - self.actors.index(b)), 1) * self.colw - 14
                lines = simpleSplit(label, "Sans", self.FS, span)
            self.rows.append(lines)
        self.headh = 22
        self.h = self.headh + 8 + sum(len(l) * 9.4 + 16 for l in self.rows) + 4
        return aw, self.h

    def draw(self):
        c = self.canv
        xs = [self.colw * (i + 0.5) for i in range(len(self.actors))]
        bw = min(self.colw - 8, 100)
        for x, name in zip(xs, self.actors):
            _box(c, x - bw / 2, self.h - self.headh, bw, self.headh, [name], self.accent, True, 8)
            c.saveState()
            c.setStrokeColor(T.RULE)
            c.setDash(2, 3)
            c.line(x, 0, x, self.h - self.headh)
            c.restoreState()
        y = self.h - self.headh - 8
        for (kind, a, b, label), lines in zip(self.msgs, self.rows):
            rh = len(lines) * 9.4 + 16
            if kind == "note":
                c.saveState()
                c.setFillColor(HexColor("#fdf3e3"))
                c.setStrokeColor(HexColor("#e5c48f"))
                c.roundRect(20, y - rh + 6, self.aw - 40, rh - 8, 3, fill=1, stroke=1)
                c.setFillColor(T.INK)
                c.setFont("Sans-Italic", self.FS)
                cy = y - rh + 6 + (rh - 8) / 2
                for i, ln in enumerate(lines):
                    c.drawCentredString(self.aw / 2,
                                        cy + (len(lines) - 1) * 9.4 / 2 - 2.6 - i * 9.4, ln)
                c.restoreState()
            else:
                xa, xb = xs[self.actors.index(a)], xs[self.actors.index(b)]
                ay = y - len(lines) * 9.4 - 5
                c.saveState()
                c.setFillColor(T.INK)
                c.setFont("Sans", self.FS)
                for i, ln in enumerate(lines):
                    c.drawCentredString((xa + xb) / 2 if xa != xb else xa + 40, y - 6 - i * 9.4, ln)
                c.restoreState()
                if xa == xb:
                    _arrow(c, xa, ay, xa + 2, ay - 4, self.accent)
                else:
                    off = 3 if xb > xa else -3
                    _arrow(c, xa + off, ay, xb - off, ay, self.accent, dashed=(kind == "dash"))
            y -= rh


def make_diagram(spec: str, accent):
    kind, _, rest = spec.partition("\n")
    kind = kind.strip().lower()
    if kind == "flow":
        return FlowDiagram(rest, accent)
    if kind == "tree":
        return TreeDiagram(rest, accent)
    if kind == "sequence":
        return SequenceDiagram(rest, accent)
    raise ValueError(f"unknown diagram kind {kind!r}")
