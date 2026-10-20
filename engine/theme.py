"""Design system for the JS + React curriculum PDFs.

One place for fonts, colors and paragraph styles so every sheet looks the same.
"""
import re
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

LIB = "/usr/share/fonts/truetype/liberation/"
DJ = "/usr/share/fonts/truetype/dejavu/"

_fonts = {
    "Sans": LIB + "LiberationSans-Regular.ttf",
    "Sans-Bold": LIB + "LiberationSans-Bold.ttf",
    "Sans-Italic": LIB + "LiberationSans-Italic.ttf",
    "Sans-BoldItalic": LIB + "LiberationSans-BoldItalic.ttf",
    "Serif-Bold": LIB + "LiberationSerif-Bold.ttf",
    "Serif": LIB + "LiberationSerif-Regular.ttf",
    "Mono": DJ + "DejaVuSansMono.ttf",
    "Mono-Bold": DJ + "DejaVuSansMono-Bold.ttf",
    "Mono-Oblique": DJ + "DejaVuSansMono-Oblique.ttf",
    "Mono-BoldOblique": DJ + "DejaVuSansMono-BoldOblique.ttf",
    "Sym": DJ + "DejaVuSans.ttf",
    "Sym-Bold": DJ + "DejaVuSans-Bold.ttf",
}
for _n, _p in _fonts.items():
    pdfmetrics.registerFont(TTFont(_n, _p))
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-Bold",
                              italic="Sans-Italic", boldItalic="Sans-BoldItalic")
pdfmetrics.registerFontFamily("Mono", normal="Mono", bold="Mono-Bold",
                              italic="Mono-Oblique", boldItalic="Mono-BoldOblique")
pdfmetrics.registerFontFamily("Sym", normal="Sym", bold="Sym-Bold",
                              italic="Sym", boldItalic="Sym-Bold")

_sans_cmap = pdfmetrics.getFont("Sans").face.charToGlyph
_mono_cmap = pdfmetrics.getFont("Mono").face.charToGlyph
_sym_cmap = pdfmetrics.getFont("Sym").face.charToGlyph


def sym_fallback(text: str) -> str:
    """Wrap characters Liberation Sans lacks (check marks, stars...) in DejaVu."""
    out = []
    for ch in text:
        if ord(ch) > 127 and ord(ch) not in _sans_cmap and ord(ch) in _sym_cmap:
            out.append(f'<font name="Sym">{ch}</font>')
        else:
            out.append(ch)
    return "".join(out)


def missing_mono_glyphs(code: str):
    return sorted({c for c in code if ord(c) > 127 and ord(c) not in _mono_cmap})


# ---------------------------------------------------------------- colors
PAGE_W, PAGE_H = A4
LM = RM = 56
TM, BM = 72, 62
CONTENT_W = PAGE_W - LM - RM

INK = HexColor("#1b2333")
MUTED = HexColor("#5b6577")
RULE = HexColor("#d9dee8")
NAVY = HexColor("#0f172a")
SOFT = HexColor("#f4f6fa")

TRACKS = {
    "js": HexColor("#b45309"),        # amber: JavaScript sheets 01-04
    "react": HexColor("#0e7490"),     # cyan: React sheets 05-10
    "craft": HexColor("#6d28d9"),     # violet: tooling / professional practice 11-12
    "index": HexColor("#1d4ed8"),
    "instructor": HexColor("#9f1239"),
}
COVER_LITE = {  # brighter accents for text on the navy cover
    "js": HexColor("#f59e0b"), "react": HexColor("#22d3ee"), "craft": HexColor("#a78bfa"),
    "index": HexColor("#60a5fa"), "instructor": HexColor("#fb7185"),
}
TRACK_NAMES = {
    "js": "JavaScript track",
    "react": "React track",
    "craft": "Professional practice track",
    "index": "Curriculum guide",
    "instructor": "Instructor edition",
}

