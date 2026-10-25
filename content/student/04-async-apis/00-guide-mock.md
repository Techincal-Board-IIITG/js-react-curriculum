---
number: 04
title: Asynchronous JavaScript and APIs
subtitle: Waiting without freezing: the event loop, promises, async/await, and talking to web services with fetch
track: js
time: Core path about 28-32 hours
edition: Student edition
goals:
  - Explain synchronous and asynchronous execution, the call stack and the event loop
  - Create and chain promises, and write the same logic with async and await
  - Send GET and POST requests with fetch, using query parameters, headers and JSON bodies
  - Handle network errors and HTTP errors reliably, with timeouts, retries and cancellation
  - Run requests in parallel, avoid unnecessary requests, and keep secrets out of front-end code
---

# 1. Study Guide and Learning Objectives

Nearly everything interesting a web page does involves **waiting**: for a server to answer, for a timer to expire, for a user to click. JavaScript handles waiting in a particular way, and misunderstanding it produces the most confusing bugs a beginner meets: values that are `undefined` "for no reason", code that runs in a surprising order, requests that finish in the wrong sequence. This sheet explains the machinery so that asynchronous code becomes predictable, then applies it to the job every front-end developer does daily: fetching data from an API.

## Learning objectives

By the end of this sheet you should be able to do each of the following without looking anything up.

- Explain why JavaScript uses asynchronous code, and describe the call stack, the task queue, the microtask queue and the event loop.
- Predict the output order of code mixing synchronous statements, `setTimeout`, promises and `queueMicrotask`.
- Create promises, explain their three states, and use `.then()`, `.catch()` and `.finally()` including chaining.
- Write `async` functions with `await` and `try/catch`, and explain what `await` pauses and what it does not.
- Use `fetch()`: build URLs with path and query parameters, send headers and JSON bodies, read `Response` objects, and tell **network failures** apart from **HTTP error statuses**.
- Explain HTTP methods and status codes, and REST conventions for resources.
- Run requests in parallel with `Promise.all()` and `Promise.allSettled()`, and know when to use `race` and `any`.
- Cancel requests with `AbortController`, add timeouts and retries, and debounce user input.
- Explain rate limits, CORS, and why secrets must never appear in front-end code.

## Recommended workload

[[widths 1.2 3.4]]
| Item | Recommendation |
|---|---|
| **Essential topics** | Sections 2 to 10 except boxes marked *Optional deep dive*. |
| **Optional deep dives** | Microtask starvation, `Promise.any` and `race`, `AbortSignal.timeout`, retry with exponential backoff and jitter. |
| **Required exercises** | Sets A to D in full; at least one challenge from set E. |
| **Core projects (do these)** | Projects 1, 2 and 3. |
| **Extension projects** | Projects 4 and 5. |
| **Estimated study time** | Reading and experimenting: 12 to 14 hours. Exercises: 6 to 7 hours. Core projects: 9 to 11 hours. Extension projects add about 5 to 6 hours. |

::: warning Prerequisites
You need Sheets 01 to 03: callbacks and closures, arrays and objects, `try/catch`, ES modules, the DOM, events and `JSON`. Promises build directly on callbacks, and every browser example uses the render-from-data pattern from Sheet 03.
:::

## The mock API: a server you run yourself

Real web services change, impose rate limits, sometimes need accounts, and are occasionally offline. To learn reliably (and to let you finish every exercise offline), this sheet comes with a small **mock API server** written in Node.js. It imitates the shapes of real, public services: a to-do list, weather by city, currency rates, GitHub-style user profiles, and a show search. It can also misbehave on purpose: respond slowly, fail, rate-limit you, and reorder responses, so you can practise handling trouble.

Save this file as `mock-server.mjs` and start it in a terminal (leave the terminal open):

```text file="Terminal"
node mock-server.mjs
```

It prints `Mock API listening on http://localhost:3001`. Press `Ctrl+C` to stop it. You do **not** need to understand its code yet; read it again after Section 6. All browser examples in this sheet call `http://localhost:3001`, and the server sends the **CORS headers** that allow pages from any origin to read its responses (Section 10 explains why that matters).

