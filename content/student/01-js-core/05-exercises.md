# 11. Exercises

## Exercises overview and rules

There are five sets, ordered from recall to independent problem solving. Complete sets A to D in full; for set E, complete at least one challenge. Full solutions are **not** in this document: your instructor holds an answer key. That is intentional. Use the acceptance criteria and hints, and use `console.log` to check your own work.

::: tip How to know you are done without a solution
Every implementation exercise lists *acceptance criteria*: concrete calls with their expected results. Write those calls as `console.log` lines under your function. If every line prints what the criteria say, and you can explain *why* it works, you have solved it.
:::

Work in a folder `js-core/exercises/`, one file per exercise (`c1-is-even.js`, and so on). Run with `node filename.js`.

## Set A: Comprehension questions

Answer in your own words, in writing. One to three sentences each.

1. What is the difference between a JavaScript engine and a JavaScript environment? Give one thing the browser provides that Node.js does not, and one thing Node.js provides that the browser does not.
2. What is the difference between a statement and an expression? Classify `let x = 5 + 2;` and `5 + 2`.
3. Why is `const` the recommended default? What does `const` actually prevent, and what does it *not* prevent?
4. Name the seven primitive types. Which of them is *not* what `typeof` reports it to be?
5. What is the difference between `null` and `undefined`, and who normally produces each?
6. Why does `"5" + 3` give `"53"` while `"5" - 3` gives `2`?
7. List the eight falsy values. Is `"0"` truthy or falsy?
8. What is short-circuit evaluation? What does `0 || "fallback"` evaluate to, and what does `"a" && "b"` evaluate to?
9. What is a closure? Describe one situation where it is useful.
10. Explain the temporal dead zone. Why is it considered helpful rather than annoying?
11. A callback is *passed* to a function but not *called* by you. Who calls it, and when?
12. What does `finally` guarantee, and why is an empty `catch` block a bad idea?

## Set B: Syntax and output prediction

For each snippet, write down exactly what is printed. Do this **before** running. Then run it and, for every mismatch, write one sentence explaining the rule you had wrong.

**B1.**

```js file="b1.js"
let a = 10;
let b = a++ + ++a;
console.log(a, b);
```

**B2.**

```js file="b2.js"
console.log("3" + 4 + 5, 3 + 4 + "5");
```

**B3.**

```js file="b3.js"
console.log(typeof null, typeof undefined, typeof NaN, typeof []);
```

**B4.**

```js file="b4.js"
let out = "";
for (let i = 0; i < 6; i++) {
  if (i === 1) continue;
  if (i === 4) break;
  out += i;
}
console.log(out);
```

**B5.**

