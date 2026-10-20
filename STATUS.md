# Production checklist

Legend: [x] done and validated, [ ] to do.

## Infrastructure
- [x] Environment inspected (ReportLab 4.4, Pygments, pdfplumber, Node 22, esbuild, Chromium available; no network)
- [x] Design system (fonts, palette per track, code theme, callouts, tables, diagrams)
- [x] Parser, builder, TOC, bookmarks, running header and footer
- [x] Code validator (syntax + execution + output comparison + structure)
- [x] Browser-page validator: `html page` blocks run in headless Chromium with scripted steps (click, fill, press, check, select, reload, print, eval); console output compared with the output block
- [x] PDF layout validator
- [x] Reference-implementation emitter, ZIP packaging, README
- [x] Curriculum index PDF

## Sheets (student / answer key)
- [x] 01 JavaScript Core Fundamentals / [x] key + reference implementations
- [x] 02 Arrays, Objects, and Modern JavaScript / [x] key (reference modules for the 5 projects are tested inside the key)
- [x] 03 DOM, Events, and Browser Storage / [x] key (every example page run in headless Chromium; reference apps emitted as runnable folders)
- [ ] 04 Asynchronous JavaScript and APIs / [ ] key
- [ ] 05 React Fundamentals and Components / [ ] key
- [ ] 06 React State, Events, and Forms / [ ] key
- [ ] 07 React Effects and API Integration / [ ] key
- [ ] 08 React Router and Multi-page Applications / [ ] key
- [ ] 09 Folder Structure, Custom Hooks, and Clean Code (includes the worked multi-file clean-architecture example) / [ ] key
- [ ] 10 State Management and Application Patterns / [ ] key
- [ ] 11 Debugging, Testing, and Accessibility / [ ] key
- [ ] 12 Git, Deployment, and Independent Projects / [ ] key

## Per-sheet definition of done
1. Front matter, study guide with workload table, learning objectives
2. Every topic: concept, syntax, worked examples, deep dives, traces, at least three mistakes
3. Exercise sets A to E with acceptance criteria and hints, no solutions
4. Five projects (three core, two extension), all ten fields each
5. Revision section with docs links (official URLs only)
6. `check_code.py` passes; `check_pdfs.py` passes; pages inspected visually
7. Matching instructor key with executed outputs

## Open decisions for the instructor
- Confirm the template (design, depth, section format) from sheet 01 before sheets 02 to 12 are written.
- Decide the React Router major version to pin (sheet 08) and the Vite/React versions (sheet 05); these should be verified against a real install.
