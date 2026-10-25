# 7. Reliable Error Handling, Timeouts and Retries

## Learning objectives for this section

- Classify the ways a request can fail and choose the right reaction to each.
- Turn technical errors into messages a user can act on.
- Add timeouts, and retry only the failures that deserve a retry, with a limit and a pause.

## Conceptual explanation

A request that depends on a network can fail in many ways, and "show an error" is not one design but several. Think of the failures in families:

[[widths 1.5 2.2 2.6]]
| Failure | How it appears | Reasonable reaction |
|---|---|---|
| **Network failure** (offline, DNS, refused, CORS block) | `fetch` rejects with a `TypeError` | Tell the user to check the connection; allow retry |
| **Timeout** | Your own timer aborts the request (`TimeoutError`) | Say the server is slow; allow retry |
| **Client error `4xx`** | `fetch` resolves, `ok` is `false` | **Do not retry the same request.** Fix the request or tell the user what to correct |
| **Rate limit `429`** | `ok` is `false`, often with `Retry-After` | Wait as instructed, then retry |
| **Server error `5xx`** | `ok` is `false` | Retry a few times (the fault may be temporary), then give up |
| **Bad body** | `response.json()` rejects with `SyntaxError` | Report a data problem; retrying rarely helps |
| **User cancelled** | `AbortError` | Not an error to show (Section 9) |

## A small toolkit

Save this as `http.js`. It gathers the helpers from this sheet: `wait`, `getJSON` (Section 6, now also recording a `Retry-After` header), `describeError` (friendly messages), `isRetryable` and `withRetry`.

```js file="http.js" bundle=net
export const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export async function getJSON(url, options) {
  const response = await fetch(url, options);
  const text = await response.text();

  let data = null;
  if (text !== "") {
    try {
      data = JSON.parse(text);
    } catch (error) {
      data = text;
    }
  }

  if (!response.ok) {
    const message = data?.error ?? data?.message ?? `HTTP ${response.status}`;
    const failure = new Error(message);
    failure.status = response.status;
    const retryAfter = Number(response.headers.get("retry-after"));
    if (Number.isFinite(retryAfter) && retryAfter > 0) {
      failure.retryAfter = retryAfter;
    }
    throw failure;
  }
  return data;
}

export function describeError(error) {
  if (error.name === "TimeoutError") return "The server took too long to answer.";
  if (error.name === "AbortError") return "Request cancelled.";
  if (error.status === 404) return "Not found.";
  if (error.status === 429) return "Too many requests. Please wait a moment.";
  if (error.status >= 500) return "The server had a problem. Try again later.";
  if (error.status >= 400) return `The request was rejected (${error.status}).`;
  if (error instanceof TypeError) return "Network problem. Check your connection.";
  return "Unexpected error.";
}

export function isRetryable(error) {
  if (error.name === "AbortError") return false;
  if (error.name === "TimeoutError") return true;
  if (error.status === undefined) return error instanceof TypeError;
  return error.status === 429 || error.status >= 500;
}

export async function withRetry(task, options = {}) {
  const { retries = 3, delayMs = 200, respectRetryAfter = true } = options;
  let attempt = 0;
  while (true) {
    try {
      return await task(attempt);
    } catch (error) {
      attempt++;
      if (attempt > retries || !isRetryable(error)) {
        throw error;
      }
      const backoff = delayMs * 2 ** (attempt - 1);
      const useHeader = respectRetryAfter && error.retryAfter;
      const pause = useHeader ? error.retryAfter * 1000 : backoff;
      await wait(Math.min(pause, 5000));
    }
  }
}
```

**Reading `withRetry`.** It calls `task`; on success it returns the result. On failure it counts the attempt and **stops (rethrows)** if the retry budget is spent *or* the error is not retryable, so a `404` is never repeated. Otherwise it pauses and loops. The pause uses **exponential backoff**: `delayMs * 2 ** (attempt - 1)` is 200 ms, 400 ms, 800 ms, and so on, so a struggling server gets progressively more breathing room; if the server sent `Retry-After`, that value wins; and no pause exceeds 5 seconds.

## Friendly messages

