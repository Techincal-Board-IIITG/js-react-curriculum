---
number: 04
title: Answer Key for Asynchronous JavaScript and APIs
subtitle: Solutions, expected outputs, debugging explanations and reference implementations
track: instructor
kind: instructor
label: INSTRUCTOR ANSWER KEY - SHEET 04
time: Do not distribute to students
edition: Instructor edition
goals:
  - Check answers to comprehension and prediction exercises
  - Compare student code with reference solutions executed against the mock server
  - Use the debugging explanations when students are stuck
  - Run the reference applications for all five mini projects
---

# 1. How to Use This Key

Every listing with an *Output* panel was **executed by the build validator**: Node.js examples in Node, browser pages in headless Chromium, and all network calls against the mock server from the student sheet (restarted and reset before every example, so results are deterministic). Reference solutions are one correct approach; grade against the acceptance criteria in the student sheet. Timing-dependent examples print only comparisons that do not vary from run to run.

::: note Running the examples yourself
Start the student sheet's `mock-server.mjs` (`node mock-server.mjs`) and save the `http.js` toolkit next to the solutions. Each listing here is a complete `.mjs` file unless it says otherwise.
:::

# 2. Set A: Comprehension Answers

1. A network request can take long; waiting on the single JavaScript thread would freeze the page, so slow work is handed to the environment and the result returns via a callback.
2. Call stack: the functions currently running. Task queue: queued timer, event and I/O callbacks (one per loop turn). Microtask queue: promise callbacks, all drained before the next task. Event loop: moves queued callbacks onto the stack when it is empty.
3. Synchronous code first; then all promise callbacks (microtasks); then `setTimeout` callbacks (tasks). Microtasks drain after the current script and after every task.
4. Pending, fulfilled, rejected. Settled means fulfilled or rejected; a settled promise never changes.
5. A new promise. (a) A returned value fulfils it; (b) a returned promise is adopted (the new promise follows it); (c) a thrown error rejects it.
6. `.catch` handles a rejection and, if its callback returns normally, **recovers** the chain. `.finally` runs either way for cleanup, receives no argument, and passes the original outcome through unchanged.
7. A promise. `await` pauses only the surrounding async function (its later lines run as a microtask once the promise settles); the rest of the program continues.
8. `forEach` ignores the promises its callback returns, so it neither waits nor lets you catch errors; use `for...of` (sequential) or `Promise.all(list.map(async ...))` (parallel).
9. `fetch` rejects when the request cannot be completed (offline, DNS, refused connection, CORS block, abort). It resolves with `ok: false` for HTTP statuses such as 404 or 500.
10. A `204` has no body; `.json()` on an empty body throws a `SyntaxError`.
11. List `GET /items`, read one `GET /items/3`, create `POST`, partial update `PATCH`, delete `DELETE`. Safe: `GET`. Idempotent: `GET`, `PUT`, `DELETE`.
12. 2xx success; 4xx the client's mistake (do not retry unchanged); 5xx server trouble (a retry may help); also `429` is worth retrying after waiting.
13. `all` fulfils with every value and fails fast on the first rejection; use when all are required. `allSettled` reports every outcome; use when partial results are acceptable.
14. An older, slower response arrives after a newer one and overwrites it. Fixes: abort the previous request, or tag requests with a counter and ignore outdated answers.
15. Delaying an action until events stop for a set time. A debounced function keeps its timer in a closure, so a new one per event would have separate timers and debounce nothing.
16. Anything shipped to the browser can be read by every user; keep secrets on a server and let the page call your server.
17. CORS is a policy enforced by the **browser**; servers grant permission with headers. `mode: "no-cors"` only yields an unreadable opaque response and hides the error.

# 3. Set B: Predicted Outputs

```js file="b1.mjs" run
console.log("A");
setTimeout(() => console.log("B"), 0);
Promise.resolve().then(() => console.log("C"));
console.log("D");
```

```output
A
D
C
B
```

Synchronous `A` and `D` first, then the microtask `C`, then the timer task `B`.

```js file="b2.mjs" run
async function f() {
  console.log("f1");
  await null;
  console.log("f2");
}
console.log("a");
f();
console.log("b");
```

```output
a
f1
b
f2
```

`f()` runs synchronously up to its first `await`, so `f1` appears before `b`; `f2` is a microtask after the script.

```js file="b3.mjs" run
Promise.resolve(1)
  .then((x) => x + 1)
  .then((x) => {
    x * 10;
  })
  .then((x) => console.log(x));
```

```output
undefined
```

The second callback has a block body with no `return`, so the next link receives `undefined`.

```js file="b4.mjs" run
Promise.reject(new Error("e"))
  .catch(() => "fixed")
  .then((v) => console.log(v))
  .finally(() => console.log("f"));
```

```output
fixed
f
```

`.catch` recovers with `"fixed"`; `.finally` then runs.

```js file="b5.mjs" run
const wait = (ms, value) => new Promise((r) => setTimeout(() => r(value), ms));
const results = await Promise.all([wait(20, "a"), wait(5, "b")]);
console.log(results);
```

```output
[ 'a', 'b' ]
```

Results keep **input order**, not completion order.

```js file="b6.mjs" run
const r = await Promise.allSettled([Promise.resolve(1), Promise.reject("no")]);
console.log(r.map((x) => x.status));
```

```output
[ 'fulfilled', 'rejected' ]
```

```js file="b7.mjs" run mock
try {
  const response = await fetch("http://localhost:3001/todos/99");
  console.log(response.status, response.ok);
  const body = await response.json();
  console.log(body.error);
} catch (error) {
  console.log("caught", error.name);
}
```

```output
404 false
Todo not found
```

A 404 is a resolved `fetch`; nothing is thrown, so `caught` is never printed.

```js file="b8.mjs" run
for (const n of [1, 2, 3]) {
  setTimeout(() => console.log("timer", n), 0);
  await null;
  console.log("loop", n);
}
```

```output
loop 1
loop 2
loop 3
timer 1
timer 2
timer 3
```

Each `await null` only yields to the microtask queue, which is drained before any timer task, so all three loop lines print before any timer.
