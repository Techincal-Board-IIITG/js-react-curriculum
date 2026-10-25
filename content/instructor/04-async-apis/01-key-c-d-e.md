# 4. Set C: Reference Solutions

#### C1. `delay(ms, value)`

```js file="c1.mjs" run
function delay(ms, value) {
  return new Promise((resolve) => setTimeout(() => resolve(value), ms));
}

console.log(await delay(20, "hi"), await delay(5));

const start = Date.now();
await Promise.all([delay(60), delay(60), delay(60)]);
console.log("three together took under 150 ms:", Date.now() - start < 150);
```

```output
hi undefined
three together took under 150 ms: true
```

#### C2. `withTimeout(promise, ms)`

```js file="c2.mjs" run
const delay = (ms, value) =>
  new Promise((resolve) => setTimeout(() => resolve(value), ms));

function withTimeout(promise, ms) {
  let timer;
  const timeout = new Promise((resolve, reject) => {
    timer = setTimeout(() => {
      const error = new Error(`Timed out after ${ms} ms`);
      error.name = "TimeoutError";
      reject(error);
    }, ms);
  });
  return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
}

console.log(await withTimeout(delay(10, "ok"), 100));

try {
  await withTimeout(delay(200, "late"), 20);
} catch (error) {
  console.log(error.name, "-", error.message);
}
```

```output
ok
TimeoutError - Timed out after 20 ms
```

`Promise.race` settles with whichever of the two promises settles first. The `finally` clears the timer when the real promise wins, so a pending timer does not keep the program alive. Note that a race stops *waiting* for the slow promise; it does not cancel it (an `AbortSignal` would).

#### C3. `getTodoOrNull(id)`

```js file="c3.mjs" run mock
const BASE = "http://localhost:3001";

async function getTodoOrNull(id, base = BASE) {
  const response = await fetch(`${base}/todos/${id}`);
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}

console.log((await getTodoOrNull(1)).title, await getTodoOrNull(99));

try {
  await getTodoOrNull(1, "http://localhost:1");
} catch (error) {
  console.log("network failure is not hidden:", error.name);
}
```

```output
Buy milk null
network failure is not hidden: TypeError
```

Only `404` becomes `null`; every other failure is surfaced. A student solution that wraps the whole function in `try/catch` and returns `null` for everything fails the third acceptance criterion.

#### C4. `loadDashboard()`

```js file="c4.mjs" run mock
const BASE = "http://localhost:3001";

async function get(path) {
  const response = await fetch(BASE + path);
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.error ?? `HTTP ${response.status}`);
  }
  return body;
}

async function loadDashboard(city) {
  const [todos, weather] = await Promise.allSettled([
    get("/todos"),
    get(`/weather?city=${encodeURIComponent(city)}`),
  ]);
  const errors = [];
  for (const result of [todos, weather]) {
    if (result.status === "rejected") {
      errors.push(result.reason.message);
    }
  }
  return {
    todos: todos.status === "fulfilled" ? todos.value : null,
    weather: weather.status === "fulfilled" ? weather.value : null,
    errors,
  };
}

const ok = await loadDashboard("Pune");
console.log(ok.todos.length, ok.weather.condition, ok.errors.length);

const partial = await loadDashboard("Atlantis");
console.log(partial.todos.length, partial.weather, partial.errors.join("; "));
```

```output
3 Sunny 0
3 null City not found
```

#### C5. `retry(task, times)`

```js file="c5.mjs" run
async function retry(task, times) {
  let lastError;
  for (let attempt = 0; attempt <= times; attempt++) {
    try {
      return await task();
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError;
}

let calls = 0;
const flaky = async () => {
  calls++;
  if (calls < 3) throw new Error("fail " + calls);
  return "ok";
};
console.log(await retry(flaky, 3), calls);

let always = 0;
try {
  await retry(async () => {
    always++;
    throw new Error("always " + always);
  }, 2);
} catch (error) {
  console.log("calls:", always, "last error:", error.message);
}

let once = 0;
await retry(async () => ++once, 5);
console.log("immediate success calls:", once);
```

