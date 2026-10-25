---
number: 02
title: Arrays, Objects, and Modern JavaScript
subtitle: Storing collections of data, transforming it with array methods, and writing code the modern way
track: js
time: Core path about 28-32 hours
edition: Student edition
goals:
  - Create, read, copy and change arrays and objects without accidentally sharing data
  - Use map, filter, find, some, every, reduce and sort, and say what each callback receives and returns
  - Use destructuring, spread, rest, optional chaining and nullish coalescing
  - Use Set and Map, and split code into ES modules
  - Write pure functions that update data without mutating it
---

# 1. Study Guide and Learning Objectives

Sheet 01 gave you single values and the control structures around them. Real programs work with **collections**: a list of products, a student record, a table of expenses. This sheet teaches the two collection types you will use every day, **arrays** (ordered lists) and **objects** (named properties), plus the array methods that React relies on for almost everything it renders.

## Learning objectives

By the end of this sheet you should be able to do each of the following without looking anything up.

- Create arrays and objects, read and change them, and nest them (arrays of objects, objects holding arrays).
- Explain why `const b = a` does not copy an array or object, and make a correct shallow copy.
- Explain what a shallow copy is, and why spread syntax does not protect nested data.
- Use `map()`, `filter()`, `find()`, `findIndex()`, `some()`, `every()`, `reduce()`, `forEach()`, `sort()`, `slice()` and `splice()`, stating each callback's arguments and return value.
- Use destructuring, spread, rest, template literals, optional chaining (`?.`) and nullish coalescing (`??`).
- Choose between an array, an object, a `Set` and a `Map`.
- Write pure functions and update data immutably.
- Split a program into ES modules with named and default exports.

## Recommended workload

[[widths 1.2 3.4]]
| Item | Recommendation |
|---|---|
| **Essential topics** | Sections 2 to 9. Skip *Optional deep dive* boxes on a first pass. |
| **Optional deep dives** | `sort()` comparator details, `structuredClone` limits, `Map` versus plain objects, module cycles. |
| **Required exercises** | Sets A to D in full; at least one challenge from set E. |
| **Core projects (do these)** | Projects 1, 2 and 3. |
| **Extension projects** | Projects 4 and 5. |
| **Estimated study time** | Reading and experimenting: 12 to 14 hours. Exercises: 6 to 7 hours. Core projects: 9 to 11 hours. Extension projects add about 5 to 6 hours. |

::: warning Prerequisite
You need Sheet 01: functions, arrow functions, callbacks, scope, and `try/catch`. Array methods are *higher-order functions*, so if callbacks still feel shaky, re-read Section 9 of Sheet 01 first.
:::

# 2. Arrays

## Learning objectives for this section

- Create arrays, read elements by index, and use `length`.
- Add and remove elements, knowing what each method returns.
- Copy and slice arrays without surprises.

## Conceptual explanation

An **array** is an ordered list of values. Each value has a numeric position called an **index**, and indexes start at **0**. Arrays are the natural choice when order matters or when you have many things of the same kind: prices, names, messages. Arrays are *objects* (Sheet 01: `typeof [] === "object"`), so they are copied and compared **by reference**, a fact that causes most array bugs.

## Syntax

```text
const list = [value0, value1, value2];   // array literal
list[0]            // read the first element
list[list.length - 1]   // read the last element
list.at(-1)        // read the last element (negative index counts from the end)
list[1] = "new";   // replace an element
list.length        // number of elements
```

## Worked example: reading and changing

```js file="array-basics.js" run
const fruits = ["apple", "banana", "cherry"];

console.log(fruits[0], fruits[2], fruits[3]);
console.log(fruits.length);
console.log(fruits.at(-1));

fruits[1] = "blueberry";
console.log(fruits);
```

```output
apple cherry undefined
3
cherry
[ 'apple', 'blueberry', 'cherry' ]
```

