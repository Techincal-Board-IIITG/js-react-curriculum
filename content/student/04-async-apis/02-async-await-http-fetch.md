# 4. `async` and `await`

## Learning objectives for this section

- Write `async` functions and explain what they return.
- Explain exactly what `await` pauses, and what it does not.
- Handle errors with `try/catch/finally`, and choose between sequential and parallel awaits.

## Conceptual explanation

Promise chains work, but long chains are awkward to read, and error handling and loops are clumsy. `async` and `await` are a notation that lets you write promise code that **looks sequential**. They do not replace promises: an `async` function *is* a function that returns a promise, and `await` *is* `.then()` written differently. Everything you learned in Section 3 still applies underneath.

## Syntax and rules

```text
async function name(params) { ... }       // declaration
const name = async (params) => { ... };   // arrow form

const value = await somePromise;   // only in an async function or module top level
```

- **An `async` function always returns a promise.** If it returns a value `v`, the promise fulfils with `v`. If it throws, the promise rejects with the error.
- **`await expr`** evaluates `expr` (usually a promise), then **pauses the async function** until that promise settles. If it fulfils, `await` produces its value. If it rejects, `await` **throws** the reason at that line, so `try/catch` works.
- **`await` pauses only the async function it is in, not the whole program.** The function's remaining lines become a microtask that runs when the promise settles; meanwhile the event loop carries on with other code.
- `await` may be used only inside an `async` function, or at the top level of an ES module (`.mjs` files and `type="module"` scripts).

```js file="async-basic.js" run
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function main() {
  console.log("start");
  const a = await wait(10).then(() => 2);
  const b = a * 3;
  console.log("b is", b);
  return b;
}

const result = main();
console.log("main returned:", result);
result.then((value) => console.log("resolved with", value));
console.log("script end");
```

```output
start
main returned: Promise { <pending> }
script end
b is 6
resolved with 6
```

**Line by line.** Line 11 calls `main()`. It runs **synchronously** up to the first `await`, so `start` prints first. At line 5, `await` pauses `main` and returns control to the caller: `main()` hands back a **pending promise** immediately, which line 12 prints. The script then continues to its end. Ten milliseconds later the awaited promise fulfils, `main` resumes at line 6, prints `b is 6`, and `return b` fulfils the promise `main()` returned, so line 13's callback prints `resolved with 6`. The key lesson: **code after `await` runs later; code after the call to the async function runs now.**

## Error handling with `try/catch/finally`

Because a rejected `await` throws, ordinary error handling from Sheet 01 works again:

```js file="async-errors.js" run
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function loadUser(id) {
  await wait(5);
  if (id === 0) {
    throw new Error("No such user");
  }
  return { id, name: "User " + id };
}

async function show(id) {
  try {
    const user = await loadUser(id);
    console.log("loaded", user.name);
  } catch (error) {
    console.log("failed:", error.message);
  } finally {
    console.log("done", id);
  }
}

await show(1);
await show(0);
```

```output
loaded User 1
done 1
failed: No such user
done 0
```

`loadUser(0)` throws inside an async function, so its promise **rejects**; `await` on line 13 rethrows that rejection, and the `catch` block handles it. `finally` runs both times. The top-level `await` on lines 22 and 23 makes the second call wait for the first (this works in `.mjs` files).

## Sequential or parallel?

Each `await` waits for its promise **before the next line starts**. That is exactly right when step two needs step one's result, and a waste when the steps are independent.

```js file="async-parallel.js" run
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function task(name, ms) {
  await wait(ms);
  return name;
}

let start = Date.now();
const a = await task("A", 100);
const b = await task("B", 100);
let elapsed = Date.now() - start;
console.log("sequential:", a + b, "about 200 ms:", elapsed >= 190 && elapsed < 300);

start = Date.now();
const [c, d] = await Promise.all([task("C", 100), task("D", 100)]);
elapsed = Date.now() - start;
console.log("parallel:", c + d, "about 100 ms:", elapsed >= 90 && elapsed < 190);
```

```output
sequential: AB about 200 ms: true
parallel: CD about 100 ms: true
```

