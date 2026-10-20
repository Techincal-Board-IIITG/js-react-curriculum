---
number: 01
title: JavaScript Core Fundamentals
subtitle: How the language runs, stores values, makes decisions, repeats work, and organises code into functions
track: js
time: Core path about 28-32 hours
edition: Student edition
goals:
  - Run JavaScript in the browser console and with Node.js, and read the error messages you get
  - Choose between let and const, predict type coercion, and avoid the == traps
  - Write conditionals, loops, functions and closures from scratch
  - Handle failures with try, catch and finally, and debug in a systematic way
  - Build five small console programs without copying a tutorial
---

# 1. Study Guide and Learning Objectives

This sheet teaches the part of JavaScript that every later sheet depends on. React, the DOM and `fetch()` are all ordinary JavaScript underneath, so every hour you invest here is repaid many times over. You already know HTML and CSS, which means you already understand *structure* and *presentation*. JavaScript adds *behaviour*: the ability to store information, make decisions and react to events.

## Learning objectives

By the end of this sheet you should be able to do each of the following **without looking anything up**.

- Explain where JavaScript runs (browser and Node.js), and say which features exist in one but not the other.
- Declare variables with `const` and `let`, explain why `var` is avoided, and predict what happens when you reassign, redeclare, or use a variable too early.
- Name the primitive types, use `typeof`, and explain the difference between `null` and `undefined`.
- Predict the result of mixed-type expressions such as `"5" + 3`, `"5" - 3`, and `[] == false`, and convert values deliberately with `Number()`, `String()` and `Boolean()`.
- Use arithmetic, comparison, logical and ternary operators, and explain short-circuit evaluation.
- Write `if`, `else if`, `switch`, `for`, `while`, `do...while`, `for...of` and `for...in`, and choose the right one.
- Write functions in three syntaxes, with parameters, default values and return values, and explain what a closure captures.
- Pass a function to another function (a callback) and explain when the callback actually runs.
- Use `try`, `catch`, `finally` and `throw`, read a stack trace, and apply a repeatable debugging routine.

## How every section is organised

Each section follows the same sequence so you always know where you are:

1. **Concept** in plain language, before any syntax.
2. **Syntax** with each part named and the rules stated.
3. **Worked examples**, complete enough to run, each followed by a line-by-line explanation and the exact output.
4. **Deep dives** for the important built-in functions (what they accept, what they return, what can go wrong).
5. **Execution traces**: tables showing the value of every variable at every step. The numbers match the code exactly.
6. **Common mistakes**: wrong code, why it fails, the symptom, the fix, and how to diagnose it yourself.

At the end you will find exercises, five mini projects, and a revision section.

::: tip Code blocks have line numbers
Explanations say things like "line 3". Those numbers refer to the gutter on the left of each code block. Code you type yourself does not need line numbers.
:::

## Recommended workload

A month is short, and understanding beats speed. Use this table to decide what is essential and what can wait.

[[widths 1.2 3.4]]
| Item | Recommendation |
|---|---|
| **Essential topics** | Sections 2 to 10. Skip anything marked *Optional deep dive* on a first pass. |
| **Optional deep dives** | Hoisting internals, `var` details, `finally` overriding `return`, labelled statements. Return to these after Sheet 03. |
| **Required exercises** | Exercise sets A to D in full. In set E, complete at least one of the two challenges. |
| **Core projects (do these)** | Projects 1, 2 and 3. |
| **Extension projects (if time allows)** | Projects 4 and 5. You do not need them to continue to Sheet 02. |
| **Estimated study time** | Reading and experimenting: 12 to 14 hours. Exercises: 6 to 7 hours. Three core projects: 9 to 11 hours. Extension projects add roughly 5 to 6 hours. |

::: warning Do not try to finish by skimming
The fastest learners are not the ones who read quickly; they are the ones who type every example, predict the output before running it, and fix their own bugs. If a section takes you twice as long as the estimate, that is normal.
:::

## Before you start: setup checklist

- [ ] A code editor you like (Visual Studio Code is a common choice).
- [ ] A modern browser with Developer Tools (Chrome, Edge or Firefox).
- [ ] Node.js, current LTS version, installed from the official site. In a terminal, `node --version` should print a version number.
- [ ] A folder called `js-core` where you will save every example from this sheet.

## The predict, run, explain habit

For every example in this document, do three things in order. First **predict** the output on paper. Then **run** it. Finally, if your prediction was wrong, **explain** to yourself exactly which line surprised you. Wrong predictions are the single most efficient way to learn a programming language, because they expose a gap in your mental model while it is cheap to repair.

