# 13. Revision and Assessment

## Summary of this sheet

JavaScript runs inside an *engine* hosted by an *environment* (the browser or Node.js); the language is the same, the extra tools differ. Programs are built from **statements** that contain **expressions**. Variables are declared with `const` by default and `let` when they must change; `var` is avoided. Values are either **primitives** (copied by value) or **objects** (copied by reference). Mixed-type operations trigger **coercion**, so convert deliberately with `Number()` and friends, check for `NaN`, and compare with `===`. Decisions use `if`/`else if`/`switch`, repetition uses `for`, `while`, `do...while`, `for...of` (values) and `for...in` (object keys). **Functions** take parameters, return values and are themselves values. **Lexical scope** decides visibility, **closures** keep scope alive for inner functions, and `let`/`const` live in a *temporal dead zone* before their declaration. A **callback** is a function handed to another function to be called later; `forEach` calls it synchronously, `setTimeout` calls it after the current code finishes. Errors are handled with `try/catch/finally` and `throw new Error(...)`, and bugs are found with a routine: reproduce, read, hypothesise, observe, isolate, fix one thing, understand.

## Key syntax reference

[[widths 1.3 3 2.2]]
| Topic | Syntax | Notes |
|---|---|---|
| Variables | `const x = 1;` `let y = 2;` | `const` by default |
| Types | `typeof value` | `typeof null` is `"object"`; test with `=== null` |
| Conversion | `Number(s)`, `parseInt(s, 10)`, `String(v)`, `Boolean(v)` | Check with `Number.isNaN()` |
| Equality | `a === b`, `a !== b` | Never `==` |
| Logical | `a && b`, `a \|\| b`, `!a` | Return an operand; short-circuit |
| Ternary | `cond ? x : y` | An expression |
| Branching | `if (c) {} else if (d) {} else {}` | First truthy condition wins |
| Switch | `switch (v) { case 1: ...; break; default: }` | Strict equality; remember `break` |
| Loops | `for (let i = 0; i < n; i++) {}` `while (c) {}` `for (const v of list) {}` | `for...in` is for object keys |
| Loop control | `break;` `continue;` | Nearest loop only |
| Function | `function f(a, b = 1) { return a + b; }` | Declarations are hoisted |
| Arrow | `(a, b) => a + b` / `(a) => ({ a })` | Parentheses for object returns |
| Callback | `list.forEach((v, i, all) => {})` | Returns `undefined` |
| Timer | `setTimeout(cb, ms)` / `clearTimeout(id)` | Runs after current code |
| Errors | `try {} catch (e) {} finally {}` / `throw new Error("m")` | Throw Errors, not strings |
| Random | `Math.floor(Math.random() * n)` | Whole number from 0 to n-1 |

## Important terms and definitions

[[widths 1.2 4]]
| Term | Definition |
|---|---|
| Engine | The program (such as V8) that reads and executes JavaScript |
| Environment | The host (browser, Node.js) providing extra objects such as `document` or `process` |
| Statement / expression | An instruction / a piece of code that produces a value |
| Primitive | An immutable simple value: string, number, boolean, undefined, null, bigint, symbol |
| Reference value | An object, array or function, compared and copied by reference |
| Coercion | Automatic conversion of a value's type by the engine |
| Truthy / falsy | How a value behaves when converted to boolean |
| Short-circuit | Skipping the right operand of `&&`/`\|\|` when the left already decides |
| Parameter / argument | The placeholder in a definition / the actual value in a call |
| Scope | The region of code where a name is visible |
| Closure | A function plus the variables of the scope where it was created |
| Hoisting | The engine registering declarations before executing a scope |
| Temporal dead zone | The period when a `let`/`const` exists but cannot yet be read |
| Callback | A function passed to another function to be called by it |
| Higher-order function | A function that takes or returns functions |
| Exception | A runtime error that unwinds the call stack until caught |
| Stack trace | The list of active function calls at the moment an error occurred |

## Common mistakes checklist

Before you consider any program finished, check each line.