```js file="describe-errors.js" run mock bundle=net
import { getJSON, describeError } from "./http.js";

const BASE = "http://localhost:3001";
const within = (ms) => ({ signal: AbortSignal.timeout(ms) });
const cases = [
  ["404", () => getJSON(`${BASE}/status/404`)],
  ["429", () => getJSON(`${BASE}/status/429`)],
  ["503", () => getJSON(`${BASE}/status/503`)],
  ["400", () => getJSON(`${BASE}/status/400`)],
  ["offline", () => getJSON("http://localhost:1/")],
  ["timeout", () => getJSON(`${BASE}/slow?ms=500`, within(50))],
];

for (const [name, run] of cases) {
  try {
    await run();
    console.log(name, "-> ok");
  } catch (error) {
    console.log(`${name} -> ${error.name}: ${describeError(error)}`);
  }
}
```

```output
404 -> Error: Not found.
429 -> Error: Too many requests. Please wait a moment.
503 -> Error: The server had a problem. Try again later.
400 -> Error: The request was rejected (400).
offline -> TypeError: Network problem. Check your connection.
timeout -> TimeoutError: The server took too long to answer.
```

Each case triggers a different kind of failure and prints the error's `name` next to the message a user would see. Raw messages such as `fetch failed` or `HTTP 503` mean nothing to a user; `describeError` translates them. Note the order of the checks: `error.status` is `undefined` for network errors, so comparisons like `undefined >= 500` are `false` and the function falls through to the `TypeError` test.

## Timeouts

`fetch` has **no timeout of its own**: a server that never answers keeps your promise pending (and your spinner spinning) indefinitely. Add one with `AbortSignal.timeout(ms)`, a signal that aborts itself after the delay; when it fires, `fetch` rejects with an error named **`TimeoutError`**, as the `timeout` case above shows. Create the signal **at the moment of the request** (as `within(50)` does when called): a timeout signal starts its clock when it is created, not when it is used. (Wrapping the request in `Promise.race` with a timer would stop *waiting* but would not stop the request itself; the signal does both.)

## Retrying

```js file="retry-demo.js" run mock bundle=net
import { getJSON, withRetry } from "./http.js";

const BASE = "http://localhost:3001";

let attempts = 0;
const data = await withRetry(
  async () => {
    attempts++;
    return getJSON(`${BASE}/flaky`);
  },
  { retries: 3, delayMs: 20, respectRetryAfter: false }
);
console.log("succeeded after", attempts, "attempts:", data);

let tries = 0;
try {
  await withRetry(async () => {
    tries++;
    return getJSON(`${BASE}/status/404`);
  });
} catch (error) {
  console.log("gave up after", tries, "try:", error.status);
}

let hits = 0;
try {
  await withRetry(
    async () => {
      hits++;
      return getJSON(`${BASE}/status/503`);
    },
    { retries: 2, delayMs: 10, respectRetryAfter: false }
  );
} catch (error) {
  console.log("503 retried", hits - 1, "times, then failed:", error.status);
}

for (let i = 1; i <= 4; i++) {
  try {
    const result = await getJSON(`${BASE}/limited`);
    console.log(i, "ok, call", result.call);
  } catch (error) {
    console.log(i, error.status, "retry after", error.retryAfter, "second");
  }
}
```

```output
succeeded after 3 attempts: { ok: true, attempt: 3 }
gave up after 1 try: 404
503 retried 2 times, then failed: 503
1 ok, call 1
2 ok, call 2
3 ok, call 3
4 429 retry after 1 second
```

The `/flaky` endpoint fails twice with `503` and then succeeds, so the task runs three times and `withRetry` returns the third result. The `404` is **not retryable**, so it is thrown after one try. A permanently failing `503` is retried twice and then the last error is thrown, so the program never loops forever. The final loop shows what the `429` answer carries: the status and a `Retry-After` of one second that `withRetry` would honour if you let it.

## A browser page that reports errors in plain words

