# 7. Mini Project Reference Implementations

Each reference is a self-contained module followed by tests that exercise the acceptance criteria. In real student projects the functions live in a module file and the tests in `main.mjs`; here they share one listing so the validator can execute them. Test data is frozen to confirm nothing is mutated. Grade against the acceptance criteria in the student sheet.

## Project 1: Student marks analyzer

```js file="analyzer.js" run
const round2 = (x) => Math.round(x * 100) / 100;

function average(numbers) {
  return numbers.length === 0 ? 0 : numbers.reduce((s, n) => s + n, 0) / numbers.length;
}

function gradeFor(avg) {
  if (avg >= 90) return "A";
  if (avg >= 80) return "B";
  if (avg >= 70) return "C";
  if (avg >= 60) return "D";
  if (avg >= 40) return "E";
  return "F";
}

function analyze(students) {
  const report = students
    .map((s) => ({
      name: s.name,
      average: round2(average(s.marks)),
      grade: gradeFor(average(s.marks)),
    }))
    .sort((a, b) => b.average - a.average);
  const classAverage = round2(average(students.map((s) => average(s.marks))));
  const gradeCounts = report.reduce(
    (acc, r) => ({ ...acc, [r.grade]: (acc[r.grade] ?? 0) + 1 }),
    {}
  );
  return { report, classAverage, topStudent: report[0]?.name ?? null, gradeCounts };
}

const students = Object.freeze([
  Object.freeze({ name: "Asha", marks: Object.freeze([82, 91, 77]) }),
  Object.freeze({ name: "Ravi", marks: Object.freeze([45, 38, 52]) }),
  Object.freeze({ name: "Meera", marks: Object.freeze([95, 88, 100]) }),
  Object.freeze({ name: "Kabir", marks: Object.freeze([60, 71, 64]) }),
]);

const result = analyze(students);
result.report.forEach((r, i) => {
  console.log(`${i + 1}. ${r.name.padEnd(6)} ${r.average.toFixed(2)}  ${r.grade}`);
});
console.log("Class average:", result.classAverage.toFixed(2));
console.log("Top student:", result.topStudent);
console.log("Grade counts:", result.gradeCounts);
console.log(average([80, 90]), average([]));
console.log(gradeFor(90), gradeFor(89.99), gradeFor(39.9));
console.log(analyze([]));
```

```output
1. Meera  94.33  A
2. Asha   83.33  B
3. Kabir  65.00  D
4. Ravi   45.00  E
Class average: 71.92
Top student: Meera
Grade counts: { A: 1, B: 1, D: 1, E: 1 }
85 0
A B F
{ report: [], classAverage: 0, topStudent: null, gradeCounts: {} }
```

## Project 2: Product inventory manager

```js file="inventory.js" run
function formatMoney(cents) {
  const dollars = Math.floor(cents / 100);
  const rest = cents % 100;
  return `$${dollars}.${rest < 10 ? "0" : ""}${rest}`;
}

function addProduct(inventory, product) {
  if (inventory.some((p) => p.id === product.id)) {
    throw new Error(`Product id ${product.id} already exists`);
  }
  return [...inventory, product];
}

function removeProduct(inventory, id) {
  if (!inventory.some((p) => p.id === id)) {
    throw new Error(`Unknown product id ${id}`);
  }
  return inventory.filter((p) => p.id !== id);
}

function updateStock(inventory, id, delta) {
  const product = inventory.find((p) => p.id === id);
  if (!product) {
    throw new Error(`Unknown product id ${id}`);
  }
  if (product.stock + delta < 0) {
    throw new Error(
      `Not enough stock for "${product.name}": have ${product.stock}, need ${-delta}`
    );
  }
  return inventory.map((p) => (p.id === id ? { ...p, stock: p.stock + delta } : p));
}

const lowStock = (inventory, threshold) =>
  inventory.filter((p) => p.stock <= threshold);
const totalValueCents = (inventory) =>
  inventory.reduce((sum, p) => sum + p.priceCents * p.stock, 0);

function sortBy(inventory, key, direction = "asc") {
  const sign = direction === "desc" ? -1 : 1;
  return [...inventory].sort((a, b) =>
    typeof a[key] === "number"
      ? sign * (a[key] - b[key])
      : sign * a[key].localeCompare(b[key])
  );
}

const inv = Object.freeze([
  Object.freeze({
    id: 1, name: "Pen", category: "stationery", priceCents: 1000, stock: 10,
  }),
  Object.freeze({
    id: 2, name: "Book", category: "stationery", priceCents: 25000, stock: 2,
  }),
  Object.freeze({
    id: 3, name: "Bag", category: "travel", priceCents: 90000, stock: 1,
  }),
  Object.freeze({
    id: 4, name: "Bottle", category: "travel", priceCents: 30000, stock: 0,
  }),
]);

console.log("Total value:", formatMoney(totalValueCents(inv)));
const low = lowStock(inv, 2).map((p) => `${p.name} (${p.stock})`);
console.log("Low stock:", low.join(", "));
const sold = updateStock(inv, 1, -3);
console.log("Pen stock:", sold[0].stock, "original:", inv[0].stock, sold[1] === inv[1]);
try {
  updateStock(inv, 2, -5);
} catch (error) {
  console.log("Error:", error.message);
}
const byPrice = sortBy(inv, "priceCents", "desc").map((p) => p.name);
console.log("By price desc:", byPrice.join(", "));
console.log(formatMoney(1250), formatMoney(5));
console.log(addProduct(inv, { id: 9 }).length, removeProduct(inv, 1).length);
try {
  addProduct(inv, { id: 1 });
} catch (error) {
  console.log("Error:", error.message);
}
```

