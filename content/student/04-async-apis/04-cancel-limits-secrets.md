# 9. Cancelling Requests, Debouncing and Stale Responses

## Learning objectives for this section

- Cancel a request with `AbortController`, and tell a cancellation from a failure.
- Explain and reproduce the stale-response (race condition) bug in a search box.
- Fix it by aborting the previous request or by ignoring outdated results.
- Write and use a debounce function to avoid sending a request on every keystroke.

## Function deep dive: `AbortController`

**What it is.** A built-in object (browsers and Node.js) that lets you cancel one or more asynchronous operations, most often `fetch` requests.

**Why it exists.** A promise cannot be cancelled once started. But an obsolete request wastes bandwidth and, worse, can deliver an old answer after a new one (below). `AbortController` gives you a standard way to say "I no longer care".

**Syntax.**

```text
const controller = new AbortController();
fetch(url, { signal: controller.signal });   // hand the signal to fetch
controller.abort();                           // later: cancel
```

**Parts.** `controller.signal` is an `AbortSignal` you pass to `fetch` (its `signal` option); `controller.abort()` triggers it; `signal.aborted` becomes `true`. A controller is **single use**: once aborted, its signal stays aborted forever, so create a **new controller for each request** you may want to cancel.

**What happens when you abort.** The fetch promise **rejects** with an error whose `name` is **`"AbortError"`**. This is *not* a failure: nothing went wrong; you asked for it. Handle it separately (usually by ignoring it). Aborting a request that already finished does nothing.

```js file="abort-basic.js" run mock bundle=net
import { getJSON } from "./http.js";

const controller = new AbortController();
const started = Date.now();

const url = "http://localhost:3001/slow?ms=500";
const request = getJSON(url, { signal: controller.signal });
setTimeout(() => controller.abort(), 30);

try {
  await request;
} catch (error) {
  const quick = Date.now() - started < 300;
  const flag = controller.signal.aborted;
  console.log(error.name, "quickly:", quick, "aborted flag:", flag);
}
```

```output
AbortError quickly: true aborted flag: true
```

A request that would have taken 500 ms is abandoned after about 30 ms. The rejection has the name `AbortError`, which your error handler must recognise (`describeError` turns it into "Request cancelled.").

## The stale-response bug

User types in a search box. Typing `s` starts request 1; typing more starts request 2 for `space c`. Request 1 is *slower* (in this mock, one-letter searches take longer). Request 2's answer arrives first and is shown; then request 1's **older** answer arrives and **overwrites** it. The screen now shows results for text the user is no longer looking at. This is a **race condition**: the outcome depends on which asynchronous operation finishes first.

```js file="stale-bug.js" run mock bundle=net
import { getJSON } from "./http.js";

const BASE = "http://localhost:3001";
let shown = "(nothing)";

async function search(term) {
  const hits = await getJSON(`${BASE}/shows?q=${encodeURIComponent(term)}`);
  shown = `"${term}" -> ${hits.length} result(s)`;
}

const first = search("s");
const second = search("space c");
await Promise.all([first, second]);
console.log("screen finally shows:", shown);
```

```output
screen finally shows: "s" -> 3 result(s)
```

The user's latest text was `space c` (one match), but the screen shows the outcome for `s` because that response arrived last. There are two standard fixes.

**Fix 1: abort the previous request.** Keep the current controller; abort it before starting a new one. The obsolete request is cancelled (saving work) and its late answer can never arrive.

```js file="stale-fix-abort.js" run mock bundle=net
import { getJSON } from "./http.js";

const BASE = "http://localhost:3001";
let shown = "(nothing)";
let controller = null;

async function search(term) {
  controller?.abort();
  controller = new AbortController();
  try {
    const hits = await getJSON(`${BASE}/shows?q=${encodeURIComponent(term)}`, {
      signal: controller.signal,
    });
    shown = `"${term}" -> ${hits.length} result(s)`;
  } catch (error) {
    if (error.name !== "AbortError") throw error;
    console.log("cancelled:", term);
  }
}

await Promise.all([search("s"), search("space c")]);
console.log("screen finally shows:", shown);
```

```output
cancelled: s
screen finally shows: "space c" -> 1 result(s)
```

