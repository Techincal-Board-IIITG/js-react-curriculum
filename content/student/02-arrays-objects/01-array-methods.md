# 4. Array Methods and Callbacks

## Learning objectives for this section

- State, for each method, what the callback receives, what it must return, and what the method returns.
- Choose the right method for a task: transform, select, search, test, combine, order.
- Know which methods change the original array and which do not.
- Chain methods to build small data pipelines.

## Conceptual explanation

In Sheet 01 you wrote loops by hand. Most loops do one of a few jobs: build a new list from an old one, pick some items, find one item, check a condition, add everything up, or put things in order. JavaScript gives each job a method that takes a **callback**, a function you write to describe *what to do for one element*. The method handles the looping; you supply the per-item logic. The result is shorter code that says what it means.

All of these methods share a pattern. They call your callback **synchronously** (immediately, one element after another, in index order) and pass it up to three arguments: the **element**, its **index**, and the **whole array**. You may declare fewer parameters than that.

```diagram
flow
Array -> *Method loops over elements -> Calls your callback(value, index, array) -> Method uses the return value -> Result
```

[[widths 1.2 2.2 2.2 1.4]]
| Method | Callback should return | Method returns | Changes the original? |
|---|---|---|---|
| `forEach` | nothing (ignored) | `undefined` | No (unless your callback does) |
| `map` | the **new element** | **new array**, same length | No |
| `filter` | **truthy to keep**, falsy to drop | **new array**, equal or shorter | No |
| `find` | truthy for the match | first matching **element**, or `undefined` | No |
| `findIndex` | truthy for the match | its **index**, or `-1` | No |
| `some` | truthy/falsy | `true` if **any** match | No |
| `every` | truthy/falsy | `true` if **all** match | No |
| `reduce` | the **new accumulator** | the **final accumulator** | No |
| `sort` | a **number** (negative, zero, positive) | the **same array**, now ordered | **Yes** |
| `slice` | (no callback) | new array | No |
| `splice` | (no callback) | removed elements | **Yes** |

## Function deep dive: `map()`

**What it is.** A method that builds a **new array** by calling your callback on every element and collecting the return values.

**Why it exists.** Transforming every item of a list is the most common array task: prices to discounted prices, user objects to names, data to display strings. In React, `map()` is how a list of data becomes a list of elements on screen.

**Syntax.** `const result = array.map(callback)` with `callback(value, index, array)`.

**Parameters of the callback.** `value`: the current element. `index`: its position. `array`: the original array (rarely needed).

**Return value.** A new array with **exactly the same length** as the original. Element *i* of the result is whatever the callback returned for element *i* of the original. The original array is not changed.

**How it works, step by step.** (1) `map` creates an empty result array. (2) For each index in order, it calls `callback(value, index, array)`. (3) It stores the callback's **return value** in the result at that same index. (4) After the last element, it returns the result.

**How it differs from `forEach`.** `forEach` ignores what the callback returns and gives back `undefined`; `map` collects the return values and gives back an array. If you do not use the result of `map`, you wanted `forEach`.

```js file="map-basic.js" run
const prices = [100, 200, 300];

const discountedPrices = prices.map((price) => price * 0.9);

console.log(discountedPrices);
console.log(prices);
```

```output
[ 90, 180, 270 ]
[ 100, 200, 300 ]
```

**Line by line.** Line 1 creates the input array. Line 3 calls `prices.map(...)` and passes an arrow function as the callback. The arrow function has one parameter, `price`, and a concise body `price * 0.9`, which means "return this value". `map` calls it three times: with `100` (returning `90`), with `200` (returning `180`), and with `300` (returning `270`). Those three returned values become the new array stored in `discountedPrices`. Line 6 proves the original is untouched.

| Callback call | `price` | `index` | Callback returns | Result array so far |
|---|---|---|---|---|
| 1 | `100` | `0` | `90` | `[90]` |
| 2 | `200` | `1` | `180` | `[90, 180]` |
| 3 | `300` | `2` | `270` | `[90, 180, 270]` |

**Variation: objects, indexes and display strings.**

```js file="map-objects.js" run
const products = [
  { id: 1, name: "Pen", price: 10 },
  { id: 2, name: "Book", price: 250 },
  { id: 3, name: "Bag", price: 900 },
];

const names = products.map((product) => product.name);
const labels = products.map((p, i) => `${i + 1}. ${p.name} (${p.price})`);
const withTax = products.map((p) => ({ ...p, price: p.price * 1.2 }));

console.log(names);
console.log(labels.join(" | "));
console.log(withTax[0], products[0]);
```

