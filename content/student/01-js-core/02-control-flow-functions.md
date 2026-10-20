# 6. Control Flow: Decisions and Loops

## Learning objectives for this section

- Write `if`, `else if`, `else` and `switch` statements and explain how the engine chooses a branch.
- Write all five loop forms and choose the right one.
- Use `break` and `continue`, and trace a loop by hand.

## Conceptual explanation

Left alone, JavaScript executes statements from top to bottom. **Control flow** statements change that order in two ways. **Branching** chooses *whether* some code runs (`if`, `switch`). **Looping** chooses *how many times* it runs (`for`, `while` and friends). Together with variables and functions, these are all the tools a program needs to express any procedure.

```diagram
flow
Start -> Test condition -> *Condition true? -> Run block -> Continue below
```

## `if`, `else if` and `else`

**Syntax.**

```text
if (condition1) {
  // runs when condition1 is truthy
} else if (condition2) {
  // runs when condition1 is falsy AND condition2 is truthy
} else {
  // runs when all conditions above were falsy
}
```

The condition is any expression; it is converted to a boolean using the truthy/falsy rules from Section 4. Conditions are tested **in order, top to bottom**, and the first truthy one wins; all remaining branches are skipped. The `else` is optional.

```js file="grade.js" run
const score = 73;
let grade;

if (score >= 90) {
  grade = "A";
} else if (score >= 80) {
  grade = "B";
} else if (score >= 70) {
  grade = "C";
} else {
  grade = "F";
}

console.log(`Score ${score} -> grade ${grade}`);
```

```output
Score 73 -> grade C
```

**Line by line.** Line 2 declares `grade` with `let` and no value, because it will be assigned inside one of the branches. Line 4 tests `73 >= 90`: false, so the engine skips to the `else if` on line 6. `73 >= 80` is false. `73 >= 70` is true, so line 9 assigns `"C"`, and the engine jumps past the whole chain to line 14. The `else` on line 11 never runs. The backticks on line 14 create a *template literal*: `${...}` inserts the value of an expression into the text.

**Why the order matters.** If you wrote `score >= 70` first, a score of 95 would match it and receive a `"C"`. Put the most restrictive condition first.

## `switch`

**What it is.** A tidy way to choose among many *exact values* of one expression.

**Syntax.**

```text
switch (expression) {
  case value1:
    // statements
    break;
  case value2:
    // statements
    break;
  default:
    // runs if no case matched
}
```

**How it works.** The engine evaluates `expression` once, compares it with each `case` using **strict equality (`===`)**, and starts executing at the first match. It then keeps running *every following statement*, even those belonging to later cases, until it meets a `break` (or the end). This is called **fallthrough**. It is sometimes useful on purpose: stacked `case` labels share one block.

```js file="switch.js" run
const day = "Sat";

switch (day) {
  case "Sat":
  case "Sun":
    console.log("Weekend");
    break;
  case "Mon":
    console.log("Start of the week");
    break;
  default:
    console.log("Weekday");
}
```

```output
Weekend
```

`"Sat"` matches the case on line 4, which has no statements, so execution falls through to line 6 and prints `Weekend`. The `break` on line 7 exits the switch. Use `switch` when you compare one value against several constants; use `if/else if` when conditions are ranges (`score >= 90`) or involve different variables.

## The five loops

A **loop** repeats a block while a condition holds. Every loop needs three things, and bugs happen when one is missing: a **starting state**, a **condition** that eventually becomes false, and an **update** that moves toward making it false.

### `for`: when you know the count

**Syntax.** `for (init; condition; update) { body }`

**Execution order.** (1) `initialisation` runs **once**. (2) `condition` is tested; if falsy, the loop ends. (3) The body runs. (4) `update` runs. (5) Go back to step 2.

```js file="for-sum.js" run
let sum = 0;

for (let i = 1; i <= 5; i++) {
  sum += i;
}

console.log("Sum:", sum);
```

```output
Sum: 15
```

| Step | Operation | `i` | `sum` |
|---|---|---|---|
| 1 | `let sum = 0` | not declared | `0` |
| 2 | Initialisation `let i = 1` | `1` | `0` |
| 3 | Test `1 <= 5` true; body `sum += 1` | `1` | `1` |
| 4 | Update `i++`; test `2 <= 5` true; body | `2` | `3` |
| 5 | Update; test `3 <= 5` true; body | `3` | `6` |
| 6 | Update; test `4 <= 5` true; body | `4` | `10` |
| 7 | Update; test `5 <= 5` true; body | `5` | `15` |
| 8 | Update `i++` gives 6; test `6 <= 5` false: loop ends | `6` (gone) | `15` |

The `let i` belongs to the loop only: it is not visible after line 5. Using `let` (not `const`) is required because `i++` reassigns it.

