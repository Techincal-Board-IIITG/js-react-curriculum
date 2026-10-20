---
number: 01
title: Answer Key for JavaScript Core Fundamentals
subtitle: Solutions, expected outputs, debugging explanations and reference implementations
track: instructor
kind: instructor
label: INSTRUCTOR ANSWER KEY - SHEET 01
time: Do not distribute to students
edition: Instructor edition
goals:
  - Check student answers to comprehension and prediction exercises
  - Compare student implementations with tested reference solutions
  - Use the debugging explanations when students are stuck
  - Run the reference implementations of all five mini projects
---

# 1. How to Use This Key

Every code listing here marked with an *Output* panel was **executed by the build validator**, and the printed output matches. Solutions are *reference* solutions: other correct approaches exist. Grade on the acceptance criteria in the student sheet, not on matching this code line for line.

::: note Grading suggestion
Core sets A to D: 60 percent. One challenge from set E: 15 percent. Three core projects: 25 percent, graded on acceptance criteria, code clarity and the student's ability to explain their code aloud. Extension projects earn extra credit.
:::

# 2. Set A: Comprehension Answers

Accept any answer that contains the key idea.

1. The *engine* executes the language itself (V8 and so on); the *environment* is the host that adds objects around it. Browser only: `document`, `window`, `localStorage`. Node only: `process`, the `fs` module, reading local files.
2. A statement performs an action; an expression produces a value. `let x = 5 + 2;` is a statement; `5 + 2` is an expression.
3. `const` forbids re-pointing the name, which prevents accidental reassignment and communicates intent. It does **not** make objects or arrays immutable: their contents can still change.
4. string, number, boolean, undefined, null, bigint, symbol. `null`, because `typeof null` reports `"object"` (a historic bug).
5. `undefined` is produced by the engine for missing values; `null` is written by the programmer to mean "intentionally empty".
6. `+` concatenates when either operand is a string; `-` has no text meaning so both sides become numbers.
7. `false`, `0`, `-0`, `0n`, `""`, `null`, `undefined`, `NaN`. `"0"` is truthy (non-empty string).
8. The right operand is skipped when the left already decides the result. `0 || "fallback"` is `"fallback"`; `"a" && "b"` is `"b"`.
9. A function together with the variables of the scope where it was created. Use: private state such as a counter, or a callback that remembers values.
10. The span between the start of a scope and the line where a `let`/`const` is initialised, during which reading it throws. It turns "use before define" bugs into immediate, clear errors.
11. The function that received it calls it, at a time of *its* choosing (immediately for `forEach`, later for `setTimeout`).
12. `finally` runs whether or not an error occurred, even after a `return`. An empty `catch` hides failures so bugs surface later, far from the cause.

# 3. Set B: Predicted Outputs

```js file="b1.js" run
let a = 10;
let b = a++ + ++a;
console.log(a, b);
```

```output
12 22
```

`a++` yields 10 and makes `a` 11; `++a` makes it 12 and yields 12; `10 + 12` is `22`.

```js file="b2.js" run
console.log("3" + 4 + 5, 3 + 4 + "5");
```

```output
345 75
```

Left to right: `"3" + 4` is `"34"`, then `"345"`. In the second, `3 + 4` is `7` first, then `7 + "5"` is `"75"`.

```js file="b3.js" run
console.log(typeof null, typeof undefined, typeof NaN, typeof []);
```

```output
object undefined number object
```

```js file="b4.js" run
let out = "";
for (let i = 0; i < 6; i++) {
  if (i === 1) continue;
  if (i === 4) break;
  out += i;
}
console.log(out);
```

```output
023
```

`out` is a string, so `+=` concatenates the numbers 0, 2, 3. At `i = 1` the iteration is skipped; at `i = 4` the loop ends.

```js file="b5.js" run
function make() {
  let n = 0;
  return () => ++n;
}
const first = make();
const second = make();
first();
first();
console.log(first(), second());
```

```output
3 1
```

```js file="b6.js" run
console.log(1 && 2 && 0, 0 || null || "end");
```

```output
0 end
```

`&&` returns the first falsy operand (`0`), or the last one if all are truthy. `||` returns the first truthy operand, or the last one.

```js file="b7.js" run
console.log(typeof f, typeof g);
function f() {}
var g = function () {};
```

```output
function undefined
```

The declaration `f` is fully hoisted; `g` is a hoisted `var` holding `undefined` until line 3 runs.

```js file="b8.js" run
function show(a, b = a * 2) {
  return [a, b];
}
console.log(show(2), show(2, 5), show(2, undefined), show(2, null));
```

```output
[ 2, 4 ] [ 2, 5 ] [ 2, 4 ] [ 2, null ]
```

Defaults apply only for `undefined`, and a default can use earlier parameters.

# 4. Set C: Reference Solutions

#### C1. `isEven`