```output
[ 'Pen', 'Book', 'Bag' ]
1. Pen (10) | 2. Book (250) | 3. Bag (900)
{ id: 1, name: 'Pen', price: 12 } { id: 1, name: 'Pen', price: 10 }
```

Line 7 extracts one property from each object. Line 8 uses the **index** argument to number the items. Line 9 returns a **new object** for every product using spread (Section 6): `{ ...p, price: ... }` copies all properties and overrides `price`. The originals are untouched (last line), which is exactly the immutable-update pattern React requires. The parentheses around `{ ... }` are needed because the arrow function returns an object literal (Sheet 01, Section 7).

::: concept Why React loves `map`
A React component receives a list of data and must produce a list of elements. a call of the form `items.map(...)` that returns one element per item is the whole idea: data array in, element array out. You will use exactly this in Sheet 05.
:::

## Optional deep dive: `["1", "2", "3"].map(parseInt)`

```js file="map-parseint.js" run
console.log(["1", "2", "3"].map(parseInt));
console.log(["1", "2", "3"].map((s) => parseInt(s, 10)));
```

```output
[ 1, NaN, NaN ]
[ 1, 2, 3 ]
```

`map` passes **three** arguments, so `parseInt` receives `(value, index, array)`, and its second parameter (the radix) becomes the index: `parseInt("2", 1)` is `NaN` because base 1 is invalid. Wrapping the call in your own arrow function controls exactly which arguments reach the inner function. Remember this whenever you pass an existing function straight into a method.

## Function deep dive: `filter()`

**What it is.** A method that builds a new array containing only the elements for which the callback returns a **truthy** value.

**Why it exists.** Selecting a subset is as common as transforming: in-stock products, search matches, unfinished tasks.

**Syntax and callback.** `array.filter(callback)`, `callback(value, index, array)`. The callback is a *predicate*: it answers yes or no.

**Return value.** A new array of the **same elements** (not copies), in the original order. Its length ranges from 0 to the original length. If nothing matches, the result is an empty array `[]`, never `undefined`.

**How it works.** For each element, call the callback; if the return value is truthy, push that *original element* into the result; otherwise skip it.

```js file="filter-basic.js" run
const products = [
  { name: "Pen", price: 10, inStock: true },
  { name: "Book", price: 250, inStock: false },
  { name: "Bag", price: 900, inStock: true },
  { name: "Bottle", price: 300, inStock: true },
];

const available = products.filter((p) => p.inStock);
const affordable = products.filter((p) => p.inStock && p.price <= 300);

console.log(available.map((p) => p.name));
console.log(affordable.map((p) => p.name));
console.log(products.filter((p) => p.price > 1000));
```

```output
[ 'Pen', 'Bag', 'Bottle' ]
[ 'Pen', 'Bottle' ]
[]
```

| Callback call | `p.name` | Callback returns | Kept? |
|---|---|---|---|
| 1 | `Pen` | `true` | yes |
| 2 | `Book` | `false` | no |
| 3 | `Bag` | `true` | yes |
| 4 | `Bottle` | `true` | yes |

Line 8 passes `(p) => p.inStock`, which returns the boolean property directly. Line 9 combines two tests with `&&`. Line 12 shows the empty-result case. We call `.map(...)` on each result to print just the names: this is a first **chain** (see below).

## Function deep dive: `find()` and `findIndex()`

**What they are.** Methods that locate the **first** element for which the callback is truthy and then **stop**. `find` returns the element; `findIndex` returns its position.

**Why they exist.** "Get the product with id 3" or "where is this user in the list" are searches for one item. `filter` would scan the whole array and return an array; `find` stops early and returns the item itself.

**Return values.** `find`: the element, or **`undefined`** if nothing matches. `findIndex`: the index, or **`-1`** if nothing matches.

```js file="find-basic.js" run
const products = [
  { id: 1, name: "Pen" },
  { id: 2, name: "Book" },
  { id: 3, name: "Bag" },
];

const bag = products.find((p) => p.id === 3);
const missing = products.find((p) => p.id === 99);

console.log(bag.name);
console.log(missing);
console.log(products.findIndex((p) => p.name === "Book"));
console.log(products.findIndex((p) => p.id === 99));
```

```output
Bag
undefined
1
-1
```

Always handle the "not found" result before using it: reading `missing.name` would throw. Compare with `includes`/`indexOf` from Section 2: those compare values with `===`, while `find`/`findIndex` run **your test**, which is what you need for objects.

## Function deep dive: `some()` and `every()`