```js file="mock-server.mjs"
import http from "node:http";

const PORT = Number(process.env.PORT ?? 3001);

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type,X-Api-Key",
};
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

let todos, nextId, flakyCalls, limitedCalls;
function reset() {
  todos = [
    { id: 1, title: "Buy milk", completed: true },
    { id: 2, title: "Write report", completed: false },
    { id: 3, title: "Call Asha", completed: false },
  ];
  nextId = 4;
  flakyCalls = 0;
  limitedCalls = 0;
}
reset();

const WEATHER = {
  pune: { city: "Pune", temperatureC: 31, condition: "Sunny" },
  oslo: { city: "Oslo", temperatureC: 4, condition: "Cloudy" },
  lima: { city: "Lima", temperatureC: 19, condition: "Fog" },
};
const RATES = {
  USD: { EUR: 0.92, GBP: 0.79, INR: 83.2 },
  EUR: { USD: 1.09, GBP: 0.86, INR: 90.5 },
  GBP: { USD: 1.27, EUR: 1.16, INR: 105.3 },
};
const PROFILES = {
  octocat: { login: "octocat", name: "The Octocat", public_repos: 2, followers: 20 },
  "asha-dev": { login: "asha-dev", name: "Asha Rao", public_repos: 1, followers: 3 },
};
const REPOS = {
  octocat: [
    { id: 1, name: "hello-world", stargazers_count: 80, language: "JavaScript" },
    { id: 2, name: "spoon-knife", stargazers_count: 12, language: "HTML" },
  ],
  "asha-dev": [{ id: 3, name: "portfolio", stargazers_count: 2, language: "CSS" }],
};
const SHOWS = [
  { id: 1, name: "Space Cats", genres: ["Comedy"], rating: { average: 7.8 } },
  {
    id: 2,
    name: "Space Station",
    genres: ["Drama", "Sci-Fi"],
    rating: { average: 8.4 },
  },
  { id: 3, name: "Spaced Out", genres: ["Comedy"], rating: { average: null } },
  { id: 4, name: "Cooking Duel", genres: ["Reality"], rating: { average: 6.1 } },
];

function send(res, status, body, extra = {}) {
  res.writeHead(status, { "Content-Type": "application/json", ...cors, ...extra });
  res.end(body === undefined || status === 204 ? "" : JSON.stringify(body));
}

async function readJson(req) {
  let text = "";
  for await (const chunk of req) {
    text += chunk;
  }
  if (text === "") return null;
  try {
    return JSON.parse(text);
  } catch (error) {
    return undefined;
  }
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, "http://localhost");
  const path = url.pathname;
  const q = url.searchParams;
  let m;

  if (req.method === "OPTIONS") return send(res, 204);
  if (path === "/__reset") {
    reset();
    return send(res, 200, { ok: true });
  }

  if (path === "/todos" && req.method === "GET") {
    let list = todos;
    if (q.has("completed")) {
      list = list.filter((t) => String(t.completed) === q.get("completed"));
    }
    return send(res, 200, list.slice(0, Number(q.get("limit") ?? list.length)));
  }
  if (path === "/todos" && req.method === "POST") {
    const body = await readJson(req);
    if (!body || typeof body.title !== "string" || body.title.trim() === "") {
      return send(res, 400, { error: "title is required" });
    }
    const todo = { id: nextId++, title: body.title.trim(), completed: false };
    todos.push(todo);
    return send(res, 201, todo);
  }
  if ((m = path.match(/^\/todos\/(\d+)$/))) {
    const id = Number(m[1]);
    const todo = todos.find((t) => t.id === id);
    if (!todo) return send(res, 404, { error: "Todo not found" });
    if (req.method === "GET") return send(res, 200, todo);
    if (req.method === "PATCH") {
      Object.assign(todo, (await readJson(req)) ?? {}, { id });
      return send(res, 200, todo);
    }
    if (req.method === "DELETE") {
      todos = todos.filter((t) => t.id !== id);
      return send(res, 204);
    }
  }

  if ((m = path.match(/^\/status\/(\d{3})$/))) {
    return send(res, Number(m[1]), { status: Number(m[1]) });
  }
  if (path === "/slow") {
    const ms = Number(q.get("ms") ?? 200);
    await wait(ms);
    return send(res, 200, { waited: ms });
  }
  if (path === "/flaky") {
    flakyCalls++;
    if (flakyCalls <= 2) {
      return send(res, 503, { error: "Try again" }, { "Retry-After": "1" });
    }
    return send(res, 200, { ok: true, attempt: flakyCalls });
  }
  if (path === "/limited") {
    limitedCalls++;
    if (limitedCalls > 3) {
      return send(res, 429, { error: "Too many requests" }, { "Retry-After": "1" });
    }
    return send(res, 200, { call: limitedCalls });
  }
  if (path === "/echo") {
    const body = await readJson(req);
    return send(res, 200, {
      method: req.method,
      query: Object.fromEntries(q),
      contentType: req.headers["content-type"] ?? null,
      apiKey: req.headers["x-api-key"] ?? null,
      body,
    });
  }

  if (path === "/no-cors") {
    res.writeHead(200, { "Content-Type": "application/json" });
    return res.end(JSON.stringify({ note: "this response has no CORS headers" }));
  }

  if (path === "/weather") {
    await wait(60);
    const data = WEATHER[(q.get("city") ?? "").toLowerCase()];
    return data ? send(res, 200, data) : send(res, 404, { error: "City not found" });
  }
  if (path === "/rates") {
    const base = (q.get("base") ?? "USD").toUpperCase();
    return RATES[base]
      ? send(res, 200, { base, date: "2026-03-14", rates: RATES[base] })
      : send(res, 404, { error: "Unknown currency" });
  }
  if ((m = path.match(/^\/github\/users\/([\w-]+)(\/repos)?$/))) {
    const name = m[1].toLowerCase();
    if (!PROFILES[name]) return send(res, 404, { message: "Not Found" });
    return send(res, 200, m[2] ? REPOS[name] : PROFILES[name]);
  }
  if (path === "/shows") {
    const term = (q.get("q") ?? "").toLowerCase();
    await wait(term.length <= 1 ? 250 : 40);
    const hits = SHOWS.filter((s) => s.name.toLowerCase().includes(term));
    return send(res, 200, hits.map((show) => ({ score: 0.9, show })));
  }

  return send(res, 404, { error: "No such route" });
});

server.listen(PORT, () => {
  console.log(`Mock API listening on http://localhost:${PORT}`);
});
```

[[widths 1.7 3.4]]
| Endpoint | What it does |
|---|---|
| `GET /todos`, `?completed=true`, `?limit=2` | List to-dos, optionally filtered |
| `GET /todos/:id` | One to-do, or `404` with `{ "error": ... }` |
| `POST /todos` | Create from a JSON body `{ "title": "..." }`; `201` on success, `400` if the title is missing |
| `PATCH /todos/:id`, `DELETE /todos/:id` | Update (`200`) or delete (`204`, no body) |
| `GET /status/:code` | Answers with exactly that status code |
| `GET /slow?ms=500` | Waits that long, then answers |
| `GET /flaky` | Fails with `503` twice, then succeeds |
| `GET /limited` | Allows three calls, then answers `429` with a `Retry-After` header |
| `GET /echo` | Reports back the method, query, headers and body you sent |
| `GET /weather?city=Pune` | Weather for `pune`, `oslo` or `lima`; `404` otherwise |
| `GET /rates?base=USD` | Currency rates for `USD`, `EUR` or `GBP` |
| `GET /github/users/octocat`, `.../repos` | A GitHub-style profile and repository list |
| `GET /shows?q=space` | Show search; one-letter searches answer slowly (used for the race-condition exercise) |
| `GET /no-cors` | Answers **without** CORS headers, so browsers refuse to let a page read it (Section 10) |
| `GET /__reset` | Restores the initial state of everything |

::: note Real services versus this mock
The projects in this sheet can run against the mock server or against real public services (Open-Meteo for weather, the GitHub API for profiles, TVMaze for shows, Frankfurter for currency rates). Put the base address in one constant so you can switch. **The mock imitates the general shape of those services but is not identical**, and real services change; always check the provider's current documentation before relying on a field name. Everything in the worked examples is tested against the mock server.
:::

::: note How the examples in this sheet were tested
Node examples were executed in Node.js. Browser examples were loaded in headless Chromium against the mock server, driven by scripted clicks and typing, and their output was compared with the output panels. Examples that depend on timing show only results that do not vary (for example "finished in under 250 ms: true"), never raw millisecond counts.
:::