```js file="c1-is-even.js" run
function isEven(n) {
  return n % 2 === 0;
}

console.log(isEven(4), isEven(7), isEven(0), isEven(-2), isEven(-3));
```

```output
true false true true false
```

Common student error: `n % 2 === 1` for the odd test fails for negatives, because `-3 % 2` is `-1`. Testing against `0` is safe.

#### C2. `fizzBuzz`

```js file="c2-fizzbuzz.js" run
function fizzBuzz(limit) {
  for (let i = 1; i <= limit; i++) {
    if (i % 15 === 0) {
      console.log("FizzBuzz");
    } else if (i % 3 === 0) {
      console.log("Fizz");
    } else if (i % 5 === 0) {
      console.log("Buzz");
    } else {
      console.log(i);
    }
  }
}

fizzBuzz(15);
```

```output
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
```

If a student tests `% 3` first, 15 prints `Fizz`: the combined case must come first.

#### C3. `countVowels`

```js file="c3-vowels.js" run
function countVowels(text) {
  let count = 0;
  for (const letter of text.toLowerCase()) {
    if ("aeiou".includes(letter)) {
      count++;
    }
  }
  return count;
}

console.log(countVowels("Hello World"), countVowels("rhythm"));
console.log(countVowels(""), countVowels("AEIOU"));
```

```output
3 0
0 5
```

#### C4. `celsiusToFahrenheit`

```js file="c4-temperature.js" run
function readNumber(text) {
  const cleaned = text.trim();
  if (cleaned === "") {
    return null;
  }
  const value = Number(cleaned);
  return Number.isNaN(value) ? null : value;
}

function celsiusToFahrenheit(text) {
  const c = readNumber(text);
  return c === null ? null : (c * 9) / 5 + 32;
}

console.log(celsiusToFahrenheit("100"), celsiusToFahrenheit("0"));
console.log(celsiusToFahrenheit(" -40 "), celsiusToFahrenheit("hot"));
console.log(celsiusToFahrenheit(""), celsiusToFahrenheit("   "));
```

```output
212 32
-40 null
null null
```

#### C5. `makeCounter` with reset

```js file="c5-counter.js" run
function makeCounter(start = 0, step = 1) {
  let count = start;
  return {
    next: () => {
      count += step;
      return count;
    },
    reset: () => {
      count = start;
    },
    current: () => count,
  };
}

const c = makeCounter(10, 5);
console.log(c.next(), c.next(), c.current());
c.reset();
console.log(c.current());
const other = makeCounter();
console.log(other.next(), c.current());
```

```output
15 20 20
10
1 10
```

#### C6. `repeatUntilValid`

```js file="c6-repeat.js" run
function repeatUntilValid(attempts, isValid, values) {
  const limit = Math.min(attempts, values.length);
  for (let i = 0; i < limit; i++) {
    if (isValid(values[i])) {
      return values[i];
    }
  }
  return null;
}

const notEmpty = (v) => v !== "";
console.log(repeatUntilValid(3, notEmpty, ["", "", "ok", "late"]));
console.log(repeatUntilValid(2, notEmpty, ["", "", "ok"]));
console.log(repeatUntilValid(5, notEmpty, []));
```

```output
ok
null
null
```

# 5. Set D: Debugging Explanations

**D1.** `if (age = 18)` assigns 18 (truthy), so every call returns `true`. Fix: `===`. Diagnosis: print `age` before and after the `if`; it changes.

```js file="d1-fixed.js" run
function isAdult(age) {
  return age >= 18;
}
console.log(isAdult(10), isAdult(30));
```

```output
false true
```

(The original also confuses "equals 18" with "18 or older"; `>=` states the real intent.)

**D2.** The block-bodied arrow function has no `return`; the subtraction is computed and discarded, so the call returns `undefined`.

```js file="d2-fixed.js" run
const applyDiscount = (price, percent) => price - (price * percent) / 100;
console.log(applyDiscount(200, 10));
```

```output
180
```

**D3.** One shared `var i` is `4` when the timers fire. Fix: `let`.

```js file="d3-fixed.js" run
for (let i = 1; i <= 3; i++) {
  setTimeout(() => console.log("Reminder", i), 100);
}
```

```output
Reminder 1
Reminder 2
Reminder 3
```

**D4.** `total + value` concatenates because `value` is a string, giving `"010520"`. Fix: convert.

```js file="d4-fixed.js" run
const inputs = ["10", "5", "20"];
let total = 0;
for (const value of inputs) {
  total = total + Number(value);
}
console.log(total);
```

```output
35
```

**D5.** Missing `break` statements cause fallthrough: `"B"` prints Good, Pass and Unknown grade.

```js file="d5-fixed.js" run
function describeGrade(grade) {
  switch (grade) {
    case "A":
      console.log("Excellent");
      break;
    case "B":
      console.log("Good");
      break;
    case "C":
      console.log("Pass");
      break;
    default:
      console.log("Unknown grade");
  }
}
describeGrade("B");
```

```output
Good
```