**What they are.** Methods that answer a yes/no question about the whole array. `some` is `true` if **at least one** element passes; `every` is `true` only if **all** elements pass. Both **short-circuit**: `some` stops at the first pass, `every` stops at the first failure.

```js file="some-every.js" run
const products = [
  { name: "Pen", price: 10, inStock: true },
  { name: "Book", price: 250, inStock: false },
  { name: "Bag", price: 900, inStock: true },
];

console.log(products.some((p) => p.price > 800));
console.log(products.every((p) => p.inStock));
console.log([].some(() => true), [].every(() => false));
```

```output
true
false
false true
```

The last line shows an easily forgotten edge case: on an **empty array**, `some` is always `false` (there is no element that passes) and `every` is always `true` (there is no element that fails; this is called *vacuous truth*). Guard for empty lists if "all of nothing" would be wrong in your program.

## Function deep dive: `reduce()`

**What it is.** A method that **combines all elements into one value**: a sum, a maximum, an object, even another array.

**Why it exists.** The other methods keep list shape (list in, list out). Sometimes you need a single answer from many items: the total of a shopping cart, the count per category.

**Syntax.** `array.reduce(callback, initialValue)` with `callback(accumulator, value, index, array)`.

**Parameters.** `accumulator`: the running result, carried from one call to the next. `value`: the current element. `initialValue`: the starting accumulator. **Always provide it.**

**Return value.** The accumulator after the last call.

**How it works, step by step.** (1) The accumulator starts as `initialValue`. (2) For each element the callback is called with the current accumulator and the element. (3) Whatever the callback **returns** becomes the accumulator for the next call. (4) After the last element, `reduce` returns the final accumulator.

```js file="reduce-basic.js" run
const nums = [10, 20, 30];

const total = nums.reduce((acc, n, i) => {
  console.log(`step ${i}: acc=${acc}, n=${n}`);
  return acc + n;
}, 0);

console.log(total);
```

```output
step 0: acc=0, n=10
step 1: acc=10, n=20
step 2: acc=30, n=30
60
```

| Step | `acc` (before) | `n` | Callback returns | `acc` (after) |
|---|---|---|---|---|
| 1 | `0` (initial value) | `10` | `10` | `10` |
| 2 | `10` | `20` | `30` | `30` |
| 3 | `30` | `30` | `60` | `60` |

The key sentence is: **the return value of one step is the accumulator of the next**. Forget the `return` and the second step receives `undefined`.

**Variation: building an object.** The accumulator can be an object, which lets you group or count.

```js file="reduce-object.js" run
const products = [
  { name: "Pen", category: "stationery", price: 10 },
  { name: "Book", category: "stationery", price: 250 },
  { name: "Bag", category: "travel", price: 900 },
  { name: "Bottle", category: "travel", price: 300 },
];

const counts = products.reduce((acc, p) => {
  acc[p.category] = (acc[p.category] || 0) + 1;
  return acc;
}, {});

const priciest = products.reduce((max, p) => (p.price > max ? p.price : max), 0);

console.log(counts);
console.log(priciest);
```

```output
{ stationery: 2, travel: 2 }
900
```

The initial value on line 11 is an empty object `{}`. For each product, line 8 reads the current count for its category (`undefined` the first time, so `|| 0` supplies zero), adds one, and stores it. Line 13 shows a maximum: the accumulator holds the biggest price seen so far.

## Function deep dive: `sort()`

**What it is.** A method that puts the elements in order, **in place**: it changes the original array and also returns it.

**Why it needs care.** Without a comparator it converts elements to **strings** and sorts alphabetically, which gives wrong results for numbers.

**Syntax.** `array.sort(compare)` with `compare(a, b)` called with two elements.

**The comparator's contract.** Return a **negative number** if `a` should come before `b`, a **positive number** if `a` should come after `b`, and **zero** if their order does not matter. For numbers, `a - b` sorts ascending and `b - a` descending.

```js file="sort-basic.js" run
console.log([10, 9, 1].sort());
console.log([10, 9, 1].sort((a, b) => a - b));
console.log([10, 9, 1].sort((a, b) => b - a));

const words = ["banana", "apple", "Cherry"];
console.log([...words].sort());
console.log([...words].sort((a, b) => a.localeCompare(b)));

const products = [
  { name: "Pen", price: 10 },
  { name: "Book", price: 250 },
  { name: "Bag", price: 900 },
  { name: "Bottle", price: 300 },
];
const byPrice = [...products].sort((a, b) => a.price - b.price);
console.log(byPrice.map((p) => p.name).join(", "));
console.log(products.map((p) => p.name).join(", "));
```

