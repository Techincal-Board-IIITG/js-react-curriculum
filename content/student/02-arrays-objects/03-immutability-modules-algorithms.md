# 7. Pure Functions and Immutability

## Learning objectives for this section

- Define a pure function and a side effect, and recognise both in code.
- Update arrays and objects **without mutating** them: add, remove, update, and update nested data.
- Explain why React depends on this habit.

## Conceptual explanation

A **pure function** has two properties: given the same arguments it always returns the same result, and it has **no side effects** (it does not change anything outside itself, including the arguments it was given). `price * quantity` is pure. A function that pushes onto an array you passed in, writes to a global variable, or prints, has side effects.

Why care? Pure functions are easy to test (inputs and outputs only), easy to reason about, and safe to call more than once. **Immutability** is the matching habit for data: instead of changing an object or array, you create a **new** one with the change applied and leave the old one untouched. The old value stays valid, so nothing that holds a reference to it is surprised.

React depends on this. React decides whether a component needs to re-render by checking whether state is a **different reference** from before. If you mutate an array and hand React the same array back, the reference is unchanged and React sees "no change". You will meet this directly in Sheet 06.

## Worked example: impure versus pure

```js file="pure-impure.js" run
function addItemImpure(list, item) {
  list.push(item);
  return list;
}

function addItem(list, item) {
  return [...list, item];
}

const cart = ["pen"];
const result = addItemImpure(cart, "book");
console.log(cart, result === cart);

const cart2 = ["pen"];
const result2 = addItem(cart2, "book");
console.log(cart2, result2);
```

```output
[ 'pen', 'book' ] true
[ 'pen' ] [ 'pen', 'book' ]
```

**Line by line.** `addItemImpure` changes its argument: after the call, `cart` itself holds two items, and the returned value *is* the same array (`result === cart`). Any other code holding `cart` has had it changed behind its back. `addItem` builds a new array with spread and leaves `cart2` untouched, so the caller decides what to do with the result.

## Immutable update recipes

[[widths 1.1 2.6 2.2]]
| Task | Immutable pattern | Avoid (mutates) |
|---|---|---|
| Add to an array | `[...list, item]` | `push`, `unshift`, `splice` |
| Remove from an array | `list.filter((x) => x.id !== id)` | `splice`, `pop`, `shift` |
| Change one item | `list.map((x) => x.id === id ? { ...x, done: true } : x)` | `list[i].done = true` |
| Sort or reverse | `[...list].sort(compare)` | `list.sort()`, `list.reverse()` |
| Change an object field | `{ ...obj, name: "New" }` | `obj.name = "New"` |
| Change a nested field | `{ ...obj, user: { ...obj.user, name: "New" } }` | `obj.user.name = "New"` |

```js file="immutable-updates.js" run
const todos = [
  { id: 1, text: "Read", done: false },
  { id: 2, text: "Write", done: false },
];

const added = [...todos, { id: 3, text: "Test", done: false }];
const removed = todos.filter((t) => t.id !== 1);
const toggled = todos.map((t) => (t.id === 2 ? { ...t, done: !t.done } : t));

console.log(todos.length, added.length, removed.length);
console.log(toggled[1].done, todos[1].done);
console.log(toggled[0] === todos[0], toggled[1] === todos[1]);

const state = { user: { name: "Asha", city: "Pune" }, theme: "light" };
const next = { ...state, user: { ...state.user, name: "Meera" } };
console.log(state.user.name, next.user.name, next.user.city, next.theme);
```

```output
2 3 1
true false
true false
Asha Meera Pune light
```

**Explanation.** `added`, `removed` and `toggled` are all new arrays; `todos` still has its two original items (line 9 prints `2 3 1`). In `toggled`, only the item with `id` 2 is *replaced* by a copy with `done` flipped; line 10 shows the new copy has `true` while the original still has `false`. Line 11 is the subtle part: the **unchanged** item is the very same object (`toggled[0] === todos[0]` is `true`) because `map` returned `t` itself, while the changed item is a new object (`false`). This sharing is safe because nobody mutates anything. Lines 13 to 15 update a nested field: you must copy **every level on the path** to the change (`state`, then `state.user`); everything else is reused.

