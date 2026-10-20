# 5. Modern Syntax: Destructuring, Spread, Rest and Safer Access

## Learning objectives for this section

- Unpack arrays and objects with destructuring, including renaming and defaults.
- Copy, merge and expand with spread; collect with rest.
- Build strings with template literals.
- Use optional chaining (`?.`) and nullish coalescing (`??`), and explain how `??` differs from `||`.

## Conceptual explanation

These features add no new abilities; they make common operations shorter and clearer. They matter for this curriculum because React code uses them on almost every line: props are destructured, state is copied with spread, and optional chaining guards data that has not loaded yet.

## Destructuring

**What it is.** Syntax that unpacks values from an array or properties from an object into separate variables in one statement.

**Syntax.** The pattern on the left mirrors the shape of the data on the right.

```text
const [a, b, ...others] = array;                     // by position
const { name, age: years, grade = "N/A" } = object;  // by key; rename; default
```

```js file="destructuring-array.js" run
const colors = ["red", "green", "blue", "yellow"];
const [first, second, ...others] = colors;
console.log(first, second, others);

const [a, b = "default", c = "default"] = ["x", undefined];
console.log(a, b, c);

let p = 1;
let q = 2;
[p, q] = [q, p];
console.log(p, q);
```

```output
red green [ 'blue', 'yellow' ]
x default default
2 1
```

**Line by line.** Line 2 assigns by position: `first` gets index 0, `second` gets index 1, and `...others` (rest) collects everything remaining into a new array. On line 5, `b` and `c` have **defaults**, used only when the value is `undefined`: the source array has one element, so `b` and `c` are both missing. Lines 8 to 10 swap two variables without a temporary: the right side builds `[2, 1]`, which is then unpacked into `p` and `q`.

```js file="destructuring-object.js" run
const student = { name: "Asha", age: 20, address: { city: "Pune" } };

const { name, age: years, grade = "N/A" } = student;
const {
  address: { city },
} = student;
console.log(name, years, grade, city);

function describe({ name, price = 0 }) {
  return `${name} costs ${price}`;
}
console.log(describe({ name: "Pen", price: 10 }), describe({ name: "Gift" }));
```

```output
Asha 20 N/A Pune
Pen costs 10 Gift costs 0
```

**Explanation.** On line 3, `name` matches the key of the same name; `age: years` reads the `age` property but names the variable `years`; `grade` does not exist in the object, so its default `"N/A"` is used. Lines 4 to 6 reach into a nested object: `city` is created, but `address` is *not* (it is only the path). The most important use is **parameter destructuring** on line 9: the function receives one object and unpacks the fields it needs, with a default for `price`. This is exactly how React components receive props.

| Pattern | Reads | Creates variables |
|---|---|---|
| `{ name }` | key `name` | `name` |
| `{ age: years }` | key `age` | `years` |
| `{ grade = "N/A" }` | key `grade`, default if `undefined` | `grade` |
| `{ address: { city } }` | key `address`, then `city` inside | `city` only |
| `[x, , z]` | positions 0 and 2 | `x`, `z` |
| `[head, ...tail]` | position 0, then the rest | `head`, `tail` |

## Spread and rest

The same three dots mean two opposite things depending on where they appear. In a **value position** (array literal, object literal, function call) `...` **spreads** an existing collection out into individual items. In a **receiving position** (a parameter list, or the left side of a destructuring) `...` **gathers** the leftovers into a collection, and is called **rest**.

```js file="spread-rest.js" run
const a = [1, 2];
const b = [3, 4];
const merged = [...a, ...b, 5];
const inserted = [0, ...a, 99];
console.log(merged, inserted);
console.log(Math.max(...merged));

const defaults = { theme: "light", size: 12 };
const options = { size: 16 };
console.log({ ...defaults, ...options });

function sum(first, ...rest) {
  return rest.reduce((total, n) => total + n, first);
}
console.log(sum(1, 2, 3, 4));
```

```output
[ 1, 2, 3, 4, 5 ] [ 0, 1, 2, 99 ]
5
{ theme: 'light', size: 16 }
10
```

