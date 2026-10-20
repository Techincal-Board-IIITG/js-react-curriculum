---
number: 00
title: Curriculum Index and Study Plan
subtitle: The complete map of the JavaScript + React beginner curriculum: order, prerequisites, workload and how to study
track: index
kind: index
structure: no
label: START HERE
time: 12 sheets
edition: Student edition
goals:
  - See how the twelve sheets build on each other
  - Know exactly what is essential and what is optional in each sheet
  - Plan your weeks with realistic time estimates
  - Know how to study independently and when to ask for help
---

# 1. How This Curriculum Works

This curriculum takes you from your first line of JavaScript to a deployed React application that you designed yourself. It assumes you already know HTML and CSS and have built a portfolio page. It is organised as **twelve sheets** (PDF files). Each sheet teaches one topic in depth, with explanations, tested code, execution traces, common mistakes, exercises, and five mini projects.

::: note Sheets may be released in batches
Your instructor may hand out the sheets in stages. Work through them in the order below; each sheet assumes the previous ones. If a sheet listed here is not in your folder yet, it has not been released.
:::

## The twelve sheets and the order to read them

```diagram
flow
01 JS Core -> 02 Arrays & Objects -> 03 DOM & Storage -> 04 Async & APIs -> 05 React Basics -> 06 State & Forms -> 07 Effects & APIs -> 08 Router -> 09 Structure & Hooks -> 10 State Patterns -> 11 Debug & Test -> 12 Git & Deploy
```

[[widths 0.4 2.3 1.1 2.6]]
| # | Sheet | Track | Prerequisite |
|---|---|---|---|
| 01 | JavaScript Core Fundamentals | JavaScript | HTML and CSS |
| 02 | Arrays, Objects, and Modern JavaScript | JavaScript | Sheet 01 |
| 03 | DOM, Events, and Browser Storage | JavaScript | Sheets 01 and 02 |
| 04 | Asynchronous JavaScript and APIs | JavaScript | Sheets 01 to 03 |
| 05 | React Fundamentals and Components | React | Sheets 01 to 04 (at least 02 and 04 basics) |
| 06 | React State, Events, and Forms | React | Sheet 05 |
| 07 | React Effects and API Integration | React | Sheets 04 and 06 |
| 08 | React Router and Multi-page Applications | React | Sheets 05 to 07 |
| 09 | Folder Structure, Custom Hooks, and Clean Code | React | Sheets 05 to 08 |
| 10 | State Management and Application Patterns | React | Sheets 06, 07 and 09 |
| 11 | Debugging, Testing, and Accessibility | Practice | Sheets 05 to 09 (read the debugging parts of 01 first) |
| 12 | Git, Deployment, and Independent Projects | Practice | Sheets 05 to 10 (start Git basics any time) |

## What every sheet contains

- **Study guide**: learning objectives, the essential topics, the optional deep dives, and a time estimate.
- **Concept sections**: plain-language explanation, then syntax, then complete examples with line-by-line commentary and exact expected output.
- **Function deep dives**: for every important function or hook, what it is, why it exists, parameters, return value, how it works, and where it goes wrong.
- **Execution traces**: tables that follow variables or state step by step.
- **Common mistakes**: wrong code, why it fails, the symptom, the fix, and how to diagnose it yourself.
- **Exercises**: comprehension, output prediction, implementation, debugging, and challenge problems, with acceptance criteria and hints. Solutions are kept in a separate instructor key.
- **Five mini projects**: ordered from easier to harder. **Projects 1 to 3 are the core workload. Projects 4 and 5 are extensions.**
- **Revision**: summary, syntax reference, glossary, mistakes checklist, self-assessment, completion checklist and official documentation links.

# 2. Workload and Pacing

The estimates below are **planning estimates for a motivated beginner who types and runs every example**. They are not measured values: they should be adjusted after a pilot group completes the first sheets. Time spent debugging is included, because debugging is where most of the learning happens.

