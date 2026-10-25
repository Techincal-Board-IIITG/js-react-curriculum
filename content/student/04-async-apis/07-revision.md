# 13. Revision and Assessment

## Summary of this sheet

JavaScript runs on **one thread**. Slow work is handed to the environment, and callbacks return through queues: the **call stack** runs your code; when it is empty the **event loop** first runs **every microtask** (promise callbacks, `queueMicrotask`), then takes **one task** (timers, events, network completions). `setTimeout(fn, 0)` is a later task, never "now". A **promise** is pending, then fulfilled or rejected, once. `.then`, `.catch` and `.finally` return **new promises**; returned values flow on, returned promises are adopted, thrown errors reject, `.catch` recovers, and every chain needs a `.catch`. **`async` functions** return promises; **`await`** pauses only that function and rethrows rejections, so `try/catch` works; independent work should be started together and awaited with `Promise.all`. **HTTP** is request and response with methods (safe `GET`; `POST`, `PUT`, `PATCH`, `DELETE`), status families (2xx, 4xx = your fault, 5xx = theirs), headers and bodies; **REST** names resources with nouns, with path parameters to identify and query parameters to refine. **`fetch`** fulfils when headers arrive, even for `404`/`500`; check `response.ok`, read the body **once**, send JSON with `JSON.stringify` and `Content-Type`, and build URLs with `URLSearchParams` and `encodeURIComponent`. Reliable code distinguishes network errors, timeouts (`AbortSignal.timeout`), HTTP statuses and cancellations, shows human messages, and retries only safe, retryable failures, with a limit and backoff. `Promise.all` fails fast, `allSettled` keeps partial results, `race` takes the first to settle and `any` the first success. `AbortController` cancels requests (create a new one each time); debounce avoids needless requests; abort or ignore stale responses. Respect **rate limits** (`429`, `Retry-After`, caching), keep **secrets** on a server, and remember **CORS** is enforced by the browser and fixed on the server.

## Key syntax reference

[[widths 1.4 3.4 2.2]]
| Topic | Syntax | Notes |
|---|---|---|
| Promise | `new Promise((resolve, reject) => { ... })` | Executor runs immediately; settles once |
| Chain | `p.then(f).catch(g).finally(h)` | Each returns a new promise; always end with `catch` |
| Async function | `async function f() { const v = await p; return v; }` | Returns a promise; `await` only inside |
| Parallel | `await Promise.all([a(), b()])` | Results in input order; fails fast |
| Partial results | `await Promise.allSettled(list)` | `{ status, value }` or `{ status, reason }` |
| First result | `Promise.race(list)`, `Promise.any(list)` | `any` rejects with `AggregateError` |
| Fetch | `const r = await fetch(url, { method, headers, body, signal })` | Resolves for 404; check `r.ok` |
| Body | `await r.json()`, `await r.text()` | Once only; empty for `204` |
| JSON request | `body: JSON.stringify(data)`, header `Content-Type: application/json` | Both required |
| URL building | `new URLSearchParams({ q })`, `encodeURIComponent(x)` | Never concatenate raw text |
| Timeout | `fetch(url, { signal: AbortSignal.timeout(5000) })` | Error name `TimeoutError` |
| Cancel | `const c = new AbortController(); fetch(url, { signal: c.signal }); c.abort()` | Error name `AbortError`; single use |
| Debounce | `const f = debounce(fn, 250)` | Create once, outside the handler |
| Timers | `setTimeout`, `clearTimeout`, `queueMicrotask` | Timers are tasks, microtasks run first |

## Important terms and definitions

[[widths 1.3 4]]
| Term | Definition |
|---|---|
| Synchronous / asynchronous | Finishes before the next line / starts now, finishes later |
| Call stack | The list of functions currently running |
| Event loop | The loop that moves queued callbacks onto the stack when it is empty |
| Task (macrotask) | A queued callback such as a timer or event; one runs per loop turn |
| Microtask | A queued promise callback; all run before the next task |
| Promise | An object representing a value available later (pending, fulfilled, rejected) |
| Settled | Fulfilled or rejected; final |
| Chaining | Using the new promise each `.then` returns to sequence steps |
| Idempotent | Repeating the request has the same effect as sending it once |
| Status code | The number in a response telling how the request went |
| REST | An API style with resources as nouns and HTTP methods as verbs |
| Preflight | The browser's `OPTIONS` request asking a server to permit a cross-origin request |
| CORS | The server-granted permission for pages from other origins to read responses |
| Race condition | A bug where the result depends on which operation finishes first |
| Debounce | Delay an action until events stop for a set time |
| Rate limit | A cap on requests per period; exceeding it gives `429` |
| Backoff | Waiting progressively longer between retries |

