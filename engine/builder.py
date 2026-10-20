"""Turn parsed curriculum source into a designed PDF."""
import html
import re
from pathlib import Path

from reportlab.lib.colors import white, HexColor
from reportlab.lib.utils import simpleSplit
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Frame, HRFlowable, KeepTogether,
                                NextPageTemplate, PageBreak, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

from . import theme as T
from .flowables import (CodeBlock, H1, H2, highlight_lines, make_diagram)
from .parser import load_source, parse_blocks, parse_front_matter

BRAND = "JavaScript + React Curriculum"


# ----------------------------------------------------------- inline markup
def inline(text, code_size=T.INLINE_CODE_SIZE):
    spans = []

    def stash(m):
        spans.append(m.group(1))
        return f"\x00{len(spans) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                  r'<a href="\2" color="#1d4ed8"><u>\1</u></a>', text)
    text = T.sym_fallback(text)

    def unstash(m):
        code = html.escape(spans[int(m.group(1))], quote=False)
        code = code.replace(" ", "&nbsp;") if len(code) < 28 else code
        return (f'<font name="Mono" size="{code_size}" color="{T.INLINE_CODE_FG}" '
                f'backColor="{T.INLINE_CODE_BG}">&#8202;{code}&#8202;</font>')

    return re.sub(r"\x00(\d+)\x00", unstash, text)


def plain(text):
    return re.sub(r"[`*]|\[([^\]]+)\]\([^)]*\)", lambda m: m.group(1) or "", text)


