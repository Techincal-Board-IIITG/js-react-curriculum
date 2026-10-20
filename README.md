# Curriculum PDF Build System

A small Python-based publishing pipeline for turning Markdown lesson files into consistently designed PDFs. It was built for a beginner JavaScript + React curriculum, with separate student handouts and instructor answer keys.

The idea is simple: **write the material in Markdown, run the build, and let the scripts handle layout, checks, PDFs, and ZIP packages.** You do not need to manually format each PDF.

> **Project status:** the build engine, design system, validators, and packaging workflow are implemented. Student sheets 01 and 02 and their available instructor keys are present. Sheets 03–12 are planned but have not been written yet, so a successful build does not mean the entire 12-sheet curriculum exists.

## What it produces

Running the full build creates a `dist/` directory similar to this:

```text
dist/
├── student/
│   ├── 00-curriculum-index.pdf
│   ├── 01-js-core.pdf
│   └── 02-arrays-objects.pdf
├── instructor/
│   ├── answer-key-01-js-core.pdf
│   ├── answer-key-02-arrays-objects.pdf
│   └── reference-implementations/
├── student-materials.zip
└── instructor-materials.zip
```

The exact files depend on which source folders exist. Student PDFs contain assignments, hints, and acceptance criteria—not the solutions. Instructor materials contain answer keys and generated reference implementations. **Do not distribute the instructor ZIP to students.**

## Requirements

- Python 3.10 or newer
- Python packages: `reportlab`, `pygments`, and `pdfplumber`
- Node.js 18 or newer, for running JavaScript examples
- `esbuild`, used by the JavaScript/JSX syntax validator
- Fonts used by the PDF theme (Liberation Sans/Serif and DejaVu Sans Mono/Sans)

Install the Python packages:

```bash
python -m pip install reportlab pygments pdfplumber
```

Check that Python and Node are available:

```bash
python --version
node --version
npm --version
```

### Windows note

The project was originally configured in a Linux build environment. `engine/theme.py` uses Linux font paths under `/usr/share/fonts/`, and `validation/check_code.py` currently contains a hard-coded Linux path to the `esbuild` executable. On Windows, install the required fonts and update those paths to locations on your machine (or change the validator to resolve `esbuild` through `PATH`) before expecting the complete build to work. The rest of the commands below assume the dependencies and paths have been configured.

## Quick start

Open a terminal in the project root—the directory containing `build.py` and `build_all.py`.

### Build one Markdown file or lesson folder

```bash
python build.py content/student/01-js-core out.pdf
```

This reads all `.md` files in the supplied folder, sorts them by filename, combines them, and writes the result to `out.pdf`. You can also pass a single `.md` file as the source:

```bash
python build.py content/_sample/00-front.md out.pdf
```

The output directory is created automatically if it does not exist.

### Build the full set

```bash
python build_all.py
```

This runs the source/code validator first. If validation passes, it rebuilds the output folders, generates the index and available student PDFs, generates available instructor answer keys, extracts instructor code marked for export, and creates the two ZIP packages.

To skip the code validator:

```bash
python build_all.py --no-check
```

Use that only when you deliberately want to bypass validation. It does not fix or validate bad examples for you.

### Run the checks separately

Validate source content and JavaScript examples:

```bash
python validation/check_code.py
```

Check selected PDFs for common layout issues:

```bash
python validation/check_pdfs.py dist/student/*.pdf dist/instructor/*.pdf
```

In PowerShell, if wildcard expansion causes trouble, pass explicit file paths or run the command from a shell that expands the pattern as expected.

## What each script does

### Build entry points

| File | What it does | When to use it |
|---|---|---|
| `build.py` | Builds a PDF from one Markdown file or a folder of Markdown files. | When working on one lesson and you want a quick preview. |
| `build_all.py` | Runs validation, builds the curriculum index and available student/instructor PDFs, exports reference code, and packages the outputs into ZIP files. | For a complete release build. |

### PDF engine (`engine/`)

| File | Responsibility |
|---|---|
| `engine/parser.py` | Reads Markdown source and turns supported Markdown/custom syntax into structured content blocks. It also handles front matter and combines files in filename order. |
| `engine/builder.py` | Coordinates PDF creation: parses source, creates page content, builds the table of contents, and writes the final PDF through ReportLab. |
| `engine/flowables.py` | Implements custom PDF elements and layout for content such as code, callouts, project blocks, and diagrams. |
| `engine/theme.py` | Central design system: fonts, colors, typography, spacing, track accents, code colors, and callout styles. |
| `engine/__init__.py` | Marks `engine` as a Python package. |

### Validation and helper scripts (`validation/`)

| File | Responsibility |
|---|---|
| `validation/check_code.py` | Checks supported JavaScript/JSX syntax, executes JavaScript blocks marked `run`, compares their output with the following `output` block, validates JSON blocks, checks code-line lengths and font glyph coverage, and enforces required sections/project fields for student sheets. |
| `validation/check_pdfs.py` | Inspects generated PDFs for empty/nearly empty pages, text outside expected margins, very small text, and missing/broken glyphs. |
| `validation/emit_reference.py` | Extracts code blocks marked `emit` with a `file="..."` attribute into real files. It removes code after the `// --- self-test ---` marker. The full build uses it to create instructor reference implementations. |
| `validation/fill_outputs.py` | For a JavaScript block marked `run` whose following `output` block contains `TBD`, runs the code with Node and replaces `TBD` with the actual standard output. Review the changed output before publishing. |