[[widths 0.4 2.6 1.7 1.4 1.5]]
| # | Sheet | Core path (hours) | Core projects | Extension projects |
|---|---|---|---|---|
| 01 | JavaScript Core | 28 to 32 | 1, 2, 3 | 4, 5 |
| 02 | Arrays and Objects | 28 to 32 | 1, 2, 3 | 4, 5 |
| 03 | DOM and Storage | 30 to 34 | 1, 2, 3 | 4, 5 |
| 04 | Async and APIs | 28 to 32 | 1, 2, 3 | 4, 5 |
| 05 | React Basics | 26 to 30 | 1, 2, 3 | 4, 5 |
| 06 | State and Forms | 28 to 32 | 1, 2, 3 | 4, 5 |
| 07 | Effects and APIs | 30 to 34 | 1, 2, 3 | 4, 5 |
| 08 | Router | 24 to 28 | 1, 2, 3 | 4, 5 |
| 09 | Structure and Hooks | 24 to 28 | 1, 2, 3 | 4, 5 |
| 10 | State Patterns | 24 to 28 | 1, 2, 3 | 4, 5 |
| 11 | Debug, Test, Accessibility | 24 to 28 | 1, 2, 3 | 4, 5 |
| 12 | Git and Deployment | 22 to 26 | 1, 2, 3 | 4, 5 |

**The honest arithmetic.** The core path is about 320 to 370 hours. At a full-time pace of 35 to 40 hours per week this is roughly **nine to ten weeks**; at a part-time pace of 15 hours per week it is more than five months. A single calendar month supports only a **compressed path** of roughly 150 to 170 hours, which means essential topics only and a reduced set of projects. Completing all 60 mini projects is **not** a one-month goal, and the curriculum does not claim it is.

## A compressed one-month path

Use this only if you have about 35 to 40 hours per week for four weeks.

[[widths 0.9 3.4 3]]
| Week | Sheets | What to do |
|---|---|---|
| 1 | 01, 02 | Essential topics and exercises in sets A to C. Core projects 1 and 2 of each sheet. |
| 2 | 03, 04 | DOM, events, storage, `fetch`. Core projects 1 and 2 of each sheet. Skip optional deep dives. |
| 3 | 05, 06, 07 | React components, state, effects. Core projects 1 and 2 of each sheet. |
| 4 | 08, 09 (parts), 12 (parts) | Routing, folder structure, Git and deployment. Then build one small independent MVP. |

Sheets 10 and 11 (state patterns, testing and accessibility) are then done afterwards, at your own pace.

# 3. How to Study Independently

1. **Type every example.** Copy-pasting teaches nothing. Typing exposes details you would skim past.
2. **Predict before you run.** Write the expected output; compare; explain every difference.
3. **Break things on purpose.** Remove a line, change a value, and see what the error says. Errors become familiar friends.
4. **Use the debugging routine from Sheet 01** on every bug before asking for help: reproduce, read the message, form a hypothesis, observe, isolate, fix one thing.
5. **Do exercises before projects**, and projects before moving on. Each sheet's projects assume its exercises.
6. **Keep a mistakes journal.** One line per bug: what happened, what it was, how you found it.
7. **Ask good questions.** Include the exact error message, the smallest code that reproduces the problem, and what you already tried.
8. **Read the official documentation** listed at the end of every sheet, *after* you try things yourself.

::: tip Signs you are ready to move on
You can explain the sheet's key idea aloud without notes, your core projects work and you understand every line, and you can fix a small bug in your own code without searching for the answer.
:::

# 4. Tools You Will Need

[[widths 1.3 3.6 2.2]]
| Tool | Purpose | From sheet |
|---|---|---|
| Code editor (for example VS Code) | Writing code | 01 |
| Modern browser with DevTools | Running and debugging web pages | 01 |
| Node.js (current LTS) and npm | Running scripts, React tooling | 01 (Node), 05 (npm) |
| Git and a GitHub account | Version control, collaboration | 12 (start earlier if you can) |
| A static hosting account | Deploying a React app | 12 |

# 5. Conventions Used in the Sheets

- **Blue-grey boxes** are notes; **green** are tips; **amber** are warnings; **indigo** are key concepts; **red** are common mistakes.
- A red code panel marked *INCORRECT* shows wrong code, followed by a green panel marked *CORRECTED*.
- An *Output* panel shows exactly what a program prints.
- Projects show a coloured banner with the project number, difficulty and *Core* or *Extension* label.
- Where an example needs an external web service, the sheet describes a mock-data fallback so you can still finish when the service is unavailable or rate limited.
- Documentation links point to official sources (MDN, react.dev, the Node.js, Vite, React Router, Vitest, Testing Library and Git documentation).