# ---------------------------------------------------------- document class
class Doc(BaseDocTemplate):
    def __init__(self, path, meta, accent, **kw):
        super().__init__(path, pagesize=T.A4, leftMargin=T.LM, rightMargin=T.RM,
                         topMargin=T.TM, bottomMargin=T.BM,
                         title=f"{meta.get('number', '')} {meta['title']}".strip(),
                         author="JS + React Curriculum", subject=meta.get("subtitle", ""),
                         **kw)
        self.meta, self.accent = meta, accent
        self.cur_h1 = ""
        self._key = 0
        body = Frame(T.LM, T.BM, T.CONTENT_W, T.PAGE_H - T.TM - T.BM, id="body",
                     leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        cover = Frame(0, 0, T.PAGE_W, T.PAGE_H, id="cover", leftPadding=0, rightPadding=0,
                      topPadding=0, bottomPadding=0)
        self.addPageTemplates([
            PageTemplate("cover", frames=[cover], onPage=self._cover, autoNextPageTemplate="body"),
            PageTemplate("body", frames=[body], onPageEnd=self._chrome),
        ])

    # -- cover -----------------------------------------------------------
    def _cover(self, c, doc):
        m, acc = self.meta, self.accent
        lite = T.COVER_LITE.get(m.get("track", "js"), acc)
        W, H = T.PAGE_W, T.PAGE_H
        c.saveState()
        c.setFillColor(T.NAVY)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        num = str(m.get("number", ""))
        if num:
            c.setFillColor(HexColor("#18233d"))
            c.setFont("Serif-Bold", 310)
            c.drawString(14, H - 400, num)
        c.setFillColor(acc)
        c.rect(0, 0, 16, H, fill=1, stroke=0)
        left = 64
        c.setFillColor(HexColor("#9fb0cf"))
        c.setFont("Sans-Bold", 8.5)
        c.drawString(left, H - 70, BRAND.upper())
        c.setFillColor(HexColor("#ffffff"))
        c.setFillAlpha(0.0)
        c.setFillAlpha(1.0)
        label = m.get("label") or (f"SHEET {num} OF 12" if num else T.TRACK_NAMES.get(m.get("track", ""), "").upper())
        c.setFillColor(lite)
        c.setFont("Sans-Bold", 10)
        c.drawString(left, H - 250, label)
        tw = W - left - 60
        title = Paragraph(inline_plain(m["title"]), self._cover_style("Serif-Bold", 36, 41, "#ffffff"))
        _, th = title.wrap(tw, 400)
        y = H - 270 - th
        title.drawOn(c, left, y)
        sub = Paragraph(inline_plain(m.get("subtitle", "")), self._cover_style("Sans", 13.5, 19, "#c3cde0"))
        _, sh = sub.wrap(tw, 200)
        y -= sh + 14
        sub.drawOn(c, left, y)
        c.setStrokeColor(acc)
        c.setLineWidth(2)
        c.line(left, y - 14, left + 60, y - 14)
        goals = m.get("goals", [])
        if goals:
            gy = y - 44
            c.setFillColor(HexColor("#9fb0cf"))
            c.setFont("Sans-Bold", 8.5)
            c.drawString(left, gy, "WHAT YOU WILL BE ABLE TO DO")
            gy -= 8
            gs = self._cover_style("Sans", 10.2, 14.2, "#e3e9f5")
            for g in goals:
                p = Paragraph(inline_plain(g), gs)
                _, gh = p.wrap(tw - 18, 100)
                gy -= gh + 4
                c.setFillColor(lite)
                c.circle(left + 3, gy + gh - 6, 2.2, fill=1, stroke=0)
                p.drawOn(c, left + 16, gy)
        c.setFillColor(HexColor("#9fb0cf"))
        c.setFont("Sans", 8.8)
        meta_line = "  \u00b7  ".join(x for x in [T.TRACK_NAMES.get(m.get("track", ""), ""),
                                                  m.get("time", ""), m.get("edition", "")] if x)
        c.drawString(left, 56, meta_line)
        c.restoreState()

    @staticmethod
    def _cover_style(font, size, lead, color):
        from reportlab.lib.styles import ParagraphStyle
        return ParagraphStyle("cv", fontName=font, fontSize=size, leading=lead,
                              textColor=HexColor(color))

    # -- header / footer -------------------------------------------------
    def _chrome(self, c, doc):
        m = self.meta
        c.saveState()
        c.setStrokeColor(T.RULE)
        c.setLineWidth(0.6)
        c.line(T.LM, T.PAGE_H - 46, T.PAGE_W - T.RM, T.PAGE_H - 46)
        c.setFont("Sans-Bold", 7.6)
        c.setFillColor(self.accent)
        c.drawString(T.LM, T.PAGE_H - 40, BRAND.upper())
        c.setFont("Sans", 7.8)
        c.setFillColor(T.MUTED)
        right = plain(self.cur_h1) if self.cur_h1 else ""
        c.drawRightString(T.PAGE_W - T.RM, T.PAGE_H - 40, right[:80])
        c.line(T.LM, 44, T.PAGE_W - T.RM, 44)
        c.setFont("Sans", 7.8)
        foot = (f"{m.get('number', '')} \u00b7 " if m.get("number") else "") + m["title"]
        if m.get("kind") == "instructor":
            foot += "  \u00b7  INSTRUCTOR EDITION \u2013 do not distribute to students"
        c.drawString(T.LM, 31, foot[:110])
        c.setFont("Sans-Bold", 8.4)
        c.setFillColor(T.INK)
        c.drawRightString(T.PAGE_W - T.RM, 31, f"{doc.page}")
        c.restoreState()

    # -- TOC / bookmarks -------------------------------------------------
    def beforeDocument(self):
        self._key = 0
        self.cur_h1 = ""

    def afterFlowable(self, f):
        if hasattr(f, "toc_level"):
            self._key += 1
            key = f"h{self._key}"
            text = f.toc_text or f.getPlainText()
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text, key, f.toc_level, closed=(f.toc_level > 0))
            self.notify("TOCEntry", (f.toc_level, text, self.page, key))
            if f.toc_level == 0:
                self.cur_h1 = text


def inline_plain(text):
    return T.sym_fallback(html.escape(plain(text), quote=False))


# -------------------------------------------------------------- converters
class Ctx:
    def __init__(self, accent):
        self.accent = accent
        self.S = T.styles(accent)
        self.h1_count = 0
        self.project_count = 0


def table_flowable(b, ctx):
    S = ctx.S
    ncol = len(b["head"])
    data = [[Paragraph(inline(c), S["cellh"]) for c in b["head"]]]
    for r in b["rows"]:
        data.append([Paragraph(inline(c), S["cell"]) for c in r])
    if b["widths"]:
        tot = sum(b["widths"])
        cw = [T.CONTENT_W * w / tot for w in b["widths"]]
    else:
        weights = []
        for j in range(ncol):
            cells = [b["head"][j]] + [r[j] for r in b["rows"]]
            lens = [len(plain(c)) for c in cells]
            longest_word = max(len(w) for c in cells for w in plain(c).split() or [""])
            avg = sum(lens) / len(lens)
            weights.append(max(7, min(avg, 46)) + 0.6 * min(longest_word, 20))
        tot = sum(weights)
        cw = [max(44, T.CONTENT_W * w / tot) for w in weights]
        scale = T.CONTENT_W / sum(cw)
        cw = [w * scale for w in cw]
    t = Table(data, colWidths=cw, repeatRows=1, splitByRow=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), T.INK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, T.RULE),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, T.RULE),
    ]
    for r in range(2, len(data), 2):
        style.append(("BACKGROUND", (0, r), (-1, r), T.SOFT))
    t.setStyle(TableStyle(style))
    t.spaceBefore, t.spaceAfter = 4, 10
    return t


