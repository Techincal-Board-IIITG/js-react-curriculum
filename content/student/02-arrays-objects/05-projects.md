# 11. Mini Projects

## Mini projects overview

Five data-processing programs, ordered from easier to harder. **Projects 1 to 3 are the core workload; projects 4 and 5 are extensions.** All five follow the same professional pattern: **pure functions in a module, a small `main` file that prints results, and tests written as `console.log` checks** (acceptance criteria give the expected values). None of them reads user input, which keeps the focus on arrays, objects and immutability; the stretch goals add interactivity using the `ask.mjs` helper from Sheet 01.

[[widths 0.5 2.2 1.2 1.1]]
| # | Project | Difficulty | Scope |
|---|---|---|---|
| 1 | Student marks analyzer | Easy | Core |
| 2 | Product inventory manager | Easy to medium | Core |
| 3 | Expense analytics calculator | Medium | Core |
| 4 | Library management system | Medium | Extension |
| 5 | Contact manager with search and filter | Medium to hard | Extension |

::: note Rules for every project
Do not mutate input data (freeze your test data with `Object.freeze` to check). Do not use index-based `for` loops where `map`, `filter`, `find`, `some`, `every` or `reduce` fits. Put logic in `*.mjs` modules with named exports and call them from `main.mjs`.
:::

:::: project Student marks analyzer | Difficulty: Easy | Core
##### Objective
Practise `map`, `filter`, `reduce`, `sort` and `find` on an array of objects, and design small pure functions.

##### Problem statement
You are given a class's marks. Produce an analysis: each student's average and grade, a ranking, the class average, and how many students fall into each grade.

##### Required features
- Starter data (extend it with at least six students):

```js file="students.mjs"
export const students = [
  { name: "Asha", marks: [82, 91, 77] },
  { name: "Ravi", marks: [45, 38, 52] },
  { name: "Meera", marks: [95, 88, 100] },
  { name: "Kabir", marks: [60, 71, 64] },
];
```

- `average(numbers)` returns the mean, or `0` for an empty list.
- `gradeFor(average)` returns `"A"` (90+), `"B"` (80+), `"C"` (70+), `"D"` (60+), `"E"` (40+) or `"F"`.
- `analyze(students)` returns `{ report, classAverage, topStudent, gradeCounts }`, where `report` is a new array of `{ name, average, grade }` sorted from highest average to lowest.
- `gradeCounts` is an object such as `{ A: 1, B: 1, D: 1, F: 1 }` listing only grades that occur.

##### Technical constraints
- No index-based loops. Use array methods only.
- `analyze` must not change `students` or any `marks` array (test with frozen data).
- Averages in the report are rounded to two decimal places as **numbers**.

##### Expected behavior
```text file="Sample output"
Ranking:
1. Meera  94.33  A
2. Asha   83.33  B
3. Kabir  65.00  D
4. Ravi   45.00  E
Class average: 71.92
Top student: Meera
Grade counts: { A: 1, B: 1, D: 1, E: 1 }
```

##### Suggested milestones
1. `average` and `gradeFor`, tested at the boundaries.
2. Map students to `{ name, average, grade }`.
3. Sort the report, compute the class average and the top student.
4. Build `gradeCounts` with `reduce`.
5. Print the formatted ranking in `main.mjs`.

##### Edge cases
- A student with no marks; an empty class; two students with identical averages (keep original order).
- Averages exactly on a grade boundary (`90`, `80`).
- Marks that are strings (decide whether to reject or convert them, and document the choice).

##### Acceptance criteria
- [ ] `average([80, 90])` returns `85`; `average([])` returns `0`.
- [ ] `gradeFor(90)` is `"A"`, `gradeFor(89.99)` is `"B"`, `gradeFor(39.9)` is `"F"`.
- [ ] The sample data gives the ranking above.
- [ ] Frozen input data does not cause an error.
- [ ] `analyze([])` returns an empty report and does not throw.

