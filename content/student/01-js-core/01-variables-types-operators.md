# 3. Variables and Declarations

## Learning objectives for this section

- Declare variables with `const` and `let`, and follow the naming rules.
- Explain the difference between *reassigning* a variable and *changing* the value it refers to.
- Explain why `var` is avoided in modern code.

## Conceptual explanation

A program must remember things: a score, a user's name, the price of an item. A **variable** is a name that the engine associates with a value held in memory. When you write the name later, the engine looks up the value. Think of a name tag attached to a value: you can move the tag to a different value (reassignment), but moving a tag is a different action from altering the thing the tag is attached to.

Modern JavaScript has two declaration keywords you should use, and one you should recognise but avoid.

[[widths 1 2.2 2.2]]
| Keyword | Meaning | Use it when |
|---|---|---|
| `const` | Declares a binding that **cannot be reassigned**. Must be given a value immediately. | The name should always point at the same value. This is the default choice. |
| `let` | Declares a binding that **can be reassigned**. | A counter, a running total, or any value that must change. |
| `var` | The pre-2015 keyword. Function-scoped, hoisted as `undefined`, allows redeclaration. | Almost never. You will meet it in old tutorials and old code. |

## Syntax

```text
const name = expression;     // must initialise
let   name = expression;     // may initialise now...
let   name;                  // ...or later; holds undefined until assigned
name = expression;           // reassignment (not allowed for const)
```

**Naming rules.** A name may contain letters, digits, `_` and `$`. It cannot start with a digit, cannot contain spaces or hyphens, and cannot be a reserved word such as `class`, `return` or `let`. Names are case-sensitive: `total` and `Total` are different variables.

**Conventions.** Use `camelCase` for ordinary variables (`studentName`, `maxScore`). Use descriptive names (`discountedPrice`, not `dp`). Use `UPPER_SNAKE_CASE` only for true fixed settings known before the program runs, such as `MAX_ATTEMPTS`.

## Worked example: a running total

```js file="variables.js" run
const taxRate = 0.2;
let subtotal = 250;

subtotal = subtotal + 50;
const total = subtotal * (1 + taxRate);

console.log("Subtotal:", subtotal);
console.log("Total:", total);
```

```output
Subtotal: 300
Total: 360
```

**Line by line.**

- Line 1 creates `taxRate` with `const` because the tax rate does not change while the program runs.
- Line 2 creates `subtotal` with `let` because we are about to change it.
- Line 4 *reassigns* `subtotal`. The right side is evaluated first (`250 + 50` gives `300`), and only then is the name re-pointed at the new value.
- Line 5 computes `1 + 0.2 = 1.2`, multiplies `300 * 1.2`, and stores `360` in a brand-new `const`.
- Lines 7 and 8 print the results.

**Execution trace.**

| Step | Operation | `taxRate` | `subtotal` | `total` |
|---|---|---|---|---|
| 1 | Line 1 runs | `0.2` | not yet declared | not yet declared |
| 2 | Line 2 runs | `0.2` | `250` | not yet declared |
| 3 | Line 4: evaluate `subtotal + 50` | `0.2` | `250` (still) | not yet declared |
| 4 | Line 4: assign result | `0.2` | `300` | not yet declared |
| 5 | Line 5: evaluate `300 * 1.2` and assign | `0.2` | `300` | `360` |

## `const` does not mean "frozen"

`const` stops you from pointing the name at a different value. It does **not** stop you from changing the *inside* of an object or array that the name refers to.

```js file="const-array.js" run
const cart = ["pen"];
cart.push("book");
console.log(cart);
```

```output
[ 'pen', 'book' ]
```

`cart` still points at the same array (the tag never moved), but the array's contents changed. Trying to move the tag is the error:

```js file="const-error.js" bad run throws
const limit = 3;
limit = 4;
```

```output
TypeError: Assignment to constant variable.
```

## Optional deep dive: why `var` is avoided

`var` ignores block boundaries. A block is any pair of braces `{ }`, such as the body of an `if`.

```js file="var-leak.js" run
if (true) {
  var a = 1;
  let b = 2;
}
console.log(a);
console.log(typeof b);
```