```output
ok 3
calls: 3 last error: always 3
immediate success calls: 1
```

#### C6. `makeLatestOnly()`

```js file="c6.mjs" run
const delay = (ms, value) =>
  new Promise((resolve) => setTimeout(() => resolve(value), ms));

function makeLatestOnly() {
  let latest = 0;
  return async (promiseFactory) => {
    const mine = ++latest;
    const value = await promiseFactory();
    return mine === latest ? value : "stale";
  };
}

const latestOnly = makeLatestOnly();
const [slow, fast] = await Promise.all([
  latestOnly(() => delay(50, "slow")),
  latestOnly(() => delay(10, "fast")),
]);
console.log(slow, fast);
console.log(await latestOnly(() => delay(5, "alone")));
```

```output
stale fast
alone
```

# 5. Set D: Debugging Explanations

**D1.** `fetch` resolved with a `404`, and `response.json()` parsed the server's **error** object, which has no `title`, so `todo.title.toUpperCase()` throws. Check `response.ok` (or the status) first.

```js file="d1-fixed.mjs" run mock
const response = await fetch("http://localhost:3001/todos/99");
if (response.status === 404) {
  console.log("Todo 99 not found");
} else if (!response.ok) {
  console.log("Server problem:", response.status);
} else {
  const todo = await response.json();
  console.log("Loaded:", todo.title.toUpperCase());
}
```

```output
Todo 99 not found
```

**D2.** `response.json()` returns a promise; `.title` of a promise is `undefined`. `await` the call first.

```js file="d2-fixed.mjs" run mock
async function loadTitle(id) {
  const response = await fetch(`http://localhost:3001/todos/${id}`);
  const todo = await response.json();
  return todo.title;
}
console.log(await loadTitle(1));
```

```output
Buy milk
```

**D3.** `forEach` does not wait for `async` callbacks, so `total` is printed before any addition happens. Use `Promise.all` with `map` (or `for...of`).

```js file="d3-fixed.mjs" run
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
let total = 0;
await Promise.all(
  [10, 20, 30].map(async (n) => {
    await wait(5);
    total += n;
  })
);
console.log("total:", total);
```

```output
total: 60
```

**D4.** A plain object in `body` becomes the text `[object Object]`, so the server sees no title. Use `JSON.stringify`.

```js file="d4-fixed.mjs" run mock
const response = await fetch("http://localhost:3001/todos", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ title: "Water plants" }),
});
console.log(response.status);
```

```output
201
```

**D5.** The slow request for `"s"` finishes after the one for `"space c"` and overwrites `shown`. Ignore outdated answers (a counter) or abort the earlier request.

```js file="d5-fixed.mjs" run mock
let shown = "";
let latest = 0;

async function search(term) {
  const mine = ++latest;
  const response = await fetch(
    `http://localhost:3001/shows?q=${encodeURIComponent(term)}`
  );
  const hits = await response.json();
  if (mine !== latest) return;
  shown = `${term}: ${hits.length}`;
}

const a = search("s");
const b = search("space c");
await Promise.all([a, b]);
console.log(shown);
```

```output
space c: 1
```

# 6. Set E: Challenge Solutions

#### E1. `fetchAll(urls, options)`

```js file="e1.mjs" run mock
const BASE = "http://localhost:3001";
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function fetchOne(url, retries, delayMs) {
  let attempt = 0;
  while (true) {
    try {
      const response = await fetch(url);
      const text = await response.text();
      const data = text === "" ? null : JSON.parse(text);
      if (response.ok) {
        return { url, ok: true, data };
      }
      const error = new Error(data?.error ?? `HTTP ${response.status}`);
      error.status = response.status;
      throw error;
    } catch (error) {
      const retryable =
        error.status === undefined
          ? error instanceof TypeError
          : error.status === 429 || error.status >= 500;
      attempt++;
      if (!retryable || attempt > retries) {
        return { url, ok: false, error: error.message };
      }
      await wait(delayMs * 2 ** (attempt - 1));
    }
  }
}

