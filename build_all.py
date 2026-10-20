#!/usr/bin/env python3
"""Validate, build and package everything.

  python3 build_all.py            validate sources, build PDFs, write ZIPs
  python3 build_all.py --no-check skip the code validator (not recommended)
"""
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from engine.builder import build_pdf  # noqa: E402

DIST = ROOT / "dist"
STUDENT = DIST / "student"
INSTRUCTOR = DIST / "instructor"


def main():
    if "--no-check" not in sys.argv:
        r = subprocess.run([sys.executable, str(ROOT / "validation/check_code.py")])
        if r.returncode:
            sys.exit("Validation failed: fix the errors above before building.")
    for d in (STUDENT, INSTRUCTOR):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)

    # student sheets, in order; the index first
    for idx in sorted((ROOT / "content/index").iterdir()):
        build_pdf(idx, STUDENT / "00-curriculum-index.pdf")
    for sheet in sorted(p for p in (ROOT / "content/student").iterdir()
                        if p.is_dir() and not (p / ".wip").exists()):
        out = STUDENT / f"{sheet.name}.pdf"
        print("student   ", out.name, build_pdf(sheet, out), "pages")
    # instructor keys + reference implementations
    for key in sorted(p for p in (ROOT / "content/instructor").iterdir()
                      if p.is_dir() and not (p / ".wip").exists()):
        out = INSTRUCTOR / f"answer-key-{key.name}.pdf"
        print("instructor", out.name, build_pdf(key, out), "pages")
        student_src = ROOT / "content/student" / key.name
        subprocess.run([sys.executable, str(ROOT / "validation/emit_reference.py"), str(key),
                        str(INSTRUCTOR / "reference-implementations" / key.name), str(student_src)],
                       check=True)
        ref = INSTRUCTOR / "reference-implementations" / key.name
        if ref.exists() and not any(ref.iterdir()):
            ref.rmdir()

    shutil.copy(ROOT / "README.md", INSTRUCTOR / "README.md")
    for name, folder, extra in (("student-materials.zip", STUDENT, []),
                                ("instructor-materials.zip", INSTRUCTOR, [])):
        with zipfile.ZipFile(DIST / name, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(folder.rglob("*")):
                if f.is_file():
                    z.write(f, f.relative_to(folder))
    print("zips:", [p.name for p in DIST.glob("*.zip")])


if __name__ == "__main__":
    main()