```output
1
undefined
```

`var a` escapes the block and remains visible on line 5, which makes code hard to reason about. `let b` is confined to the braces; outside them the name `b` does not exist, so `typeof b` reports `"undefined"` (and, as you learned, `typeof` never throws for unknown names). Section 8 returns to this with scope rules.

::: concept Decision rule
Start every variable as `const`. Change it to `let` only when the compiler (your own reading of the code) tells you it must be reassigned. Do not use `var`.
:::

## Common mistakes in this section

#### Mistake 1: Reassigning a `const`

**Why it is wrong.** `const` forbids re-pointing the name. Often the real need is a changing value, which should have been declared with `let`.

```js bad nocheck
const score = 0;
score = score + 10;
```

**Symptom.** `TypeError: Assignment to constant variable.` raised at runtime on line 2.

```js good run
let score = 0;
score = score + 10;
console.log(score);
```

```output
10
```

**How to diagnose it yourself.** The error message names the variable. Go to its declaration and ask: "Does this need to change?" If yes, use `let`.

#### Mistake 2: Declaring the same name twice

**Why it is wrong.** In one scope each `let` or `const` name may be declared only once, which catches accidental name collisions.

```js bad nocheck
let count = 1;
let count = 2;
```

**Symptom.** `SyntaxError` saying the identifier `'count'` has already been declared. Because this is a syntax error the *entire file* refuses to run.

```js good run
let count = 1;
count = 2;
console.log(count);
```

```output
2
```

**How to diagnose it yourself.** Search the file for the repeated name. Remove the second `let` and keep only the assignment.

#### Mistake 3: Using a variable before its declaration line

**Why it is wrong.** `let` and `const` names exist from the start of their block but cannot be *read* until the declaration line has executed. This gap is called the temporal dead zone (Section 8).

```js bad run throws
console.log(price);
const price = 10;
```

```output
ReferenceError: Cannot access 'price' before initialization
```

```js good run
const price = 10;
console.log(price);
```

```output
10
```

**How to diagnose it yourself.** The message says "before initialization": move the declaration above its first use.

#### Mistake 4: Believing `const` makes data unchangeable

**Why it is wrong.** `const` protects the name, not the contents (see the `cart` example). A bug that mutates a `const` array is invisible to a reader who trusts the keyword.

**Symptom.** No error at all; data silently changes. The fix is to be deliberate: treat shared data as read-only by convention, and in Sheet 02 you will learn how to produce updated *copies* instead of mutating.

# 4. Values, Types and Conversion

## Learning objectives for this section

- Name the primitive types and use `typeof` correctly, including its famous quirk.
- Explain the difference between `null` and `undefined`.
- Explain how primitives and objects behave differently when copied.
- Predict implicit coercion and perform explicit conversion with `Number()`, `parseInt()`, `parseFloat()`, `String()` and `Boolean()`.
- Classify any value as truthy or falsy.

## Conceptual explanation

Every value has a **type**, which determines what you can do with it. You can multiply numbers but not meaningfully multiply a sentence. JavaScript is **dynamically typed**: a variable has no fixed type, only the *value* it currently holds has one. This is flexible, but it means the engine will not stop you from mixing types; it will quietly convert them, sometimes producing nonsense. Understanding conversion rules is how you stay in control.

Values fall into two families.

**Primitive values** are simple, indivisible and immutable (they cannot be altered, only replaced).

[[widths 1 1.6 1.2 3]]
| Type | Examples | `typeof` gives | Notes |
|---|---|---|---|
| string | `"hello"`, `'hi'`, `` `total ${x}` `` | `"string"` | Text. Immutable. |
| number | `42`, `3.14`, `-7`, `NaN`, `Infinity` | `"number"` | One type for integers and decimals (64-bit floating point). |
| boolean | `true`, `false` | `"boolean"` | Result of comparisons. |
| undefined | `undefined` | `"undefined"` | "No value has been given." |
| null | `null` | `"object"` (historic bug) | "Deliberately empty." |
| bigint | `12345678901234567890n` | `"bigint"` | Very large integers; rarely needed. |
| symbol | `Symbol("id")` | `"symbol"` | Unique keys; rarely needed. |