```output
[ 1, 10, 9 ]
[ 1, 9, 10 ]
[ 10, 9, 1 ]
[ 'Cherry', 'apple', 'banana' ]
[ 'apple', 'banana', 'Cherry' ]
Pen, Book, Bottle, Bag
Pen, Book, Bag, Bottle
```

**Explanation.** Line 1 shows the trap: as strings, `"10"` sorts before `"9"` (the character `"1"` comes before `"9"`), giving `[1, 10, 9]`. Lines 2 and 3 use a numeric comparator. For `[10, 9, 1]` and `(a, b) => a - b`, comparing `10` and `9` gives `1` (positive: `10` goes after `9`), so ascending order results. Lines 5 and 6 sort text: the default sort places uppercase letters before lowercase (by character code), so `"Cherry"` comes first; `localeCompare` follows dictionary order. Line 13 copies the array first with spread, so line 15 shows the original order unchanged: **`sort` mutates, so copy first when you need the original** (a `toSorted()` method that returns a new array also exists in current browsers and Node.js 20 and later).

## Chaining methods into pipelines

Because `map`, `filter` and `slice` return **arrays**, you can call another array method on the result directly.

```js file="chain.js" run
const products = [
  { name: "Pen", price: 10, inStock: true },
  { name: "Book", price: 250, inStock: false },
  { name: "Bag", price: 900, inStock: true },
  { name: "Bottle", price: 300, inStock: true },
];

const total = products
  .filter((p) => p.inStock)
  .map((p) => p.price)
  .reduce((sum, price) => sum + price, 0);

console.log(total);
```

```output
1210
```

Read it as a sentence: *keep the in-stock products, take their prices, add them up*. `filter` yields three products; `map` turns them into `[10, 900, 300]`; `reduce` sums to `1210`. Each stage is small and testable. Do not chain so long that you cannot name the intermediate steps; split into named `const` variables when a pipeline passes four or five stages.

## Common mistakes in this section

#### Mistake 1: A `map` callback with a block body and no `return`

**Why it is wrong.** Braces mean a block body, and a block needs an explicit `return` (Sheet 01, Section 7).

```js bad run
const doubled = [1, 2, 3].map((n) => {
  n * 2;
});
console.log(doubled);
```

```output
[ undefined, undefined, undefined ]
```

```js good run
const doubled = [1, 2, 3].map((n) => {
  return n * 2;
});
console.log(doubled);
```

```output
[ 2, 4, 6 ]
```

**Symptom.** An array full of `undefined` (or `NaN` when you calculate with it later). **Diagnosis:** log the result of `map` right away; if it holds `undefined`, check for a missing `return`.

#### Mistake 2: Sorting numbers without a comparator

**Why it is wrong.** The default comparison is alphabetical, and `sort` also changes the original array.

```js bad run
const marks = [25, 100, 5];
marks.sort();
console.log(marks);
```

```output
[ 100, 25, 5 ]
```

```js good run
const marks = [25, 100, 5];
const sorted = [...marks].sort((a, b) => a - b);
console.log(sorted, marks);
```

```output
[ 5, 25, 100 ] [ 25, 100, 5 ]
```

**Symptom.** Numbers in a seemingly random order. **Diagnosis:** whenever sorted numbers look "alphabetical", you forgot the comparator.

#### Mistake 3: `reduce` on a possibly empty array without an initial value

**Why it is wrong.** With no initial value, `reduce` uses the first element as the starting accumulator. An empty array has no first element.

```js bad run throws
const empty = [];
console.log(empty.reduce((sum, n) => sum + n));
```

```output
TypeError: Reduce of empty array with no initial value
```

```js good run
const empty = [];
console.log(empty.reduce((sum, n) => sum + n, 0));
```

```output
0
```

**Symptom.** A crash that only happens when a list is empty (for example, an empty shopping cart). **Diagnosis:** always pass the second argument to `reduce`.

#### Mistake 4: Using the result of `find` without checking for `undefined`

**Why it is wrong.** `find` returns `undefined` when nothing matches, and reading a property of `undefined` throws.

```js bad run throws
const users = [{ id: 1, name: "Asha" }];
console.log(users.find((u) => u.id === 2).name);
```

```output
TypeError: Cannot read properties of undefined (reading 'name')
```

```js good run
const users = [{ id: 1, name: "Asha" }];
const user = users.find((u) => u.id === 2);
console.log(user ? user.name : "User not found");
```

```output
User not found
```

**Symptom.** A crash when the id is absent. **Diagnosis:** read the message: the object *before* `.name` is `undefined`. Print what `find` returned and add the check.