**Explanation.** Line 3 builds a new array by spreading `a` and `b` and adding `5`. Line 6 turns an array into separate arguments: `Math.max(...merged)` means `Math.max(1, 2, 3, 4, 5)`. On line 10 later properties **override** earlier ones, so `size` becomes `16` while `theme` survives; **order matters**. In `sum`, `...rest` gathers every argument after the first into a real array `[2, 3, 4]`, so `reduce` starts from `first` (`1`) and returns `10`. Remember that spread makes **shallow** copies (Section 3).

## Template literals

Backticks create strings that can contain **expressions** inside `${ }` and can span several lines.

```js file="template-literals.js" run
const item = "Pen";
const price = 10;
const qty = 3;

const line = `${item} x${qty} = ${price * qty}`;
const multi = `Line one
Line two`;

console.log(line);
console.log(multi);
```

```output
Pen x3 = 30
Line one
Line two
```

Anything valid as an expression may go inside `${ }`: arithmetic, function calls, even a ternary. The result is converted to text. Prefer template literals to joining with `+`, which makes the number-versus-text trap from Sheet 01 easy to hit.

## Optional chaining (`?.`) and nullish coalescing (`??`)

**Optional chaining** `?.` stops and evaluates to `undefined` if the value *before* it is `null` or `undefined`, instead of throwing. It works for properties (`a?.b`), indexes (`a?.[0]`) and calls (`a.fn?.()`).

**Nullish coalescing** `a ?? b` returns `b` only when `a` is `null` or `undefined`. It differs from `||`, which replaces **every falsy** value (including `0`, `""` and `false`). In Sheet 01 you saw that `||` breaks defaults when `0` is a legitimate value; `??` is the fix.

```js file="optional-nullish.js" run
const user = { profile: { nickname: "Ace" }, tags: ["a"] };
console.log(user.profile?.nickname, user.settings?.theme);
console.log(user.tags?.[0], user.greet?.());

const emptyName = "";
const viaOr = JSON.stringify(emptyName || "anonymous");
const viaNullish = JSON.stringify(emptyName ?? "anonymous");
console.log(viaOr, viaNullish);

const count = 0;
console.log(count || 10, count ?? 10);
```

```output
Ace undefined
a undefined
"anonymous" ""
10 0
```

**Explanation.** On line 2, `user.settings` is `undefined`, so `user.settings?.theme` short-circuits to `undefined` rather than throwing. `user.greet?.()` calls the method only if it exists. Lines 6 to 8 use `JSON.stringify` so the empty string is visible: `||` replaced the empty string with `"anonymous"`, while `??` kept it, because `""` is not `null` or `undefined`. The last line: `0 || 10` gives `10`, `0 ?? 10` keeps `0`.

::: warning Do not use `?.` to hide bugs
Optional chaining is for data that is *legitimately* missing (a user without a profile, an API field that arrives later). If a value *must* exist, let the error happen: a loud `TypeError` is easier to fix than a silent `undefined` three steps later.
:::

## Common mistakes in this section

#### Mistake 1: Destructuring `undefined` or `null`

**Why it is wrong.** There is nothing to unpack.

```js bad run throws
const response = undefined;
const { data } = response;
console.log(data);
```

```output
TypeError: Cannot destructure property 'data' of 'response' as it is undefined.
```

```js good run
const response = undefined;
const { data = [] } = response ?? {};
console.log(data);
```

```output
[]
```

**Symptom.** A `TypeError` mentioning "destructure". **Diagnosis:** print the value on the right of `=`; supply a fallback object with `??`.

#### Mistake 2: Using `||` where `??` was needed

**Why it is wrong.** `||` treats `0`, `""` and `false` as "missing".

```js bad run
const settings = { volume: 0 };
const volume = settings.volume || 50;
console.log(volume);
```

```output
50
```

```js good run
const settings = { volume: 0 };
const volume = settings.volume ?? 50;
console.log(volume);
```

```output
0
```

**Symptom.** A user's deliberate `0` or empty value silently becomes the default. **Diagnosis:** whenever a legitimate falsy value is being replaced, switch to `??`.