**Reference values** are objects: plain objects `{ }`, arrays `[ ]`, functions, dates and more. They are mutable and they are compared and copied *by reference* (explained below).

## Syntax and the `typeof` operator

`typeof value` is an **operator**, not a function (parentheses are optional), and it always returns one of a small set of strings.

```js file="typeof-demo.js" run
console.log(typeof "hi");
console.log(typeof 42);
console.log(typeof 3.14);
console.log(typeof true);
console.log(typeof undefined);
console.log(typeof null);
console.log(typeof NaN);
console.log(typeof [1, 2]);
console.log(typeof { a: 1 });
console.log(typeof (() => 1));
console.log(typeof 10n);
```

```output
string
number
number
boolean
undefined
object
number
object
object
function
bigint
```

**Reading the surprises.** Line 6: `typeof null` is `"object"`. This is a bug from the first version of JavaScript that can never be fixed without breaking old websites. To test for `null`, write `value === null`. Line 7: `NaN` stands for "Not a Number" but is *of type number*; it is the number-shaped result of a failed calculation. Line 8: arrays are objects; to detect an array use `Array.isArray(value)` (Sheet 02). Line 10: functions report `"function"` although they are technically objects.

## `undefined` versus `null`

```js file="null-undefined.js" run
let notAssigned;
const emptyOnPurpose = null;
const student = { name: "Asha" };

function doNothing() {}

console.log(notAssigned);
console.log(emptyOnPurpose);
console.log(student.age);
console.log(doNothing());
```

```output
undefined
null
undefined
undefined
```

`undefined` is what the *engine* hands you when something was never given a value: a declared-but-unassigned variable (line 7), a property that does not exist (line 9), or a function with no `return` (line 10). `null` is what *you* write to say "there is intentionally no value here" (line 8). Rule of thumb: never assign `undefined` yourself; use `null` for "empty by choice".

## Numbers: two facts you must know

JavaScript numbers are binary floating-point, so some decimals cannot be stored exactly.

```js file="float.js" run
console.log(0.1 + 0.2);
console.log(0.1 + 0.2 === 0.3);
console.log(5 / 0);
console.log("abc" * 2);
console.log((0.1 + 0.2).toFixed(2));
```

```output
0.30000000000000004
false
Infinity
NaN
0.30
```

Line 1 shows the classic rounding artefact (the same happens in every language that uses standard floating point). Line 3 shows that dividing by zero does not crash; it yields `Infinity`. Line 4 shows `NaN`, the result of a meaningless calculation. Line 5 uses `toFixed(2)`, which formats a number with two decimals but **returns a string**, not a number: use it only for display. For money, store whole cents (`1999` for 19.99) and divide only when showing the value.

## Copying: primitives versus references

```js file="copy-semantics.js" run
let a = 5;
let b = a;
b = 10;
console.log(a, b);

const p = { score: 1 };
const q = p;
q.score = 99;
console.log(p.score, q.score);
console.log({} === {});
```

```output
5 10
99 99
false
```

**Explanation.** On line 2, `b = a` copies the *value* `5`. The two variables are independent afterwards, so changing `b` leaves `a` alone. On line 7, `q = p` copies the *reference* to one object, not the object itself. Both names now lead to the same object, so line 8 changes what `p` sees too. On line 10, two separately written `{}` are two different objects, so strict equality is `false` even though they look identical: objects are equal only if they are *the same object*.

| Step | Operation | `a` | `b` | `p.score` | `q.score` |
|---|---|---|---|---|---|
| 1 | `let a = 5; let b = a;` | 5 | 5 | n/a | n/a |
| 2 | `b = 10` | 5 | 10 | n/a | n/a |
| 3 | `const p = { score: 1 }; const q = p;` | 5 | 10 | 1 | 1 |
| 4 | `q.score = 99` | 5 | 10 | 99 | 99 |

## Type conversion and coercion