**Fix 2: ignore outdated results.** When you cannot cancel the work (for example the operation is not a `fetch`), tag each call with a number and discard any answer that is not from the latest call:

```js file="stale-fix-id.js" run mock bundle=net
import { getJSON } from "./http.js";

const BASE = "http://localhost:3001";
let shown = "(nothing)";
let latest = 0;

async function search(term) {
  const myId = ++latest;
  const hits = await getJSON(`${BASE}/shows?q=${encodeURIComponent(term)}`);
  if (myId !== latest) {
    console.log("ignored stale answer for:", term);
    return;
  }
  shown = `"${term}" -> ${hits.length} result(s)`;
}

await Promise.all([search("s"), search("space c")]);
console.log("screen finally shows:", shown);
```

```output
ignored stale answer for: s
screen finally shows: "space c" -> 1 result(s)
```

The counter `latest` is shared; each call remembers its own `myId`. When an answer arrives, only the call whose `myId` still equals `latest` is allowed to update the screen. Aborting is better when possible (it also saves the work); the counter is a universal fallback. React uses the same two ideas, as you will see in Sheet 07.

## Debouncing: not asking on every keystroke

Even with the stale-response problem solved, sending a request for every keystroke is wasteful and can trip rate limits (Section 10). **Debouncing** delays the action until the user has *paused* for a set time; if another event arrives during the pause, the timer restarts. Only the last event in a burst triggers the work.

```js file="debounce.js" bundle=net
export function debounce(fn, delay) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}
```

**How it works.** `debounce` returns a **new function** that closes over a private `timer` variable (closures, Sheet 01). Each call cancels the pending timer and starts a new one, so the wrapped function `fn` runs only after `delay` ms of silence, with the *last* arguments (`...args` is rest, `...args` in the call is spread; Sheet 02).

```js file="debounce-demo.js" run bundle=net
import { debounce } from "./debounce.js";
import { wait } from "./http.js";

const calls = [];
const search = debounce((term) => calls.push(term), 50);

search("s");
search("sp");
search("spa");
await wait(20);
search("spac");
await wait(120);
console.log(calls);

search("again");
await wait(120);
console.log(calls);
```

```output
[ 'spac' ]
[ 'spac', 'again' ]
```

Four rapid calls collapse into one (`spac`), because every call within 50 ms of the previous restarted the timer. A later, separate call runs on its own. **Debounce** waits for a pause (good for search boxes and autosave); its cousin **throttle** runs at most once per interval (good for scroll handlers).

## Putting it together: a search page

This page combines everything: debounce to reduce requests, abort to avoid stale answers, and all four states (idle, loading, results, empty, error).

```html file="index.html" page mock bundle=net steps="fill #q s | fill #q sp | fill #q space c | wait 700 | print #status | print #results | eval String(window.requestCount) | fill #q zzz | wait 700 | print #status"
<!DOCTYPE html>
<html lang="en">
  <body>
    <input id="q" placeholder="Search shows" />
    <p id="status"></p>
    <ul id="results"></ul>
    <script type="module">
      import { getJSON } from "./http.js";
      import { debounce } from "./debounce.js";

      const BASE = "http://localhost:3001";
      const status = document.getElementById("status");
      const results = document.getElementById("results");
      window.requestCount = 0;
      let controller = null;

      async function search(term) {
        controller?.abort();
        const clean = term.trim();
        if (clean === "") {
          status.textContent = "";
          results.replaceChildren();
          return;
        }
        controller = new AbortController();
        window.requestCount++;
        status.textContent = "Searching...";
        try {
          const url = `${BASE}/shows?q=${encodeURIComponent(clean)}`;
          const hits = await getJSON(url, { signal: controller.signal });
          results.replaceChildren(
            ...hits.map(({ show }) => {
              const li = document.createElement("li");
              li.textContent = show.name;
              return li;
            })
          );
          status.textContent =
            hits.length === 0 ? "No results" : `${hits.length} result(s)`;
        } catch (error) {
          if (error.name === "AbortError") return;
          status.textContent = `Error: ${error.message}`;
        }
      }

      const searchLater = debounce(search, 250);
      document.getElementById("q").addEventListener("input", (event) => {
        searchLater(event.target.value);
      });
    </script>
  </body>
</html>
```

```output
1 result(s)
Space Cats
1
No results
```