##### Stretch goals
- Per-subject analysis (the marks arrays are positional: subject 1, 2, 3).
- Identify the most improved student if each student has two exam arrays.
- Interactive version: add students with `ask()`.

##### Concepts practiced
Sections 2 to 4 and 7: array methods, callbacks, object construction, immutability.
::::

:::: project Product inventory manager | Difficulty: Easy to medium | Core
##### Objective
Practise immutable add, remove and update operations on an array of objects, and filtering and sorting.

##### Problem statement
Model a shop's inventory as an array of product objects. Write functions that return **new** inventories for each change and functions that answer questions about an inventory.

##### Required features
- Product shape: `{ id, name, category, priceCents, stock }`.
- `addProduct(inventory, product)`: rejects duplicate ids by throwing an `Error`.
- `removeProduct(inventory, id)` and `updateStock(inventory, id, delta)`: `delta` may be negative; stock may never go below zero (throw an `Error` instead).
- `lowStock(inventory, threshold)` returns products with `stock <= threshold`.
- `totalValueCents(inventory)` sums `priceCents * stock`.
- `sortBy(inventory, key, direction)` returns a sorted copy for string or numeric keys.
- `formatMoney(cents)` returns text such as `"$12.50"`.

##### Technical constraints
- Every change function returns a new array; the old inventory must be unchanged and unchanged products must be the **same objects**.
- Keep money in integer cents.
- Throw `Error` objects with clear messages; handle them in `main.mjs` with `try/catch`.

##### Expected behavior
```text file="Illustrative output (your numbers will differ)"
Total value: $1540.00
Low stock (<= 5): Book (2), Bottle (0)
After selling 3 pens: Pen stock = 7
Error: Not enough stock for "Book": have 2, need 5
Sorted by price (desc): Bag, Bottle, Book, Pen
```

##### Suggested milestones
1. Starter data and `formatMoney`.
2. The read-only queries (`lowStock`, `totalValueCents`, `sortBy`).
3. `addProduct` and `removeProduct`.
4. `updateStock` with its error cases.
5. `main.mjs` demonstrating every function, including the errors.

##### Edge cases
- Removing or updating an id that does not exist (decide: throw or no-op, and be consistent).
- Stock exactly `0`; a delta that makes stock exactly `0`.
- Sorting with equal keys (keep the original order); sorting by a missing key.
- A price that is not a whole number of cents.

##### Acceptance criteria
- [ ] After `updateStock(inv, 1, -3)`, the original `inv` still shows the old stock.
- [ ] Products not touched by an update are `===` to their originals.
- [ ] `updateStock` throws for a change that would make stock negative.
- [ ] `formatMoney(1250)` is `"$12.50"` and `formatMoney(5)` is `"$0.05"`.
- [ ] `lowStock(inv, 5)` includes products with stock exactly `5`.

##### Stretch goals
- Format totals with thousands separators (research `toLocaleString`).
- A `restock` report that proposes how many units to order to reach a target level.
- A menu interface with `ask()`.

##### Concepts practiced
Immutable updates (`map`, `filter`, spread), `reduce`, `sort` on a copy, error handling, modules.
::::

:::: project Expense analytics calculator | Difficulty: Medium | Core
##### Objective
Practise `reduce` into objects and `Map`s, grouping, percentages and sorting on realistic data.

##### Problem statement
Given a list of expenses, compute spending per category and per month, find the biggest expenses, and print a monthly report.

##### Required features
- Expense shape: `{ date: "2026-03-14", category, description, amountCents }`.
- `totalsByCategory(expenses)` returns an array of `{ category, totalCents, count, sharePercent }` sorted by total descending.
- `totalsByMonth(expenses)` groups by the first seven characters of `date` (use `slice(0, 7)`) and returns months in chronological order.
- `biggestExpenses(expenses, n)` returns the `n` largest.
- `averageDailySpend(expenses)` divides the total by the number of **distinct dates** that have at least one expense.
- `monthlyReport(expenses, month)` returns a printable multi-line string for one month.