**Conversion** is changing a value from one type to another. It is **explicit** when you ask for it (`Number("42")`) and **implicit** (also called *coercion*) when the engine does it for you. The engine applies three families of rules:

1. The `+` operator: if either side is a string, the result is **string concatenation**. Otherwise it adds numbers.
2. The operators `-`, `*`, `/`, `%`: both sides are converted to **numbers**.
3. Anything inside an `if (...)`, `!`, `&&` or `||` test is converted to a **boolean**.

```js file="coercion.js" run
console.log("5" + 3, typeof ("5" + 3));
console.log("5" - 3, typeof ("5" - 3));
console.log("5" * "2");
console.log(true + 1);
console.log(null + 1);
console.log(undefined + 1);
console.log("abc" - 1);
console.log(1 + 2 + "3");
console.log("1" + 2 + 3);
```

```output
53 string
2 number
10
2
1
NaN
NaN
33
123
```

**Reading each result.** `"5" + 3` joins text, giving `"53"`. `"5" - 3` has no text meaning for minus, so `"5"` becomes the number 5. `true` becomes 1 and `null` becomes 0 in arithmetic, while `undefined` becomes `NaN` (no number), and any calculation involving `NaN` stays `NaN`. The last two lines show that evaluation goes left to right: `1 + 2` is `3` first, and only then does `+ "3"` concatenate; but in `"1" + 2 + 3` the text appears first, so everything after joins as text.

## Function deep dive: `Number()`, `parseInt()` and `parseFloat()`

**Why these matter.** Everything a user types arrives as a *string*, whether it comes from `prompt()`, a terminal, or an `<input>` element in Sheet 03. If you add two typed numbers without converting, you concatenate them. These three functions are how text becomes a number.

[[widths 1.1 2.2 2.2 2.2]]
| | `Number(value)` | `parseInt(text, radix)` | `parseFloat(text)` |
|---|---|---|---|
| Parameters | Any value | `text`: string to read. `radix`: base 2 to 36 (use 10) | `text`: string to read |
| Strictness | Strict: whole string must be numeric | Lenient: reads leading digits, stops at first invalid character | Lenient: reads a leading decimal number |
| Returns | A number, or `NaN` | An **integer**, or `NaN` | A number, or `NaN` |
| Decimals | Keeps them | Drops them (truncates) | Keeps them |
| Empty string | `0` | `NaN` | `NaN` |

**How they work, step by step.** `Number()` trims whitespace around the string, then tries to interpret the *entire* remainder as a numeric literal; if any character does not fit, the result is `NaN`. `parseInt()` and `parseFloat()` scan from the left, accept characters while they still form a valid number, and return what they have collected when they hit something else. If not even the first character is valid they return `NaN`. **None of them throws an error**: failure is signalled by the value `NaN`, so you must check for it.

```js file="conversion.js" run
console.log(Number("42"));
console.log(Number("  7 "));
console.log(Number(""));
console.log(Number("12px"));
console.log(parseInt("12px", 10));
console.log(parseInt("3.99", 10));
console.log(parseInt("abc", 10));
console.log(parseFloat("3.14abc"));
console.log(parseInt("101", 2));
console.log(Number.isNaN(Number("hello")));
```

```output
42
7
0
NaN
12
3
NaN
3.14
5
true
```

**Line by line.** Line 2: whitespace around the digits is ignored. Line 3: an empty string becomes `0`, a classic trap (a blank input would silently count as zero). Line 4: `Number` rejects the stray `px`. Line 5: `parseInt` stops at `p` and keeps `12`. Line 6: `parseInt` truncates (it does not round), giving `3`. Line 9: the second argument `2` means "read as binary", so `101` is `5`. Line 10: `Number.isNaN(x)` returns `true` only for the actual value `NaN`.

**Variation: a safe reader.** Combine conversion and validation in one helper.

```js file="safe-number.js" run
function readNumber(text) {
  const cleaned = text.trim();
  if (cleaned === "") {
    return null;
  }
  const value = Number(cleaned);
  return Number.isNaN(value) ? null : value;
}

console.log(readNumber("19.5"));
console.log(readNumber("   "));
console.log(readNumber("19,5"));
```