#### Mistake 3: Spreading in the wrong order

**Why it is wrong.** Later properties win, so defaults placed last overwrite the user's choices.

```js bad run
const defaults = { theme: "light", size: 12 };
const options = { size: 16 };
console.log({ ...options, ...defaults });
```

```output
{ size: 12, theme: 'light' }
```

```js good run
const defaults = { theme: "light", size: 12 };
const options = { size: 16 };
console.log({ ...defaults, ...options });
```

```output
{ theme: 'light', size: 16 }
```

**Symptom.** Options seem to be ignored. **Diagnosis:** read the spreads left to right and ask which one is applied last: it wins.

#### Mistake 4: Putting a rest element in the wrong place

**Why it is wrong.** `...rest` means "everything remaining", so nothing can follow it.

```js bad nocheck
const [first, ...middle, last] = [1, 2, 3, 4];
```

```js good run
const items = [1, 2, 3, 4];
const [first, ...middle] = items;
const last = items.at(-1);
console.log(first, middle, last);
```

```output
1 [ 2, 3, 4 ] 4
```

**Symptom.** A `SyntaxError` saying the rest element must be last; no code in the file runs. **Diagnosis:** the message names the problem. Take the last element another way (such as `at(-1)`).

# 6. Set and Map

## Learning objectives for this section

- Use `Set` for unique values and `Map` for key-value pairs with any key type.
- Use their core methods and iterate over them.
- Decide between an array, an object, a `Set` and a `Map`.

## Conceptual explanation

Arrays allow duplicates and finding an item means searching; plain objects only allow text keys. Two built-in collection types fill the gaps. A **`Set`** is a collection of **unique** values: adding something that is already there changes nothing. A **`Map`** stores **key-value pairs** where keys can be **any** value (numbers, objects, anything), and it remembers insertion order.

## `Set`

```js file="set-basic.js" run
const tags = new Set(["js", "css", "js"]);
console.log(tags.size);

console.log(tags.add("html") === tags);
tags.add("css");
console.log(tags.size, tags.has("js"), tags.has("python"));
console.log(tags.delete("css"), tags.delete("css"));
console.log([...tags]);

const unique = [...new Set([3, 1, 3, 2, 1])];
console.log(unique);
```

```output
2
true
3 true false
true false
[ 'js', 'html' ]
[ 3, 1, 2 ]
```

**Explanation.** The constructor `new Set(iterable)` copies values from any iterable and drops duplicates, so the initial size is `2`. `add(value)` returns **the set itself** (which allows chaining) and silently ignores a value already present. `has(value)` returns a boolean. `delete(value)` returns `true` if something was removed and `false` otherwise: the second call finds nothing. Sets are iterable in insertion order, so spread turns one back into an array. The last two lines are the classic **de-duplication** idiom: `[...new Set(array)]`. Sets compare with the same rule as `===` (with `NaN` treated as equal to itself), so two different objects with equal contents are *not* duplicates.

| Set member | Meaning |
|---|---|
| `new Set(iterable)` | create, optionally filled |
| `add(v)` | add; returns the set |
| `has(v)` | membership test; returns boolean |
| `delete(v)` | remove; returns boolean |
| `size` | count (a property, **not** `length`) |
| `clear()` | remove everything |

## `Map`

```js file="map-basic.js" run
const stock = new Map();
stock.set("pen", 10).set("book", 0);

console.log(stock.get("pen"), stock.get("bag"), stock.has("book"), stock.size);

for (const [name, qty] of stock) {
  console.log(name, qty);
}

const keyObject = { id: 1 };
const byObject = new Map([[keyObject, "object key"]]);
console.log(byObject.get(keyObject), byObject.get({ id: 1 }));
```

```output
10 undefined true 2
pen 10
book 0
object key undefined
```

**Explanation.** `set(key, value)` returns the Map, so calls chain. `get(key)` returns the value or `undefined` when the key is absent. `has` and `size` work like `Set`. Iterating a Map yields `[key, value]` pairs, which is why the loop destructures `[name, qty]` right in the loop header. The last lines show what objects cannot do: a Map can use an **object as a key**, but lookup is by **identity**, so a different object with the same contents does not find the entry.

