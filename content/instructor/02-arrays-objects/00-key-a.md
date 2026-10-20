---
number: 02
title: Answer Key for Arrays, Objects, and Modern JavaScript
subtitle: Solutions, expected outputs, debugging explanations and reference implementations
track: instructor
kind: instructor
label: INSTRUCTOR ANSWER KEY - SHEET 02
time: Do not distribute to students
edition: Instructor edition
goals:
  - Check answers to comprehension and prediction exercises
  - Compare student code with tested reference solutions
  - Use the debugging explanations when students are stuck
  - Run the reference modules for all five mini projects
---

# 1. How to Use This Key

Every listing with an *Output* panel was **executed by the build validator** and the printed output matches. Reference solutions are one correct approach among several: grade against the acceptance criteria in the student sheet. Each solution is also tested with **frozen input** where relevant, to confirm it does not mutate its arguments.

# 2. Set A: Comprehension Answers

1. Index `4`. Reading index `5` gives `undefined` (no error).
2. Mutating: `push`, `pop`, `splice` (also `shift`, `unshift`, `sort`, `reverse`). Non-mutating: `slice`, `map`, `filter`. `push` returns the **new length**.
3. `const b = a` copies the reference, so both names lead to one array. Real shallow copies: `[...a]` and `a.slice()`.
4. A shallow copy duplicates only the top level; nested objects remain shared. A deep copy duplicates everything. `structuredClone(value)`; it cannot copy functions (it throws).
5. `(value, index, array)`. `map` returns a new array of the same length containing the callback's return values. `forEach` ignores returns and gives `undefined`.
6. A truthy value to keep the element. Returns `[]` when nothing matches.
7. `find` returns `undefined`; `findIndex` returns `-1`.
8. It returns the final accumulator. The callback's return value becomes the accumulator of the next step. Without an initial value an empty array throws, and the first element is used as the start otherwise (which changes the first step).
9. The default sort compares elements as strings, so `"10"` comes before `"9"`. Yes, `sort` mutates the array in place.
10. `a ?? b` falls back only for `null`/`undefined`; `a || b` falls back for every falsy value. They differ when `a` is `0`, `""` or `false`.
11. Spread: `[...x]` and `{ ...x }`. Rest: `...args` in the parameter list.
12. Same inputs give the same output and there are no side effects. React compares references to decide whether state changed, so changing data in place can leave the reference unchanged and skip a re-render.
13. `Map` when keys are not strings or change at runtime (and for `size` and clean iteration); `Set` when you need uniqueness or fast membership tests.
14. Named: `export const x` / `import { x } from "./f.js"` (braces, exact name). Default: `export default v` / `import anyName from "./f.js"` (no braces, importer chooses the name).

# 3. Set B: Predicted Outputs

```js file="b1.js" run
const nums = [1, 2, 3, 4];
console.log(nums.map((n) => n * 2).filter((n) => n > 4));
```

```output
[ 6, 8 ]
```

`map` gives `[2, 4, 6, 8]`; `filter` keeps those above 4.

```js file="b2.js" run
console.log([3, 20, 100].sort());
```

```output
[ 100, 20, 3 ]
```

Default sort compares text: `"100"`, `"20"`, `"3"`.

```js file="b3.js" run
const a = [1, 2, 3];
const b = a;
b.push(4);
console.log(a.length, [...a].length === b.length);
```

```output
4 true
```

`a` and `b` are the same array (length 4); the spread copy has the same length.

```js file="b4.js" run
const { x, y = 5, ...rest } = { x: 1, z: 3, w: 4 };
console.log(x, y, rest);
```

```output
1 5 { z: 3, w: 4 }
```

```js file="b5.js" run
const product = [1, 2, 3, 4].reduce((acc, n) => acc * n, 1);
console.log(product, [].every(Boolean), [0, ""].some(Boolean));
```

```output
24 true false
```

`24`; `every` on an empty array is vacuously `true`; both `0` and `""` are falsy, so `some` is `false`.

```js file="b6.js" run
const user = { profile: null };
console.log(user.profile?.name ?? "n/a", user.profile ?? "none");
```

```output
n/a none
```

```js file="b7.js" run
const s = new Set("hello");
console.log(s.size, [...s].join(""));
```

```output
4 helo
```

A string is iterable letter by letter; the duplicate `l` is dropped.

```js file="b8.js" run
const o = { a: { b: 1 } };
const c = { ...o };
c.a.b = 2;
console.log(o.a.b, o === c);
```