In the sequential version task B does not even *start* until A has finished, so the times add up. In the parallel version both tasks are started at once (the array is built before anything is awaited) and `Promise.all` (Section 8) waits for both, so the total is the time of the slowest. Rule of thumb: **start independent work together, then await the results**.

## Loops with `await`

```js file="async-loops.js" run
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const items = [1, 2, 3];

items.forEach(async (n) => {
  await wait(10);
  console.log("forEach item", n);
});
console.log("forEach returned immediately");
await wait(50);

for (const n of items) {
  await wait(5);
  console.log("for-of item", n);
}
console.log("for-of finished");

const doubled = await Promise.all(
  items.map(async (n) => {
    await wait(5);
    return n * 2;
  })
);
console.log(doubled);
```

```output
forEach returned immediately
forEach item 1
forEach item 2
forEach item 3
for-of item 1
for-of item 2
for-of item 3
for-of finished
[ 2, 4, 6 ]
```

**Explanation.** `forEach` ignores what its callback returns, including the promise from an `async` callback, so it does **not** wait: it starts three tasks and returns at once (line 8 prints first). A `for...of` loop awaits inside its own body, so the items are processed **one after another**, and `for-of finished` really comes last. To run all items in **parallel** and collect results, use `map` with an `async` callback (which produces an array of promises) wrapped in `Promise.all`.

## Common mistakes in this section

#### Mistake 1: Forgetting `await`

**Why it is wrong.** Without `await`, you hold the **promise**, not the value inside it.

```js bad run
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
async function loadUser() {
  await wait(5);
  return { name: "Asha" };
}

const user = loadUser();
console.log(user.name);
console.log(user);
```

```output
undefined
Promise { <pending> }
```

```js good run
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
async function loadUser() {
  await wait(5);
  return { name: "Asha" };
}

const user = await loadUser();
console.log(user.name);
```

```output
Asha
```

**Symptom.** `undefined` properties and `Promise { <pending> }` in the log. **Diagnosis:** `console.log` the variable; seeing `Promise` means a missing `await`.

#### Mistake 2: Using `forEach` with an `async` callback and expecting it to wait

**Why it is wrong.** `forEach` does not wait for the promises its callback returns.

```js bad run
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
let total = 0;
[1, 2, 3].forEach(async (n) => {
  await wait(5);
  total += n;
});
console.log("total:", total);
```

```output
total: 0
```

```js good run
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
let total = 0;
for (const n of [1, 2, 3]) {
  await wait(5);
  total += n;
}
console.log("total:", total);
```

```output
total: 6
```

**Symptom.** Results are missing at the moment you use them. **Fix:** `for...of` for sequential work, or `Promise.all(items.map(async ...))` for parallel work.

#### Mistake 3: Awaiting independent tasks one by one

**Why it is wrong.** Needless sequencing makes the program as slow as the sum of the delays.

```js bad run
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const start = Date.now();
await wait(100);
await wait(100);
await wait(100);
console.log("three independent waits took about 300 ms:", Date.now() - start >= 290);
```

```output
three independent waits took about 300 ms: true
```

```js good run
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const start = Date.now();
await Promise.all([wait(100), wait(100), wait(100)]);
console.log("in parallel they took under 200 ms:", Date.now() - start < 200);
```

```output
in parallel they took under 200 ms: true
```

**Symptom.** A page that loads data slowly. **Diagnosis:** if no await uses the result of the previous one, the calls can run in parallel.

#### Mistake 4: Using `await` outside an `async` function

**Why it is wrong.** `await` is only valid in async functions and module top level.

```js bad nocheck
function load() {
  const data = await fetch("/data");
  return data;
}
```

**Symptom.** A `SyntaxError` saying `await` is only valid in async functions and module top level; nothing in the file runs.

```js good nocheck
async function load() {
  const data = await fetch("/data");
  return data;
}
```

**Diagnosis.** The message names the cause. Add `async` to the function. Remember that the *callers* of `load` now receive a promise and must `await` it or use `.then`.

# 5. HTTP and REST Fundamentals

## Learning objectives for this section

- Describe the request and response messages of HTTP.
- Choose the right method and interpret the status codes you meet daily.
- Explain REST conventions: resources, path parameters, query parameters.
- Build URLs safely with `URL` and `URLSearchParams`.

## Conceptual explanation

