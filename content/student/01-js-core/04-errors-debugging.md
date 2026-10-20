# 10. Errors, Exceptions and Debugging

## Learning objectives for this section

- Tell syntax errors, runtime errors and logic errors apart.
- Read an error message and a stack trace and find the line that matters.
- Use `try`, `catch`, `finally` and `throw` correctly, including when *not* to.
- Apply a repeatable debugging routine instead of guessing.

## Conceptual explanation

Programs fail. A user types letters where a number was expected, a file is missing, or you simply made a typing mistake. What matters is how you *find* the problem and how your program *behaves* when it happens. There are three categories.

[[widths 1.2 2.4 2.4]]
| Category | When it appears | Example |
|---|---|---|
| **Syntax error** | Before anything runs. The whole file is rejected. | A missing `)` or `}` |
| **Runtime error** (exception) | While the program runs. Execution stops at that line unless you catch it. | `null.name`, calling an undefined function |
| **Logic error** | Never reported. The program runs but gives a wrong answer. | `<=` instead of `<`, `+` joining text |

Logic errors are the hardest because no message points to them. The debugging routine at the end of this section exists mainly for them.

## The built-in error types

| Type | Meaning | Typical cause |
|---|---|---|
| `SyntaxError` | The code breaks the grammar rules | Missing bracket, duplicate `let` |
| `ReferenceError` | A name does not exist (or is in the dead zone) | Typo, wrong scope |
| `TypeError` | A value is not of the kind the operation needs | Calling a non-function, reading a property of `null` or `undefined` |
| `RangeError` | A number is outside the allowed range | Negative array length, infinite recursion |

## Reading an error message and stack trace

```text file="Example error output"
TypeError: Cannot read properties of null (reading 'name')
    at greetUser (/home/me/js-core/app.js:3:22)
    at main (/home/me/js-core/app.js:8:3)
    at Object.<anonymous> (/home/me/js-core/app.js:11:1)
```

Read it in this order:

1. **First line**: the error *type* (`TypeError`) and *message*. The message here says you tried to read `name` from `null`.
2. **The stack**: one line (a *frame*) per function that was running, with the **innermost call first**. Here `greetUser` was running when the crash happened; it was called by `main`, which was called from the top level.
3. **The first frame inside your own file**: `app.js:3:22` means file `app.js`, line `3`, column `22`. Open that file at that line. That is where the failing operation is.
4. **The frames below it** tell you *how execution got there*, which helps you find which caller passed the bad value.

## `try`, `catch`, `finally` and `throw`

**What they are.** Statements that let your code *handle* a runtime error instead of crashing.

**Why they exist.** Some operations can fail for reasons your code cannot prevent (invalid external input, network trouble). You want to respond gracefully: show a message, use a fallback, clean up.

**Syntax.**

```text
try {
  // code that might throw
} catch (error) {
  // runs only if the try block threw; `error` is the thrown value
} finally {
  // runs always: after try, or after catch, even if they return
}

throw new Error("message");   // creates and throws an error yourself
```

**How it works, step by step.** The engine runs the `try` block. If every statement succeeds, `catch` is skipped. If a statement **throws** (either the engine or your own `throw`), the rest of the `try` block is abandoned, the engine jumps to `catch`, and `error` receives the thrown value. After that, `finally` runs no matter what. If *no* `catch` exists anywhere up the call stack, the program crashes with the stack trace you saw above.

```diagram
flow
Run try block -> *Did a line throw? -> Yes: jump to catch -> finally always runs -> Continue after
```

**The error object.** Errors created by `new Error(message)` (or `new RangeError(message)` and so on) carry three useful properties: `name` (the type as text), `message` (your description) and `stack` (the trace). Always throw **Error objects**, not strings, because only Error objects record a stack trace.

```js file="parse-age.js" run
function parseAge(text) {
  const age = Number(text);
  if (Number.isNaN(age)) {
    throw new Error(`"${text}" is not a number`);
  }
  if (age < 0 || age > 120) {
    throw new RangeError("Age must be between 0 and 120");
  }
  return age;
}

for (const input of ["25", "abc", "200"]) {
  try {
    console.log("Parsed:", parseAge(input));
  } catch (error) {
    console.log(`${error.name}: ${error.message}`);
  } finally {
    console.log("Checked", input);
  }
}
```