CALLOUTS = {  # kind -> (label, bar color, tint)
    "tip": ("TIP", HexColor("#0f766e"), HexColor("#eaf6f4")),
    "warning": ("WARNING", HexColor("#b45309"), HexColor("#fdf3e3")),
    "concept": ("KEY CONCEPT", HexColor("#3730a3"), HexColor("#eef0fc")),
    "note": ("NOTE", HexColor("#475569"), HexColor("#f1f4f8")),
    "mistake": ("COMMON MISTAKE", HexColor("#b91c1c"), HexColor("#fceeee")),
    "try": ("TRY IT", HexColor("#047857"), HexColor("#e9f7f0")),
    "hint": ("HINT", HexColor("#6d28d9"), HexColor("#f3effc")),
}

# code theme (dark, high contrast)
CODE_BG = HexColor("#121a2b")
CODE_HEAD = HexColor("#1f2a44")
CODE_FG = HexColor("#e6ebf5")
CODE_GUTTER = HexColor("#6d7a96")
CODE_COLORS = {
    "comment": HexColor("#8b98b5"),
    "keyword": HexColor("#c8a2ff"),
    "string": HexColor("#a6e3a1"),
    "number": HexColor("#fab387"),
    "func": HexColor("#8ab4ff"),
    "builtin": HexColor("#ffd479"),
    "tag": HexColor("#ff8f9c"),
    "attr": HexColor("#ffd479"),
    "op": HexColor("#8be9fd"),
    "punct": HexColor("#b4bfd6"),
    "fg": CODE_FG,
}
OUT_BG = HexColor("#eef2f7")
OUT_FG = HexColor("#1b2333")
BAD_COLOR = HexColor("#b91c1c")
GOOD_COLOR = HexColor("#047857")


def styles(accent):
    base = dict(fontName="Sans", textColor=INK, alignment=TA_LEFT)
    s = {}
    s["body"] = ParagraphStyle("body", fontSize=10, leading=14.6, spaceAfter=6.5, **base)
    s["li"] = ParagraphStyle("li", parent=s["body"], spaceAfter=2.5, leftIndent=17,
                             bulletIndent=5, bulletFontName="Sans-Bold", bulletColor=accent)
    s["li_check"] = ParagraphStyle("li_check", parent=s["li"], bulletFontName="Sym")
    s["h2"] = ParagraphStyle("h2", fontName="Serif-Bold", fontSize=16.5, leading=20,
                             textColor=INK, spaceBefore=16, spaceAfter=4)
    s["h3"] = ParagraphStyle("h3", fontName="Sans-Bold", fontSize=12.5, leading=16,
                             textColor=accent, spaceBefore=12, spaceAfter=4)
    s["h4"] = ParagraphStyle("h4", fontName="Sans-Bold", fontSize=10.5, leading=14,
                             textColor=INK, spaceBefore=9, spaceAfter=3)
    s["h5"] = ParagraphStyle("h5", fontName="Sans-Bold", fontSize=8.6, leading=11.5,
                             textColor=accent, spaceBefore=7, spaceAfter=2)
    s["cell"] = ParagraphStyle("cell", fontName="Sans", fontSize=8.8, leading=11.6,
                               textColor=INK)
    s["cellh"] = ParagraphStyle("cellh", parent=s["cell"], fontName="Sans-Bold",
                                textColor=white)
    s["callout"] = ParagraphStyle("callout", fontName="Sans", fontSize=9.6, leading=13.6,
                                  textColor=INK)
    s["toc1"] = ParagraphStyle("toc1", fontName="Sans-Bold", fontSize=10.5, leading=15,
                               textColor=INK, spaceBefore=6)
    s["toc2"] = ParagraphStyle("toc2", fontName="Sans", fontSize=9.2, leading=12.8,
                               textColor=MUTED, leftIndent=14)
    return s


INLINE_CODE_SIZE = 8.7
INLINE_CODE_BG = "#e9edf5"
INLINE_CODE_FG = "#7a1f4d"
