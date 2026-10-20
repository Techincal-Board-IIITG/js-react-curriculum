# 8. Scope, Closures, Hoisting and the Temporal Dead Zone

## Learning objectives for this section

- Define scope and predict which variables are visible at any line.
- Explain lexical scope, block scope, shadowing and the scope chain.
- Explain what a closure is and use one to keep private state.
- Explain hoisting and the temporal dead zone, and why `let`/`const` behave differently from `var`.

## Conceptual explanation

**Scope** answers the question: *from which places in the code can this name be used?* Without scope, every variable would be visible everywhere and any two parts of a program could accidentally overwrite each other's data. Scope keeps names local so that a function can use `i` or `total` without disturbing the rest of the program.

JavaScript uses **lexical scope**: visibility is decided by *where the code is written*, not by where it is called from. You can work out the scope of any name just by reading the file.

There are three kinds of scope:

- **Global scope**: names declared outside every function and block. Visible everywhere.
- **Function scope**: names declared inside a function. Visible only in that function (including its inner blocks and inner functions).
- **Block scope**: names declared with `let` or `const` inside `{ }` (an `if`, a loop body, a bare block). Visible only inside those braces.

When the engine meets a name, it looks in the current scope first, then in the enclosing scope, then the one outside that, up to the global scope. This sequence is the **scope chain**. If the name is not found anywhere, you get a `ReferenceError`.

```diagram
tree
Global scope | siteName, showCourse
  showCourse() scope | course
    if-block scope | note
```

Inner scopes can read outer names (the lines go upward), but outer scopes cannot see inner names.

```js file="scope-chain.js" run
const siteName = "Learn JS";

function showCourse() {
  const course = "Functions";
  if (course.length > 3) {
    const note = "long name";
    console.log(siteName, course, note);
  }
  console.log(typeof note);
}

showCourse();
```

```output
Learn JS Functions long name
undefined
```

**Line by line.** Inside the `if` block, line 7 can see `note` (own scope), `course` (function scope) and `siteName` (global): the chain is searched outward. Line 9 runs after the block ended; `note` no longer exists there, so `typeof note` yields `"undefined"` rather than throwing.

## Shadowing

If an inner scope declares a name that already exists outside, the inner one **shadows** (hides) the outer one while inside that scope. The outer variable is untouched.

```js file="shadowing.js" run
const label = "outer";

function demo() {
  const label = "inner";
  console.log(label);
}

demo();
console.log(label);
```

```output
inner
outer
```

Shadowing is legal but can confuse readers; prefer distinct names.

## Closures

**What it is.** A **closure** is a function together with the variables from the scope where the function was *created*. The function keeps access to those variables even after the outer function has finished running.

**Why it exists.** Because scope is lexical, an inner function is *defined* inside the outer one and naturally refers to its variables. The engine must therefore keep those variables alive for as long as any such inner function exists.

**What problem it solves.** It lets a function carry **private state** that no other code can touch, without using global variables.

```js file="counter.js" run
function makeCounter() {
  let count = 0;
  return function () {
    count++;
    return count;
  };
}

const counterA = makeCounter();
const counterB = makeCounter();

console.log(counterA(), counterA(), counterA());
console.log(counterB());
```

```output
1 2 3
1
```

**Line by line and flow of data.**

- Line 1 defines `makeCounter`. Each *call* to it creates a fresh scope containing its own `count`.
- Line 3 returns an inner function. That function mentions `count` (lines 4 and 5), which lives in the scope of the call that created it.
- Line 9: the call creates scope A with `count = 0` and returns the inner function, which we store as `counterA`. `makeCounter` has now finished, yet scope A is **not** discarded, because `counterA` still needs it.
- Line 10: a second call creates a *separate* scope B with its own `count = 0`.
- Line 12: three calls to `counterA` each increment scope A's `count`: 1, 2, 3.
- Line 13: `counterB` has its own `count`, so it starts at 1.

| Step | Operation | scope A `count` | scope B `count` | Returned |
|---|---|---|---|---|
| 1 | `counterA = makeCounter()` | 0 | n/a | inner function |
| 2 | `counterB = makeCounter()` | 0 | 0 | inner function |
| 3 | `counterA()` | 1 | 0 | `1` |
| 4 | `counterA()` | 2 | 0 | `2` |
| 5 | `counterA()` | 3 | 0 | `3` |
| 6 | `counterB()` | 3 | 1 | `1` |

Nothing outside can read or set `count` directly; the only access is through the returned function. Closures are why a React component can remember a value between clicks, and why one specific class of React bug (a *stale closure*, Sheet 07) exists.

## Closures in loops: `var` versus `let`