Three quick edits (`s`, `sp`, `space c`) caused **one** request (the counter shows `1`), and the screen shows the one matching show. Typing `zzz` then reaches the empty state. A returned `AbortError` is deliberately ignored: a cancelled search is neither results nor an error.

## Common mistakes in this section

#### Mistake 1: Treating `AbortError` as a failure

**Why it is wrong.** You cancelled it on purpose; showing "Something went wrong" is misleading.

```js bad run mock bundle=net
import { getJSON } from "./http.js";

const controller = new AbortController();
const url = "http://localhost:3001/slow?ms=300";
const request = getJSON(url, { signal: controller.signal });
controller.abort();
try {
  await request;
} catch (error) {
  console.log("Error banner shown to user:", error.name);
}
```

```output
Error banner shown to user: AbortError
```

```js good run mock bundle=net
import { getJSON } from "./http.js";

const controller = new AbortController();
const url = "http://localhost:3001/slow?ms=300";
const request = getJSON(url, { signal: controller.signal });
controller.abort();
try {
  await request;
} catch (error) {
  if (error.name === "AbortError") {
    console.log("cancelled on purpose: no banner");
  } else {
    console.log("real error:", error.message);
  }
}
```

```output
cancelled on purpose: no banner
```

**Symptom.** A flash of error text every time the user types. **Fix:** check `error.name === "AbortError"` first and return quietly.

#### Mistake 2: Reusing an aborted controller

**Why it is wrong.** An aborted signal stays aborted; every later request using it is cancelled immediately.

```js bad run mock bundle=net
import { getJSON } from "./http.js";

const controller = new AbortController();
controller.abort();
try {
  await getJSON("http://localhost:3001/todos/1", { signal: controller.signal });
  console.log("loaded");
} catch (error) {
  console.log("second request failed at once:", error.name);
}
```

```output
second request failed at once: AbortError
```

**Symptom.** After the first cancellation, no request works again. **Fix:** `controller = new AbortController()` before every request, as the search page does.

#### Mistake 3: Creating the debounced function inside the event handler

**Why it is wrong.** Each event then creates a **new** debounced function with its own private timer, so nothing is ever shared and nothing is debounced.

```js bad run bundle=net
import { debounce } from "./debounce.js";
import { wait } from "./http.js";

let runs = 0;
function handler() {
  const debounced = debounce(() => runs++, 30);
  debounced();
}

handler();
handler();
handler();
await wait(100);
console.log("work ran", runs, "times");
```

```output
work ran 3 times
```

```js good run bundle=net
import { debounce } from "./debounce.js";
import { wait } from "./http.js";

let runs = 0;
const debounced = debounce(() => runs++, 30);
function handler() {
  debounced();
}

handler();
handler();
handler();
await wait(100);
console.log("work ran", runs, "time");
```

```output
work ran 1 time
```

**Symptom.** Debouncing has no effect. **Fix:** create the debounced function **once**, outside the handler, and call that same function every time.

#### Mistake 4: Letting a slower, older response win

**Why it is wrong.** This is the stale-response bug shown above: whichever answer arrives *last* wins, not whichever request was *latest*.

**Symptom.** Search results that do not match what is typed, usually intermittently and usually on slow connections, which makes it hard to reproduce. **Fix:** abort the previous request, or compare a request counter (as shown). **Diagnosis:** log the term when a request is **sent** and again when its answer **arrives**; arrivals in a different order than sends is the proof.

# 10. Rate Limits, Secrets and CORS

## Learning objectives for this section

- Explain rate limits and use caching, debouncing and `Retry-After` to stay within them.
- Explain why a secret in front-end code is public, and what to do instead.
- Explain what CORS is, who enforces it, and what the common "fixes" really do.

## Rate limits

Most APIs limit how many requests you may make in a period, to protect themselves from overload and abuse. Exceeding the limit gives `429 Too Many Requests`, often with a **`Retry-After`** header (seconds to wait) and sometimes provider-specific headers (such as remaining quota) that you should read in the provider's documentation. Persistent offenders can be blocked.

How to stay within limits:

- **Debounce** input-driven requests (Section 9).
- **Cache** answers you already have, and reuse them.
- **Request only what you need** (filters, limits, only visible pages).
- **Retry politely**: back off, honour `Retry-After`, give up after a few tries (Section 7).
- **Never loop** a failing request without a pause.