### `while`: when you do not know the count

**Syntax.** `while (condition) { body }`. The condition is checked *before* every iteration, so the body may run zero times.

```js file="while-halve.js" run
let value = 100;
let steps = 0;

while (value >= 1) {
  value = value / 2;
  steps++;
}

console.log(steps, value);
```

```output
7 0.78125
```

We cannot easily know in advance how many halvings it takes to drop below 1, which makes `while` the natural choice. The values of `value` are 50, 25, 12.5, 6.25, 3.125, 1.5625 and finally 0.78125 after the seventh iteration, at which point `0.78125 >= 1` is false and the loop stops.

### `do...while`: run at least once

**Syntax.** `do { body } while (condition);` The body runs first, then the condition is checked. This suits "ask, then validate" patterns.

```js file="do-while.js" run
let attempts = 0;

do {
  attempts++;
  console.log("Attempt", attempts);
} while (attempts < 3);
```

```output
Attempt 1
Attempt 2
Attempt 3
```

### `for...of`: the values of a list

**What it does.** Visits each *value* of an iterable such as an array or a string, in order. You do not manage an index. It is the preferred loop for reading every item.

```js file="for-of.js" run
const fruits = ["apple", "banana", "cherry"];

for (const fruit of fruits) {
  console.log("Fruit:", fruit);
}

for (const letter of "hey") {
  console.log(letter);
}
```

```output
Fruit: apple
Fruit: banana
Fruit: cherry
h
e
y
```

`const` works here because each iteration creates a **fresh** variable; nothing is reassigned. Read line 3 as "for each `fruit` in `fruits`".

### `for...in`: the keys of an object

**What it does.** Visits the property *names* (always strings) of an object. Use it for objects, not arrays.

```js file="for-in.js" run
const student = { name: "Asha", age: 20, city: "Pune" };

for (const key in student) {
  console.log(key, "=", student[key]);
}

for (const index in ["a", "b"]) {
  console.log(index, typeof index);
}
```

```output
name = Asha
age = 20
city = Pune
0 string
1 string
```

`student[key]` (square-bracket access) reads the property whose name is *stored in the variable* `key`. The second loop shows why `for...in` is wrong for arrays: the "indexes" are strings, and `for...in` can also pick up extra properties someone added to the array. Use `for...of` instead.

[[widths 1 2.4 2.4]]
| Loop | Best for | Gives you |
|---|---|---|
| `for` | Counting, or needing the index | Whatever you write |
| `while` | Unknown number of repetitions | Nothing automatic |
| `do...while` | Must run at least once | Nothing automatic |
| `for...of` | Reading every item of an array or string | Each **value** |
| `for...in` | Inspecting an object's property names | Each **key** (string) |

## `break` and `continue`

`break` leaves the nearest loop (or `switch`) immediately. `continue` abandons the current iteration and moves straight to the next one (in a `for` loop, it still runs the update).

```js file="break-continue.js" run
for (let i = 1; i <= 10; i++) {
  if (i % 2 === 1) {
    continue;
  }
  if (i > 8) {
    break;
  }
  console.log(i);
}
```

```output
2
4
6
8
```

Odd numbers hit `continue` on line 3 and skip the print. At `i = 10` the number is even, so it reaches line 5, where `10 > 8` triggers `break`, and the loop ends before printing `10`.

## Common mistakes in this section

#### Mistake 1: Off-by-one in the loop condition

**Why it is wrong.** Array positions run from `0` to `length - 1`. Using `<=` visits one position too many.

```js bad run
const colors = ["red", "green"];
for (let i = 0; i <= colors.length; i++) {
  console.log(colors[i]);
}
```

```output
red
green
undefined
```

**Symptom.** An extra `undefined`; in real code, later a `TypeError` about reading properties of undefined.

```js good run
const colors = ["red", "green"];
for (let i = 0; i < colors.length; i++) {
  console.log(colors[i]);
}
```

```output
red
green
```

**How to diagnose it yourself.** Write the first and last value of `i` on paper and compare with the valid positions (0 and 1). Better still, use `for...of`, which cannot make this error.

#### Mistake 2: A loop that never ends

**Why it is wrong.** The condition can only become false if something inside the body changes it.

```js bad nocheck
let count = 0;
while (count < 3) {
  console.log("working...");
}
```

**Symptom.** The terminal prints forever (or the browser tab freezes). Press `Ctrl+C` in the terminal to stop it.

```js good run
let count = 0;
while (count < 3) {
  console.log("working...");
  count++;
}
```

```output
working...
working...
working...
```

**How to diagnose it yourself.** Ask the three loop questions: what is the starting state, what is the condition, and *which line moves the state toward ending?* Add a `console.log(count)` inside to watch it.