```output
19.5
null
null
```

Line 2 trims spaces. Lines 3 to 5 reject empty input *before* `Number("")` can turn it into `0`. Line 6 converts. Line 7 returns `null` ("no valid number") when the result is `NaN`, using the ternary operator from Section 5. Callers can now test `if (result === null)`.

## Truthy and falsy values

When a non-boolean appears where a condition is expected, JavaScript converts it with `Boolean()`. Exactly **eight** values become `false` (the *falsy* values): `false`, `0`, `-0`, `0n`, `""`, `null`, `undefined` and `NaN`. **Everything else is truthy**, including some that surprise beginners.

```js file="truthy.js" run
console.log("0:", Boolean(0));
console.log('"":', Boolean(""));
console.log('"0":', Boolean("0"));
console.log('" ":', Boolean(" "));
console.log("[]:", Boolean([]));
console.log("{}:", Boolean({}));
console.log("null:", Boolean(null));
console.log("NaN:", Boolean(NaN));
console.log("-1:", Boolean(-1));
```

```output
0: false
"": false
"0": true
" ": true
[]: true
{}: true
null: false
NaN: false
-1: true
```

The string `"0"` is truthy because it is a non-empty string, and an empty array or object is truthy because it is an object. To test "is this array empty?" you must check `array.length === 0` (Sheet 02).

## Common mistakes in this section

#### Mistake 1: Adding numbers that are really text

**Why it is wrong.** User input is a string, and `+` concatenates when either side is a string.

```js bad run
const first = "10";
const second = "20";
console.log(first + second);
```

```output
1020
```

**Symptom.** No error, just a wrong answer (`1020` instead of `30`). Silent wrong answers are the most dangerous kind.

```js good run
const first = "10";
const second = "20";
console.log(Number(first) + Number(second));
```

```output
30
```

**How to diagnose it yourself.** Print `typeof` for each operand: `console.log(typeof first)`. If it says `"string"` the value needs converting.

#### Mistake 2: Comparing with `NaN`

**Why it is wrong.** `NaN` is the only value in JavaScript not equal to itself, so `=== NaN` is always `false`.

```js bad run
const result = Number("abc");
console.log(result === NaN);
```

```output
false
```

```js good run
const result = Number("abc");
console.log(Number.isNaN(result));
```

```output
true
```

**Symptom.** The check never fires, so invalid input slips through. **Diagnosis:** whenever a calculation prints `NaN`, find the *first* operation that produced it by logging each intermediate value.

#### Mistake 3: Testing for `null` with `typeof`

**Why it is wrong.** `typeof null` is `"object"`, so `typeof value === "object"` is true for `null` too. Code that then reads `value.name` throws `TypeError: Cannot read properties of null`.

```js bad run
const user = null;
console.log(typeof user === "object");
```

```output
true
```

```js good run
const user = null;
console.log(user !== null && typeof user === "object");
```

```output
false
```

**Diagnosis.** The error `Cannot read properties of null (reading 'x')` means a variable you expected to hold an object holds `null`. Log it just before the failing line.

#### Mistake 4: Treating `toFixed()` as a number

**Why it is wrong.** `toFixed` returns a string, so later arithmetic concatenates.

```js bad run
const price = (19.999).toFixed(2);
console.log(price + 1);
```

```output
20.001
```

```js good run
const price = Number((19.999).toFixed(2));
console.log(price + 1);
```

```output
21
```

**Symptom.** `"20.00" + 1` gives the text `"20.001"`. **Diagnosis:** `typeof` again. Format for *display* at the very last step, never before further calculations.

# 5. Operators and Expressions

## Learning objectives for this section

- Use arithmetic, assignment, comparison, logical and ternary operators correctly.
- Explain the difference between `===` and `==`, and always choose `===`.
- Explain short-circuit evaluation and predict the value (not just the truthiness) of `&&` and `||`.
- Predict the result of a mixed expression using operator precedence.

## Conceptual explanation

An **operator** combines values (called *operands*) into a new value. An expression such as `price * quantity` is a small machine: operands go in, a single value comes out. Understanding operators means knowing three things for each one: which types it expects, what it returns, and in which order it is applied relative to its neighbours.