# 2. How JavaScript Runs

## Learning objectives for this section

- Run JavaScript three ways: browser console, a `<script>` tag, and Node.js.
- Distinguish a statement from an expression.
- Use `console.log()` confidently and write comments.
- Recognise when code depends on the browser or on Node.js.

## Conceptual explanation

JavaScript is a programming language. A program is a list of instructions written as text. Something has to read that text and carry out the instructions: that something is a **JavaScript engine**. Chrome and Edge use an engine called V8, Firefox uses SpiderMonkey, and Safari uses JavaScriptCore. The engine reads your code, checks that its grammar is valid, and then executes it from top to bottom, one instruction at a time.

An engine alone cannot show a web page or read a file. It only knows the language itself: numbers, text, functions and so on. The *environment* that hosts the engine adds extra abilities.

[[widths 1.1 2 2]]
| | Browser | Node.js |
|---|---|---|
| Hosts the engine | Yes (V8 in Chrome) | Yes (V8) |
| Special objects | `window`, `document`, `localStorage`, `fetch` | `process`, `require`/`import` of built-in modules such as `fs` |
| Typical purpose | Make web pages interactive | Run scripts, tools and servers |
| Can touch the page (DOM) | Yes | No |
| Can read files on your disk | No (only with explicit user permission) | Yes |
| How you run code | Console, `<script>` tag | `node file.js` in a terminal |

The language is identical in both places: `if`, `for`, functions and arrays behave the same. What differs is the extra equipment each environment provides. This matters because an error such as `document is not defined` does not mean your code is wrong; it usually means you ran browser code in Node.

```diagram
flow
Your source code -> *JavaScript engine (V8) -> Environment APIs (DOM, fs...) -> Visible result
```

## Three ways to run JavaScript

**1. The browser console.** Open any page, press F12, choose the Console tab, type `2 + 2` and press Enter. The console evaluates the expression and shows `4`. This is ideal for quick experiments, but nothing is saved.

**2. A `<script>` tag.** Create two files in your `js-core` folder.

```html file="index.html"
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>First script</title>
  </head>
  <body>
    <h1>Open the console (F12)</h1>
    <script src="hello.js"></script>
  </body>
</html>
```

```js file="hello.js" nocheck
console.log("Hello from the browser");
document.title = "Changed by JavaScript";
```

Open `index.html` in a browser. The page tab title changes, and the console shows `Hello from the browser`. Line 2 of `hello.js` uses `document`, which only exists in browsers. The `<script>` tag is placed at the end of `<body>` so the elements above it already exist when the script runs.

**3. Node.js.** In a terminal, inside the `js-core` folder, create `node-hello.js`:

```js file="node-hello.js" run
console.log("Hello from Node.js");
console.log(2 + 2);
```

```output
Hello from Node.js
4
```

Run it with the command `node node-hello.js`. Node reads the file, executes line 1, then line 2, and exits when it runs out of instructions.

## Statements, expressions and comments

A **statement** is a complete instruction: it *does* something. An **expression** is a piece of code that *produces a value*. Most programs are statements built from expressions.

[[widths 2 1.4 3]]
| Code | Kind | Explanation |
|---|---|---|
| `42` | Expression | Produces the value 42 |
| `3 * 4` | Expression | Produces 12 |
| `price > 100` | Expression | Produces `true` or `false` |
| `let total = 3 * 4;` | Statement | Creates a variable; the right side is an expression |
| `if (ok) { ... }` | Statement | Chooses whether to run a block |

A simple test: if you can put it inside `console.log( )` or on the right side of `=`, it is an expression. A statement ends with a semicolon `;`. JavaScript can often guess where statements end when you omit semicolons (this is called automatic semicolon insertion), but the guess is sometimes wrong in surprising ways, so this curriculum always writes them.

**Comments** are notes for humans that the engine ignores.

```js file="comments.js" run
// A single-line comment runs to the end of the line.
const taxRate = 0.18; // a comment can follow code

/*
  A block comment can span
  several lines.
*/
console.log("Tax rate is", taxRate);
```

```output
Tax rate is 0.18
```

Use comments to explain *why* the code does something, not to repeat *what* it does. Commenting out a line (putting `//` in front of it) is also a quick way to disable code while debugging.

## Function deep dive: `console.log()`

**What it is.** `console.log()` is a function provided by both browsers and Node.js. It prints values to the console, a text output area meant for developers.