- [ ] Every variable is `const` unless it truly changes, and none is `var`.
- [ ] Text read from a user has been converted with `Number()` and checked with `Number.isNaN()`.
- [ ] Every comparison uses `===` or `!==`, and no `=` appears inside an `if` condition.
- [ ] Every loop has a start, a condition that can become false, and an update.
- [ ] Loop bounds use `<` with `length`, not `<=`.
- [ ] Every `switch` case ends with `break` (unless fallthrough is deliberate and commented).
- [ ] Every function that should give back a value has a `return` on every path.
- [ ] Callbacks are passed as `fn`, not called as `fn()`.
- [ ] Loop variables captured by callbacks are declared with `let`.
- [ ] No `catch` block is empty; errors thrown are `Error` objects.
- [ ] Work that happens later (timers, events) has its own error handling.

## Self-assessment questions

Answer without notes. If you hesitate, re-read the matching section.

1. Where does the JavaScript in a browser tab run, and where does the JavaScript run when you type `node app.js`? (Section 2)
2. Which line of this code fails, and with what error: `console.log(x); let x = 1;`? (Sections 3, 8)
3. What does `typeof` report for `null`, `[]`, `NaN` and `() => {}`? (Section 4)
4. What are `Number("")`, `Number("12px")`, `parseInt("12px", 10)` and `parseFloat("3.5kg")`? (Section 4)
5. Why does `0.1 + 0.2 === 0.3` evaluate to `false`, and how do you store money safely? (Section 4)
6. What are the values of `null || "x"` and `0 || "x"`? When is the second one a bug? (Section 5)
7. List three results of `==` that show why `===` is preferred. (Section 5)
8. How does `for` execute, in order? When does the update run? (Section 6)
9. Which loop would you choose to read every item of an array, and which to inspect an object's keys? (Section 6)
10. What does a function return when it has no `return` statement? (Section 7)
11. Why does `const makePoint = (x, y) => { x, y };` return `undefined`? (Section 7)
12. In the counter example, why do two counters not share a `count`? (Section 8)
13. Why does a `var` loop with `setTimeout` print the same number every time while `let` does not? (Section 8)
14. What is the difference between `forEach` and a normal `for` loop regarding `return` and `break`? (Section 9)
15. In what order do `console.log("a"); setTimeout(() => console.log("b"), 0); console.log("c");` print, and why? (Section 9)
16. When does `finally` run, and what does `throw "text"` lose compared with `throw new Error("text")`? (Section 10)
17. Describe the seven-step debugging routine in your own words. (Section 10)

## Practical completion checklist

You are ready for Sheet 02 when you can tick every box honestly.

- [ ] I typed and ran every worked example and compared my prediction with the real output.
- [ ] I completed exercise sets A, B, C and D, and at least one challenge from set E.
- [ ] I completed core projects 1, 2 and 3 and can explain every line of my code aloud.
- [ ] I can explain scope, closures and callbacks to a classmate without notes.
- [ ] I can read a stack trace and name the file and line where an error originated.
- [ ] I can debug using `console.log` and a DevTools breakpoint.
- [ ] I kept my code in a folder under version control or at least in dated backups.
- [ ] (Optional) I completed one or both extension projects.

## Official documentation

These are the authoritative references. Read them *after* attempting the material, as a way to deepen and verify what you learned.

- [MDN: JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide) (the full tutorial-style overview)
- [MDN: Grammar and types](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Grammar_and_types) (variables, declarations, literals)
- [MDN: Expressions and operators](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Expressions_and_operators)
- [MDN: Control flow and error handling](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Control_flow_and_error_handling)
- [MDN: Loops and iteration](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Loops_and_iteration)
- [MDN: Functions](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Functions)
- [MDN: Closures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures)
- [MDN: Equality comparisons and sameness](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Equality_comparisons_and_sameness)
- [MDN: JavaScript data types and data structures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Data_structures)
- [MDN: JavaScript reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference)
- [Node.js: Getting started guides](https://nodejs.org/en/learn)
- [Node.js: API documentation](https://nodejs.org/api/)