The web runs on **HTTP**, a conversation in which a **client** (your browser or script) sends a **request** and a **server** sends back one **response**. The server never speaks first and remembers nothing between requests unless you send identifying information again. This design is called **stateless**, and it is why each request must carry everything the server needs.

A **request** has four parts: a **method** (what to do), a **URL** (to which resource), **headers** (extra information), and an optional **body** (data to send). A **response** has a **status code** (how it went), **headers**, and usually a **body**.

## Anatomy of a URL

```js file="url-parts.js" run
const url = new URL("https://api.example.com:8443/v1/todos/3?done=false&limit=5#top");

console.log(url.protocol, url.hostname, url.port);
console.log(url.pathname);
console.log(url.search, url.hash);
console.log(url.searchParams.get("limit"), url.searchParams.get("missing"));
```

```output
https: api.example.com 8443
/v1/todos/3
?done=false&limit=5 #top
5 null
```

The pieces: the **scheme** (`https:`), **host** (`api.example.com`), **port** (`8443`; omitted when it is the default), **path** (`/v1/todos/3`, which identifies the resource), the **query string** (`?done=false&limit=5`, which refines the request) and the **fragment** (`#top`, which the browser keeps to itself and never sends). `URL` parses addresses reliably, and `searchParams.get` returns a **string** or `null`.

## Methods

[[widths 1 2.6 1.3 1.3]]
| Method | Meaning | Safe? | Idempotent? |
|---|---|---|---|
| `GET` | Read a resource; must not change anything | Yes | Yes |
| `POST` | Create a resource (or trigger an action); the body carries the data | No | No |
| `PUT` | Replace a resource completely | No | Yes |
| `PATCH` | Change part of a resource | No | Usually not guaranteed |
| `DELETE` | Remove a resource | No | Yes |

*Safe* means "does not change data on the server". *Idempotent* means "sending it twice has the same effect as once": deleting item 3 twice leaves the same state, whereas posting a new order twice creates two orders. This is why a browser may safely repeat a `GET` but asks before re-submitting a `POST`.

## Status codes

The first digit gives the family; learn the family first and the exact codes second.

[[widths 0.8 2.0 3.6]]
| Code | Name | Meaning in practice |
|---|---|---|
| `200` | OK | Success; the body has the result |
| `201` | Created | A resource was created (typical answer to `POST`) |
| `204` | No Content | Success, **no body** (typical for `DELETE`); do not call `.json()` |
| `301`, `302` | Redirect | Look at another URL (fetch follows these automatically) |
| `304` | Not Modified | Your cached copy is still valid |
| `400` | Bad Request | The request was malformed or failed validation |
| `401` | Unauthorized | You are not identified (missing or invalid credentials) |
| `403` | Forbidden | Identified, but not allowed |
| `404` | Not Found | No such resource |
| `409` | Conflict | Conflicts with current state (such as a duplicate) |
| `422` | Unprocessable Content | Well-formed but semantically invalid data |
| `429` | Too Many Requests | You are being rate-limited; see `Retry-After` |
| `500` | Internal Server Error | The server failed (a bug on their side) |
| `502`, `503`, `504` | Bad Gateway, Unavailable, Timeout | Server or network trouble, often temporary |

Families: **2xx** success, **3xx** redirection, **4xx** *you* made a mistake (do not retry unchanged), **5xx** *they* failed (a retry may help). This distinction drives error handling in Section 7.

## REST conventions

**REST** is a style for designing web APIs around **resources** (things), named with **nouns** in the path, and the HTTP method as the **verb**.

[[widths 1.8 1.1 2.6]]
| Operation | Request | Typical answer |
|---|---|---|
| List all | `GET /todos` | `200` and an array |
| Read one | `GET /todos/3` | `200` and an object, or `404` |
| Create | `POST /todos` with JSON body | `201` and the new object |
| Update part | `PATCH /todos/3` with JSON body | `200` and the updated object |
| Delete | `DELETE /todos/3` | `204` and no body |