```output
2 false
```

Shallow copy: the nested object is shared, so `o.a.b` is `2`; the top-level objects differ.

# 4. Set C: Reference Solutions

#### C1. `sumOfEvenSquares`

```js file="c1.js" run
function sumOfEvenSquares(numbers) {
  return numbers
    .filter((n) => n % 2 === 0)
    .map((n) => n * n)
    .reduce((sum, n) => sum + n, 0);
}

const input = Object.freeze([1, 2, 3, 4]);
console.log(sumOfEvenSquares(input), sumOfEvenSquares([]), sumOfEvenSquares([1, 3, 5]));
```

```output
20 0 0
```

#### C2. `groupBy`

```js file="c2.js" run
function groupBy(list, keyFn) {
  return list.reduce((groups, item) => {
    const key = keyFn(item);
    const existing = groups[key] ?? [];
    return { ...groups, [key]: [...existing, item] };
  }, {});
}

console.log(JSON.stringify(groupBy(["apple", "avocado", "banana"], (w) => w[0])));
const parity = (n) => (n % 2 === 0 ? "even" : "odd");
console.log(JSON.stringify(groupBy([1, 2, 3, 4], parity)));
console.log(JSON.stringify(groupBy([], (x) => x)));
```

```output
{"a":["apple","avocado"],"b":["banana"]}
{"odd":[1,3],"even":[2,4]}
{}
```

This version is fully immutable (it rebuilds the accumulator each step). Accept a version that mutates the **accumulator** `acc` (which is created inside `reduce`) but not the input list.

#### C3. Immutable todo helpers

```js file="c3.js" run
function addTodo(todos, text) {
  const nextId = Math.max(0, ...todos.map((t) => t.id)) + 1;
  return [...todos, { id: nextId, text, done: false }];
}

function toggleTodo(todos, id) {
  return todos.map((t) => (t.id === id ? { ...t, done: !t.done } : t));
}

function removeTodo(todos, id) {
  return todos.filter((t) => t.id !== id);
}

const empty = Object.freeze([]);
const one = addTodo(empty, "Read");
const two = addTodo(one, "Write");
two.forEach((t) => Object.freeze(t));
Object.freeze(two);

console.log(two.map((t) => t.id).join(","), two.every((t) => t.done === false));
const toggled = toggleTodo(two, 2);
console.log(toggled[0] === two[0], toggled[1].done, two[1].done);
console.log(removeTodo(two, 1).length, removeTodo(two, 99).length);
```

```output
1,2 true
true true false
1 2
```

`Math.max(0, ...ids)` handles the empty list (it would otherwise give `-Infinity`).

#### C4. `uniqueSorted`

```js file="c4.js" run
function uniqueSorted(values) {
  return [...new Set(values)].sort((a, b) =>
    typeof a === "number" && typeof b === "number"
      ? a - b
      : String(a).localeCompare(String(b))
  );
}

const input = Object.freeze([3, 1, 3, 10, 2, 1]);
console.log(uniqueSorted(input));
console.log(uniqueSorted(["pear", "apple", "pear"]));
```

```output
[ 1, 2, 3, 10 ]
[ 'apple', 'pear' ]
```

#### C5. `topN`

```js file="c5.js" run
function topN(items, key, n) {
  return [...items].sort((a, b) => b[key] - a[key]).slice(0, n);
}

const items = Object.freeze([
  { name: "A", score: 5 },
  { name: "B", score: 9 },
  { name: "C", score: 7 },
]);
console.log(topN(items, "score", 2).map((i) => i.name).join(""));
console.log(topN(items, "score", 10).length, topN(items, "score", 0));
console.log(items.map((i) => i.name).join(""));
```

```output
BC
3 []
ABC
```

#### C6. `pick`

```js file="c6.js" run
function pick(object, keys) {
  return keys.reduce((result, key) => {
    return key in object ? { ...result, [key]: object[key] } : result;
  }, {});
}

console.log(pick({ a: 1, b: 2, c: 3 }, ["a", "c"]));
console.log(pick({ a: 1 }, ["a", "zzz"]));
console.log(pick({ a: 1 }, []));
```

```output
{ a: 1, c: 3 }
{ a: 1 }
{}
```

# 5. Set D: Debugging Explanations

**D1.** The block-bodied arrow function has no `return`, so every element becomes `undefined`.