**Line by line.** Line 3 reads positions 0, 2 and 3. Position 3 does not exist (the last index is `length - 1`, which is 2), so the result is `undefined`, not an error. Line 4 prints the element count. Line 5 uses `at(-1)`: negative numbers count from the end. Line 7 replaces the element at index 1. Notice the array is declared with `const`: the *contents* changed but the variable still points at the same array.

## The adding and removing methods

These four methods **mutate** (change) the array they are called on, and each returns something different.

[[widths 1.2 2.6 2.6]]
| Method | What it does | Returns |
|---|---|---|
| `push(...items)` | Adds items at the **end** | The **new length** |
| `pop()` | Removes the **last** item | The removed item (or `undefined` if empty) |
| `unshift(...items)` | Adds items at the **start** | The **new length** |
| `shift()` | Removes the **first** item | The removed item (or `undefined` if empty) |

```js file="array-mutators.js" run
const stack = [1, 2, 3];

console.log(stack.push(4, 5));
console.log(stack.pop());
console.log(stack.unshift(0));
console.log(stack.shift());
console.log(stack);
```

```output
5
5
5
0
[ 1, 2, 3, 4 ]
```

| Step | Call | Array after the call | Returned |
|---|---|---|---|
| 1 | start | `[1, 2, 3]` | n/a |
| 2 | `push(4, 5)` | `[1, 2, 3, 4, 5]` | `5` (new length) |
| 3 | `pop()` | `[1, 2, 3, 4]` | `5` (removed item) |
| 4 | `unshift(0)` | `[0, 1, 2, 3, 4]` | `5` (new length) |
| 5 | `shift()` | `[1, 2, 3, 4]` | `0` (removed item) |

Two of those calls return a length and two return an item, and the length happens to equal `5` three times here, which makes the trace worth studying carefully.

## Function deep dive: `slice()` versus `splice()`

The names differ by one letter and the behaviour differs completely. This pair is a classic source of bugs.

**`slice(start, end)`** returns a **new array** containing the elements from `start` up to but **not including** `end`. It does **not** change the original. A negative index counts from the end. Both parameters are optional: `slice()` copies the whole array.

**`splice(start, deleteCount, ...itemsToInsert)`** **changes the original array**: it removes `deleteCount` elements beginning at `start`, inserts the given items in their place, and **returns an array of the removed elements**.

```js file="slice-splice.js" run
const letters = ["a", "b", "c", "d", "e"];

console.log(letters.slice(1, 3));
console.log(letters.slice(-2));
console.log(letters);

const removed = letters.splice(1, 2, "X", "Y", "Z");
console.log(removed);
console.log(letters);
```

```output
[ 'b', 'c' ]
[ 'd', 'e' ]
[ 'a', 'b', 'c', 'd', 'e' ]
[ 'b', 'c' ]
[ 'a', 'X', 'Y', 'Z', 'd', 'e' ]
```

**Explanation.** `slice(1, 3)` takes indexes 1 and 2 (`b`, `c`); index 3 is excluded. `slice(-2)` takes the last two. After the slices, line 5 shows the original is untouched. `splice(1, 2, "X", "Y", "Z")` starts at index 1, removes two elements (`b`, `c`), and inserts three new ones; the removed elements come back as the return value. Remember: **slice is safe (copies), splice is destructive (edits)**.

## Searching

```js file="array-search.js" run
const fruits = ["apple", "banana", "cherry"];

console.log(fruits.includes("apple"));
console.log(fruits.indexOf("cherry"), fruits.indexOf("grape"));
console.log(fruits.join(" + "));
console.log(Array.isArray(fruits), Array.isArray("apple"));
```

```output
true
2 -1
apple + banana + cherry
true false
```

`includes(x)` answers yes or no. `indexOf(x)` returns the position, or **`-1`** when the value is absent. `join(separator)` builds a string. `Array.isArray()` is the reliable array test (recall that `typeof` says `"object"`).

## Copying arrays: references again