**Why it exists.** Programs run invisibly. Without a way to look inside, you could not tell what a variable holds at a given moment. `console.log()` is the simplest debugging tool and the one you will use most often.

**What problem it solves.** It makes a hidden value visible without changing the behaviour of your program.

**Syntax.** `console.log(value1, value2, ...)`

**Parameters.** It accepts any number of arguments of any type. Each argument is converted to a readable text form. Strings print as plain text; numbers and booleans print as themselves; arrays and objects print in a structured form. The values are separated by a single space in the output.

**Return value.** It returns `undefined`. It is used for its *side effect* (printing), not for its result. This is why you never write `const x = console.log(...)`.

**How it works, step by step.** (1) JavaScript evaluates every argument expression from left to right. (2) It passes the resulting values to `console.log`. (3) The console formats each value. (4) The text is written to the output stream and a newline is added.

```js file="log-demo.js" run
const name = "Asha";
const age = 20;

console.log("Total:", 3 + 4);
console.log("Items", ["pen", "book"]);
console.log({ name, age });
console.log(typeof console.log("hi"));
```

```output
Total: 7
Items [ 'pen', 'book' ]
{ name: 'Asha', age: 20 }
hi
undefined
```

**Line-by-line.**

- Lines 1 and 2 create two variables (explained fully in Section 3).
- Line 4: two arguments, the text `"Total:"` and the expression `3 + 4`. The expression is evaluated first (7), then both are printed separated by a space.
- Line 5: the second argument is an array, printed with square brackets. Node shows strings inside arrays with single quotes so you can tell they are strings.
- Line 6: `{ name, age }` is shorthand for `{ name: name, age: age }`. Objects print with braces.
- Line 7: the inner `console.log("hi")` runs first and prints `hi`. It returns `undefined`. The outer call receives `typeof undefined`, which is the text `"undefined"`, and prints it. This proves that `console.log` returns `undefined`.

**Variation.** The console has siblings with different meaning: `console.error()` and `console.warn()` print in red or yellow in a browser (and to a different stream in Node), and `console.table(arrayOfObjects)` prints a table in the browser, which is excellent for inspecting lists.

::: tip Label what you print
`console.log(total)` prints a bare number; after a while you will not know which line produced it. Write `console.log("total:", total)` so every line of output explains itself.
:::

## Common mistakes in this section

#### Mistake 1: Running browser code in Node

**Why it is wrong.** `document` is provided by the browser. Node has no web page, so the name does not exist.

```js bad nocheck
console.log(document.title);
```

**Symptom.** Node stops with `ReferenceError: document is not defined`.

**Corrected code.** Check whether the browser object exists before using it.

```js good run
if (typeof document === "undefined") {
  console.log("Running in Node.js: there is no page to read");
} else {
  console.log(document.title);
}
```

```output
Running in Node.js: there is no page to read
```

**How to diagnose it yourself.** Read the *first* line of the error: it names the missing identifier. Ask: "Is this a browser feature or a Node feature?" The `typeof` check is safe because `typeof` never throws for an undeclared name.

#### Mistake 2: Wrong capitalisation

**Why it is wrong.** JavaScript is **case-sensitive**: `console` and `Console` are different names.

```js bad nocheck
Console.log("hello");
```

**Symptom.** `ReferenceError: Console is not defined`.

```js good run
console.log("hello");
```

```output
hello
```

**How to diagnose it yourself.** When a name is "not defined" and you are certain it exists, compare the spelling and capital letters character by character. Editors with autocomplete prevent most of these.

#### Mistake 3: A missing bracket

**Why it is wrong.** Every `(` needs a matching `)`. The engine cannot even begin to run a file with broken grammar.

```js bad nocheck
console.log("Total:", 3 + 4;
```

**Symptom.** `SyntaxError: missing ) after argument list`. Nothing in the file runs, not even earlier lines, because the engine checks grammar for the whole file before it executes anything.

```js good run
console.log("Total:", 3 + 4);
```

```output
Total: 7
```

**How to diagnose it yourself.** The error message includes a file name and a line number. Look at that line *and the line above it*, since the real mistake is often just before the place where the engine gave up.

#### Mistake 4: Running from the wrong folder

**Why it is wrong.** `node hello.js` looks for `hello.js` in the *current directory* of the terminal, not in the folder where your editor has it open.

**Symptom.** the message `Cannot find module`.

**Fix and diagnosis.** Run `pwd` (macOS/Linux) or `cd` with no arguments (Windows) to see where the terminal is, `ls` or `dir` to list the files there, and `cd js-core` to move into the right folder.