```js file="d1-fixed.js" run
const prices = [10, 20, 30];
const withTax = prices.map((p) => p * 1.2);
console.log(withTax);
```

```output
[ 12, 24, 36 ]
```

**D2.** `sort()` without a comparator orders text-wise, and it **mutates** `scores`. Fix: copy, then compare numerically.

```js file="d2-fixed.js" run
const scores = [70, 9, 100, 25];
const ranked = [...scores].sort((a, b) => b - a);
console.log(ranked, scores);
```

```output
[ 100, 70, 25, 9 ] [ 70, 9, 100, 25 ]
```

**D3.** Spread is shallow: `a.panel`, `b.panel` and `base.panel` are one object. Copy the nested level that changes.

```js file="d3-fixed.js" run
const base = { theme: "dark", panel: { open: true } };
const a = { ...base, panel: { ...base.panel } };
const b = { ...base };
a.panel.open = false;
console.log(base.panel.open, b.panel.open);
```

```output
true true
```

**D4.** `find` returns `undefined` for id 3, and `.name` of `undefined` throws.

```js file="d4-fixed.js" run
const users = [
  { id: 1, name: "Asha" },
  { id: 2, name: "Meera" },
];
function nameOf(id) {
  const user = users.find((u) => u.id === id);
  return user ? user.name : "Unknown";
}
console.log(nameOf(1), nameOf(3));
```

```output
Asha Unknown
```

**D5.** The callback has braces but no `return`, so the accumulator becomes `undefined` after the first step.

```js file="d5-fixed.js" run
const cart = [{ price: 10 }, { price: 25 }, { price: 5 }];
const total = cart.reduce((sum, item) => sum + item.price, 0);
console.log(total);
```

```output
40
```

# 6. Set E: Challenge Solutions

#### E1. `summarize`

```js file="e1.js" run
function summarize(transactions) {
  const grand = transactions.reduce((sum, t) => sum + t.amountCents, 0);
  const byCategory = transactions.reduce((map, t) => {
    const fresh = { category: t.category, totalCents: 0, count: 0 };
    const current = map.get(t.category) ?? fresh;
    return map.set(t.category, {
      ...current,
      totalCents: current.totalCents + t.amountCents,
      count: current.count + 1,
    });
  }, new Map());

  return [...byCategory.values()]
    .map((c) => {
      const sharePercent = Math.round((c.totalCents / grand) * 1000) / 10;
      return { ...c, sharePercent };
    })
    .sort(
      (a, b) => b.totalCents - a.totalCents || a.category.localeCompare(b.category)
    );
}

const line = (r) => `${r.category} ${r.totalCents} ${r.count} ${r.sharePercent}`;
const show = (rows) => rows.map(line).join("\n");

console.log(
  show(
    summarize([
      { category: "food", amountCents: 500 },
      { category: "rent", amountCents: 1500 },
      { category: "food", amountCents: 500 },
    ])
  )
);
console.log(summarize([]));
console.log(
  show(
    summarize([
      { category: "a", amountCents: 100 },
      { category: "b", amountCents: 100 },
      { category: "c", amountCents: 100 },
    ])
  )
);
```

```output
rent 1500 1 60
food 1000 2 40
[]
a 100 1 33.3
b 100 1 33.3
c 100 1 33.3
```

The empty list never divides by zero because `map` over an empty array never runs the percentage calculation.

#### E2. Least-recently-used cache

```js file="e2.js" run
function createCache(limit) {
  const entries = new Map();
  return {
    get(key) {
      if (!entries.has(key)) {
        return undefined;
      }
      const value = entries.get(key);
      entries.delete(key);
      entries.set(key, value);
      return value;
    },
    set(key, value) {
      if (entries.has(key)) {
        entries.delete(key);
      } else if (entries.size >= limit) {
        const oldest = entries.keys().next().value;
        entries.delete(oldest);
      }
      entries.set(key, value);
    },
    size() {
      return entries.size;
    },
  };
}

const cache = createCache(2);
cache.set("a", 1);
cache.set("b", 2);
cache.get("a");
cache.set("c", 3);
console.log(cache.get("a"), cache.get("b"), cache.get("c"), cache.size());
cache.set("a", 10);
console.log(cache.get("a"), cache.size());
```

```output
1 undefined 3 2
10 2
```

The key idea is that a `Map` iterates in insertion order, so re-inserting a key on every read moves it to the "newest" end, and the first key is always the least recently used.
