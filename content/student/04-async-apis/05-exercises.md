# 11. Exercises

## Exercises overview and rules

Five sets, from recall to independent problem solving. Complete sets A to D in full; for set E complete at least one challenge. Solutions are in the instructor key. Use the acceptance criteria to check your own work, and run `node mock-server.mjs` in a separate terminal whenever an exercise calls `http://localhost:3001`.

::: tip How to check asynchronous code
Log when each operation **starts** and when it **finishes**, with a label. Most asynchronous bugs become obvious from the order of those lines. Use the `http.js` toolkit from Section 7 (put it in your exercise folder) so you do not rewrite `getJSON`.
:::

Work in `js-async/exercises/`, one `.mjs` file per exercise (top-level `await` needs a module).

## Set A: Comprehension questions

1. Why does JavaScript use asynchronous code for network requests instead of simply waiting?
2. Name the call stack, the task queue, the microtask queue and the event loop, and say in one sentence what each does.
3. In what order do the following run: synchronous code, `setTimeout(fn, 0)` callbacks, and promise `.then` callbacks? Why?
4. What are the three states of a promise? What does *settled* mean?
5. What does `.then()` return? What happens to the next link when a `.then` callback (a) returns a value, (b) returns a promise, (c) throws?
6. How does `.catch()` differ from `.finally()` in what it does to the chain's outcome?
7. What does an `async` function return? What does `await` do, and what does it **not** pause?
8. Why is `array.forEach(async ...)` a poor way to wait for several asynchronous tasks?
9. When does `fetch` reject, and when does it resolve with `ok: false`? Give an example of each.
10. Why must a `204` response not be parsed with `response.json()`?
11. Match methods to operations: list, read one, create, partial update, delete. Which are safe, and which are idempotent?
12. Explain the families 2xx, 4xx and 5xx, and which of them are worth retrying.
13. What is the difference between `Promise.all` and `Promise.allSettled`? Give a situation for each.
14. What is a stale-response (race condition) bug in a search box, and what are two ways to fix it?
15. What is debouncing? Why must the debounced function be created once?
16. Explain why a secret in front-end code is not a secret, and what you do instead.
17. What is CORS, who enforces it, and why is `mode: "no-cors"` not a fix?

## Set B: Syntax and output prediction

Write the **exact output** before running. B1 to B6 and B8 need only Node.js; B7 needs the mock server.

**B1.**

```js file="b1.mjs"
console.log("A");
setTimeout(() => console.log("B"), 0);
Promise.resolve().then(() => console.log("C"));
console.log("D");
```

**B2.**

```js file="b2.mjs"
async function f() {
  console.log("f1");
  await null;
  console.log("f2");
}
console.log("a");
f();
console.log("b");
```

**B3.**

```js file="b3.mjs"
Promise.resolve(1)
  .then((x) => x + 1)
  .then((x) => {
    x * 10;
  })
  .then((x) => console.log(x));
```

**B4.**

```js file="b4.mjs"
Promise.reject(new Error("e"))
  .catch(() => "fixed")
  .then((v) => console.log(v))
  .finally(() => console.log("f"));
```

**B5.**

```js file="b5.mjs"
const wait = (ms, value) => new Promise((r) => setTimeout(() => r(value), ms));
const results = await Promise.all([wait(20, "a"), wait(5, "b")]);
console.log(results);
```

**B6.**

```js file="b6.mjs"
const r = await Promise.allSettled([Promise.resolve(1), Promise.reject("no")]);
console.log(r.map((x) => x.status));
```

**B7.** The mock server answers `GET /todos/99` with status `404` and a JSON body.

```js file="b7.mjs"
try {
  const response = await fetch("http://localhost:3001/todos/99");
  console.log(response.status, response.ok);
  const body = await response.json();
  console.log(body.error);
} catch (error) {
  console.log("caught", error.name);
}
```

**B8.**

```js file="b8.mjs"
for (const n of [1, 2, 3]) {
  setTimeout(() => console.log("timer", n), 0);
  await null;
  console.log("loop", n);
}
```

## Set C: Small implementation exercises

#### C1. `delay(ms, value)`

**Problem.** Write a function that returns a promise which fulfils with `value` after `ms` milliseconds.

**Acceptance criteria.**

- `await delay(50, "hi")` gives `"hi"` after about 50 ms.
- `delay(10)` fulfils with `undefined`.
- Three calls started together with `Promise.all` finish in about the time of the longest.

**Hint.** `new Promise` with `setTimeout`; the `wait` helper from Section 3 is a starting point.

#### C2. `withTimeout(promise, ms)`

**Problem.** Return a promise that behaves like `promise`, but **rejects** with an `Error` whose `name` is `"TimeoutError"` if `promise` has not settled within `ms` milliseconds.

**Acceptance criteria.**

- `withTimeout(delay(10, "ok"), 100)` fulfils with `"ok"`.
- `withTimeout(delay(200, "late"), 20)` rejects with `error.name === "TimeoutError"`.
- The timer is cleared when the promise settles first, so the program can exit immediately.