```js file="cache.js" run mock bundle=net
import { getJSON, wait } from "./http.js";

const cache = new Map();

async function cachedGetJSON(url, ttlMs) {
  const hit = cache.get(url);
  if (hit && Date.now() - hit.savedAt < ttlMs) {
    return hit.data;
  }
  const data = await getJSON(url);
  cache.set(url, { data, savedAt: Date.now() });
  return data;
}

const url = "http://localhost:3001/limited";
console.log((await cachedGetJSON(url, 100)).call);
console.log((await cachedGetJSON(url, 100)).call);
console.log((await cachedGetJSON(url, 100)).call);

await wait(150);
console.log((await cachedGetJSON(url, 100)).call);
```

```output
1
1
1
2
```

The `/limited` endpoint counts every call it actually receives. The first call reaches it (call `1`); the next two are answered from the `Map` without a request (still `1`), so the allowance is not consumed. After the entry expires (`ttlMs` of 100 ms), the fourth call goes to the server again (call `2`). A cache with a lifetime is the simplest way to cut request volume. Never cache data that must always be fresh, and never share cached private data between users.

## Secrets must never be in front-end code

Everything your JavaScript contains or sends, whether in a script file, a bundled build, or the request headers, **can be read by anyone** using the browser's DevTools (Sources and Network tabs) or "View source". There is no way to hide a value in code that runs on the user's machine.

[[widths 1.8 3.6]]
| Looks like a secret | What actually happens |
|---|---|
| An API key in your script | Anyone can copy it and use your quota, or run up your bill |
| A key in an environment variable used by a front-end build tool | The build **copies the value into the shipped JavaScript**; it is public (Sheet 09 shows this) |
| A password or token in `localStorage` | Any script on your page can read it (Sheet 03, Section 11) |
| A key in a private Git repository, but loaded by the page | The repository is private; the website's JavaScript is not |

The pattern that works is a **backend proxy**: a small server that you control holds the key and makes the real request, and your page calls *your* server. The key never reaches the browser.

```text
Browser  ->  your server (holds the secret key)  ->  third-party API
```

```js file="proxy.mjs"
import http from "node:http";

const API_KEY = process.env.WEATHER_API_KEY;
if (!API_KEY) {
  throw new Error("Set WEATHER_API_KEY before starting the proxy");
}

http
  .createServer(async (req, res) => {
    const url = new URL(req.url, "http://localhost");
    if (url.pathname !== "/api/weather") {
      res.writeHead(404).end();
      return;
    }
    const city = url.searchParams.get("city") ?? "";
    const upstream = new URL("https://weather.example.com/v1/current");
    upstream.searchParams.set("city", city);
    const answer = await fetch(upstream, { headers: { "X-Api-Key": API_KEY } });
    res.writeHead(answer.status, { "Content-Type": "application/json" });
    res.end(await answer.text());
  })
  .listen(3002);
```

This is a sketch (the upstream address is a placeholder): the key is read from the server's **environment variable**, so it exists only on the server; the page calls `/api/weather?city=Pune` on your own server and never sees the key. A production proxy would also validate `city`, limit how often each visitor may call it, and handle errors. Some APIs offer **public keys** designed for browsers, restricted by website address or allowed actions; for those the provider's documentation says so explicitly. The rule: *if abuse of the key could cost money or expose data, it belongs on a server.*

## CORS: why the browser blocks some responses

Browsers apply the **same-origin policy**: a page from one **origin** (scheme, host and port together) may not read responses from a different origin, unless that other server explicitly agrees. The agreement is **CORS** (Cross-Origin Resource Sharing), expressed by response headers such as `Access-Control-Allow-Origin`.

Points that clear up most confusion:

- **The browser enforces CORS, not the server.** A tool like Node.js or `curl` ignores it. The server may well have answered; the *browser* refuses to give the page the response.
- **The fix lives on the server** (or in a proxy that makes the call from the server side). Nothing in your front-end `fetch` call can legitimately remove the restriction.
- For "non-simple" requests (JSON `Content-Type`, custom headers like `X-Api-Key`, methods such as `PATCH` or `DELETE`) the browser first sends a **preflight** `OPTIONS` request asking permission; the server must answer it with the allowed methods and headers. The mock server does exactly that.
- Whether a response arrives or not, the browser does not reveal *why* in JavaScript: `fetch` simply rejects with a `TypeError`. The explanation is in the DevTools Console, which says something like "...has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource".