```html file="index.html" page mock bundle=net ignore="Failed to load resource" steps="click #go | wait 200 | print #message | select #scenario /status/404 | click #go | wait 200 | print #message | select #scenario /status/503 | click #go | wait 200 | print #message"
<!DOCTYPE html>
<html lang="en">
  <body>
    <select id="scenario">
      <option value="/todos/1">Works</option>
      <option value="/status/404">Missing</option>
      <option value="/status/503">Server down</option>
    </select>
    <button id="go">Load</button>
    <p id="message"></p>
    <script type="module">
      import { getJSON, describeError } from "./http.js";

      const BASE = "http://localhost:3001";
      const scenario = document.getElementById("scenario");
      const message = document.getElementById("message");
      const button = document.getElementById("go");

      button.addEventListener("click", async () => {
        message.textContent = "Loading...";
        button.disabled = true;
        try {
          const data = await getJSON(BASE + scenario.value);
          message.textContent = `Loaded: ${data.title}`;
        } catch (error) {
          message.textContent = describeError(error);
        } finally {
          button.disabled = false;
        }
      });
    </script>
  </body>
</html>
```

```output
Loaded: Buy milk
Not found.
The server had a problem. Try again later.
```

(When a request returns `404` or `503`, DevTools also prints a red `Failed to load resource` line in the Console. That is the browser reporting the HTTP status, not an error in your code, and it is not shown in the output panel above.) The `finally` block re-enables the button whatever happened, a typical use of `finally` for cleanup (Sheet 01, Section 10). The user sees `Loading...` while waiting, then either the data or a sentence they can understand.

## Common mistakes in this section

#### Mistake 1: Swallowing the error

**Why it is wrong.** An empty `catch` hides the failure from you and from the user.

```js bad run mock bundle=net
import { getJSON } from "./http.js";

let title = "(not loaded)";
try {
  title = (await getJSON("http://localhost:3001/todos/99")).title;
} catch (error) {}
console.log("page shows:", title);
```

```output
page shows: (not loaded)
```

```js good run mock bundle=net
import { getJSON, describeError } from "./http.js";

let title = "(not loaded)";
let problem = "";
try {
  title = (await getJSON("http://localhost:3001/todos/99")).title;
} catch (error) {
  problem = describeError(error);
}
console.log("page shows:", title, "| message:", problem);
```

```output
page shows: (not loaded) | message: Not found.
```

**Symptom.** A page that is quietly empty with no explanation. **Diagnosis:** every `catch` should either handle the failure visibly or rethrow it; at the least, log it.

#### Mistake 2: Retrying a request that can create duplicates

**Why it is wrong.** If a `POST` reaches the server but the *answer* is lost, a retry creates the item twice. Only retry requests that are safe to repeat (`GET`, and `PUT`/`DELETE` which are idempotent), unless the API provides an idempotency key.

```js bad run mock bundle=net
import { getJSON } from "./http.js";

const BASE = "http://localhost:3001";
const create = () =>
  getJSON(`${BASE}/todos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: "Pay rent" }),
  });

await create();
await create();
const todos = await getJSON(`${BASE}/todos`);
console.log(todos.filter((t) => t.title === "Pay rent").length, "copies of Pay rent");
```

```output
2 copies of Pay rent
```

**Symptom.** Duplicate orders, payments or messages after a flaky network moment. **Fix:** retry only idempotent requests; for `POST`, ask the user before repeating, or design the API with a unique request key that lets the server detect repeats.

#### Mistake 3: Showing technical messages to users

**Why it is wrong.** `fetch failed` or `HTTP 503` tells a user nothing and may leak internals.

```js bad run mock bundle=net
import { getJSON } from "./http.js";