- A **path parameter** identifies *which* resource: `/todos/3`, `/users/octocat`.
- **Query parameters** *refine* a request: filtering (`?completed=true`), limiting (`?limit=10`), sorting (`?sort=title`), paging (`?page=2`), searching (`?q=space`).
- Data usually travels as **JSON**, announced by the header `Content-Type: application/json`; a client states what it wants back with `Accept: application/json`.
- Common headers: `Content-Type` and `Accept` (formats), `Authorization` or `X-Api-Key` (credentials), `Retry-After` (when to try again), `Cache-Control` (caching).

## Building URLs safely

Characters such as spaces, `&`, `=` and `?` have special meaning in URLs. A value containing them must be **encoded**. Never glue user text into a URL by hand: use `URLSearchParams` for query strings and `encodeURIComponent` for a single path segment.

```js file="url-build.js" run
const params = new URLSearchParams({ q: "space cats & dogs", limit: 5 });
console.log(params.toString());

console.log(`/search?${params}`);
console.log(encodeURIComponent("a&b=c d"));

const user = "asha dev/admin";
console.log(`/users/${encodeURIComponent(user)}`);

const url = new URL("/todos", "http://localhost:3001");
url.searchParams.set("completed", "false");
url.searchParams.append("limit", 2);
console.log(url.href);
```

```output
q=space+cats+%26+dogs&limit=5
/search?q=space+cats+%26+dogs&limit=5
a%26b%3Dc%20d
/users/asha%20dev%2Fadmin
http://localhost:3001/todos?completed=false&limit=2
```

`URLSearchParams` accepts an object (values are converted to strings), encodes spaces as `+` and `&` as `%26`, and its `toString()` is used automatically inside a template literal. `encodeURIComponent` encodes everything that is special, including `/`, so a user-supplied path segment cannot add extra path levels. The `URL` class builds the full address: `searchParams.set` replaces a parameter and `append` adds another.

## Common mistakes in this section

#### Mistake 1: Building query strings by hand

**Why it is wrong.** Special characters in the value change the meaning of the URL.