```html file="index.html" page mock ignore="Access to fetch;Failed to load resource" steps="wait 400"
<!DOCTYPE html>
<html lang="en">
  <body>
    <script type="module">
      const BASE = "http://localhost:3001";

      try {
        const response = await fetch(`${BASE}/no-cors`);
        console.log("read ok", response.status);
      } catch (error) {
        console.log("blocked:", error.name);
      }

      const opaque = await fetch(`${BASE}/no-cors`, { mode: "no-cors" });
      console.log(opaque.type, opaque.status, JSON.stringify(await opaque.text()));

      const patch = await fetch(`${BASE}/todos/1`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ completed: false }),
      });
      console.log("PATCH allowed:", patch.status);
    </script>
  </body>
</html>
```

```output
blocked: TypeError
opaque 0 ""
PATCH allowed: 200
```

The first request goes to the endpoint that sends **no CORS headers**: the page cannot read the response and `fetch` rejects with a `TypeError`. The second uses `mode: "no-cors"`, the most common wrong "fix": the request is *sent*, but the answer is an **opaque response** (`type` is `"opaque"`, status `0`, empty body) that you can never read, so it cannot give you data. The third request (a `PATCH` with a JSON body) triggers a preflight, which the mock server answers correctly, so it succeeds. (The Console also shows the red CORS error, which is not repeated in the output panel because its text contains the test page's address.)

## Common mistakes in this section

#### Mistake 1: Putting an API key in front-end code

**Why it is wrong.** It is public the moment the page loads.

```js bad nocheck
// anyone can open DevTools and copy this
const API_KEY = "sk_live_51H8...";
const response = await fetch("https://api.paid-service.example/v1/charge", {
  headers: { Authorization: `Bearer ${API_KEY}` },
});
```

**Symptom.** Unexpected usage or charges, a provider email about leaked keys, or the key found by automated scanners within hours of being published (also on public Git repositories). **Fix:** move the call to a server (the proxy above) and **rotate** the leaked key (replace it with a new one; deleting the line does not un-leak it). **Diagnosis:** search your built JavaScript for strings that look like keys, and read the Network tab as a stranger would.

#### Mistake 2: Hammering a rate-limited API

**Why it is wrong.** The server refuses once you exceed the limit, and you waste requests (and may be blocked).

```js bad run mock bundle=net
import { getJSON } from "./http.js";

const statuses = [];
for (let i = 0; i < 6; i++) {
  try {
    await getJSON("http://localhost:3001/limited");
    statuses.push(200);
  } catch (error) {
    statuses.push(error.status);
  }
}
console.log(statuses.join(" "));
```

```output
200 200 200 429 429 429
```

**Symptom.** After the first few calls every answer is `429`. **Fix:** cache, debounce, and when you do get a `429`, wait for `Retry-After` before trying again (see `withRetry`). **Diagnosis:** DevTools Network tab: a column of red `429` rows.

#### Mistake 3: "Fixing" CORS with `mode: "no-cors"`

**Why it is wrong.** It does not remove the restriction; it only hides the error, because you get an unreadable opaque response (shown above).

**Symptom.** The request seems to succeed (no exception), but `response.status` is `0` and `await response.json()` throws. **Fix:** configure the server to send the right CORS headers, or call it through your own backend or a development proxy. **Diagnosis:** read the Console message; it names the missing header.

#### Mistake 4: Committing secrets to Git

**Why it is wrong.** A repository keeps its full history. A key committed once and later deleted is still readable in an earlier commit, and public repositories are scanned by bots continuously.

**Symptom.** A leaked-key alert, or unexplained usage. **Fix:** treat the key as compromised and **revoke and replace it**; keep real values in files such as `.env` that are listed in `.gitignore`, and commit a `.env.example` with placeholder names only (Sheet 09 and Sheet 12 cover this in detail). **Diagnosis:** run `git log -p` and search for the key text; if it is there, rotation is the only cure.