```js file="array-copy.js" run
const original = [1, 2, 3];
const alias = original;
const copy = [...original];

alias.push(4);

console.log(original);
console.log(copy);
console.log(original === alias, original === copy);
```

```output
[ 1, 2, 3, 4 ]
[ 1, 2, 3 ]
true false
```

`alias = original` copies the **reference**: both names lead to the same array, so pushing through `alias` changes what `original` sees. `[...original]` (spread, Section 6) builds a **new array** with the same elements; `original.slice()` does the same. Last line: `original === alias` is `true` (same array); `original === copy` is `false` (different arrays with equal contents).

## Common mistakes in this section

#### Mistake 1: Treating `length` as the last index

**Why it is wrong.** The last valid index is `length - 1`.

```js bad run
const items = ["a", "b", "c"];
console.log(items[items.length]);
```

```output
undefined
```

```js good run
const items = ["a", "b", "c"];
console.log(items[items.length - 1], items.at(-1));
```

```output
c c
```

**Symptom.** `undefined`, and later `Cannot read properties of undefined`. **Diagnosis:** write out the valid indexes on paper (0, 1, 2) and compare.

#### Mistake 2: Thinking `const b = a` copies the array

**Why it is wrong.** It copies the reference (see above), so edits through either name are visible through both.

```js bad run
const cart = ["pen"];
const backup = cart;
cart.push("book");
console.log(backup);
```

```output
[ 'pen', 'book' ]
```

```js good run
const cart = ["pen"];
const backup = [...cart];
cart.push("book");
console.log(backup);
```

```output
[ 'pen' ]
```

**Symptom.** The "backup" changes when the original does. **Diagnosis:** compare with `===`; if it prints `true`, they are the same array.

#### Mistake 3: Using `splice` when you meant `slice`

**Why it is wrong.** `splice` edits the original; code that only wanted a piece of the list deletes data.

```js bad run
const scores = [90, 80, 70, 60];
const topTwo = scores.splice(0, 2);
console.log(topTwo, scores);
```

```output
[ 90, 80 ] [ 70, 60 ]
```

```js good run
const scores = [90, 80, 70, 60];
const topTwo = scores.slice(0, 2);
console.log(topTwo, scores);
```

```output
[ 90, 80 ] [ 90, 80, 70, 60 ]
```

**Symptom.** The original list is missing items. **Diagnosis:** print the original array before and after each suspicious call.

#### Mistake 4: Using `indexOf` as a boolean

**Why it is wrong.** `indexOf` returns `-1` when absent, and `-1` is **truthy**; the first element's index `0` is **falsy**.

```js bad run
const names = ["Asha", "Meera"];
if (names.indexOf("Asha")) {
  console.log("found");
} else {
  console.log("not found");
}
```

```output
not found
```

```js good run
const names = ["Asha", "Meera"];
if (names.includes("Asha")) {
  console.log("found");
} else {
  console.log("not found");
}
```

```output
found
```

**Symptom.** A value that is in the list is reported missing (and a missing value is reported found). **Diagnosis:** log the raw return value of `indexOf`; use `includes()` for yes/no.

# 3. Objects

## Learning objectives for this section

- Create objects and read, add, change and delete properties.
- Write methods and explain the basics of `this`.
- Nest objects and arrays, and navigate them.
- Explain mutation through shared references, shallow copies, and why spread is shallow.

## Conceptual explanation

An **object** groups related values under **names** (called *keys* or *properties*). Where an array answers "which position?", an object answers "which name?". A student record has a `name`, an `age`, and a list of `courses`; an array of numbers cannot say what each number means, but an object can. Objects are the main way JavaScript models real-world things, and nearly all data from web APIs arrives as objects and arrays of objects.

## Syntax