#### Mistake 3: Forgetting `break` in a `switch`

**Why it is wrong.** Without `break`, execution falls through into the next case.

```js bad run
const level = "easy";
switch (level) {
  case "easy":
    console.log("Easy mode");
  case "hard":
    console.log("Hard mode");
}
```

```output
Easy mode
Hard mode
```

```js good run
const level = "easy";
switch (level) {
  case "easy":
    console.log("Easy mode");
    break;
  case "hard":
    console.log("Hard mode");
    break;
}
```

```output
Easy mode
```

**Symptom.** More than one branch runs. **Diagnosis:** whenever two branches run together, check for a missing `break` above the second one.

#### Mistake 4: Using `for...in` on an array

**Why it is wrong.** It yields string keys, so arithmetic on them concatenates.

```js bad run
const prices = [10, 20];
let total = 0;
for (const i in prices) {
  total += i;
}
console.log(total);
```

```output
001
```

```js good run
const prices = [10, 20];
let total = 0;
for (const price of prices) {
  total += price;
}
console.log(total);
```

```output
30
```

**Symptom.** `total` becomes the string `"001"` (the number `0` followed by the text `"0"` then `"1"`). **Diagnosis:** log `typeof` of the loop variable.

# 7. Functions

## Learning objectives for this section

- Write functions using declarations, expressions and arrow syntax.
- Explain parameters versus arguments, and what a function returns when you forget `return`.
- Use default parameter values.
- Explain what happens, step by step, when a function is called.

## Conceptual explanation

A **function** is a named, reusable block of code that accepts input, does some work, and gives back an output. If you have ever written a CSS class and applied it in many places, the idea is similar: define once, reuse everywhere. Functions solve three problems. They remove repetition, they let you give a *name* to an idea (`calculateTotal` explains more than five lines of arithmetic), and they let you test and fix one small piece in isolation. They are also the foundation of React: a React component is, quite literally, a function.

## Syntax: three ways to write the same thing

```js file="three-syntaxes.js" run
function square(n) {
  return n * n;
}

const squareExpression = function (n) {
  return n * n;
};

const squareArrow = (n) => n * n;

console.log(square(4), squareExpression(4), squareArrow(4));
```

```output
16 16 16
```

**Anatomy of a declaration** (lines 1 to 3).

- `function` is the keyword that starts it.
- `square` is the function's name.
- `(n)` is the **parameter list**. A *parameter* is a placeholder variable that exists only inside the function.
- `{ ... }` is the **body**: the statements that run each time the function is called.
- `return n * n;` ends the function and sends a value back to whoever called it.

**Calling** a function means writing its name followed by parentheses containing **arguments**: `square(4)`. The argument `4` is the actual value bound to the parameter `n` for this call. People often mix up the two words: *parameters* appear in the definition, *arguments* appear in the call.

**Function expression** (lines 5 to 7): an anonymous function is created and stored in a `const`, like any other value. **Arrow function** (line 9): a shorter notation. When the body is a single expression you can omit the braces and `return`; the expression's value is returned automatically (an *implicit return*).

::: concept Declarations are hoisted, expressions are not
A function *declaration* can be called before the line where it appears. A function stored with `const` cannot. Section 8 explains why. This curriculum defines functions before using them, so you will rarely notice.
:::

## What happens when a function is called

```diagram
flow
Call square(4) -> Create parameter n = 4 -> Run the body -> *return 16 -> Caller continues with 16
```

1. The engine evaluates the arguments (`4`) left to right.
2. It creates a **new, private scope** for this call and binds each parameter to its argument (`n` becomes `4`).
3. It runs the body statements top to bottom until it reaches `return` or the closing brace.
4. The returned value replaces the call expression at the place where the function was called, and execution resumes there.
5. The private scope is discarded (unless a closure keeps part of it alive; see Section 8).

Because every call gets its own scope, calling `square(4)` and `square(9)` never interferes.

## Return values

- `return value;` ends the function immediately and gives back `value`. Any statements after it never run.
- A function that reaches its end without a `return`, or has a bare `return;`, gives back **`undefined`**.
- A function can return only **one** value. To return several, return an object or an array.

## Default parameters, and mismatched argument counts

JavaScript does not check how many arguments you pass. Extra arguments are ignored. Missing arguments leave their parameters as `undefined`. A **default parameter** supplies a replacement when the argument is missing or exactly `undefined`.

```js file="calculate-total.js" run
function calculateTotal(price, quantity, taxRate = 0.2) {
  const subtotal = price * quantity;
  return subtotal * (1 + taxRate);
}

console.log(calculateTotal(100, 3));
console.log(calculateTotal(100, 3, 0));
console.log(calculateTotal(100));
```

```output
360
300
NaN
```