def callout_flowable(kind, title, children, ctx):
    label, bar, tint = T.CALLOUTS[kind]
    S = ctx.S
    head = f'<font name="Sans-Bold" size="7.6" color="{bar.hexval().replace("0x", "#")}">{label}</font>'
    if title:
        head += f'&nbsp;&nbsp;<font name="Sans-Bold">{inline(title)}</font>'
    rows = [[Paragraph(head, S["callout"])]]
    for b in children:
        if b["t"] == "para":
            rows.append([Paragraph(inline(b["text"]), S["callout"])])
        elif b["t"] == "list":
            n = 0
            for it in b["items"]:
                n += 1
                bullet = f"{n}." if it["ordered"] else "\u2022"
                st = S["callout"].clone("cl", leftIndent=14 + 12 * it["level"],
                                        bulletIndent=2 + 12 * it["level"], bulletFontName="Sans-Bold")
                rows.append([Paragraph(inline(it["text"]), st, bulletText=bullet)])
        elif b["t"] == "code":
            raise ValueError("code blocks are not allowed inside callouts; place them after")
    t = Table(rows, colWidths=[T.CONTENT_W], splitByRow=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), tint),
        ("LINEBEFORE", (0, 0), (0, -1), 3.2, bar),
        ("LEFTPADDING", (0, 0), (-1, -1), 11), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("TOPPADDING", (0, 0), (-1, 0), 7), ("BOTTOMPADDING", (0, -1), (-1, -1), 7),
    ]))
    t.spaceBefore, t.spaceAfter = 5, 10
    return t


def project_header(args, ctx):
    ctx.project_count += 1
    parts = [p.strip() for p in args.split("|")]
    title = parts[0]
    diff = parts[1] if len(parts) > 1 else ""
    scope = parts[2] if len(parts) > 2 else ""
    left = (f'<font name="Sans-Bold" size="7.6" color="#ffffff">PROJECT {ctx.project_count}</font><br/>'
            f'<font name="Serif-Bold" size="13.5" color="#ffffff">{inline_plain(title)}</font>')
    right = ""
    if diff:
        right += f'<font name="Sans-Bold" size="8" color="#ffffff">{T.sym_fallback(html.escape(diff))}</font><br/>'
    if scope:
        right += f'<font name="Sans-Bold" size="7.6" color="#ffffff">{html.escape(scope.upper())}</font>'
    from reportlab.lib.styles import ParagraphStyle
    ls = ParagraphStyle("pl", fontName="Sans", fontSize=10, leading=17, textColor=white)
    rs = ParagraphStyle("pr", parent=ls, alignment=2, leading=11.5)
    t = Table([[Paragraph(left, ls), Paragraph(right, rs)]],
              colWidths=[T.CONTENT_W - 130, 130], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), ctx.accent),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    t.spaceBefore, t.spaceAfter = 6, 6
    return t


def code_flowable(b, ctx):
    lang, attrs, flags = b["lang"], b["attrs"], b["flags"]
    label = attrs.get("file") or attrs.get("env") or ""
    if not label and lang not in ("output", "text", "tree", ""):
        label = {"js": "JavaScript", "jsx": "JSX", "html": "HTML", "css": "CSS", "json": "JSON",
                 "bash": "Terminal", "sh": "Terminal"}.get(lang, lang)
    if lang == "output":
        label = label or "Output"
        return CodeBlock(highlight_lines(b["code"], "output", T.OUT_FG), label, "output", False)
    if lang in ("text", "tree"):
        label = label or ("File tree" if lang == "tree" else "")
        return CodeBlock(highlight_lines(b["code"], "text", T.CODE_FG), label, "code", False,
                         accent=ctx.accent)
    kind = "bad" if "bad" in flags else "good" if "good" in flags else "code"
    return CodeBlock(highlight_lines(b["code"], lang), label, kind, True, accent=ctx.accent)