## Optional deep dive: `Object.freeze`

`Object.freeze(obj)` makes an object's own properties read-only, which can catch accidental mutation. It is **shallow**: nested objects stay changeable. In modules (strict mode) assigning to a frozen property throws.

```js file="freeze.js" run
const config = Object.freeze({ theme: "light", panel: { open: true } });

try {
  config.theme = "dark";
} catch (error) {
  console.log(error.name);
}

config.panel.open = false;
console.log(config.theme, config.panel.open, Object.isFrozen(config.panel));
```

```output
TypeError
light false false
```

## Common mistakes in this section

#### Mistake 1: A function that changes its argument

**Why it is wrong.** The caller's data changes unexpectedly, so a function called twice can give different results.

```js bad run
function addTax(prices) {
  for (let i = 0; i < prices.length; i++) {
    prices[i] = prices[i] * 1.2;
  }
  return prices;
}
const base = [100, 200];
addTax(base);
console.log(addTax(base));
```

```output
[ 144, 288 ]
```

```js good run
function addTax(prices) {
  return prices.map((p) => p * 1.2);
}
const base = [100, 200];
addTax(base);
console.log(addTax(base), base);
```

```output
[ 120, 240 ] [ 100, 200 ]
```

**Symptom.** Tax applied twice, because the first call corrupted the input. **Diagnosis:** print the input array before and after calling the function; if it changed, the function mutates.

#### Mistake 2: Mutating and then expecting a "change" to be detected

**Why it is wrong.** Detection by reference sees the same array.

```js bad run
const before = [1, 2];
const after = before;
after.push(3);
console.log(before === after);
```

```output
true
```

```js good run
const before = [1, 2];
const after = [...before, 3];
console.log(before === after, before, after);
```

```output
false [ 1, 2 ] [ 1, 2, 3 ]
```

**Symptom (in React).** The screen does not update after you change state. **Diagnosis:** compare old and new with `===`; `true` means you handed back the same reference.

#### Mistake 3: Reversing or sorting the original

**Why it is wrong.** `reverse()` and `sort()` change the array in place *and* return it.

```js bad run
const items = [1, 2, 3];
const reversed = items.reverse();
console.log(items === reversed, items);
```

```output
true [ 3, 2, 1 ]
```

```js good run
const items = [1, 2, 3];
const reversed = [...items].reverse();
console.log(items, reversed);
```

```output
[ 1, 2, 3 ] [ 3, 2, 1 ]
```

**Symptom.** The original list is mysteriously reordered. **Diagnosis:** `true` from `items === reversed` proves the "result" is the original.

#### Mistake 4: Copying only the top level of nested data

**Why it is wrong.** Spread is shallow (Section 3).

```js bad run
const state = { user: { name: "Asha" } };
const next = { ...state };
next.user.name = "Meera";
console.log(state.user.name);
```

```output
Meera
```

```js good run
const state = { user: { name: "Asha" } };
const next = { ...state, user: { ...state.user, name: "Meera" } };
console.log(state.user.name, next.user.name);
```

```output
Asha Meera
```

**Symptom.** Changing "the new state" also changes the old. **Diagnosis:** compare nested references: `state.user === next.user` is `true` for the bad version.

# 8. ES Modules

## Learning objectives for this section

- Split a program into files and connect them with `export` and `import`.
- Distinguish named exports from default exports and use each correctly.
- Run modules in Node.js and in the browser.

## Conceptual explanation

A single file of 2000 lines is hard to read and impossible to reuse. A **module** is a file with its own private scope. Nothing inside it is visible to other files unless it is **exported**, and a file can only use another file's code if it **imports** it. This keeps names from colliding and makes each file responsible for one thing. React projects consist of hundreds of small modules (one component per file), so this syntax appears at the top of every file you write from Sheet 05 onward.

## Syntax