```output
Total value: $1500.00
Low stock: Book (2), Bag (1), Bottle (0)
Pen stock: 7 original: 10 true
Error: Not enough stock for "Book": have 2, need 5
By price desc: Bag, Bottle, Book, Pen
$12.50 $0.05
5 3
Error: Product id 1 already exists
```

## Project 3: Expense analytics calculator

```js file="expenses.js" run
const round1 = (x) => Math.round(x * 10) / 10;
const money = (cents) => `$${(cents / 100).toFixed(2)}`;

function totalsByCategory(expenses) {
  const grand = expenses.reduce((s, e) => s + e.amountCents, 0);
  const map = expenses.reduce((m, e) => {
    const cur = m.get(e.category) ?? { category: e.category, totalCents: 0, count: 0 };
    return m.set(e.category, {
      ...cur,
      totalCents: cur.totalCents + e.amountCents,
      count: cur.count + 1,
    });
  }, new Map());
  return [...map.values()]
    .map((c) => ({ ...c, sharePercent: round1((c.totalCents / grand) * 100) }))
    .sort(
      (a, b) => b.totalCents - a.totalCents || a.category.localeCompare(b.category)
    );
}

function totalsByMonth(expenses) {
  const map = expenses.reduce((m, e) => {
    const month = e.date.slice(0, 7);
    return m.set(month, (m.get(month) ?? 0) + e.amountCents);
  }, new Map());
  return [...map.entries()].sort((a, b) => a[0].localeCompare(b[0]));
}

const biggestExpenses = (expenses, n) =>
  [...expenses].sort((a, b) => b.amountCents - a.amountCents).slice(0, n);

function averageDailySpend(expenses) {
  const days = new Set(expenses.map((e) => e.date)).size;
  const total = expenses.reduce((s, e) => s + e.amountCents, 0);
  return days === 0 ? 0 : Math.round(total / days);
}

const expenses = Object.freeze([
  {
    date: "2026-03-01", category: "rent", description: "March rent", amountCents: 90000,
  },
  { date: "2026-03-02", category: "food", description: "Groceries", amountCents: 4050 },
  {
    date: "2026-03-02",
    category: "transport",
    description: "Metro card",
    amountCents: 3000,
  },
  { date: "2026-03-05", category: "food", description: "Dinner", amountCents: 2500 },
  { date: "2026-02-20", category: "food", description: "Groceries", amountCents: 5000 },
  { date: "2026-02-25", category: "transport", description: "Taxi", amountCents: 1500 },
]);

const march = expenses.filter((e) => e.date.startsWith("2026-03"));
totalsByCategory(march).forEach((c) => {
  const share = c.sharePercent.toFixed(1).padStart(5);
  console.log(`${c.category.padEnd(10)} ${money(c.totalCents).padStart(8)} ${share}%`);
});
console.log(totalsByMonth(expenses).map(([m, c]) => `${m}: ${money(c)}`).join(" | "));
console.log(biggestExpenses(expenses, 2).map((e) => e.description).join(", "));
console.log(averageDailySpend(march), averageDailySpend([]), totalsByCategory([]));
```

```output
rent        $900.00  90.4%
food         $65.50   6.6%
transport    $30.00   3.0%
2026-02: $65.00 | 2026-03: $995.50
March rent, Groceries
33183 0 []
```

## Project 4: Library management system