## Common mistakes checklist

- [ ] Every promise chain ends with `.catch`, or the `await` sits inside `try/catch`.
- [ ] Every `.then` callback with a block body has a `return`.
- [ ] I pass functions to `.then` and `setTimeout`, never calls (`fn`, not `fn()`).
- [ ] I `await` every promise I need the value of, including `response.json()`.
- [ ] Independent requests run together with `Promise.all`; I never use `forEach` with `async`.
- [ ] After every `fetch` I check `response.ok`; I do not call `.json()` on a `204`.
- [ ] I send objects with `JSON.stringify` and a `Content-Type` header.
- [ ] URLs are built with `URLSearchParams` and `encodeURIComponent`.
- [ ] Every request has a timeout; retries are limited, spaced out, and only for safe, retryable failures.
- [ ] Search-as-you-type is debounced and aborts or ignores stale responses; `AbortError` is not shown as an error.
- [ ] Each request that may be cancelled gets a **new** `AbortController`.
- [ ] No secret appears in front-end code, `localStorage`, or Git history.

## Self-assessment questions

1. Why is `setTimeout(fn, 0)` slower than a `.then` callback? (Section 2)
2. What does this print: `console.log(1); setTimeout(() => console.log(2)); Promise.resolve().then(() => console.log(3)); console.log(4);`? (Section 2)
3. What are the three states of a promise, and can a settled promise change? (Section 3)
4. What does the next `.then` receive if the previous callback forgot `return`? (Section 3)
5. How does `.catch` change a rejected chain? How does `.finally` differ? (Section 3)
6. What does `async function f() { return 5; }` return? What does `await` pause? (Section 4)
7. Why is `for (const x of list) await task(x)` slower than `await Promise.all(list.map(task))`, and when is it still right? (Section 4)
8. Which methods are safe? Which are idempotent? Why should a `POST` not be retried blindly? (Section 5)
9. What do 201, 204, 400, 401, 403, 404, 429 and 503 mean? Which would you retry? (Section 5)
10. Does `fetch` reject for a `404`? What does it reject for? (Section 6)
11. Why can you not call `response.json()` twice? (Section 6)
12. List what must accompany a JSON `POST` body. (Section 6)
13. How do you distinguish a timeout from an HTTP error from a user cancellation? (Sections 7, 9)
14. What does `Promise.all` do if one promise rejects? What do the others do? (Section 8)
15. When do you prefer `allSettled`, `race` or `any`? (Section 8)
16. Explain and fix the stale-response bug in two ways. (Section 9)
17. Why does `debounce` need a closure, and why must it be created only once? (Section 9)
18. Why is an API key in a front-end build not secret? What is the alternative? (Section 10)
19. Who enforces CORS, and what does `mode: "no-cors"` really do? (Section 10)
20. Which `Retry-After` and caching habits keep you inside rate limits? (Section 10)

## Practical completion checklist

- [ ] I ran every worked example (with the mock server where needed) and compared my predictions with the output.
- [ ] I completed exercise sets A to D and at least one challenge from set E.
- [ ] I completed core projects 1, 2 and 3; each handles loading, success, empty and error states.
- [ ] My projects use `http.js` (or equivalent) with a base-URL constant that I can switch between the mock and a real API.
- [ ] My search project aborts or ignores stale responses and debounces input.
- [ ] I can explain the event loop order of a small program without running it.
- [ ] I can find, in DevTools, a request's method, status, headers, payload and timing.
- [ ] (Optional) I completed one or both extension projects.

## Official documentation

- [MDN: Asynchronous JavaScript](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Asynchronous)
- [MDN: The event loop](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Event_loop)
- [MDN: Promise](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise)
- [MDN: async function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function)
- [MDN: Using the Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)
- [MDN: AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController)
- [MDN: HTTP overview](https://developer.mozilla.org/en-US/docs/Web/HTTP)
- [MDN: HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [MDN: Cross-Origin Resource Sharing (CORS)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Node.js: The event loop, timers and nextTick](https://nodejs.org/en/learn/asynchronous-work/event-loop-timers-and-nexttick)
- [GitHub REST API documentation](https://docs.github.com/en/rest)
- [Open-Meteo weather API documentation](https://open-meteo.com/en/docs)
- [TVMaze API documentation](https://www.tvmaze.com/api)