```js bad run
const term = "salt & pepper";
console.log(`/search?q=${term}&limit=5`);
console.log(new URL(`http://x.test/search?q=${term}&limit=5`).searchParams.get("q"));
```

```output
/search?q=salt & pepper&limit=5
salt 
```

```js good run
const term = "salt & pepper";
const params = new URLSearchParams({ q: term, limit: 5 });
console.log(`/search?${params}`);
console.log(new URL(`http://x.test/search?${params}`).searchParams.get("q"));
```

```output
/search?q=salt+%26+pepper&limit=5
salt & pepper
```

**Symptom.** The server receives a truncated value (`salt `), because the `&` was read as the start of a new parameter. **Diagnosis:** log the final URL; hand-built ones with unescaped spaces or `&` in values are the culprit.

#### Mistake 2: Putting secrets or user text in the path without encoding

**Why it is wrong.** A `/` or `?` inside a path value changes which resource you address.

```js bad run
const name = "../admin";
console.log(`/users/${name}/profile`);
```

```output
/users/../admin/profile
```

```js good run
const name = "../admin";
console.log(`/users/${encodeURIComponent(name)}/profile`);
```

```output
/users/..%2Fadmin/profile
```

**Symptom.** Requests reach resources you did not intend (a security problem, called path traversal, when the value comes from a user). **Fix:** `encodeURIComponent` on every dynamic path segment.

#### Mistake 3: Using the wrong method for the job

**Why it is wrong.** `GET` is expected to be safe and may be cached, retried, or prefetched. Using it to change data causes accidents; using `POST` for everything hides your intent from tools and teammates.

**Symptom.** Items created twice by a retry, data deleted by a link prefetcher, or cached responses that never update. **Fix:** follow the REST table above: read with `GET`, create with `POST`, change with `PATCH` or `PUT`, remove with `DELETE`.

**Diagnosis.** Open the browser DevTools Network tab and look at the *Method* column for the request that behaves oddly.

#### Mistake 4: Treating every non-200 status as the same problem

**Why it is wrong.** `404`, `429` and `503` need different reactions: show "not found", wait and retry, or retry a few times and then give up.

**Symptom.** Users see "Something went wrong" for everything, or the app hammers a server that asked it to slow down. **Fix:** branch on `response.status` (or its family) as Section 7 shows. **Diagnosis:** log `response.status` along with the URL for every failing request.

# 6. `fetch()` in Depth

## Learning objectives for this section

- Explain what `fetch` returns, when it resolves, and when it rejects.
- Read `Response` properties and parse bodies, knowing a body can be read only once.
- Send `GET`, `POST`, `PATCH` and `DELETE` requests with headers and JSON bodies.
- Build a reusable `getJSON` helper that turns HTTP errors into exceptions.

## Function deep dive: `fetch()`

**What it is.** A built-in function (in browsers and in Node.js 18 and later) that sends an HTTP request and returns a promise for the response.

**Why it exists.** Pages need to get and send data without reloading. `fetch` replaced the older `XMLHttpRequest` with a promise-based design.

**Syntax.** `fetch(resource, options)`, usually written `await fetch(url, options)`.

**Parameters.**

- `resource`: the URL (a string or a `URL` object).
- `options` (optional): an object with, among others, `method` (default `"GET"`), `headers` (an object), `body` (a string, `FormData` and more; **not allowed for `GET`**), `signal` (for cancellation, Section 9).

**Return value.** A **promise** that fulfils with a **`Response`** object as soon as the server has sent the **status and headers**, which can be before the body has fully arrived.

**The most important rule.** `fetch` **rejects only when the request could not be completed at all**: no network, DNS failure, a connection refused, a CORS block, or an abort. A response that arrives with status `404` or `500` is a **successful fetch**: the promise **fulfils**, and you must check `response.ok` yourself.

**How it works, step by step.** (1) `fetch` starts the request through the environment and returns a pending promise at once. (2) The environment connects, sends the request and waits. (3) When the response headers arrive, the promise fulfils with a `Response`. (4) You then read the body with one of the body methods, each of which also returns a promise.

### The `Response` object

[[widths 1.7 3.9]]
| Member | Meaning |
|---|---|
| `response.ok` | `true` for status 200 to 299, otherwise `false` |
| `response.status` | The numeric status code |
| `response.statusText` | The reason text (may be empty with HTTP/2) |
| `response.headers.get("name")` | A header value (names are case-insensitive), or `null` |
| `response.url` | The final URL after redirects |
| `await response.json()` | Parses the body as JSON; rejects with `SyntaxError` if it is not valid JSON |
| `await response.text()` | The body as a string |
| `await response.blob()` | The body as binary data (images, files) |
| `response.bodyUsed` | `true` once the body has been read; **a body can be read only once** |

```js file="fetch-get.js" run mock
const BASE = "http://localhost:3001";

const response = await fetch(`${BASE}/todos/2`);
console.log(response.status, response.ok, response.headers.get("content-type"));

const todo = await response.json();
console.log(todo.title, response.bodyUsed);
```

```output
200 true application/json
Write report true
```

**Line by line.** Line 3 awaits the `Response`. Line 4 shows the three facts you check first: the status (`200`), the boolean `ok`, and a header (the content type). Line 6 awaits the second promise: the **body** is parsed as JSON into an object, and line 7 confirms that the body is now marked as used.

## HTTP errors do not throw

```js file="fetch-404.js" run mock
const BASE = "http://localhost:3001";

const response = await fetch(`${BASE}/todos/99`);
console.log("fetch resolved:", response.status, response.ok);
const body = await response.json();
console.log("server says:", body.error);

try {
  await fetch("http://localhost:1/unreachable");
} catch (error) {
  console.log("fetch rejected:", error.name);
}
```

```output
fetch resolved: 404 false
server says: Todo not found
fetch rejected: TypeError
```

Two completely different failures. A `404` is a **valid HTTP answer**: `fetch` resolves, `ok` is `false`, and the server's explanation is in the body (here a JSON error object). A **network failure** (nothing is listening on port 1) makes `fetch` reject with a `TypeError`. The message differs by environment (`fetch failed` in Node.js, `Failed to fetch` in browsers) so rely on the error *type*, not the text. A robust program handles both.

## A reusable helper: `getJSON`

Checking `ok`, parsing JSON (or tolerating an empty body), and building a useful error is the same every time. Write it once.

```js file="get-json.js" run mock
async function getJSON(url, options) {
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
    throw failure;
  }
  return data;
}

const BASE = "http://localhost:3001";

