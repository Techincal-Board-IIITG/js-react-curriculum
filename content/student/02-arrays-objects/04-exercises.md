# 10. Exercises

## Exercises overview and rules

Five sets, ordered from recall to independent problem solving. Complete sets A to D in full; for set E, complete at least one challenge. Solutions are in the instructor key, not here. Use the acceptance criteria: write the listed calls as `console.log` lines under your function and compare with the expected results.

::: tip Never mutate the input
Unless an exercise says otherwise, a function must **not change** the arrays or objects it receives. A good habit: wrap test data in `Object.freeze` (arrays too) and see whether your function still works. Frozen data throws in a module if you try to change it.
:::

Work in `js-arrays/exercises/`, one file per exercise. Name files `.mjs` if you use `import`.

## Set A: Comprehension questions

1. What is the index of the last element of an array of length 5? What does reading index 5 give?
2. Which of `push`, `pop`, `slice`, `splice`, `map`, `filter` change the original array? What does `push` return?
3. Why does `const b = a` not copy an array? Give two ways to make a real (shallow) copy.
4. What is the difference between a shallow and a deep copy? Name a built-in way to make a deep copy and one of its limits.
5. State the three arguments a `map` callback receives, and what `map` returns. How does `map` differ from `forEach`?
6. What must a `filter` callback return? What does `filter` return when nothing matches?
7. What do `find` and `findIndex` return when nothing matches?
8. What does `reduce` return, and what happens to the callback's return value on each step? Why should you always pass an initial value?
9. Why does `[10, 9, 1].sort()` not give `[1, 9, 10]`? Does `sort` change the original array?
10. What is the difference between `a ?? b` and `a || b`? Give a value of `a` where they differ.
11. In `[...x]`, `{ ...x }` and `function f(...args)`, which dots are spread and which are rest?
12. What is a pure function? Why does React care about immutable updates?
13. When would you pick a `Map` over a plain object? A `Set` over an array?
14. What is the difference between a named export and a default export, and how is each imported?

## Set B: Syntax and output prediction

Write the exact output **before** running. Then run it and explain any mismatch.

**B1.**

```js file="b1.js"
const nums = [1, 2, 3, 4];
console.log(nums.map((n) => n * 2).filter((n) => n > 4));
```

**B2.**

```js file="b2.js"
console.log([3, 20, 100].sort());
```

**B3.**

```js file="b3.js"
const a = [1, 2, 3];
const b = a;
b.push(4);
console.log(a.length, [...a].length === b.length);
```

**B4.**

```js file="b4.js"
const { x, y = 5, ...rest } = { x: 1, z: 3, w: 4 };
console.log(x, y, rest);
```

**B5.**

```js file="b5.js"
const product = [1, 2, 3, 4].reduce((acc, n) => acc * n, 1);
console.log(product, [].every(Boolean), [0, ""].some(Boolean));
```

**B6.**

```js file="b6.js"
const user = { profile: null };
console.log(user.profile?.name ?? "n/a", user.profile ?? "none");
```

**B7.**

```js file="b7.js"
const s = new Set("hello");
console.log(s.size, [...s].join(""));
```

**B8.**

```js file="b8.js"
const o = { a: { b: 1 } };
const c = { ...o };
c.a.b = 2;
console.log(o.a.b, o === c);
```

## Set C: Small implementation exercises

#### C1. `sumOfEvenSquares(numbers)`

**Problem.** Return the sum of the squares of the even numbers in an array, using `filter`, `map` and `reduce` (no loops).

**Acceptance criteria.**

- `sumOfEvenSquares([1, 2, 3, 4])` returns `20`.
- `sumOfEvenSquares([])` and `sumOfEvenSquares([1, 3, 5])` return `0`.
- The input array is not changed.

**Hint.** Chain three methods; give `reduce` an initial value so the empty case works.

#### C2. `groupBy(list, keyFn)`

**Problem.** Return an object whose keys are the values produced by `keyFn(item)` and whose values are arrays of the items with that key, in original order.

**Acceptance criteria.**

- `groupBy(["apple", "avocado", "banana"], (w) => w[0])` returns `{ a: ["apple", "avocado"], b: ["banana"] }`.
- `groupBy([1, 2, 3, 4], (n) => (n % 2 === 0 ? "even" : "odd"))` returns `{ odd: [1, 3], even: [2, 4] }`.
- `groupBy([], (x) => x)` returns `{}`.

**Hint.** `reduce` with `{}` as the initial value. If `acc[key]` does not exist yet, create it with `[]`.

#### C3. Immutable todo helpers

**Problem.** Write `addTodo(todos, text)`, `toggleTodo(todos, id)` and `removeTodo(todos, id)`. A todo is `{ id, text, done }`. New ids are one greater than the current maximum id (or `1` for an empty list).

**Acceptance criteria.**

- Starting from `[]`, `addTodo` twice gives ids `1` and `2`, both `done: false`.
- `toggleTodo` flips `done` for the matching id only; unchanged todos are the **same objects** as before (`===`).
- `removeTodo` removes only the matching id; an unknown id returns an equal list.
- None of the three changes its input (test with frozen arrays and frozen objects).