```text
// math.js: named exports (as many as you like)
export function add(a, b) { return a + b; }
export const PI = 3.14159;

// format.js: one default export (at most one per file)
export default function formatPrice(value) { ... }

// main.js: importing
import { add, PI } from "./math.js";          // named: braces, exact names
import formatPrice from "./format.js";        // default: no braces, any name
import { add as sum } from "./math.js";       // rename on import
import * as math from "./math.js";            // everything as one object: math.add(...)
```

| Form | Export side | Import side | Name rules |
|---|---|---|---|
| Named | `export const x`, `export function f` | `import { x, f } from "./file.js"` | Must match the exported names (rename with `as`) |
| Default | `export default value` | `import anyName from "./file.js"` | Importer chooses the name |
| Namespace | n/a | `import * as ns from "./file.js"` | Access as `ns.x`, `ns.default` |

## A complete multi-file example

```tree
js-modules/
├── math.js
├── format.js
└── main.js
```

```js file="math.js"
export function add(a, b) {
  return a + b;
}

export function multiply(a, b) {
  return a * b;
}

export const TAX_RATE = 0.2;
```

```js file="format.js"
export default function formatPrice(value) {
  return "$" + value.toFixed(2);
}
```

```js file="main.js"
import { add, multiply, TAX_RATE } from "./math.js";
import formatPrice from "./format.js";

const subtotal = add(multiply(2, 50), 20);
const total = subtotal * (1 + TAX_RATE);

console.log(formatPrice(subtotal));
console.log(formatPrice(total));
```

```output
$120.00
$144.00
```

**How the files connect.** `math.js` exports two functions and a constant by name. `format.js` exports one function as its default. `main.js` imports the named items inside braces (names must match exactly) and imports the default without braces (the name `formatPrice` is chosen by the importer, and happens to match). Then `main.js` runs: `multiply(2, 50)` is `100`, `add(100, 20)` is `120`, and the total with 20 percent tax is `144`. Run it with `node main.js` after naming the files `.mjs` (for example `main.mjs`, importing `./math.mjs`) or after adding a `package.json` containing `{ "type": "module" }` in that folder. Imports in Node.js and in browsers must include the **file extension** and a leading `./` for local files.

**What modules guarantee.** Each module runs **once**, the first time it is imported, and the result is shared by every importer. Variables inside a module are private unless exported. Modules always run in strict mode.

## Running modules in the browser

Add `type="module"` to the script tag:

```html file="index.html"
<script type="module" src="main.js"></script>
```

Browsers refuse to load modules from a page opened as a `file://` address (a security rule), so serve the folder over HTTP. A simple way is to run `npx serve` in the folder, or use Vite, which Sheet 05 introduces and which also removes the need to write file extensions yourself.

## Named or default?

Prefer **named exports** for utilities (`add`, `formatDate`) because the name is fixed and editors can auto-import them. Use a **default export** for the one main thing a file provides; in React that is the component. A common rule: one default export per component file, named exports for helpers.

## Common mistakes in this section

#### Mistake 1: Importing a named export without braces

**Why it is wrong.** Without braces the import asks for the **default** export, and `math.js` has none.

```js bad nocheck
import add from "./math.js";
```

**Symptom.** A `SyntaxError` saying the requested module does not provide an export named `default`.

```js good nocheck
import { add } from "./math.js";
```

**How to diagnose it yourself.** Open the exporting file and look at how the name is exported: `export function add` needs braces, `export default` does not.

#### Mistake 2: Forgetting the file extension or `./`

**Why it is wrong.** Node.js and browsers do not guess extensions for ES modules, and a path without `./` is treated as a package name.

```js bad nocheck
import { add } from "./math";
import { add } from "math.js";
```

**Symptom.** `ERR_MODULE_NOT_FOUND` in Node.js, or a 404 request in the browser's Network tab.

```js good nocheck
import { add } from "./math.js";
```

**Diagnosis.** Compare the path character by character with the real file name and location. (Build tools such as Vite let you omit extensions for your own files, but writing them is never wrong.)

#### Mistake 3: Mixing `require` with `import`