console.log((await getJSON(`${BASE}/todos/1`)).title);

for (const path of ["/todos/99", "/status/500", "/status/204"]) {
  try {
    const data = await getJSON(BASE + path);
    console.log(path, "->", data);
  } catch (error) {
    console.log(path, "-> failed:", error.status, error.message);
  }
}
```

```output
Buy milk
/todos/99 -> failed: 404 Todo not found
/status/500 -> failed: 500 HTTP 500
/status/204 -> null
```

**How it works.** The helper reads the body as **text** first so it can cope with an empty `204` response (calling `.json()` on an empty body would throw). It tries `JSON.parse` and falls back to the raw text. If the status is not OK it builds an `Error` whose message comes from the server's `error` or `message` field when present (`?.` and `??` from Sheet 02), attaches the `status` number, and throws, so callers can use `try/catch` and branch on `error.status`. For the `500` the server sent a JSON body without an `error` field, so the message falls back to `HTTP 500`. For `204` it returns `null`. The helper is used in the rest of this sheet.

## Sending data: POST, PATCH and DELETE

To send JSON, you must do **two** things: convert the object with `JSON.stringify` and declare the format with the `Content-Type` header.

```js file="fetch-write.js" run mock
const BASE = "http://localhost:3001";
const JSON_HEADERS = { "Content-Type": "application/json" };

const created = await fetch(`${BASE}/todos`, {
  method: "POST",
  headers: JSON_HEADERS,
  body: JSON.stringify({ title: "Learn fetch" }),
});
console.log(created.status, await created.json());

const patched = await fetch(`${BASE}/todos/4`, {
  method: "PATCH",
  headers: JSON_HEADERS,
  body: JSON.stringify({ completed: true }),
});
console.log(patched.status, (await patched.json()).completed);

const removed = await fetch(`${BASE}/todos/4`, { method: "DELETE" });
console.log(removed.status, JSON.stringify(await removed.text()));

const rejected = await fetch(`${BASE}/todos`, {
  method: "POST",
  headers: JSON_HEADERS,
  body: JSON.stringify({ title: "   " }),
});
console.log(rejected.status, await rejected.json());

const list = await (await fetch(`${BASE}/todos`)).json();
console.log(list.map((t) => t.id).join(","));
```

```output
201 { id: 4, title: 'Learn fetch', completed: false }
200 true
204 ""
400 { error: 'title is required' }
1,2,3
```

**Line by line.** The `POST` returns `201` and the new object with the id the server chose. The `PATCH` changes only `completed`. The `DELETE` answers `204` with an **empty body** (the text is `""`; calling `.json()` would have failed). The last `POST` has a blank title and is refused with `400` and an explanation: **validation errors are normal responses, not exceptions**, which is why you read `response.ok`. The final list shows the to-do with id 4 is gone.

## Query parameters, path parameters and headers in requests

```js file="fetch-params.js" run mock
const BASE = "http://localhost:3001";

const query = new URLSearchParams({ completed: "false", limit: 1 });
const open = await (await fetch(`${BASE}/todos?${query}`)).json();
console.log(open.length, open[0].title);

const username = "asha-dev";
const profileUrl = `${BASE}/github/users/${encodeURIComponent(username)}`;
const profile = await (await fetch(profileUrl)).json();
console.log(profile.login, profile.public_repos);

const echoed = await (
  await fetch(`${BASE}/echo?x=1&y=two`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Api-Key": "demo-key" },
    body: JSON.stringify({ hello: "server" }),
  })
).json();
console.log(echoed.method, echoed.query, echoed.apiKey, echoed.body);
```

```output
1 Write report
asha-dev 1
POST { x: '1', y: 'two' } demo-key { hello: 'server' }
```

The `/echo` endpoint reports what it received, which makes it a good way to *see* what `fetch` actually sends: the method, the parsed query parameters, a custom header, and the JSON body. Remember: **anything in front-end code, including this header, is visible to every user**; never put a real private key there (Section 10).

## A complete browser example: loading, success and error states

Every data-driven interface shows one of three states. Make them explicit.

```html file="index.html" page mock steps="wait 300 | print #status | print #list"
<!DOCTYPE html>
<html lang="en">
  <body>
    <p id="status">Loading...</p>
    <ul id="list"></ul>
    <script type="module">
      const BASE = "http://localhost:3001";

      async function load() {
        const status = document.getElementById("status");
        const list = document.getElementById("list");
        status.textContent = "Loading...";
        list.replaceChildren();
        try {
          const response = await fetch(`${BASE}/todos`);
          if (!response.ok) {
            throw new Error(`Server answered ${response.status}`);
          }
          const todos = await response.json();
          for (const todo of todos) {
            const li = document.createElement("li");
            li.textContent = todo.title;
            list.append(li);
          }
          status.textContent = `${todos.length} todos`;
        } catch (error) {
          status.textContent = `Error: ${error.message}`;
        }
      }

      load();
    </script>
  </body>