```text
const person = {
  name: "Asha",            // key: value, separated by commas
  age: 20,
  greet() {                // method shorthand: a function stored as a property
    return "Hi, " + this.name;
  },
};

person.name           // dot notation (key is written literally)
person["name"]        // bracket notation (key can be a variable or any string)
person.email = "x";   // add or change
delete person.age;    // remove
"name" in person      // does the key exist?
```

## Worked example: reading and changing

```js file="object-basics.js" run
const student = {
  name: "Asha",
  age: 20,
  courses: ["Math", "CS"],
  address: { city: "Pune" },
};

console.log(student.name, student["age"]);

const key = "name";
console.log(student[key]);

student.email = "asha@example.com";
delete student.age;

console.log("age" in student);
console.log(Object.keys(student));
console.log(student.address.city, student.courses[1]);
```

```output
Asha 20
Asha
false
[ 'name', 'courses', 'address', 'email' ]
Pune CS
```

**Line by line.** Line 8 shows both access styles. Lines 10 and 11: with a **variable** key you must use brackets (`student.key` would look for a property literally named `"key"`). Line 13 adds a property, line 14 deletes one. Line 16: `"age" in student` is `false` after the delete. Line 17: `Object.keys()` returns an array of the keys, in the order they were created (deleting `age` leaves `name`, `courses`, `address`, then the new `email`). Line 18 shows chained access into nested data: the object's `address` property is itself an object, and `courses` is an array.

## Function deep dive: `Object.keys()`, `Object.values()`, `Object.entries()`

**What they are.** Functions on the built-in `Object` that turn an object into an array you can loop over or transform.

[[widths 1.3 2.5 2.7]]
| Function | Returns | For `{ pen: 10, book: 250 }` |
|---|---|---|
| `Object.keys(obj)` | Array of the object's own keys | `["pen", "book"]` |
| `Object.values(obj)` | Array of the values | `[10, 250]` |
| `Object.entries(obj)` | Array of `[key, value]` pairs | `[["pen", 10], ["book", 250]]` |

```js file="object-iteration.js" run
const prices = { pen: 10, book: 250 };

for (const item of Object.keys(prices)) {
  console.log(item, prices[item]);
}

let total = 0;
for (const price of Object.values(prices)) {
  total += price;
}
console.log("Total:", total);
console.log(Object.entries(prices));
```

```output
pen 10
book 250
Total: 260
[ [ 'pen', 10 ], [ 'book', 250 ] ]
```

These functions are the modern replacement for `for...in` on objects, because they return real arrays and can be combined with the array methods in Section 4.

## Methods and `this`

A **method** is a function stored as an object property. Inside a method called as `object.method()`, the keyword `this` refers to that object.

```js file="object-method.js" run
const counter = {
  count: 0,
  increment() {
    this.count++;
    return this.count;
  },
};

console.log(counter.increment(), counter.increment());
console.log(counter.count);
```

```output
1 2
2
```

`counter.increment()` is called *on* `counter`, so `this` is `counter`, and `this.count++` changes `counter.count`. The value of `this` is decided by **how the function is called**, not where it is written (a source of Mistake 3 below). Arrow functions do not have their own `this`, which is why object methods are written with the shorthand shown here.

## References, mutation and shallow copies

Objects behave like arrays: `const b = a` copies the reference. To get a separate object, copy it. The **spread** syntax `{ ...original }` creates a new object with the same properties, but it is a **shallow copy**: only the *top level* is duplicated. Any nested object or array is still shared.

```js file="shallow-copy.js" run
const original = { name: "Asha", address: { city: "Pune" } };
const copy = { ...original };

copy.name = "Meera";
copy.address.city = "Delhi";

console.log(original.name, original.address.city);

const deep = structuredClone(original);
deep.address.city = "Goa";
console.log(original.address.city, deep.address.city);
```

```output
Asha Delhi
Delhi Goa
```