**Why it is wrong.** `require` belongs to the older CommonJS system. In an ES module it does not exist.

```js bad nocheck
const { add } = require("./math.js");
```

**Symptom.** A `ReferenceError` saying `require` is not defined in ES module scope.

```js good nocheck
import { add } from "./math.js";
```

**Diagnosis.** If you see this message, decide which system your project uses: `.mjs` or `"type": "module"` means ES modules, so use `import`.

#### Mistake 4: Opening a module page straight from disk

**Why it is wrong.** Browsers block module loading from `file://` addresses.

**Symptom.** The console shows a CORS error such as "has been blocked by CORS policy" and your script does nothing.

**Fix and diagnosis.** Serve the folder (`npx serve`, a VS Code live server extension, or Vite). Check the address bar: it should start with `http://localhost`, not `file://`.

# 9. Algorithmic Thinking with Arrays and Objects

## Learning objectives for this section

- Apply a repeatable method to turn a problem statement into working code.
- Recognise three reusable patterns: counting, lookup tables, and nested comparison.
- Test with edge cases and explain, roughly, how work grows with input size.

## Conceptual explanation

Knowing syntax is not the same as knowing how to solve a problem. An **algorithm** is a precise sequence of steps that solves a problem. Programmers get better by following a routine, not by waiting for inspiration:

1. **Restate** the problem in your own words and identify the inputs and the output.
2. **Write examples**, including an empty input and an awkward one, with the expected answers.
3. **Describe a solution in plain words** before writing any code.
4. **Code it** in small pieces, printing intermediate values.
5. **Test** with your examples; then think of inputs that could break it.
6. **Improve** only after it works: is there a simpler or faster way?

## Worked problem 1: find duplicates

*Input:* an array of numbers. *Output:* an array of the values that appear more than once, each listed once.

*Plan in words:* walk through the numbers; remember the ones already seen; if a number is already in "seen", record it as a duplicate.

```js file="duplicates.js" run
function findDuplicates(numbers) {
  const seen = new Set();
  const duplicates = new Set();
  for (const n of numbers) {
    if (seen.has(n)) {
      duplicates.add(n);
    }
    seen.add(n);
  }
  return [...duplicates];
}

console.log(findDuplicates([1, 2, 3, 2, 4, 1, 2]));
console.log(findDuplicates([]));
console.log(findDuplicates([5, 6, 7]));
```

```output
[ 2, 1 ]
[]
[]
```

`seen` remembers every number; `duplicates` collects repeats and, being a `Set`, lists each once. Trace for `[1, 2, 3, 2, 4, 1, 2]`: 1, 2 and 3 are new; the second `2` is already seen, so it is a duplicate; 4 is new; the second `1` is a duplicate (added after `2`, so the result is `[2, 1]`); the third `2` is already recorded. Note how the empty array and the no-duplicates array both return `[]` without special code.

## Worked problem 2: two numbers that add up to a target

*Input:* an array of numbers and a target. *Output:* the indexes of two different elements whose sum equals the target, or `null`.

**First idea (brute force): compare every pair.**

```js file="two-sum-brute.js" run
function twoSumBrute(numbers, target) {
  for (let i = 0; i < numbers.length; i++) {
    for (let j = i + 1; j < numbers.length; j++) {
      if (numbers[i] + numbers[j] === target) {
        return [i, j];
      }
    }
  }
  return null;
}

console.log(twoSumBrute([2, 7, 11, 15], 9));
console.log(twoSumBrute([3, 3], 6));
console.log(twoSumBrute([1, 2], 10));
```

```output
[ 0, 1 ]
[ 0, 1 ]
null
```

Starting the inner loop at `j = i + 1` avoids pairing an element with itself and avoids checking each pair twice.

**Second idea (lookup table): remember what you have seen.** For each number, the partner you need is `target - number`. If you have already seen that partner, you are done.