This is the most famous closure puzzle, and it explains why `var` is avoided.

```js file="loop-closure.js" run
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log("var", i), 0);
}

for (let j = 0; j < 3; j++) {
  setTimeout(() => console.log("let", j), 0);
}
```

```output
var 3
var 3
var 3
let 0
let 1
let 2
```

`setTimeout` (deep dive in Section 9) schedules the arrow function to run *later*, after the current code has finished. With `var`, there is **one** shared `i` for the whole loop. By the time the callbacks run, the loop has finished and `i` is `3`, so all three callbacks print 3. With `let`, **every iteration gets its own fresh `j`**, and each callback closes over a different one: 0, 1 and 2.

## Hoisting and the temporal dead zone

**What happens first.** Before the engine executes a scope, it performs a scan and registers every declaration in that scope. This is **hoisting**. What it does with each kind of declaration differs.

[[widths 1.2 2.4 1.6 1.6]]
| Declaration | Registered before execution as | Usable before its line? | Redeclare in same scope? |
|---|---|---|---|
| `function name() {}` | Name **and** complete function body | Yes, fully | Yes (last wins) |
| `var x` | Name, initialised to `undefined` | Yes, but value is `undefined` | Yes |
| `let x` / `const x` | Name, but **uninitialised** | No: throws `ReferenceError` | No: `SyntaxError` |
| `const f = () => {}` | Same as `const` | No | No |

The period between the start of the scope and the moment the `let`/`const` line executes is the **temporal dead zone** (TDZ). Touching the variable in that zone is an error, which is a *good* thing: it turns silent bugs into loud ones.

```js file="hoisting.js" run
console.log(sayHi());
console.log(legacy);
console.log(legacy === undefined);

function sayHi() {
  return "hi";
}

var legacy = 1;
console.log(legacy);
```

```output
hi
undefined
true
1
```

`sayHi` works on line 1 because the whole function was registered up front. `legacy` exists at line 2 but holds `undefined` (only the *name* was hoisted, not the assignment on line 9). The TDZ in action:

```js file="tdz.js" run throws
function demo() {
  console.log("start");
  console.log(secret);
  const secret = 42;
}

demo();
```

```output
start
ReferenceError: Cannot access 'secret' before initialization
```

The message says "before initialization" rather than "is not defined": the engine knows `secret` exists in this function (hoisted) but refuses to let you read it before line 4 has run.

## Common mistakes in this section

#### Mistake 1: A shared `var` loop variable captured by callbacks

**Why it is wrong.** One `var i` is shared by all callbacks (see above).

```js bad run
for (var i = 1; i <= 3; i++) {
  setTimeout(() => console.log("Task", i), 0);
}
```

```output
Task 4
Task 4
Task 4
```

**Symptom.** Every callback sees the final value `4`.

```js good run
for (let i = 1; i <= 3; i++) {
  setTimeout(() => console.log("Task", i), 0);
}
```

```output
Task 1
Task 2
Task 3
```

**How to diagnose it yourself.** If a callback created in a loop sees "the last value" every time, check whether the loop variable is declared with `var`.

#### Mistake 2: Using a block variable outside its block

**Why it is wrong.** `let` and `const` do not survive past the closing brace.

```js bad run throws
if (true) {
  const message = "inside";
}
console.log(message);
```

```output
ReferenceError: message is not defined
```

```js good run
let message = "default";
if (true) {
  message = "inside";
}
console.log(message);
```

```output
inside
```

**Symptom.** `ReferenceError: ... is not defined`. **Diagnosis:** find the declaration, and check whether its enclosing braces have closed before the failing line. If you need the value outside, declare it *outside* with `let`.

#### Mistake 3: Assigning to an undeclared name

**Why it is wrong.** Forgetting `let`/`const` means there is no variable to assign to. In old non-module scripts this silently creates a *global variable*, which any other code can read or overwrite. In modules (and in files run as `.mjs`) it is an error.

```js bad run throws
function addTax(price) {
  total = price * 1.2;
  return total;
}
console.log(addTax(100));
```

```output
ReferenceError: total is not defined
```

```js good run
function addTax(price) {
  const total = price * 1.2;
  return total;
}
console.log(addTax(100));
```

```output
120
```

**Symptom.** An error, or (worse, in a plain script) mysterious interference between functions. **Diagnosis:** put `"use strict";` at the top of a plain script to make this mistake loud; modules are strict automatically.

#### Mistake 4: Reading a `const` in its dead zone

**Why it is wrong.** A function expression stored in `const` is not callable before its line runs.

```js bad run throws
console.log(double(4));
const double = (n) => n * 2;
```

```output
ReferenceError: Cannot access 'double' before initialization
```