## Arithmetic and assignment operators

[[widths 1 3 2]]
| Operator | Meaning | Example and result |
|---|---|---|
| `+` | Add (or concatenate text) | `7 + 2` gives `9` |
| `-` | Subtract | `7 - 2` gives `5` |
| `*` | Multiply | `7 * 2` gives `14` |
| `/` | Divide (always a decimal result) | `7 / 2` gives `3.5` |
| `%` | Remainder after division | `7 % 2` gives `1` |
| `**` | Exponent | `2 ** 3` gives `8` |
| `++` / `--` | Add or subtract one | `n++`, `n--` |
| `+=`, `-=`, `*=`, `/=` | Compute and assign in one step | `n += 5` means `n = n + 5` |

The remainder operator is more useful than it looks: `n % 2 === 0` tests for even numbers, and `index % length` wraps an index around a list. Integer division does not exist as an operator; use `Math.floor(7 / 2)` which gives `3`.

```js file="arithmetic.js" run
let n = 5;
console.log(n++);
console.log(n);
console.log(++n);
n += 3;
n *= 2;
console.log(n);
console.log(7 % 3, -7 % 3, 2 ** 10);
```

```output
5
6
7
20
1 -1 1024
```

**Line by line.** Line 2 uses *postfix* `n++`: it returns the **old** value (5) and then increments, so `n` becomes 6 (confirmed on line 3). Line 4 uses *prefix* `++n`: it increments first (to 7) and returns the **new** value. Line 5 makes `n` equal to `10` (`7 + 3`), line 6 doubles it to `20`. On the last line, `-7 % 3` is `-1` because the sign of the result follows the left operand.

## Comparison and equality

Comparison operators (`<`, `>`, `<=`, `>=`) produce booleans. For equality there are two pairs, and the difference is important.

- **Strict equality** `===` and `!==`: true only if the values have the **same type and the same value**. No conversion is performed.
- **Loose equality** `==` and `!=`: if the types differ, the engine first converts one or both sides using a long rule list, then compares.

```js file="equality.js" run
console.log(5 === "5");
console.log(5 == "5");
console.log(0 == "");
console.log(0 == "0");
console.log("" == "0");
console.log(null == undefined);
console.log(null === undefined);
console.log(null == 0);
console.log(NaN == NaN);
console.log([] == false);
```

```output
false
true
true
true
false
true
false
false
false
true
```

Lines 3, 4 and 5 expose the inconsistency of loose equality: `0` equals `""` and `0` equals `"0"`, yet `""` does *not* equal `"0"`. Equality that is not transitive is impossible to reason about, which is why the rule for this curriculum is simple: **always use `===` and `!==`**.

::: warning Strings compare character by character
`"10" < "9"` is `true`, because the comparison looks at the first characters (`"1"` comes before `"9"`). Convert to numbers first: `Number("10") < Number("9")` is `false`.
:::

## Logical operators and short-circuiting

| Operator | Name | Behaviour |
|---|---|---|
| `a && b` | AND | If `a` is falsy, returns `a`. Otherwise returns `b`. |
| `a \|\| b` | OR | If `a` is truthy, returns `a`. Otherwise returns `b`. |
| `!a` | NOT | Returns the opposite boolean of `Boolean(a)`. |

Two points surprise beginners. First, `&&` and `||` return one of their **operands**, not necessarily `true` or `false`. Second, they **short-circuit**: if the left operand already decides the result, the right operand is never evaluated.

```js file="logical.js" run
console.log("a" && "b");
console.log(0 && "b");
console.log("" || "default");
console.log(0 || 10);
console.log(!"hello");

let calls = 0;
false && calls++;
true || calls++;
true && calls++;
console.log(calls);
```

```output
b
0
default
10
false
1
```

**Explanation.** `"a" && "b"`: left is truthy so the answer is the right operand, `"b"`. `0 && "b"`: left is falsy, so `0` is returned and `"b"` is ignored. `"" || "default"` is the classic way to supply a fallback. In the counting section, line 8 (`false && calls++`) skips the increment, line 9 (`true || calls++`) skips it as well, and only line 10 (`true && calls++`) evaluates the right side, so `calls` ends at `1`.