def blocks_to_flowables(blocks, ctx):
    S, out = ctx.S, []
    skip_next = False
    for idx, b in enumerate(blocks):
        if skip_next:
            skip_next = False
            continue
        t = b["t"]
        nxt = blocks[idx + 1] if idx + 1 < len(blocks) else None
        if (t == "code" and b["lang"] not in ("output", "diagram", "text", "tree") and nxt
                and nxt["t"] == "code" and nxt["lang"] == "output"
                and len(b["code"].split("\n")) <= 30):
            out.append(KeepTogether([code_flowable(b, ctx), code_flowable(nxt, ctx)]))
            skip_next = True
            continue
        if t == "h":
            lvl, txt = b["level"], b["text"]
            if lvl == 1:
                ctx.h1_count += 1
                m = re.match(r"^(\d+|[A-Z])\.\s+(.*)$", txt)
                label = f"Section {m.group(1)}" if m else "Section"
                title = m.group(2) if m else txt
                out.append(PageBreak())
                st = S["h2"].clone("h1s", fontSize=25, leading=29, spaceBefore=0, spaceAfter=0)
                h = H1(inline_plain(title), label, st, ctx.accent)
                h.toc_text = plain(txt)
                out.append(h)
                out.append(Spacer(1, 10))
            elif lvl == 2:
                out.append(CondPageBreak(130))
                h = H2(inline_plain(b["text"]), S["h2"], ctx.accent)
                h.toc_text = plain(b["text"])
                out.append(h)
            elif lvl == 3:
                out.append(CondPageBreak(100))
                out.append(Paragraph(inline(b["text"]), S["h3"]))
            elif lvl == 4:
                out.append(CondPageBreak(80))
                out.append(Paragraph(inline(b["text"]), S["h4"]))
            else:
                out.append(CondPageBreak(60))
                out.append(Paragraph(inline(b["text"]).upper() if "<" not in inline(b["text"]) else inline(b["text"]), S["h5"]))
        elif t == "para":
            out.append(Paragraph(inline(b["text"]), S["body"]))
        elif t == "list":
            counters = {}
            for it in b["items"]:
                lvl = it["level"]
                counters = {k: v for k, v in counters.items() if k <= lvl}
                text = it["text"]
                style = S["li"]
                if it["ordered"]:
                    counters[lvl] = counters.get(lvl, 0) + 1
                    bullet = f"{counters[lvl]}."
                else:
                    counters.pop(lvl, None)
                    bullet = "\u2022" if lvl == 0 else "\u2013"
                    if text.startswith("[ ] "):
                        bullet, text, style = "\u2610", text[4:], S["li_check"]
                st = style.clone("lx", leftIndent=17 + 15 * lvl, bulletIndent=5 + 15 * lvl)
                out.append(Paragraph(inline(text), st, bulletText=bullet))
            out.append(Spacer(1, 4))
        elif t == "table":
            out.append(table_flowable(b, ctx))
        elif t == "code":
            if b["lang"] == "diagram":
                out.append(make_diagram(b["code"].strip("\n"), ctx.accent))
            else:
                out.append(code_flowable(b, ctx))
        elif t == "pagebreak":
            out.append(PageBreak())
        elif t == "hr":
            out.append(HRFlowable(width="100%", thickness=0.6, color=T.RULE, spaceBefore=6, spaceAfter=8))
        elif t == "container":
            kind, args = b["kind"], b["args"]
            if kind in T.CALLOUTS:
                out.append(callout_flowable(kind, args, b["children"], ctx))
            elif kind == "project":
                out.append(CondPageBreak(200))
                out.append(project_header(args, ctx))
                out.extend(blocks_to_flowables(b["children"], ctx))
                out.append(HRFlowable(width="100%", thickness=0.6, color=T.RULE, spaceBefore=4, spaceAfter=10))
            else:
                raise ValueError(f"unknown container kind {kind!r}")
    return out


# ------------------------------------------------------------------ driver
def build_pdf(src, out_pdf):
    files, text = load_source(src)
    meta, body = parse_front_matter(text)
    track = meta.get("track", "js")
    accent = T.TRACKS[track]
    ctx = Ctx(accent)
    blocks = parse_blocks(body)
    story = [Spacer(1, 1), PageBreak()]  # cover page; template switches to body
    if meta.get("toc", "yes") != "no":
        story.append(Paragraph("Contents", ctx.S["h2"].clone("tochead", fontSize=24, leading=28,
                                                            spaceAfter=10)))
        toc = TableOfContents()
        toc.levelStyles = [ctx.S["toc1"], ctx.S["toc2"]]
        toc.dotsMinLevel = 0
        story.append(toc)
    story.extend(blocks_to_flowables(blocks, ctx))
    doc = Doc(str(out_pdf), meta, accent)
    doc.multiBuild(story)
    return doc.page