```js good run
const double = (n) => n * 2;
console.log(double(4));
```

```output
8
```

**Diagnosis.** The words "before initialization" mean: move the declaration above its first use.

# 9. Callbacks and Higher-Order Functions

## Learning objectives for this section

- Explain that functions are values and can be passed as arguments.
- Define *callback* and *higher-order function*, and write one of each.
- Explain `forEach()` and `setTimeout()` completely: parameters, return values, and when the callback runs.

## Conceptual explanation

Since a function is just a value, you can hand one to another function, the same way you hand over a number. A function passed in this way is a **callback**: "call me back when you need me". A **higher-order function** is a function that takes a function as an argument, or returns a function (or both).

Why would you want this? Because it separates *what to repeat* from *what to do each time*. A loop function can know how to repeat; you supply the action. This idea runs through everything that follows: array methods (`map`, `filter`), event handlers in the browser, `fetch().then(...)`, and React's `useEffect`.

```diagram
flow
You write a callback -> Pass it to a function -> *That function decides when to call it -> Callback runs with its arguments
```

## Worked example: writing a higher-order function

```js file="repeat.js" run
function repeat(times, action) {
  for (let i = 0; i < times; i++) {
    action(i);
  }
}

repeat(3, (n) => console.log("Run number", n));
```

```output
Run number 0
Run number 1
Run number 2
```

**Line by line and data flow.** Line 1: `repeat` takes two parameters. `times` receives a number, `action` receives a *function*. Line 3: `action(i)` calls whatever function was passed, handing it the current loop index. Line 7: the arrow function `(n) => console.log(...)` is created and passed as the second argument. It is not called here; `repeat` calls it, three times, when *it* chooses. The parameter `n` of the arrow function receives the value of `i` each time.

**Returning functions.** A higher-order function can also build and return a customised function.

```js file="multiplier.js" run
function makeMultiplier(factor) {
  return (n) => n * factor;
}

const triple = makeMultiplier(3);

console.log(triple(5));
console.log(makeMultiplier(10)(2));
```

```output
15
20
```

`makeMultiplier(3)` returns an arrow function that closes over `factor = 3` (Section 8). On the last line, `makeMultiplier(10)` returns a function, and the second pair of parentheses calls it immediately with `2`.

## Function deep dive: `Array.prototype.forEach()`

**What it is.** A method on every array that calls a callback once for each element.

**Why it exists.** To loop over an array without managing an index variable, and to express "do this for every item" as a callback.

**Syntax.** `array.forEach(callback)` where `callback` is called as `callback(value, index, array)`.

**Parameters of the callback.**

- `value`: the current element.
- `index`: the position of that element (starting at 0). Optional to declare.
- `array`: the array being traversed. Optional to declare.

**Return value.** `undefined`. `forEach` is used for *side effects* (printing, updating something) and never produces a result.

**How it works.** It reads the array's length once, then for positions `0, 1, 2, ...` it calls your callback *synchronously* (one after another, before `forEach` returns), passing the three arguments. It always visits every element: there is no way to stop early with `break`.

```js file="foreach.js" run
const prices = [100, 200, 300];

prices.forEach((price, index, all) => {
  console.log(`${index + 1}/${all.length}: ${price}`);
});

const result = prices.forEach((price) => price * 2);
console.log(result);
```

```output
1/3: 100
2/3: 200
3/3: 300
undefined
```

| Call | `price` | `index` | `all` | Printed |
|---|---|---|---|---|
| 1 | `100` | `0` | `[100, 200, 300]` | `1/3: 100` |
| 2 | `200` | `1` | `[100, 200, 300]` | `2/3: 200` |
| 3 | `300` | `2` | `[100, 200, 300]` | `3/3: 300` |

Lines 3 to 5 pass an arrow function with a block body; it uses all three arguments. Lines 7 and 8 prove the return value: the arrow function returns `price * 2`, but `forEach` throws all return values away and returns `undefined` itself. If you need a *new array of results*, you need `map()`, which Sheet 02 covers in full.

## Function deep dive: `setTimeout()`

**What it is.** A function (provided by the browser and by Node.js, not by the language itself) that runs a callback once after a delay.

**Why it exists.** Programs often need to wait without freezing everything else: show a message for three seconds, retry a request later, debounce typing. Blocking the whole program with a busy loop would make a web page unresponsive.

**Syntax.** `setTimeout(callback, delayMs, ...args)`

**Parameters.** `callback`: the function to run later. `delayMs`: the *minimum* wait in milliseconds (default `0`). Extra arguments after the delay are passed to the callback when it runs.

**Return value.** A timer identifier (a number in browsers, an object in Node.js). Pass it to `clearTimeout(id)` to cancel the timer before it fires.