**Worked example: counting words.**

```js file="map-count.js" run
const words = ["to", "be", "or", "not", "to", "be"];
const freq = new Map();

for (const word of words) {
  freq.set(word, (freq.get(word) ?? 0) + 1);
}

console.log(freq);
console.log([...freq.entries()].sort((a, b) => b[1] - a[1])[0]);
```

```output
Map(4) { 'to' => 2, 'be' => 2, 'or' => 1, 'not' => 1 }
[ 'to', 2 ]
```

For each word, line 5 reads its current count (`undefined` for a new word, so `?? 0` supplies zero), adds one, and stores it. Line 9 turns the Map into an array of pairs, sorts by count descending, and takes the first pair. `Array.prototype.sort` is stable, so equal counts keep their original order (`'to'` is before `'be'`).

## Choosing the right collection

[[widths 1.2 2.6 2.6]]
| Need | Use | Why |
|---|---|---|
| An ordered list, possibly with duplicates | Array | Index access, all the array methods |
| A record with fixed, known field names | Object | Readable dot access; matches JSON from APIs |
| Unique values; fast "is it in there?" | `Set` | No duplicates, `has` is direct |
| Lookup table with changing keys, or non-text keys | `Map` | Any key type, `size`, clean iteration |
| Data to send as JSON or store in `localStorage` | Array or object | `JSON.stringify` handles them (see below) |

## Common mistakes in this section

#### Mistake 1: Using `length` on a `Set` or `Map`

**Why it is wrong.** The count property is called `size`.

```js bad run
const tags = new Set(["a", "b"]);
console.log(tags.length);
```

```output
undefined
```

```js good run
const tags = new Set(["a", "b"]);
console.log(tags.size);
```

```output
2
```

**Symptom.** `undefined` and loops that never run. **Diagnosis:** log the collection itself to see its type (`Set(2) { 'a', 'b' }`).

#### Mistake 2: Expecting a `Set` to de-duplicate objects by content

**Why it is wrong.** Different objects are different values, even when their contents match.

```js bad run
const people = new Set([{ id: 1 }, { id: 1 }]);
console.log(people.size);
```

```output
2
```

```js good run
const list = [{ id: 1 }, { id: 1 }, { id: 2 }];
const byId = new Map();
for (const person of list) {
  byId.set(person.id, person);
}
console.log(byId.size);
```

```output
2
```

**Symptom.** "Duplicates" survive. **Diagnosis:** to de-duplicate objects, choose a unique key (such as `id`) and use a `Map` keyed by it.

#### Mistake 3: Using object keys when keys are not text

**Why it is wrong.** Plain object keys are converted to strings, so different objects collide.

```js bad run
const labels = {};
const a = { id: 1 };
const b = { id: 2 };
labels[a] = "first";
labels[b] = "second";
console.log(Object.keys(labels));
```

```output
[ '[object Object]' ]
```

```js good run
const labels = new Map();
const a = { id: 1 };
const b = { id: 2 };
labels.set(a, "first").set(b, "second");
console.log(labels.size);
```

```output
2
```

**Symptom.** The second assignment overwrites the first. **Diagnosis:** print `Object.keys`; if you see `[object Object]`, switch to `Map`.

#### Mistake 4: Trying to `JSON.stringify` a `Map` or `Set`

**Why it is wrong.** `JSON.stringify` only understands plain objects and arrays; a `Map` has no enumerable properties.

```js bad run
const stock = new Map([["pen", 10]]);
console.log(JSON.stringify(stock));
```

```output
{}
```

```js good run
const stock = new Map([["pen", 10]]);
console.log(JSON.stringify(Object.fromEntries(stock)));
console.log(JSON.stringify([...new Set([1, 2, 2])]));
```

```output
{"pen":10}
[1,2]
```

**Symptom.** Saved data comes back empty (important for `localStorage` in Sheet 03). **Diagnosis:** convert before saving: `Object.fromEntries(map)` for a Map, `[...set]` for a Set.