async function fetchAll(urls, { limit = 3, retries = 2, delayMs = 10 } = {}) {
  const results = new Array(urls.length);
  let next = 0;

  async function runner() {
    while (next < urls.length) {
      const index = next++;
      results[index] = await fetchOne(urls[index], retries, delayMs);
    }
  }

  await Promise.all(Array.from({ length: Math.min(limit, urls.length) }, runner));
  return results;
}

let active = 0;
let maxActive = 0;
const realFetch = globalThis.fetch;
globalThis.fetch = async (...args) => {
  active++;
  maxActive = Math.max(maxActive, active);
  try {
    return await realFetch(...args);
  } finally {
    active--;
  }
};

const urls = [
  "/todos/1",
  "/slow?ms=40",
  "/slow?ms=40",
  "/slow?ms=40",
  "/todos/99",
  "/flaky",
  "/weather?city=Pune",
  "/todos/2",
].map((path) => BASE + path);

const results = await fetchAll(urls, { limit: 3, retries: 2 });
console.log(results.map((r) => (r.ok ? "ok" : r.error)).join(" | "));
console.log("first result is /todos/1:", results[0].data.title);
console.log("last result is /todos/2:", results[7].data.title);
console.log("max concurrent requests <= 3:", maxActive <= 3);
```

```output
ok | ok | ok | ok | Todo not found | ok | ok | ok
first result is /todos/1: Buy milk
last result is /todos/2: Write report
max concurrent requests <= 3: true
```

The 404 is returned immediately as a failure (not retried), while `/flaky` fails twice with `503` and succeeds on the third try. The counter wraps `fetch` itself to *prove* the concurrency limit. Results are written by index, so their order is the input order whatever the completion order.

#### E2. `poll(task, options)`

```js file="e2.mjs" run mock
const BASE = "http://localhost:3001";

function sleep(ms, signal) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(resolve, ms);
    signal?.addEventListener(
      "abort",
      () => {
        clearTimeout(timer);
        reject(signal.reason);
      },
      { once: true }
    );
  });
}

async function poll(task, options = {}) {
  const { intervalMs = 100, until, signal, maxAttempts = 20 } = options;
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    signal?.throwIfAborted();
    const result = await task();
    if (until(result)) {
      return result;
    }
    if (attempt < maxAttempts) {
      await sleep(intervalMs, signal);
    }
  }
  throw new Error(`Gave up after ${maxAttempts} attempts`);
}

const getTodo = async (id) => (await fetch(`${BASE}/todos/${id}`)).json();

let calls = 0;
const first = await poll(
  async () => {
    calls++;
    return getTodo(1);
  },
  { intervalMs: 30, until: (t) => t.completed }
);
console.log("already done:", first.title, "after", calls, "call");

setTimeout(() => {
  fetch(`${BASE}/todos/2`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ completed: true }),
  });
}, 150);
let attempts = 0;
const changed = await poll(
  async () => {
    attempts++;
    return getTodo(2);
  },
  { intervalMs: 40, until: (t) => t.completed }
);
const several = attempts >= 3;
console.log("noticed the change:", changed.completed, "after several calls:", several);

const controller = new AbortController();
let requests = 0;
setTimeout(() => controller.abort(), 100);
try {
  await poll(
    async () => {
      requests++;
      return getTodo(3);
    },
    { intervalMs: 30, until: (t) => t.completed, signal: controller.signal }
  );
} catch (error) {
  const before = requests;
  await sleep(150);
  console.log(error.name, "| no more requests after abort:", requests === before);
}

try {
  const never = (t) => t.completed;
  await poll(() => getTodo(3), { intervalMs: 5, until: never, maxAttempts: 3 });
} catch (error) {
  console.log(error.message);
}
```

```output
already done: Buy milk after 1 call
noticed the change: true after several calls: true
AbortError | no more requests after abort: true
Gave up after 3 attempts
```

The loop is **sequential**: the next call is only made after the previous one finished and the sleep elapsed, so at most one request is ever in flight. The abort listener cancels the pending sleep and rejects with the signal's reason (an `AbortError`), and `throwIfAborted()` at the top of each iteration stops an already-sleeping loop that was aborted between checks.