**How it works.** `setTimeout` hands the callback and the delay to the environment's timer system and returns immediately. Your code **continues to the end**. When the delay has passed *and* nothing else is running, the callback is placed into a queue and then executed. The delay is a minimum, not a promise: if other code is busy, the callback waits longer. Even `setTimeout(fn, 0)` runs **after** the current code finishes.

```diagram
sequence
actors: Your code | Timer system | Callback queue
Your code -> Timer system: setTimeout(callback, 0)
Timer system --> Callback queue: delay over: callback waits in line
note: Your code keeps running to its last line. Only then can queued callbacks run.
Callback queue -> Your code: callback is executed
```

```js file="timeout-order.js" run
console.log("1: start");

setTimeout(() => console.log("3: timer callback"), 0);

console.log("2: end of script");
```

```output
1: start
2: end of script
3: timer callback
```

The output order differs from the line order. Line 3 only *schedules* the callback; lines 1 and 5 run in order; the callback runs last. Sheet 04 explains the call stack and event loop behind this behaviour.

```js file="timeout-args.js" run
const id = setTimeout(() => console.log("never printed"), 50);
clearTimeout(id);
console.log("cancelled");

setTimeout((name, mood) => console.log("Hi", name, mood), 10, "Asha", "happy");
```

```output
cancelled
Hi Asha happy
```

Line 2 cancels the first timer before it can fire. Line 5 passes two extra arguments after the delay, which arrive as the callback's parameters. For repeated execution there is a sibling, `setInterval(callback, delayMs)`, cancelled with `clearInterval(id)`; you will use it for the Pomodoro timer in Sheet 03.

## Common mistakes in this section

#### Mistake 1: Calling the callback instead of passing it

**Why it is wrong.** `greet()` *runs* the function right now and passes its **return value** (`undefined`) to `setTimeout`.

```js bad run throws
function greet() {
  console.log("Hello!");
}
setTimeout(greet(), 10);
```

```output
Hello!
TypeError [ERR_INVALID_ARG_TYPE]: The "callback" argument must be of type function
```

**Symptom.** The greeting appears *immediately* rather than after the delay. Node.js also raises a `TypeError`, whereas a browser ignores the invalid callback silently, which hides the bug.

```js good run
function greet() {
  console.log("Hello!");
}
setTimeout(greet, 10);
```

```output
Hello!
```

**How to diagnose it yourself.** If something that should happen later happens at once, look for parentheses after the function name where you pass it. To pass arguments, wrap the call: `setTimeout(() => greet("Asha"), 10)`.

#### Mistake 2: Expecting `forEach` to return a result

**Why it is wrong.** `forEach` always returns `undefined`.

```js bad run
const prices = [100, 200];
const doubled = prices.forEach((p) => p * 2);
console.log(doubled);
```

```output
undefined
```

**Symptom.** `undefined`, and later a `TypeError` when you use it. **Fix:** use `map()` (Sheet 02) or push into a result array yourself.

```js good run
const prices = [100, 200];
const doubled = [];
prices.forEach((p) => {
  doubled.push(p * 2);
});
console.log(doubled);
```

```output
[ 200, 400 ]
```

**Diagnosis.** When a variable that should hold an array holds `undefined`, check whether it was assigned from a `forEach` call.

#### Mistake 3: Trying to stop `forEach` with `return`

**Why it is wrong.** `return` inside the callback only ends that *one* call of the callback; the next iteration still happens. It behaves like `continue`, not `break`.

```js bad run
[1, 2, 3, 4].forEach((n) => {
  if (n === 2) {
    return;
  }
  console.log(n);
});
```

```output
1
3
4
```

**Symptom.** You expected `1` only (stop at 2) but got `1`, `3`, `4`.

```js good run
for (const n of [1, 2, 3, 4]) {
  if (n === 2) {
    break;
  }
  console.log(n);
}
```

```output
1
```

**Diagnosis.** If you need early exit, use a regular `for` or `for...of` loop with `break`.

#### Mistake 4: Assuming timers run in the order they were written

**Why it is wrong.** Timers run in order of their *delays*, not their position in the file.

```js bad run
setTimeout(() => console.log("A (written first, 30 ms)"), 30);
setTimeout(() => console.log("B (written second, 0 ms)"), 0);
```

```output
B (written second, 0 ms)
A (written first, 30 ms)
```

**Symptom.** Output order differs from code order, which breaks code that assumes sequence. **Fix:** when order matters, start the second task from inside the first callback (nesting), or, preferably, use Promises and `async/await` (Sheet 04).

**Diagnosis.** Add `console.log` statements with step numbers at the start of each callback and read the real order.