##### Technical constraints
- Use `Map` or `reduce` for grouping; no index-based loops.
- Do not change the input array or its objects.
- Percentages are rounded to one decimal place and are numbers.
- Amounts are integer cents; format only when printing.

##### Expected behavior
```text file="Illustrative output (your numbers will differ)"
March 2026
  rent       $900.00   62.1%
  food       $410.50   28.3%
  transport  $140.00    9.6%
Total: $1,450.50   Days with spending: 9   Average per day: $161.17
Biggest: rent $900.00 (2026-03-01)
```

##### Suggested milestones
1. A dataset of at least 15 expenses across at least two months and four categories.
2. `totalsByCategory` with a hand-checked small example.
3. `totalsByMonth` and `averageDailySpend` (use a `Set` for distinct dates).
4. `biggestExpenses` (sort a copy).
5. `monthlyReport` and formatting.

##### Edge cases
- No expenses; a month with no expenses; one category only.
- Ties in category totals (sort alphabetically for a stable result).
- Percentages that do not add up to exactly 100 because of rounding (decide how to present this).
- Dates out of order in the input list.

##### Acceptance criteria
- [ ] Category shares add up to between 99.9 and 100.1 percent for non-empty data.
- [ ] `totalsByMonth` returns months in ascending order even if input is shuffled.
- [ ] `averageDailySpend([])` returns `0` without `NaN`.
- [ ] Input data is unchanged after every function is called.
- [ ] A hand calculation of one category total matches the program.

##### Stretch goals
- Month-over-month change per category (percentage up or down).
- Detect "unusual" expenses: more than twice the average of their category.
- A budget object per category, and a report of which budgets were exceeded.

##### Concepts practiced
`reduce`, `Map`, `Set`, `sort` with tie-breaks, rounding, immutability.
::::

:::: project Library management system | Difficulty: Medium | Extension
##### Objective
Model relationships between objects (books, members, loans) using immutable updates, lookup tables and meaningful errors.

##### Problem statement
Build the logic of a small library: members borrow and return books, loans have due dates, and the librarian can list overdue loans.

##### Required features
- A library state is `{ books, members, loans }`. Book: `{ id, title, author, copies }`. Member: `{ id, name }`. Loan: `{ bookId, memberId, dueDay }`, where `dueDay` is a whole number of days since the library opened.
- `borrow(state, bookId, memberId, today)`: creates a loan with `dueDay = today + 14`.
- `giveBack(state, bookId, memberId)`: removes that loan.
- `availableCopies(state, bookId)` is `copies` minus current loans of that book.
- `overdue(state, today)` returns loans past due with the member's name, book title and days overdue.
- `search(state, text)` finds books by title or author, case-insensitively.

##### Technical constraints
- Every function returns a **new state** and never mutates the old one.
- Throw an `Error` with a clear message for: unknown book or member, no copies available, a member borrowing the same book twice, returning a book that was not borrowed.
- Build `Map` lookups by id inside functions that need them; do not search with nested loops.

##### Expected behavior
```text file="Illustrative output (your numbers will differ)"
Alice borrows "Dune" on day 1 (due day 15)
Available copies of "Dune": 1
Error: No copies of "Emma" are available
Day 20 overdue: Alice has "Dune" (5 days overdue)
Search "aus": Emma by Jane Austen
```

##### Suggested milestones
1. Data model and `availableCopies`.
2. `borrow` with all its error checks.
3. `giveBack`.
4. `overdue` joining loans with members and books.
5. `search`, then a demonstration script covering each error.

##### Edge cases
- Borrowing the last copy; returning then re-borrowing; a book with `copies: 0`.
- A loan due exactly today (not overdue).
- Two members with the same name but different ids.
- A search for empty text (decide and document: everything or nothing).