```js file="b5.js"
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

**B6.**

```js file="b6.js"
console.log(1 && 2 && 0, 0 || null || "end");
```

**B7.**

```js file="b7.js"
console.log(typeof f, typeof g);
function f() {}
var g = function () {};
```

**B8.**

```js file="b8.js"
function show(a, b = a * 2) {
  return [a, b];
}
console.log(show(2), show(2, 5), show(2, undefined), show(2, null));
```

## Set C: Small implementation exercises

Write each function from scratch. Do not copy code from the sheet; use it for ideas only.

#### C1. `isEven(n)`

**Problem.** Write a function that returns `true` if a number is even and `false` otherwise.

**Acceptance criteria.**

- `isEven(4)` returns `true`; `isEven(7)` returns `false`; `isEven(0)` returns `true`.
- `isEven(-2)` returns `true` and `isEven(-3)` returns `false`.
- The function *returns* a boolean; it does not print.

**Hint.** The remainder operator `%` and strict equality. Negative numbers: what is `-3 % 2`?

#### C2. `fizzBuzz(limit)`

**Problem.** Print the numbers from 1 to `limit`, but print `Fizz` for multiples of 3, `Buzz` for multiples of 5, and `FizzBuzz` for multiples of both.

**Acceptance criteria.**

- `fizzBuzz(15)` prints 15 lines; line 3 is `Fizz`, line 5 is `Buzz`, line 15 is `FizzBuzz`, line 7 is `7`.
- `fizzBuzz(0)` prints nothing.

**Hint.** Test the "both" case *first*. Why does order matter in an `if / else if` chain?

#### C3. `countVowels(text)`

**Problem.** Return how many vowels (`a e i o u`, either case) appear in a string.

**Acceptance criteria.**

- `countVowels("Hello World")` returns `3`.
- `countVowels("rhythm")` returns `0`; `countVowels("")` returns `0`; `countVowels("AEIOU")` returns `5`.

**Hint.** `for...of` can loop over the letters of a string. The string method `toLowerCase()` and `"aeiou".includes(letter)` (see the MDN String reference) will help. Neither is taught in this sheet; look them up.

#### C4. `celsiusToFahrenheit(text)`

**Problem.** Take **text** (as if typed by a user), convert it to a number, and return the Fahrenheit value. If the text is not a valid number, return `null`.

**Acceptance criteria.**

- `celsiusToFahrenheit("100")` returns `212`; `celsiusToFahrenheit("0")` returns `32`; `celsiusToFahrenheit(" -40 ")` returns `-40`.
- `celsiusToFahrenheit("hot")`, `celsiusToFahrenheit("")` and `celsiusToFahrenheit("   ")` all return `null` (an empty string must **not** become `0`).

**Hint.** Reuse the `readNumber` idea from Section 4. Formula: `c * 9 / 5 + 32`.

#### C5. `makeCounter` with reset

**Problem.** Extend the closure counter: `makeCounter(start = 0, step = 1)` returns an object with three functions, `next()`, `reset()` and `current()`, all sharing one private count.

**Acceptance criteria.**

- `const c = makeCounter(10, 5);` then `c.next()` returns `15`, again returns `20`, `c.current()` returns `20`, `c.reset()` makes `c.current()` return `10`.
- Two counters created separately never affect each other.
- There is no way to change the count other than through the three functions.

**Hint.** Return an object literal whose values are functions: `{ next: () => ..., reset: () => ... }`. Objects are covered in depth in Sheet 02; here you only need this shape.

#### C6. `repeatUntilValid(attempts, isValid, values)`

**Problem.** Simulate "ask until valid" without any user input. `values` is an array of strings (the simulated answers), `isValid` is a callback that receives a string and returns `true` or `false`, and `attempts` is the maximum number of values to examine. Return the first valid value, or `null` if none is valid within `attempts` tries.

**Acceptance criteria.**

- `repeatUntilValid(3, (v) => v !== "", ["", "", "ok", "late"])` returns `"ok"`.
- `repeatUntilValid(2, (v) => v !== "", ["", "", "ok"])` returns `null` (the valid value arrived too late).
- `repeatUntilValid(5, (v) => v !== "", [])` returns `null` without throwing.

**Hint.** A `for` loop whose bound uses both `attempts` and `values.length`; `break` or an early `return`.

## Set D: Debugging exercises

Each program is broken. For each: (1) run it, (2) write down the **evidence** (expected versus actual), (3) state your **hypothesis**, (4) fix it, (5) explain in one sentence *why* it was wrong. Apply the routine from Section 10.

**D1. Everyone is an adult.**

```js file="d1.js"
function isAdult(age) {
  if (age = 18) {
    return true;
  }
  return false;
}
console.log(isAdult(10), isAdult(30));
```

*Expected:* `false true`.

**D2. The discount that vanished.**

```js file="d2.js"
const applyDiscount = (price, percent) => {
  price - (price * percent) / 100;
};
console.log(applyDiscount(200, 10));
```

*Expected:* `180`.

**D3. Three identical messages.**

```js file="d3.js"
for (var i = 1; i <= 3; i++) {
  setTimeout(() => console.log("Reminder", i), 100);
}
```

*Expected:* `Reminder 1`, `Reminder 2`, `Reminder 3`.

**D4. The total that grew too long.**

```js file="d4.js"
const inputs = ["10", "5", "20"];
let total = 0;
for (const value of inputs) {
  total = total + value;
}
console.log(total);
```

*Expected:* `35`.

**D5. Too many messages.**

```js file="d5.js"
function describeGrade(grade) {
  switch (grade) {
    case "A":
      console.log("Excellent");
    case "B":
      console.log("Good");
    case "C":
      console.log("Pass");
    default:
      console.log("Unknown grade");
  }
}
describeGrade("B");
```

*Expected:* only `Good`.

## Set E: Challenges

These require independent thought. There is no hint beyond the problem statement; if you are stuck for more than 30 minutes, write down what you have tried and ask for guidance.

#### E1. Password strength checker

**Problem.** Write `checkPassword(password)` that returns an object `{ score, problems }`. `score` is a whole number from 0 to 5, earning one point for each rule satisfied: at least 8 characters; contains a lowercase letter; contains an uppercase letter; contains a digit; contains a character that is neither a letter nor a digit. `problems` is an array of short strings, one for each rule that failed.

**Acceptance criteria.**

- `checkPassword("abc")` has a `score` of `1` and four problems (it passes only the lowercase rule).
- `checkPassword("Abcdef12!")` has a `score` of `5` and an empty `problems` array.
- `checkPassword("")` has a `score` of `0` and five problems.
- Each rule is checked by logic you wrote (loops and conditions); you may not use regular expressions.

#### E2. Decimal to binary

**Problem.** Write `toBinary(n)` that converts a non-negative whole number to a string of binary digits **without** using `n.toString(2)`. Use only a loop, the `%` operator, and `Math.floor`.

**Acceptance criteria.**

- `toBinary(0)` returns `"0"`; `toBinary(1)` returns `"1"`; `toBinary(5)` returns `"101"`; `toBinary(255)` returns `"11111111"`.
- For every `n` from `0` to `100`, `toBinary(n)` equals `n.toString(2)`. Write a loop that checks this and prints `"all correct"` or the first value that disagrees.
- For a negative number or a non-integer, the function throws an `Error` with a helpful message.