</html>
```

```output
3 todos
Buy milk / Write report / Call Asha
```

The page starts in the **loading** state. After the response arrives it renders the **success** state; for a failure, the `catch` shows an **error** state. The check `if (!response.ok) throw ...` turns HTTP errors into the same error path as network failures, so one `catch` handles both. Sheet 07 adds the fourth state, **empty**, and shows how React handles all four.

## Common mistakes in this section

#### Mistake 1: Assuming `fetch` rejects on `404` or `500`

**Why it is wrong.** `fetch` only rejects on network failure.

```js bad run mock
const response = await fetch("http://localhost:3001/todos/99");
const todo = await response.json();
console.log("treated as success:", todo.title);
```

```output
treated as success: undefined
```

```js good run mock
const response = await fetch("http://localhost:3001/todos/99");
if (!response.ok) {
  console.log("request failed with status", response.status);
} else {
  const todo = await response.json();
  console.log(todo.title);
}
```

```output
request failed with status 404
```

**Symptom.** `undefined` fields, because the parsed body is the server's *error* object, not a to-do. **Diagnosis:** log `response.status`; or use the `getJSON` helper, which checks for you.

#### Mistake 2: Forgetting `await response.json()`

**Why it is wrong.** `response.json()` returns a promise.

```js bad run mock
const response = await fetch("http://localhost:3001/todos/1");
const todo = response.json();
console.log(todo.title);
console.log(todo instanceof Promise);
```

```output
undefined
true
```

```js good run mock
const response = await fetch("http://localhost:3001/todos/1");
const todo = await response.json();
console.log(todo.title);
```

```output
Buy milk
```

**Symptom.** `undefined` properties; `Promise { <pending> }` when you log the variable. This is the "missing `await`" mistake from Section 4 in its most common place.

#### Mistake 3: Reading the body twice

**Why it is wrong.** The body is a stream that can be consumed once.

```js bad run throws mock
const response = await fetch("http://localhost:3001/todos/1");
console.log("first read:", (await response.json()).title);
console.log("second read:", await response.text());
```

```output
first read: Buy milk
TypeError: Body is unusable
```

```js good run mock
const response = await fetch("http://localhost:3001/todos/1");
const text = await response.text();
console.log("raw text:", text);
console.log("parsed:", JSON.parse(text).title);
```

```output
raw text: {"id":1,"title":"Buy milk","completed":true}
parsed: Buy milk
```

**Symptom.** A `TypeError` about the body being used (wording varies: browsers say the body stream is already read). **Fix:** read the body once into a variable (`text` here, then parse it yourself), or `response.clone()` before reading. This is why `getJSON` reads text first.

#### Mistake 4: Sending an object without `JSON.stringify`

**Why it is wrong.** A plain object in `body` is converted to the text `[object Object]`.

```js bad run mock
const response = await fetch("http://localhost:3001/todos", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: { title: "Forgot to stringify" },
});
console.log(response.status, await response.json());
```

```output
400 { error: 'title is required' }
```

```js good run mock
const response = await fetch("http://localhost:3001/todos", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ title: "Stringified properly" }),
});
console.log(response.status, await response.json());
```

```output
201 { id: 4, title: 'Stringified properly', completed: false }
```

**Symptom.** The server answers `400` or says the data is missing. **Diagnosis:** send the same request to the `/echo` endpoint (or look in the DevTools Network tab, *Payload*) to see what was actually transmitted. Also set `Content-Type: application/json`: without it real servers may refuse or misread the body.