##### Acceptance criteria
- [ ] The old state object is unchanged after `borrow` and `giveBack`.
- [ ] Every listed error case throws an `Error` with a distinct message.
- [ ] A loan due on day 15 is not overdue on day 15, but is `1` day overdue on day 16.
- [ ] `availableCopies` is correct after multiple borrows and returns.
- [ ] Searching is case-insensitive and matches author or title.

##### Stretch goals
- Per-member borrowing limit and a fine calculation.
- A reservation queue for books with no copies.
- Persist the state as JSON text and rebuild it (converting any `Map` to plain data first).

##### Concepts practiced
Immutable state updates, `Map` lookups, error design, joining related data, `find`/`filter`/`some`.
::::

:::: project Contact manager with search and filter | Difficulty: Medium to hard | Extension
##### Objective
Combine searching, filtering, sorting, grouping and validation in one data module, in the shape you will later put behind a React interface.

##### Problem statement
Manage a contact list: add and edit contacts with validation, search by text, filter by tag, group alphabetically, remove duplicates, and export or import the list as JSON text.

##### Required features
- Contact shape: `{ id, name, email, phone, tags }` where `tags` is an array of strings.
- `addContact(list, data)` validates (name required, email contains `@` and a dot after it, phone digits only after removing spaces and dashes) and returns a new list, or throws an `Error` listing the problems.
- `updateContact(list, id, changes)` and `deleteContact(list, id)`.
- `search(list, text)`: case-insensitive match on name, email or phone.
- `filterByTags(list, tags)`: contacts having **all** of the given tags.
- `groupByInitial(list)`: an object like `{ A: [...], B: [...] }`, with contacts sorted by name inside each group.
- `removeDuplicates(list)`: duplicates share the same email ignoring case; keep the first.
- `exportJson(list)` and `importJson(text)`; invalid JSON or wrong shape produces an `Error`, not a crash.

##### Technical constraints
- Pure functions; no mutation; unchanged contacts keep their identity.
- Validation lives in one function returning a list of problems; callers decide whether to throw.
- Use `try/catch` only where an error can really occur (`JSON.parse`, validation failures).

##### Expected behavior
```text file="Illustrative output (your numbers will differ)"
Search "ash": Asha Rao <asha@example.com>
Tag filter [work, friend]: Meera Das
Groups: A (2), K (1), M (1)
Added contact failed: Name is required; Email is invalid
Duplicates removed: 6 -> 5
Import failed: Contacts data is not valid JSON
```

##### Suggested milestones
1. Contact data, `validateContact`, and `addContact`.
2. `updateContact`, `deleteContact`, and their immutability tests.
3. `search` and `filterByTags`.
4. `groupByInitial` and `removeDuplicates`.
5. `exportJson` and `importJson` with its error handling.

##### Edge cases
- Names with leading spaces or lowercase first letters; names starting with a non-letter.
- Emails differing only by case; a contact with no tags; an empty tag filter (decide and document).
- Importing valid JSON that is not an array, or contacts missing fields.
- Searching text with regular-expression characters such as `.` or `(`.

##### Acceptance criteria
- [ ] Adding an invalid contact throws one `Error` whose message lists every problem.
- [ ] Search is case-insensitive and finds partial matches in name, email or phone.
- [ ] `filterByTags(list, ["work", "friend"])` returns only contacts with both tags.
- [ ] `removeDuplicates` keeps the first contact and is case-insensitive on email.
- [ ] `importJson(exportJson(list))` returns a list equal to the original.

##### Stretch goals
- Sort options (name, recently added) and a stable pagination function `page(list, pageNumber, pageSize)`.
- Merge duplicates by combining tags instead of discarding.
- Highlight matches in search results.

##### Concepts practiced
Everything in this sheet: array methods, objects, spread, `Set`, `Map`, optional chaining, immutability, modules, error handling, JSON.
::::