**Explanation.** `copy.name = "Meera"` only changes `copy`, because the string `"Asha"` was copied by value. But `copy.address` and `original.address` are **the same object**, so changing `copy.address.city` also changes `original` (line 7 prints `Delhi`). `structuredClone()` (built into modern browsers and Node.js) makes a **deep copy**: the nested objects are duplicated too, so `deep.address.city = "Goa"` leaves `original` alone. `structuredClone` cannot copy functions and throws an error if it meets one.

::: concept Shallow versus deep
A shallow copy duplicates one level; anything nested is still shared. Before you "copy" data, ask: does it contain nested objects or arrays I plan to change? If yes, either copy each nested level you change (Section 8) or use `structuredClone`.
:::

## Arrays of objects

The shape you will meet most often, especially in React and API responses, is an **array of objects**.

```js file="array-of-objects.js" run
const products = [
  { id: 1, name: "Pen", price: 10, inStock: true },
  { id: 2, name: "Book", price: 250, inStock: false },
  { id: 3, name: "Bag", price: 900, inStock: true },
];

console.log(products.length);
console.log(products[1].name);

for (const product of products) {
  console.log(`${product.name}: ${product.price}`);
}
```

```output
3
Book
Pen: 10
Book: 250
Bag: 900
```

`products[1]` is the second object, and `.name` reads its property. Section 4 replaces that manual loop with `map`, `filter` and friends.

## Common mistakes in this section

#### Mistake 1: Reading a property of `undefined`

**Why it is wrong.** `student.address` is `undefined` when absent, and reading a property of `undefined` throws.

```js bad run throws
const student = { name: "Asha" };
console.log(student.address.city);
```

```output
TypeError: Cannot read properties of undefined (reading 'city')
```

```js good run
const student = { name: "Asha" };
console.log(student.address?.city);
console.log(student.address === undefined ? "no address" : student.address.city);
```

```output
undefined
no address
```

**Symptom.** A `TypeError` saying it cannot read properties of undefined. **Diagnosis:** the text in parentheses names the property you tried to read; the object *before* it is the one that is `undefined`. Print it. Section 6 explains `?.`.

#### Mistake 2: Assuming spread copies nested objects

**Why it is wrong.** Spread is shallow (see above).

```js bad run
const settings = { theme: "dark", panel: { open: true } };
const draft = { ...settings };
draft.panel.open = false;
console.log(settings.panel.open);
```

```output
false
```

```js good run
const settings = { theme: "dark", panel: { open: true } };
const draft = { ...settings, panel: { ...settings.panel } };
draft.panel.open = false;
console.log(settings.panel.open);
```

```output
true
```

**Symptom.** Changing the "copy" changes the original. **Diagnosis:** compare `settings.panel === draft.panel`; `true` means the nested object is shared. This exact pattern (copy the level you change) is how React state is updated.

#### Mistake 3: Detaching a method from its object

**Why it is wrong.** `this` depends on the call. Calling the bare function has no object in front of it.

```js bad run throws
const counter = {
  count: 0,
  increment() {
    this.count++;
    return this.count;
  },
};
const detached = counter.increment;
console.log(detached());
```

```output
TypeError: Cannot read properties of undefined (reading 'count')
```

```js good run
const counter = {
  count: 0,
  increment() {
    this.count++;
    return this.count;
  },
};
const bound = () => counter.increment();
console.log(bound());
```

```output
1
```

**Symptom.** `this` is `undefined` (in modules and strict code) inside a method that worked when called normally. **Diagnosis:** whenever you pass a method as a callback, ask whether it still has its object. Wrap the call as shown, or avoid `this` by using plain functions and closures.

#### Mistake 4: Using dot notation with a variable key

**Why it is wrong.** `obj.key` always means the property literally named `key`.

```js bad run
const prices = { pen: 10, book: 250 };
const item = "book";
console.log(prices.item);
```

```output
undefined
```

```js good run
const prices = { pen: 10, book: 250 };
const item = "book";
console.log(prices[item]);
```

```output
250
```

**Symptom.** `undefined` with no error. **Diagnosis:** if the property name is stored in a variable, use brackets.