## Where the content lives

```text
content/
├── index/
│   └── 00-index/
├── student/
│   ├── 01-js-core/
│   └── 02-arrays-objects/
├── instructor/
│   ├── 01-js-core/
│   └── 02-arrays-objects/
└── _sample/
```

- `content/student/` contains student-facing lesson sources.
- `content/instructor/` contains matching answer keys and instructor material.
- `content/index/` contains the curriculum index source.
- `content/_sample/` is a sample/template source; it is not automatically treated as a normal student sheet by the full build.

When a lesson is stored in a folder, its `.md` files are concatenated in **alphabetical filename order**. Prefix files with numbers (`00-`, `01-`, `02-`) to control the reading order. Keep student assignments and solutions in their respective folders.

`STATUS.md` is the progress checklist for the curriculum. Update it as sheets and answer keys are completed.

## Writing lesson Markdown

The parser supports a practical Markdown subset plus a few curriculum-specific conventions. Examples:

### Headings, lists, tables, and code

```markdown
# Lesson title

## Learning objectives

By the end, you should be able to explain the concept and use it in a small program.

- First objective
- Second objective

| Method | Purpose |
| --- | --- |
| `map()` | Transform each item |
| `filter()` | Keep matching items |

```js file="example.js" run
console.log("Hello, world!");
```

```output
Hello, world!
```
```

The `run` flag tells the validator to execute the JavaScript in Node. If an `output` block follows, its text is compared against the actual standard output. Keep examples deterministic so the expected output stays stable.

### Code block attributes and flags

Fenced code blocks can include attributes such as `file="example.js"` and flags such as:

- `run` — execute supported JavaScript in Node and compare its output with the following `output` block.
- `emit` — export the code to a real file when processing instructor material; requires a `file="..."` attribute.
- `nocheck` — skip the applicable code-validation steps for that block. Use sparingly and deliberately.
- `bad`, `good`, and `throws` — presentation/validation flags used by the curriculum engine for examples with different intent. Check existing source examples before using them.

JavaScript/JSX syntax is checked with `esbuild`; executable `run` examples are run in Node. Browser-only examples (for example, code relying on `document` or `localStorage`) cannot run in Node as written. React examples are not fully runtime-tested by this pipeline and should be tested in a real Vite/React project before release.

### Output blocks

Place an `output` block directly after a JavaScript block marked `run`:

````markdown
```js run
console.log(2 + 2);
```

```output
4
```
````

### Callouts

Use the supported callout types to draw attention to explanations:

````markdown
::: tip
A useful practical tip goes here.
:::

::: warning
A common pitfall goes here.
:::
````

Supported types include `tip`, `warning`, `concept`, `note`, `mistake`, `try`, and `hint`.

### Project blocks

Student project blocks use the `:::: project` container and include the project title, difficulty, and track/category. The validator expects each student sheet to contain five projects with the required fields: objective, problem statement, required features, technical constraints, expected behavior, suggested milestones, edge cases, acceptance criteria, stretch goals, and concepts practiced.

Follow the structure used in the existing student sheets so new content passes the validator and matches the curriculum's design.

### Diagrams, tables, and page breaks

The engine supports custom `diagram` fences for `flow`, `tree`, and `sequence` diagrams. Tables can use a width hint immediately before them, such as `[[widths 1 2 3]]`, to control relative column widths. Insert `---pagebreak---` when a deliberate page break is needed.

Because this is a custom parser—not a full Markdown implementation—check existing examples for the exact syntax before relying on an advanced Markdown feature. Unsupported syntax may render incorrectly or be treated as plain text.

## A typical editing workflow

1. Edit the relevant `.md` file under `content/`.
2. If you added executable JavaScript, run `python validation/check_code.py` and fix any errors.
3. Build just that lesson with `python build.py <source-folder> preview.pdf`.
4. Open the PDF and visually check page breaks, code wrapping, tables, and diagrams.
5. Run `python validation/check_pdfs.py <generated-pdf>`.
6. Once the content is ready, run `python build_all.py` to regenerate the release PDFs and ZIP packages.
7. Inspect the final PDFs and verify that the student and instructor packages contain only the intended files.

## Known limitations and gotchas

- **The full curriculum is not finished.** See `STATUS.md` for the current checklist.
- The parser supports a defined Markdown subset and custom syntax; it is not a universal Markdown-to-PDF converter.
- `check_code.py` currently uses a hard-coded `esbuild` path that must be changed for most machines, especially Windows.
- `engine/theme.py` uses Linux font paths. Update them if the fonts live elsewhere on your system.
- Browser-only code cannot be executed by the Node-based validator.
- React examples are syntax-checked but are not fully run through a real React environment by this build pipeline. Test them in Vite before release.
- The PDF checker is a useful automated sanity check, not a substitute for opening the PDFs and reviewing them visually.
- Output from some runtime errors can differ between Node versions, so avoid depending on exact engine-specific error text.

## In short

Write content in `content/`, use the project's supported Markdown conventions, run the validators, preview the PDF, and use `build_all.py` when you're ready to package a release. The scripts take care of repetitive publishing work; you still review the content and final layout before sharing it.
