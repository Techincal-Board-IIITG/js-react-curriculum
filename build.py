#!/usr/bin/env python3
"""Build curriculum PDFs.  Usage: python3 build.py <source-dir> <out.pdf>"""
import sys
from pathlib import Path
from engine.builder import build_pdf

if __name__ == "__main__":
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.parent.mkdir(parents=True, exist_ok=True)
    pages = build_pdf(src, out)
    print(f"built {out} ({pages} pages)")