**Line by line.**

- Line 1 declares three parameters; `taxRate` has the default `0.2`.
- Line 2 creates a local constant, `subtotal`, which exists only during this call.
- Line 3 returns the result. Line 6 passes two arguments, so `taxRate` uses its default: `300 * 1.2` is `360`.
- Line 7 passes `0` as the third argument. `0` is not `undefined`, so the default is *not* used, giving `300`.
- Line 8 passes only one argument: `quantity` is `undefined`, and `100 * undefined` is `NaN`. The language did not warn you; this is why you must validate inputs in real programs.

| Step | Operation (call on line 6) | `price` | `quantity` | `taxRate` | `subtotal` |
|---|---|---|---|---|---|
| 1 | Arguments `100`, `3` evaluated | | | | |
| 2 | Parameters bound; default applied | `100` | `3` | `0.2` | not declared |
| 3 | Line 2 runs | `100` | `3` | `0.2` | `300` |
| 4 | Line 3: `300 * 1.2` returned | `100` | `3` | `0.2` | `300` |
| 5 | Call replaced by `360`; scope discarded | gone | gone | gone | gone |

## Arrow function details

```js file="arrow-forms.js" run
const double = (n) => n * 2;
const add = (a, b) => a + b;
const greet = () => "Hello!";
const describe = (n) => {
  const kind = n % 2 === 0 ? "even" : "odd";
  return `${n} is ${kind}`;
};
const makePoint = (x, y) => ({ x, y });

console.log(double(5), add(2, 3), greet());
console.log(describe(7));
console.log(makePoint(2, 3));
```

```output
10 5 Hello!
7 is odd
{ x: 2, y: 3 }
```

Lines 1 to 3 use *concise bodies* (a single expression, implicit return). Line 4 uses a *block body*: braces mean you must write `return` yourself. Line 8 wraps `{ x, y }` in parentheses: without them, the engine reads the braces as a block body, not as an object (see Mistake 3).

## Why functions matter later

Functions are **values**: you can store them in variables (as above), pass them to other functions, and return them from functions. Section 9 builds on exactly this idea, and Sheet 02 uses it constantly with `map()` and `filter()`.

## Common mistakes in this section

#### Mistake 1: Forgetting `return`

**Why it is wrong.** Computing a value is not the same as returning it. Without `return`, the value is discarded when the call ends.

```js bad run
function add(a, b) {
  a + b;
}
console.log(add(2, 3));
```

```output
undefined
```

**Symptom.** `undefined` where a number was expected, often followed by `NaN` further on.

```js good run
function add(a, b) {
  return a + b;
}
console.log(add(2, 3));
```

```output
5
```

**How to diagnose it yourself.** Print the call result directly: `console.log(add(2, 3))`. If you see `undefined`, read the function body for a missing `return`.

#### Mistake 2: Referencing a function instead of calling it

**Why it is wrong.** Without parentheses the name is only a *reference to the function*, not the result of running it.

```js bad run
function add(a, b) {
  return a + b;
}
const result = add;
console.log(result);
```

```output
[Function: add]
```

```js good run
function add(a, b) {
  return a + b;
}
const result = add(2, 3);
console.log(result);
```

```output
5
```

**Symptom.** The console prints `[Function: add]` (or `ƒ add(a, b)` in browsers). **Diagnosis:** if you expect a value and see a function, look for missing `()`. Later, the opposite mistake (calling when you should pass a reference) appears with callbacks.

#### Mistake 3: Returning an object from an arrow function without parentheses

**Why it is wrong.** After `=>`, a `{` starts a *block*. The text `x, y` inside is just an expression statement, and there is no `return`.

```js bad run
const makePoint = (x, y) => { x, y };
console.log(makePoint(2, 3));
```

```output
undefined
```

```js good run
const makePoint = (x, y) => ({ x, y });
console.log(makePoint(2, 3));
```

```output
{ x: 2, y: 3 }
```

**Symptom.** `undefined` and no error message at all. **Diagnosis:** when an arrow function is meant to return an object, wrap the object in parentheses; or use a block body with an explicit `return`.

#### Mistake 4: Expecting `null` to trigger a default

**Why it is wrong.** Defaults apply only for `undefined`. `null` is a real value (Section 4).

```js bad run
function greet(name = "friend") {
  return `Hello, ${name}!`;
}
console.log(greet(null));
```

```output
Hello, null!
```

```js good run
function greet(name) {
  const who = name === null || name === undefined ? "friend" : name;
  return `Hello, ${who}!`;
}
console.log(greet(null));
```

```output
Hello, friend!
```

**Symptom.** The word `null` appears in your output. **Diagnosis:** log the argument at the top of the function and check for `null`; handle it explicitly when it is a possible input.