```js file="two-sum-map.js" run
function twoSum(numbers, target) {
  const seenAt = new Map();
  for (let i = 0; i < numbers.length; i++) {
    const needed = target - numbers[i];
    if (seenAt.has(needed)) {
      return [seenAt.get(needed), i];
    }
    seenAt.set(numbers[i], i);
  }
  return null;
}

console.log(twoSum([2, 7, 11, 15], 9));
console.log(twoSum([3, 3], 6));
console.log(twoSum([1, 2], 10));
```

```output
[ 0, 1 ]
[ 0, 1 ]
null
```

**Comparing the two.** The brute-force version has a loop inside a loop: for 1000 numbers it examines up to about 500,000 pairs; for 100,000 numbers, about five billion. The `Map` version has a single loop: 1000 numbers means about 1000 steps, because a `Map` lookup does not scan. Programmers describe this as *growth rate*: nested loops grow with the **square** of the input, one loop grows in direct proportion. You do not need the formal notation yet, but you should notice nested loops over the same data and ask whether a lookup table could replace the inner loop.

## Worked problem 3: are two words anagrams?

```js file="anagram.js" run
function letterCounts(word) {
  const counts = {};
  for (const ch of word.toLowerCase()) {
    counts[ch] = (counts[ch] ?? 0) + 1;
  }
  return counts;
}

function isAnagram(a, b) {
  if (a.length !== b.length) {
    return false;
  }
  const countsA = letterCounts(a);
  const countsB = letterCounts(b);
  for (const letter of Object.keys(countsA)) {
    if (countsA[letter] !== countsB[letter]) {
      return false;
    }
  }
  return true;
}

console.log(isAnagram("Listen", "Silent"), isAnagram("apple", "pale"));
console.log(isAnagram("rat", "car"), isAnagram("", ""));
```

```output
true false
false true
```

The pattern is **counting**: reduce each word to a table of letter frequencies, then compare the tables. The length check up front is a cheap early exit. If the lengths match and every letter count in `a` equals the count in `b`, no letter can be left over in `b`.

## Common mistakes in this section

#### Mistake 1: Not testing the empty input

**Why it is wrong.** Many built-in helpers have surprising results on empty data.

```js bad run
const scores = [];
console.log(Math.max(...scores));
```

```output
-Infinity
```

```js good run
const scores = [];
const best = scores.length === 0 ? null : Math.max(...scores);
console.log(best);
```

```output
null
```

**Symptom.** `-Infinity` or `NaN` flowing into later calculations. **Diagnosis:** always run your function with `[]`, one element, and duplicates before trusting it.

#### Mistake 2: Starting the inner loop at zero

**Why it is wrong.** It pairs an element with itself and counts every pair twice.

```js bad run
const nums = [5, 5];
let pairs = 0;
for (let i = 0; i < nums.length; i++) {
  for (let j = 0; j < nums.length; j++) {
    if (nums[i] + nums[j] === 10) pairs++;
  }
}
console.log(pairs);
```

```output
4
```

```js good run
const nums = [5, 5];
let pairs = 0;
for (let i = 0; i < nums.length; i++) {
  for (let j = i + 1; j < nums.length; j++) {
    if (nums[i] + nums[j] === 10) pairs++;
  }
}
console.log(pairs);
```

```output
1
```

**Symptom.** Counts are too high (here `4` instead of `1`). **Diagnosis:** log `i` and `j` for each comparison on a tiny input.

#### Mistake 3: Writing code before understanding the examples

**Why it is wrong.** If you cannot say what the output is for three inputs by hand, you cannot know whether your code is right. **Symptom:** you rewrite the same function repeatedly. **Fix:** write three input/output pairs in comments first, and make them your tests.

**Diagnosis.** When stuck, explain the problem and your plan aloud to someone (or something) else, without looking at code.

#### Mistake 4: Optimising before it works

**Why it is wrong.** A clever but wrong solution is worse than a slow correct one. **Symptom:** a half-finished tricky version nobody understands. **Fix:** write the brute-force solution first, confirm it passes your examples, then improve it while *keeping those examples as a check*.

**Diagnosis.** Keep the old version; run both on the same inputs and compare the answers.