**Hint.** Spread, `map` and `filter`. For the next id, think about what `Math.max` does with an empty list.

#### C4. `uniqueSorted(values)`

**Problem.** Return a new array of the distinct values in ascending order. Work for numbers and for strings.

**Acceptance criteria.**

- `uniqueSorted([3, 1, 3, 10, 2, 1])` returns `[1, 2, 3, 10]` (numeric order, not alphabetical).
- `uniqueSorted(["pear", "apple", "pear"])` returns `["apple", "pear"]`.
- The input array is not changed.

**Hint.** `Set`, spread, and a comparator that handles both types (`typeof` can choose).

#### C5. `topN(items, key, n)`

**Problem.** Return the `n` items with the highest value of `item[key]`, largest first. Ties keep their original relative order.

**Acceptance criteria.**

- With `[{ name: "A", score: 5 }, { name: "B", score: 9 }, { name: "C", score: 7 }]`, `topN(items, "score", 2)` returns the objects for B then C.
- `topN(items, "score", 10)` returns all three items; `topN(items, "score", 0)` returns `[]`.
- The input is not reordered.

**Hint.** Copy before sorting; then `slice`.

#### C6. `pick(object, keys)`

**Problem.** Return a new object containing only the listed keys that exist in `object`.

**Acceptance criteria.**

- `pick({ a: 1, b: 2, c: 3 }, ["a", "c"])` returns `{ a: 1, c: 3 }`.
- `pick({ a: 1 }, ["a", "zzz"])` returns `{ a: 1 }` (no `zzz: undefined` key).
- `pick({ a: 1 }, [])` returns `{}`.

**Hint.** `reduce` over the keys, or `Object.fromEntries` with `filter` and `map`. Check key existence with `in`.

## Set D: Debugging exercises

Apply the debugging routine from Sheet 01: evidence, hypothesis, observation, one fix, explanation.

**D1. The empty prices.**

```js file="d1.js"
const prices = [10, 20, 30];
const withTax = prices.map((p) => {
  p * 1.2;
});
console.log(withTax);
```

*Expected:* `[ 12, 24, 36 ]`.

**D2. The unsorted scores.**

```js file="d2.js"
const scores = [70, 9, 100, 25];
const ranked = scores.sort().reverse();
console.log(ranked, scores);
```

*Expected:* `ranked` is `[ 100, 70, 25, 9 ]` and `scores` is **unchanged**.

**D3. The settings that changed twice.**

```js file="d3.js"
const base = { theme: "dark", panel: { open: true } };
const a = { ...base };
const b = { ...base };
a.panel.open = false;
console.log(base.panel.open, b.panel.open);
```

*Expected:* `true true` (`base` and `b` must not be affected).

**D4. The crashing lookup.**

```js file="d4.js"
const users = [
  { id: 1, name: "Asha" },
  { id: 2, name: "Meera" },
];
function nameOf(id) {
  return users.find((u) => u.id === id).name;
}
console.log(nameOf(1), nameOf(3));
```

*Expected:* `Asha Unknown`.

**D5. The total that vanished.**

```js file="d5.js"
const cart = [{ price: 10 }, { price: 25 }, { price: 5 }];
const total = cart.reduce((sum, item) => {
  sum + item.price;
}, 0);
console.log(total);
```

*Expected:* `40`.

## Set E: Challenges

#### E1. Transaction summary

**Problem.** Write `summarize(transactions)`. Each transaction is `{ category, amountCents }`. Return an array of `{ category, totalCents, count, sharePercent }`, sorted by `totalCents` descending (ties: alphabetical by category). `sharePercent` is the category's share of the grand total rounded to one decimal place.

**Acceptance criteria.**

- For `[{ category: "food", amountCents: 500 }, { category: "rent", amountCents: 1500 }, { category: "food", amountCents: 500 }]` the result lists `rent` first (`totalCents: 1500`, `count: 1`, `sharePercent: 60`) then `food` (`totalCents: 1000`, `count: 2`, `sharePercent: 40`).
- An empty list returns `[]` and does not divide by zero.
- Percentages are rounded numbers (`33.3`), not strings.
- The input is not changed, and no loops with indexes are used.

#### E2. A small cache that forgets the oldest entry

**Problem.** Write `createCache(limit)` returning an object with `get(key)`, `set(key, value)` and `size()`. The cache holds at most `limit` entries. When a new key is added to a full cache, the **least recently used** entry is removed. Reading a key with `get` counts as using it.

**Acceptance criteria.**

- With `limit` 2: set `a`, set `b`, `get("a")`, set `c`: now `b` has been evicted, `get("a")` and `get("c")` work, `get("b")` returns `undefined`.
- Setting an existing key updates its value and marks it as most recently used, without growing the size.
- `size()` never exceeds `limit`.
- Hint for thinking (not code): a `Map` remembers insertion order, and deleting then re-adding a key moves it to the end.