try {
  await getJSON("http://localhost:1/");
} catch (error) {
  console.log("User sees:", error.name);
}
```

```output
User sees: TypeError
```

**Fix.** Show `describeError(error)` (see above) and send the technical detail (status, URL, original message) to the Console or a logging service for developers.

#### Mistake 4: No timeout and no retry limit

**Why it is wrong.** Without a timeout a hung request waits forever; without a limit and a pause, a retry loop hammers a server that is already struggling and may get you blocked.

**Symptom.** A spinner that never ends, or a flood of requests (visible in the DevTools Network tab) after one failure. **Fix:** `AbortSignal.timeout(...)` on every request, `retries` capped (three is typical), exponential backoff, and respect for `Retry-After`. **Diagnosis:** watch the Network tab while the server is unavailable; the request count should stay small.

# 8. Running Requests Concurrently

## Learning objectives for this section

- Start independent requests together and wait for all of them with `Promise.all()`.
- Choose between `Promise.all`, `Promise.allSettled`, `Promise.race` and `Promise.any`.
- Explain that results keep the order of the input, not the order of completion.
- Limit how many requests run at once.

## Conceptual explanation

Section 4 showed that independent awaits placed one after another add up their delays. Starting them **together** and then waiting for the set takes only as long as the slowest. The `Promise` object provides four **combinators**: functions that take an array of promises and return **one** promise that settles based on all of them.

[[widths 1.2 2.4 2.0 2.4]]
| Combinator | Fulfils with | Rejects when | Typical use |
|---|---|---|---|
| `Promise.all(list)` | **array of all values**, in input order | **any one** rejects (fails fast, with that reason) | Everything is required |
| `Promise.allSettled(list)` | array of `{ status, value }` or `{ status, reason }` for **every** promise | **never** | Partial results are acceptable |
| `Promise.race(list)` | the value of the **first to settle** | the first to settle is a rejection | Timeouts, "whichever answers first" |
| `Promise.any(list)` | the value of the **first to fulfil** | **all** reject (`AggregateError` with an `errors` array) | Several mirrors of one resource |

All four accept non-promise values too (they are treated as already fulfilled).

```js file="combinators.js" run mock bundle=net
import { getJSON, wait } from "./http.js";

const BASE = "http://localhost:3001";
const cities = ["Pune", "Oslo", "Atlantis"];
const weather = (city) => getJSON(`${BASE}/weather?city=${encodeURIComponent(city)}`);

const [pune, oslo] = await Promise.all([weather("Pune"), weather("Oslo")]);
console.log(pune.temperatureC, oslo.temperatureC);

try {
  await Promise.all(cities.map(weather));
} catch (error) {
  console.log("all() rejected:", error.message);
}

const results = await Promise.allSettled(cities.map(weather));
results.forEach((result, i) => {
  if (result.status === "fulfilled") {
    console.log(cities[i], "->", result.value.condition);
  } else {
    console.log(cities[i], "-> failed:", result.reason.message);
  }
});

const slowOne = wait(60).then(() => "slow");
const fastOne = wait(10).then(() => "fast");
console.log(await Promise.race([slowOne, fastOne]));

const broken = getJSON(`${BASE}/status/500`);
const winner = await Promise.any([broken, getJSON(`${BASE}/todos/1`)]);
console.log(winner.title);

try {
  await Promise.any([getJSON(`${BASE}/status/500`), getJSON(`${BASE}/status/404`)]);
} catch (error) {
  console.log(error.name, error.errors.length);
}
```

```output
31 4
all() rejected: City not found
Pune -> Sunny
Oslo -> Cloudy
Atlantis -> failed: City not found
fast
Buy milk
AggregateError 2
```

**Explanation.** `Promise.all` with two valid cities gives both values at once. With the unknown city `Atlantis` included it **rejects** with the first failure and the two good answers are thrown away, which is right only when you cannot proceed without all of them. `allSettled` never rejects: it reports a status per request, so the page can show Pune and Oslo and an error for Atlantis. `race` returns whichever finishes first (`fast`). `any` skips the failing request and returns the first success; when **every** request fails it rejects with an `AggregateError` holding all the reasons (here, two).

**Results keep the input order.** `Promise.all([slow, fast])` gives `[slowValue, fastValue]` even though `fast` finishes first, so `results[i]` always belongs to `list[i]`.

## Optional deep dive: limiting concurrency

Firing 500 requests at once can overload a server, trip a rate limit, or exhaust the browser's connections. A **pool** runs at most *N* at a time: *N* "workers" each repeatedly take the next item.

```js file="pool.js" run bundle=net
import { wait } from "./http.js";

async function mapWithLimit(items, limit, worker) {
  const results = new Array(items.length);
  let next = 0;

  async function runner() {
    while (next < items.length) {
      const index = next++;
      results[index] = await worker(items[index], index);
    }
  }

  const count = Math.min(limit, items.length);
  await Promise.all(Array.from({ length: count }, runner));
  return results;
}