```output
Parsed: 25
Checked 25
Error: "abc" is not a number
Checked abc
RangeError: Age must be between 0 and 120
Checked 200
```

**Line by line.** Lines 1 to 10 are a *validating function*: it either returns a valid number or **throws**, never both. `throw` on line 4 immediately ends `parseAge`; no `return` is needed. The loop on line 12 tries three inputs. For `"25"`, line 14 prints and `catch` is skipped. For `"abc"`, `Number("abc")` is `NaN`, line 4 throws, the engine jumps to line 15, and `error.name` is `"Error"`. For `"200"`, line 7 throws a `RangeError`, whose `name` is `"RangeError"`. `finally` runs in all three cases.

| Step | Input | What happens in `parseAge` | Block that runs next | Printed |
|---|---|---|---|---|
| 1 | `"25"` | `age = 25`, passes both checks, returns `25` | `try` finishes | `Parsed: 25` |
| 2 | `"25"` | n/a | `finally` | `Checked 25` |
| 3 | `"abc"` | `age = NaN`, line 4 throws `Error` | `catch` | `Error: "abc" is not a number` |
| 4 | `"abc"` | n/a | `finally` | `Checked abc` |
| 5 | `"200"` | `age = 200`, line 7 throws `RangeError` | `catch` | `RangeError: Age must be between 0 and 120` |
| 6 | `"200"` | n/a | `finally` | `Checked 200` |

**Variation: wrapping a function that throws.** `JSON.parse(text)` (formally covered in Sheet 03) converts JSON text into a value and throws a `SyntaxError` when the text is invalid. A common pattern turns that failure into a fallback value.

```js file="safe-parse.js" run
function safeParse(text) {
  try {
    return JSON.parse(text);
  } catch (error) {
    return null;
  }
}

console.log(safeParse('{"ok": true}'));
console.log(safeParse("{broken"));
```

```output
{ ok: true }
null
```

## Optional deep dive: `finally` and `return`

`finally` runs even when `try` has already decided to `return`. The returned value is held, `finally` runs, and *then* the function returns.

```js file="finally-return.js" run
function test() {
  try {
    return "from try";
  } finally {
    console.log("cleanup runs first");
  }
}

console.log(test());
```

```output
cleanup runs first
from try
```

This is why `finally` is the right place for cleanup (closing a connection, hiding a loading spinner). Avoid putting a `return` *inside* `finally`: it overrides everything, including thrown errors.

::: concept When to use `try/catch`
Use it around operations that can fail **for reasons outside your control**, and catch only what you can actually handle. Do not wrap whole programs in it to silence errors. If you cannot handle an error meaningfully in a `catch`, re-throw it with `throw error;` so that the real problem stays visible.
:::

## A debugging routine that works

Debugging is not talent; it is a procedure. Follow these steps in order.

1. **Reproduce.** Find the exact input or sequence of actions that triggers the problem every time. A bug you cannot reproduce cannot be fixed.
2. **Read the evidence.** For errors: type, message, first stack frame in your file. For wrong output: compare *expected* with *actual*, and write both down.
3. **Form one hypothesis.** "I think `sum` becomes `NaN` because the loop reads past the end of the array." A hypothesis must be something you can test.
4. **Test the hypothesis** by observing, not by editing at random: print variables with labels, or use a breakpoint (below).
5. **Isolate.** Shrink the problem: delete or comment out code until the smallest program that still fails remains. Often the bug becomes obvious at this point.
6. **Fix one thing, run again.** Changing three things at once teaches you nothing.
7. **Understand why it broke**, then add a check (a validation, or later a test) so it cannot silently return.

### Worked example: a function that returns `NaN`

```js file="average-bug.js" run
function average(numbers) {
  let sum = 0;
  for (let i = 0; i <= numbers.length; i++) {
    sum += numbers[i];
  }
  return sum / numbers.length;
}

console.log(average([10, 20, 30]));
```

```output
NaN
```

*Evidence:* expected `20`, actual `NaN`. *Hypothesis:* something in the sum is not a number. *Test:* print each step.

```js file="average-debug.js" run
function average(numbers) {
  let sum = 0;
  for (let i = 0; i <= numbers.length; i++) {
    console.log("i =", i, "value =", numbers[i], "sum =", sum);
    sum += numbers[i];
  }
  return sum / numbers.length;
}

console.log(average([10, 20, 30]));
```