```js file="library.js" run
const DUE_DAYS = 14;

function availableCopies(state, bookId) {
  const book = state.books.find((b) => b.id === bookId);
  if (!book) throw new Error(`Unknown book ${bookId}`);
  return book.copies - state.loans.filter((l) => l.bookId === bookId).length;
}

function borrow(state, bookId, memberId, today) {
  const book = state.books.find((b) => b.id === bookId);
  if (!book) throw new Error(`Unknown book ${bookId}`);
  if (!state.members.some((m) => m.id === memberId)) {
    throw new Error(`Unknown member ${memberId}`);
  }
  if (state.loans.some((l) => l.bookId === bookId && l.memberId === memberId)) {
    throw new Error(`Member ${memberId} already has "${book.title}"`);
  }
  if (availableCopies(state, bookId) <= 0) {
    throw new Error(`No copies of "${book.title}" are available`);
  }
  const loan = { bookId, memberId, dueDay: today + DUE_DAYS };
  return { ...state, loans: [...state.loans, loan] };
}

function giveBack(state, bookId, memberId) {
  const same = (l) => l.bookId === bookId && l.memberId === memberId;
  if (!state.loans.some(same)) {
    throw new Error("That book was not borrowed by that member");
  }
  const loans = state.loans.filter((l) => !same(l));
  return { ...state, loans };
}

function overdue(state, today) {
  const books = new Map(state.books.map((b) => [b.id, b]));
  const members = new Map(state.members.map((m) => [m.id, m]));
  return state.loans
    .filter((l) => l.dueDay < today)
    .map((l) => ({
      member: members.get(l.memberId).name,
      title: books.get(l.bookId).title,
      daysOverdue: today - l.dueDay,
    }));
}

function search(state, text) {
  const q = text.toLowerCase();
  return state.books.filter(
    (b) => b.title.toLowerCase().includes(q) || b.author.toLowerCase().includes(q)
  );
}

const start = Object.freeze({
  books: Object.freeze([
    { id: 1, title: "Dune", author: "Frank Herbert", copies: 2 },
    { id: 2, title: "Emma", author: "Jane Austen", copies: 1 },
  ]),
  members: Object.freeze([
    { id: 10, name: "Alice" },
    { id: 11, name: "Bob" },
  ]),
  loans: Object.freeze([]),
});

let state = borrow(start, 1, 10, 1);
console.log("Due day:", state.loans[0].dueDay);
console.log("Available Dune:", availableCopies(state, 1));
state = borrow(state, 2, 11, 2);
console.log("Original loans:", start.loans.length, "| now:", state.loans.length);

const attempts = [
  () => borrow(state, 2, 10, 3),
  () => borrow(state, 1, 10, 3),
  () => borrow(state, 99, 10, 3),
  () => borrow(state, 1, 99, 3),
  () => giveBack(state, 2, 10),
];
for (const attempt of attempts) {
  try {
    attempt();
  } catch (error) {
    console.log("Error:", error.message);
  }
}
console.log(overdue(state, 15).length, overdue(state, 16));
state = giveBack(state, 1, 10);
console.log(availableCopies(state, 1), search(state, "AUS").map((b) => b.title));
```

```output
Due day: 15
Available Dune: 1
Original loans: 0 | now: 2
Error: No copies of "Emma" are available
Error: Member 10 already has "Dune"
Error: Unknown book 99
Error: Unknown member 99
Error: That book was not borrowed by that member
0 [ { member: 'Alice', title: 'Dune', daysOverdue: 1 } ]
2 [ 'Emma' ]
```

## Project 5: Contact manager with search and filter