let active = 0;
let maxActive = 0;
const out = await mapWithLimit([1, 2, 3, 4, 5, 6], 2, async (n) => {
  active++;
  maxActive = Math.max(maxActive, active);
  await wait(20);
  active--;
  return n * 10;
});
console.log(out, "max concurrent:", maxActive);
```

```output
[ 10, 20, 30, 40, 50, 60 ] max concurrent: 2
```

`Array.from({ length: count }, runner)` creates `count` runners (a handy way to repeat a function a number of times; each is an `async` function, so it produces a promise). Each runner claims the next index with `next++` (safe because JavaScript runs one piece of code at a time), awaits its item, then claims another until none are left. At most two items are ever in flight, and `results[index]` keeps the original order.

## Common mistakes in this section

#### Mistake 1: `map` with an `async` callback but no `Promise.all`

**Why it is wrong.** `map` returns an array of promises, not of values.

```js bad run mock bundle=net
import { getJSON } from "./http.js";

const ids = [1, 2];
const todos = ids.map(async (id) => getJSON(`http://localhost:3001/todos/${id}`));
console.log(todos[0] instanceof Promise, todos[0].title);
```

```output
true undefined
```

```js good run mock bundle=net
import { getJSON } from "./http.js";

const ids = [1, 2];
const todos = await Promise.all(
  ids.map((id) => getJSON(`http://localhost:3001/todos/${id}`))
);
console.log(todos.map((t) => t.title).join(" and "));
```

```output
Buy milk and Write report
```

**Symptom.** `undefined` properties and `Promise` objects where data was expected.

#### Mistake 2: Using `Promise.all` when partial results would do

**Why it is wrong.** One failure discards every success.

```js bad run mock bundle=net
import { getJSON } from "./http.js";

const names = ["octocat", "nobody-here", "asha-dev"];
try {
  const profiles = await Promise.all(
    names.map((n) => getJSON(`http://localhost:3001/github/users/${n}`))
  );
  console.log(profiles.length, "profiles");
} catch (error) {
  console.log("lost everything:", error.message);
}
```

```output
lost everything: Not Found
```

```js good run mock bundle=net
import { getJSON } from "./http.js";

const names = ["octocat", "nobody-here", "asha-dev"];
const settled = await Promise.allSettled(
  names.map((n) => getJSON(`http://localhost:3001/github/users/${n}`))
);
const good = settled.filter((r) => r.status === "fulfilled").map((r) => r.value.login);
console.log(good.join(", "), "| failed:", settled.length - good.length);
```

```output
octocat, asha-dev | failed: 1
```

**Fix.** Use `allSettled` and filter by `status`. **Diagnosis:** ask "if one of these fails, should the others still be shown?"

#### Mistake 3: Expecting results in order of completion

**Why it is wrong.** `Promise.all` orders by *input*, which is usually what you want, but not if you expected the fastest first.

```js bad run bundle=net
import { wait } from "./http.js";

const order = [];
const results = await Promise.all([
  wait(50).then(() => {
    order.push("A");
    return "A";
  }),
  wait(10).then(() => {
    order.push("B");
    return "B";
  }),
]);
console.log("finished in order:", order.join(""), "| results array:", results.join(""));
```

```output
finished in order: BA | results array: AB
```

**Symptom.** Confusion about which result belongs to which request. **Lesson:** `results[i]` always matches `list[i]`; if you need completion order, use `race`, events, or sort by timestamp.

#### Mistake 4: Believing a rejected `Promise.all` cancels the others

**Why it is wrong.** The other promises are not cancelled: they keep running, and their side effects still happen. Only an `AbortController` (Section 9) can stop requests.

```js bad run bundle=net
import { wait } from "./http.js";

Promise.all([
  Promise.reject(new Error("first failed")),
  wait(30).then(() => console.log("other task still ran")),
]).catch((error) => console.log("all() rejected:", error.message));

await wait(80);
```

```output
all() rejected: first failed
other task still ran
```

**Symptom.** Work you thought was abandoned (requests, state updates) still happens, sometimes after the interface has moved on. **Fix:** give related requests one `AbortController` signal and abort it when you give up.