## The ternary operator

`condition ? valueIfTrue : valueIfFalse` is an *expression*, so it can appear inside a larger statement.

```js file="ternary.js" run
const age = 17;
const label = age >= 18 ? "adult" : "minor";
console.log(label);
console.log(`You are ${age >= 18 ? "allowed" : "not allowed"} to enter.`);
```

```output
minor
You are not allowed to enter.
```

Line 2 evaluates `age >= 18` (`false`), so the second branch `"minor"` becomes the value. Use a ternary for a simple either/or *value*. If you are tempted to nest one ternary inside another, use `if ... else` instead; readability matters more than brevity.

## Operator precedence

When an expression has several operators, **precedence** decides which is applied first. From highest to lowest (for the operators in this sheet): parentheses `( )`, then `**`, then `* / %`, then `+ -`, then comparisons `< > <= >=`, then `=== !==`, then `&&`, then `||`, then the ternary `? :`, then assignment. `!` binds tighter than all binary operators. When in doubt, add parentheses; they cost nothing and document your intent.

Trace for `2 + 3 * 4 ** 2 > 40 && !false`:

| Step | Sub-expression evaluated | Result | Remaining expression |
|---|---|---|---|
| 1 | `4 ** 2` | `16` | `2 + 3 * 16 > 40 && !false` |
| 2 | `3 * 16` | `48` | `2 + 48 > 40 && !false` |
| 3 | `2 + 48` | `50` | `50 > 40 && !false` |
| 4 | `50 > 40` | `true` | `true && !false` |
| 5 | `!false` | `true` | `true && true` |
| 6 | `true && true` | `true` | final value: `true` |

## Common mistakes in this section

#### Mistake 1: Using `=` where `===` was meant

**Why it is wrong.** `=` assigns; `===` compares. An assignment is also an expression whose value is the assigned value, so the condition silently becomes truthy.

```js bad run
let level = 1;
if (level = 5) {
  console.log("Boss level!");
}
console.log(level);
```

```output
Boss level!
5
```

**Symptom.** The branch always runs *and* the variable has been overwritten.

```js good run
let level = 1;
if (level === 5) {
  console.log("Boss level!");
}
console.log(level);
```

```output
1
```

**How to diagnose it yourself.** Print the variable before and after the `if`. If it changed, you assigned inside the condition. Linters (ESLint) flag this automatically.

#### Mistake 2: Using `||` for defaults when `0` is valid

**Why it is wrong.** `||` replaces *any* falsy left side, including legitimate values such as `0` or `""`.

```js bad run
const savedVolume = 0;
const volume = savedVolume || 50;
console.log(volume);
```

```output
50
```

```js good run
const savedVolume = 0;
const volume = savedVolume === undefined ? 50 : savedVolume;
console.log(volume);
```

```output
0
```

**Symptom.** A user who deliberately chose `0` gets `50`. **Diagnosis:** whenever a default "ignores" a legitimate falsy value, replace `||` with an explicit check. (Sheet 02 introduces `??`, the operator designed for exactly this case.)

#### Mistake 3: Chained comparisons

**Why it is wrong.** `1 < x < 10` is evaluated as `(1 < x) < 10`. The first part is a boolean, which becomes `0` or `1`, and both are less than `10`.

```js bad run
const x = 50;
console.log(1 < x < 10);
```

```output
true
```

```js good run
const x = 50;
console.log(x > 1 && x < 10);
```

```output
false
```

**Diagnosis.** Break an unexpected result into pieces and print each: `console.log(1 < x)` shows `true`, which explains the surprise.

#### Mistake 4: Comparing text numbers

**Why it is wrong.** Strings compare character by character, not by numeric size.

```js bad run
console.log("10" > "9");
```

```output
false
```

```js good run
console.log(Number("10") > Number("9"));
```

```output
true
```

**Diagnosis.** If a numeric comparison gives an impossible answer, check `typeof` on both sides.