**Hint.** `Promise.race`, and `clearTimeout` in a `finally`.

#### C3. `getTodoOrNull(id)`

**Problem.** Using `fetch` and the mock server, return the to-do object for `id`, or `null` if the server answers `404`. For any other failure (other statuses, network errors) the function must **throw**.

**Acceptance criteria.**

- `getTodoOrNull(1)` resolves with an object whose `title` is `"Buy milk"`.
- `getTodoOrNull(99)` resolves with `null`.
- With the server stopped, the call rejects (it does not return `null`).
- The function uses `response.ok` or `response.status`, not a blanket `try/catch` that hides every error.

**Hint.** Check `response.status === 404` before `response.ok`.

#### C4. `loadDashboard()`

**Problem.** Load `GET /todos` and `GET /weather?city=Pune` **in parallel**. Return `{ todos, weather, errors }`. If one request fails, its field is `null` and a message is added to `errors`; the other still appears.

**Acceptance criteria.**

- With the mock server running, `errors` is empty and both fields are filled.
- Replace the city with `Atlantis`: `weather` is `null`, `errors` has one message, and `todos` is still filled.
- Total time is about the slowest single request, not the sum.

**Hint.** `Promise.allSettled`.

#### C5. `retry(task, times)`

**Problem.** Call `task()` (a function returning a promise). If it rejects, call it again, up to `times` additional attempts, and return the first success. If every attempt fails, throw the **last** error.

**Acceptance criteria.**

- A task that fails twice then succeeds, with `times = 3`, is called exactly 3 times and resolves.
- A task that always fails, with `times = 2`, is called exactly 3 times and the last error is thrown.
- A task that succeeds immediately is called once.

**Hint.** A loop with `try/catch` around `await task()`.

#### C6. `makeLatestOnly()`

**Problem.** Write a function that returns a wrapper `latestOnly(promiseFactory)`. When several calls overlap, only the **most recent** call's result is delivered; results of older calls are **ignored** (the wrapper's promise for an older call resolves to the string `"stale"`).

**Acceptance criteria.**

- Starting a slow call and then a fast call: the fast call's value is delivered, the slow call gives `"stale"`.
- A single call delivers its value normally.
- Starting a new call after the previous one finished works normally.

**Hint.** A shared counter, as in the stale-response example.

## Set D: Debugging exercises

Each snippet is broken. State the **evidence**, your **hypothesis**, the **fix** and *why* it was wrong.

**D1. The 404 that looked like success.**

```js file="d1.mjs"
const response = await fetch("http://localhost:3001/todos/99");
const todo = await response.json();
console.log("Loaded:", todo.title.toUpperCase());
```

*Expected:* a clear message "Todo 99 not found" instead of a crash.

**D2. The missing title.**

```js file="d2.mjs"
async function loadTitle(id) {
  const response = await fetch(`http://localhost:3001/todos/${id}`);
  return response.json().title;
}
console.log(await loadTitle(1));
```

*Expected:* `Buy milk`.

**D3. The total that stays zero.**

```js file="d3.mjs"
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
let total = 0;
[10, 20, 30].forEach(async (n) => {
  await wait(5);
  total += n;
});
console.log("total:", total);
```

*Expected:* `total: 60`.

**D4. The server says the title is missing.**

```js file="d4.mjs"
const response = await fetch("http://localhost:3001/todos", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: { title: "Water plants" },
});
console.log(response.status);
```

*Expected:* `201`.

**D5. Old results winning.**

```js file="d5.mjs"
let shown = "";
async function search(term) {
  const response = await fetch(`http://localhost:3001/shows?q=${term}`);
  const hits = await response.json();
  shown = `${term}: ${hits.length}`;
}
const a = search("s");
const b = search("space c");
await Promise.all([a, b]);
console.log(shown);
```

*Expected:* `space c: 1`.

## Set E: Challenges

#### E1. `fetchAll(urls, options)`

**Problem.** Fetch many URLs with at most `limit` requests in flight at once, retrying retryable failures (network errors, `429`, `5xx`) up to `retries` times, and return an array **in the same order as `urls`** of `{ url, ok: true, data }` or `{ url, ok: false, error }`.

**Acceptance criteria.**

- With 8 URLs and `limit: 3`, never more than 3 requests are active at once (prove it with a counter).
- Results are in input order, regardless of completion order.
- A `404` is **not** retried; `/flaky` succeeds after retries.
- One failing URL does not stop the others.

#### E2. `poll(task, options)`

**Problem.** Call `task()` repeatedly every `intervalMs` until `until(result)` returns `true`, or until an `AbortSignal` passed as `options.signal` is aborted, or until `maxAttempts` is reached. Resolve with the last result when the condition is met; reject with an `AbortError` if aborted; reject with an `Error` if attempts run out.

**Acceptance criteria.**

- Polling `/todos/1` until `completed` is `true` returns immediately on the first attempt.
- Polling a PATCH-driven change (the test changes the item after 300 ms) stops soon after it happens.
- Aborting the signal during a wait stops further requests at once.
- At most one request is in flight at any moment (no overlapping calls).