```js file="contacts.js" run
function validateContact(data) {
  const problems = [];
  if (!data.name || data.name.trim() === "") problems.push("Name is required");
  const at = (data.email ?? "").indexOf("@");
  const email = data.email ?? "";
  if (at < 1 || !email.slice(at).includes(".")) problems.push("Email is invalid");
  const digits = (data.phone ?? "").replace(/[\s-]/g, "");
  if (digits !== "" && !/^\d+$/.test(digits)) {
    problems.push("Phone must contain digits only");
  }
  return problems;
}

function addContact(list, data) {
  const problems = validateContact(data);
  if (problems.length > 0) throw new Error(problems.join("; "));
  const id = Math.max(0, ...list.map((c) => c.id)) + 1;
  return [...list, { id, tags: [], phone: "", ...data, name: data.name.trim() }];
}

const updateContact = (list, id, changes) =>
  list.map((c) => (c.id === id ? { ...c, ...changes } : c));
const deleteContact = (list, id) => list.filter((c) => c.id !== id);

function search(list, text) {
  const q = text.toLowerCase();
  return list.filter((c) =>
    [c.name, c.email, c.phone].some((field) => field.toLowerCase().includes(q))
  );
}

const filterByTags = (list, tags) =>
  list.filter((c) => tags.every((t) => c.tags.includes(t)));

function groupByInitial(list) {
  const sorted = [...list].sort((a, b) => a.name.localeCompare(b.name));
  return sorted.reduce((groups, c) => {
    const key = c.name[0].toUpperCase();
    return { ...groups, [key]: [...(groups[key] ?? []), c] };
  }, {});
}

function removeDuplicates(list) {
  const seen = new Set();
  return list.filter((c) => {
    const key = c.email.toLowerCase();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

const exportJson = (list) => JSON.stringify(list);

function importJson(text) {
  let data;
  try {
    data = JSON.parse(text);
  } catch (error) {
    throw new Error("Contacts data is not valid JSON");
  }
  if (!Array.isArray(data) || !data.every((c) => c && typeof c.name === "string")) {
    throw new Error("Contacts data has the wrong shape");
  }
  return data;
}

let list = [];
const add = (data) => {
  list = addContact(list, data);
};
add({ name: "Asha Rao", email: "asha@example.com", tags: ["friend"] });
add({ name: "Meera Das", email: "meera@example.com", tags: ["work", "friend"] });
add({ name: "Kabir Shah", email: "kabir@example.com", phone: "555-0100" });
add({ name: "Amit Roy", email: "AMIT@example.com" });
add({ name: "Amit R.", email: "amit@Example.com" });

console.log(search(list, "ASH").map((c) => c.name));
console.log(search(list, "0100").map((c) => c.name));
console.log(filterByTags(list, ["work", "friend"]).map((c) => c.name));
const groups = Object.entries(groupByInitial(list));
console.log(groups.map(([k, v]) => `${k} (${v.length})`).join(", "));
console.log(`Duplicates removed: ${list.length} -> ${removeDuplicates(list).length}`);
try {
  addContact(list, { name: " ", email: "nope" });
} catch (error) {
  console.log("Add failed:", error.message);
}
console.log(importJson(exportJson(list)).length === list.length);
for (const bad of ["{oops", '{"a":1}']) {
  try {
    importJson(bad);
  } catch (error) {
    console.log("Import failed:", error.message);
  }
}
const edited = updateContact(list, 1, { phone: "999" });
console.log(edited[0].phone, list[0].phone === "", edited[1] === list[1]);
console.log(deleteContact(list, 1).length);
```

```output
[ 'Asha Rao' ]
[ 'Kabir Shah' ]
[ 'Meera Das' ]
A (3), K (1), M (1)
Duplicates removed: 5 -> 4
Add failed: Name is required; Email is invalid
true
Import failed: Contacts data is not valid JSON
Import failed: Contacts data has the wrong shape
999 true true
4
```

::: note About regular expressions in Project 5
The reference uses two small regular expressions for phone validation. Students have not been taught them; accept `replaceAll` plus a loop with `"0123456789".includes(ch)` instead, and do not require regular expressions.
:::

# 8. Self-Assessment Answers

1. `3` and `undefined`.
2. `push` returns the new length; `splice(1, 1)` returns an array holding the removed element.
3. `a` is `[1, 2]`: `a` and `b` are the same array.
4. Yes, whenever `address` is a nested object: spread copies only the top level, so `c.address` and `o.address` are one object.
5. `[1, 2, 3].map((n) => n * 2)` and `[1, 2, 3].filter((n) => n % 2 === 1)`.
6. The new accumulator for the next step (and, after the last step, the final result).
7. `map` passes `(value, index, array)` and `parseInt` reads the index as its radix.
8. `[...[10, 9, 1]].sort((a, b) => a - b)`.
9. `const { name, age = 18 } = user;`
10. `0`, `5`, `5` and `undefined`.
11. Rest: `...args` in the parameter list. Spread: both `...args` inside the array literal.
12. `[...new Set(array)]`; a `Map` (or object) counter updated in a loop or `reduce`.
13. Object keys are converted to strings; a `Map` compares keys by identity (`SameValueZero`), so any value can be a key.
14. No: `Math.max(...[])` is `-Infinity`; guard for the empty array.
15. `function add(list, x) { return [...list, x]; }`
16. React decides whether state changed by comparing references, so a mutated array that keeps the same reference may not trigger a re-render.
17. The first imports a named export (braces, exact name); the second imports the default export (no braces, any local name).