```output
i = 0 value = 10 sum = 0
i = 1 value = 20 sum = 10
i = 2 value = 30 sum = 30
i = 3 value = undefined sum = 60
NaN
```

The fourth line of output reveals it: at `i = 3` there is no element, so `numbers[3]` is `undefined` and `60 + undefined` is `NaN`. The loop condition `i <= numbers.length` is an off-by-one. Changing it to `i < numbers.length` fixes the bug.

### Tools beyond `console.log`

- **Label and shape your logs.** `console.log("sum:", sum)` is better than `console.log(sum)`. In the browser, `console.table(array)` prints a readable grid.
- **The `debugger;` statement.** With browser DevTools open, execution pauses at that line, and you can inspect every variable.
- **Breakpoints in DevTools.** Open the Sources tab, open your file, and click a line number. When that line is about to run, the page pauses. Use *Step over* (run this line), *Step into* (enter the called function) and the *Scope* and *Call Stack* panels to watch values change line by line.
- **Debugging Node.js.** Start the script with `node --inspect-brk file.js`, then open `chrome://inspect` in Chrome to attach the same debugger. VS Code also has a built-in debugger.
- **Rubber duck debugging.** Explain your code line by line, aloud, to an object. The act of explaining exposes wrong assumptions surprisingly often.

## Common mistakes in this section

#### Mistake 1: An empty `catch` block

**Why it is wrong.** It hides failures. The program continues with bad or missing data and breaks later in a place far from the real cause.

```js bad run throws
function load(text) {
  let data;
  try {
    data = JSON.parse(text);
  } catch (error) {}
  return data.name;
}
console.log(load("{oops"));
```

```output
TypeError: Cannot read properties of undefined (reading 'name')
```

**Symptom.** A confusing `TypeError` on a line that looks fine. The real failure (invalid JSON) was swallowed.

```js good run
function load(text) {
  try {
    return JSON.parse(text).name;
  } catch (error) {
    console.log("Could not read data:", error.message);
    return "Unknown";
  }
}
console.log(load("{oops"));
```

```output
Could not read data: Expected property name or '}' in JSON at position 1 (line 1 column 2)
Unknown
```

**How to diagnose it yourself.** At the very least log the error inside every `catch`. Search your code for `catch` blocks with nothing in them. (The exact wording of the JSON message varies between JavaScript engines and versions.)

#### Mistake 2: Throwing a string instead of an `Error`

**Why it is wrong.** A string has no `message`, no `name` and no stack trace.

```js bad run
try {
  throw "something broke";
} catch (error) {
  console.log(error.message);
}
```

```output
undefined
```

```js good run
try {
  throw new Error("something broke");
} catch (error) {
  console.log(error.message);
}
```

```output
something broke
```

**Symptom.** `undefined` where a message should be, and no line number to investigate. **Diagnosis:** search for `throw "` and `throw '` and replace with `throw new Error(...)`.

#### Mistake 3: Putting too much inside `try`

**Why it is wrong.** If a `try` block holds 40 lines, a failure anywhere is reported by the same generic `catch`, and you cannot tell which operation failed or whether the failure is even one you intended to handle. Keep the `try` around the one risky operation.

**Symptom.** An unhelpful catch-all message such as "Something went wrong" for ten different causes. **Fix:** move non-risky statements outside the block and keep only the call that can throw inside it.

**Diagnosis.** In the `catch`, log `error.name` and `error.message`. If they describe something your handler cannot fix, re-throw with `throw error;`.

#### Mistake 4: Expecting `try/catch` to catch errors in a later callback

**Why it is wrong.** The callback runs *after* the `try` statement has already finished, so it is outside the protected region.

```js bad run throws
try {
  setTimeout(() => {
    throw new Error("late failure");
  }, 0);
} catch (error) {
  console.log("caught");
}
```

```output
Error: late failure
```

**Symptom.** The `catch` never runs and the program crashes. Instead of `caught`, you see the uncaught error.

```js good run
setTimeout(() => {
  try {
    throw new Error("late failure");
  } catch (error) {
    console.log("caught inside the callback");
  }
}, 0);
```

```output
caught inside the callback
```

**How to diagnose it yourself.** Ask: "When does this code actually run?" Anything that runs later (timers, events, network responses) needs its *own* error handling inside it. Sheet 04 shows how `async/await` makes this much easier.
