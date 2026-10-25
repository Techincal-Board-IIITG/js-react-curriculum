## Project 4: Currency converter

```js file="currency-logic.js" bundle=w4
export function parseAmount(text) {
  return Number(text.trim().replace(",", "."));
}

export function validateAmount(text) {
  const value = parseAmount(text);
  if (text.trim() === "" || !Number.isFinite(value) || value <= 0) {
    return "Enter a positive number";
  }
  return "";
}

export function convert(amount, from, to, table) {
  if (from === to) {
    return amount;
  }
  const rateFrom = from === table.base ? 1 : table.rates[from];
  const rateTo = to === table.base ? 1 : table.rates[to];
  if (rateFrom === undefined || rateTo === undefined) {
    throw new Error(`No rate for ${rateFrom === undefined ? from : to}`);
  }
  return (amount / rateFrom) * rateTo;
}

export const formatAmount = (value) => value.toFixed(2);
```

```js file="test-currency.mjs" run bundle=w4
import {
  validateAmount, parseAmount, convert, formatAmount,
} from "./currency-logic.js";

const table = { base: "USD", rates: { EUR: 0.92, GBP: 0.79 } };
console.log(convert(100, "USD", "EUR", table), convert(50, "EUR", "EUR", table));
console.log(formatAmount(convert(100, "EUR", "GBP", table)));
const small = formatAmount(convert(0.1, "USD", "EUR", table));
const huge = formatAmount(convert(1e9, "USD", "GBP", table));
console.log(small, huge);

const inputs = ["", "abc", "-2", "0", "1,5", " 12 "];
const verdicts = inputs.map((t) => (validateAmount(t) === "" ? "valid" : "invalid"));
console.log(parseAmount("1,5"));
console.log(verdicts.join(" "));

try {
  convert(1, "USD", "JPY", table);
} catch (error) {
  console.log(error.message);
}
```

```output
92 50
85.87
0.09 790000000.00
1.5
invalid invalid invalid invalid valid valid
No rate for JPY
```

Conversion goes **through the base currency**: divide by the source rate to get base units, multiply by the target rate. Rounding happens only in `formatAmount`, at the very last step. The comma decimal separator is accepted by replacing `,` before `Number()`.

```html file="index.html" bundle=w4,net page mock ignore="Failed to load resource" steps="fill #amount 100 | click #go | wait 300 | print #result | eval String(window.requestCount) | click #swap | wait 300 | print #result | eval String(window.requestCount) | click #swap | wait 300 | print #result | eval String(window.requestCount) | fill #amount abc | click #go | print #result | eval String(window.requestCount) | fill #amount 1,5 | click #go | wait 300 | print #result | reload | eval document.getElementById('from').value"
<!DOCTYPE html>
<html lang="en">
  <body>
    <input id="amount" />
    <select id="from">
      <option>USD</option>
      <option>EUR</option>
      <option>GBP</option>
    </select>
    <select id="to">
      <option>EUR</option>
      <option>USD</option>
      <option>GBP</option>
    </select>
    <button id="go">Convert</button>
    <button id="swap" type="button">Swap</button>
    <p id="result"></p>
    <script type="module">
      import { getJSON } from "./http.js";
      import {
        validateAmount, parseAmount, convert, formatAmount,
      } from "./currency-logic.js";

      const BASE = "http://localhost:3001";
      const TTL = 10 * 60 * 1000;
      const $ = (id) => document.getElementById(id);
      const cache = new Map();
      window.requestCount = 0;

      try {
        const saved = JSON.parse(localStorage.getItem("pair-v1"));
        if (saved) {
          $("from").value = saved.from;
          $("to").value = saved.to;
        }
      } catch (error) {
        /* ignore corrupted storage */
      }

      async function getRates(base) {
        const hit = cache.get(base);
        if (hit && Date.now() - hit.at < TTL) return hit.table;
        window.requestCount++;
        const table = await getJSON(`${BASE}/rates?base=${base}`);
        cache.set(base, { table, at: Date.now() });
        return table;
      }

      async function run() {
        const error = validateAmount($("amount").value);
        if (error) {
          $("result").textContent = error;
          return;
        }
        const from = $("from").value;
        const to = $("to").value;
        localStorage.setItem("pair-v1", JSON.stringify({ from, to }));
        $("result").textContent = "Loading rates...";
        try {
          const table = await getRates(from);
          const amount = parseAmount($("amount").value);
          const value = formatAmount(convert(amount, from, to, table));
          const rate = Math.round(convert(1, from, to, table) * 10000) / 10000;
          $("result").textContent =
            `${value} ${to} (1 ${from} = ${rate} ${to}, rates as of ${table.date})`;
        } catch (failure) {
          $("result").textContent = "Could not load rates. Try again.";
        }
      }

      $("go").addEventListener("click", run);
      $("swap").addEventListener("click", () => {
        const from = $("from").value;
        $("from").value = $("to").value;
        $("to").value = from;
        run();
      });
    </script>
  </body>
</html>
```

```output
92.00 EUR (1 USD = 0.92 EUR, rates as of 2026-03-14)
1
109.00 USD (1 EUR = 1.09 USD, rates as of 2026-03-14)
2
92.00 EUR (1 USD = 0.92 EUR, rates as of 2026-03-14)
2
Enter a positive number
2
1.38 EUR (1 USD = 0.92 EUR, rates as of 2026-03-14)
USD
```

In order: the converted result and request count for `100 USD -> EUR` (one request); after **Swap** (`EUR -> USD`, a new base, so a second request); after swapping back (`USD` rates were cached, so the count stays at two); the validation message for `abc` (no request); `1,5` with a comma decimal; and, after a reload, the remembered "from" currency.

## Project 5: Concurrent API data aggregator

```js file="aggregator-logic.js" bundle=w5
export function parseCities(text, max = 30) {
  const seen = new Set();
  const list = [];
  for (const line of text.split("\n")) {
    const city = line.trim();
    const key = city.toLowerCase();
    if (city !== "" && !seen.has(key)) {
      seen.add(key);
      list.push(city);
    }
  }
  return list.slice(0, max);
}

export function summarise(rows) {
  const ok = rows.filter((r) => r.status === "ok");
  if (ok.length === 0) {
    return {
      succeeded: 0,
      total: rows.length,
      average: null,
      hottest: null,
      coldest: null,
    };
  }
  const sum = ok.reduce((total, r) => total + r.temperatureC, 0);
  const hottest = ok.reduce((a, b) => (b.temperatureC > a.temperatureC ? b : a));
  const coldest = ok.reduce((a, b) => (b.temperatureC < a.temperatureC ? b : a));
  return {
    succeeded: ok.length,
    total: rows.length,
    average: Math.round((sum / ok.length) * 10) / 10,
    hottest: hottest.city,
    coldest: coldest.city,
  };
}

export async function mapPool(items, limit, worker, signal) {
  const results = new Array(items.length);
  let next = 0;

  async function runner() {
    while (next < items.length && !signal?.aborted) {
      const index = next++;
      results[index] = await worker(items[index], index);
    }
  }

  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, runner));
  return results;
}
```

```js file="test-aggregator.mjs" run bundle=w5,net
import { parseCities, summarise, mapPool } from "./aggregator-logic.js";
import { wait } from "./http.js";

console.log(parseCities(" Pune \n\nOslo\nAtlantis\nLima\npune\n"));
console.log(parseCities("a\nb\nc\nd", 2));

const rows = [
  { city: "Pune", status: "ok", temperatureC: 31 },
  { city: "Oslo", status: "ok", temperatureC: 4 },
  { city: "Atlantis", status: "not found" },
  { city: "Lima", status: "ok", temperatureC: 19 },
];
console.log(summarise(rows));
console.log(summarise([{ city: "X", status: "failed after retries" }]));
console.log(summarise([]));

const controller = new AbortController();
let started = 0;
const results = await mapPool(
  [1, 2, 3, 4, 5, 6],
  2,
  async (n) => {
    started++;
    if (n === 3) controller.abort();
    await wait(20);
    return n;
  },
  controller.signal
);
const finished = results.filter((r) => r !== undefined).length;
console.log("started:", started, "| finished:", finished);
```

```output
[ 'Pune', 'Oslo', 'Atlantis', 'Lima' ]
[ 'a', 'b' ]
{
  succeeded: 3,
  total: 4,
  average: 18,
  hottest: 'Pune',
  coldest: 'Oslo'
}
{ succeeded: 0, total: 1, average: null, hottest: null, coldest: null }
{ succeeded: 0, total: 0, average: null, hottest: null, coldest: null }
started: 3 | finished: 3
```

`summarise` ignores failures and returns `null` statistics (not `NaN`) when there are no successes. `mapPool` stops **starting** new items once the signal is aborted: here item 3 aborts the run, items 1 to 3 had started, and items 4 to 6 never did.

```html file="index.html" bundle=w5,net page mock ignore="Failed to load resource" steps="eval (cities.value = 'Pune\nOslo\nAtlantis\nLima\npune', 'list set') | click #run | wait 900 | print #progress | eval rowsText() | print #summary | eval String(window.maxActive <= 3) | eval (window.artificialDelayMs = 400, 'slow mode on') | click #run | wait 100 | click #cancel | wait 300 | eval rowsText() | print #summary | eval String(document.getElementById('run').disabled)"
<!DOCTYPE html>
<html lang="en">
  <body>
    <textarea id="cities" rows="6"></textarea>
    <button id="run">Fetch weather</button>
    <button id="cancel" type="button" disabled>Cancel</button>
    <p id="progress"></p>
    <table>
      <thead>
        <tr><th>City</th><th>Temp</th><th>Condition</th><th>Status</th></tr>
      </thead>
      <tbody id="rows"></tbody>
    </table>
    <p id="summary"></p>
    <script type="module">
      import { getJSON, withRetry } from "./http.js";
      import { parseCities, summarise, mapPool } from "./aggregator-logic.js";

      const BASE = "http://localhost:3001";
      const LIMIT = 3;
      const $ = (id) => document.getElementById(id);
      window.maxActive = 0;
      let active = 0;
      let controller = null;
      let current = [];

      function abortableWait(ms, signal) {
        return new Promise((resolve, reject) => {
          const timer = setTimeout(resolve, ms);
          signal.addEventListener("abort", () => {
            clearTimeout(timer);
            reject(signal.reason);
          }, { once: true });
        });
      }

      async function fetchCity(city, signal) {
        try {
          if (window.artificialDelayMs) {
            await abortableWait(window.artificialDelayMs, signal);
          }
          active++;
          window.maxActive = Math.max(window.maxActive, active);
          try {
            const url = `${BASE}/weather?city=${encodeURIComponent(city)}`;
            const request = () => {
              const both = AbortSignal.any([signal, AbortSignal.timeout(3000)]);
              return getJSON(url, { signal: both });
            };
            const data = await withRetry(request, { retries: 2, delayMs: 20 });
            return {
              city,
              status: "ok",
              temperatureC: data.temperatureC,
              condition: data.condition,
            };
          } finally {
            active--;
          }
        } catch (error) {
          if (error.name === "AbortError") return { city, status: "cancelled" };
          if (error.status === 404) return { city, status: "not found" };
          return { city, status: "failed after retries" };
        }
      }

      function render(rows) {
        current = rows;
        $("rows").replaceChildren();
        for (const row of rows) {
          const tr = document.createElement("tr");
          const cells = [
            row.city,
            row.temperatureC ?? "-",
            row.condition ?? "-",
            row.status,
          ];
          for (const value of cells) {
            const td = document.createElement("td");
            td.textContent = value;
            tr.append(td);
          }
          $("rows").append(tr);
        }
      }

      function showSummary(rows) {
        const s = summarise(rows);
        const head = `${s.succeeded} of ${s.total} succeeded`;
        const stats =
          s.average === null
            ? "no statistics"
            : `average ${s.average} C, hottest ${s.hottest}, coldest ${s.coldest}`;
        $("summary").textContent = `${head}, ${stats}`;
      }

      $("run").addEventListener("click", async () => {
        const cities = parseCities($("cities").value);
        if (cities.length === 0) {
          $("progress").textContent = "Enter at least one city.";
          return;
        }
        controller = new AbortController();
        const { signal } = controller;
        const rows = cities.map((city) => ({ city, status: "waiting" }));
        let done = 0;
        render(rows);
        $("progress").textContent = `0/${cities.length}`;
        $("run").disabled = true;
        $("cancel").disabled = false;

        await mapPool(cities, LIMIT, async (city, i) => {
          rows[i] = await fetchCity(city, signal);
          done++;
          $("progress").textContent = `${done}/${cities.length}`;
          render(rows);
        }, signal);

        for (let i = 0; i < rows.length; i++) {
          if (rows[i].status === "waiting") {
            rows[i] = { city: cities[i], status: "cancelled" };
          }
        }
        render(rows);
        showSummary(rows);
        $("run").disabled = false;
        $("cancel").disabled = true;
      });

      $("cancel").addEventListener("click", () => controller?.abort());

      window.rowsText = () =>
        [...document.querySelectorAll("#rows tr")]
          .map((tr) => [...tr.children].map((td) => td.textContent).join(" "))
          .join(" / ");
    </script>
  </body>
</html>
```

```output
list set
4/4
Pune 31 Sunny ok / Oslo 4 Cloudy ok / Atlantis - - not found / Lima 19 Fog ok
3 of 4 succeeded, average 18 C, hottest Pune, coldest Oslo
true
slow mode on
Pune - - cancelled / Oslo - - cancelled / Atlantis - - cancelled / Lima - - cancelled
0 of 4 succeeded, no statistics
false
```

First run, in order: the progress `4/4` (the duplicate `pune` was removed, so four unique cities); the table in input order with a clear status per row; the summary computed only from the three successes; and a check that no more than three requests were ever active. For the second run the test-only hook `window.artificialDelayMs` slows every request so that **Cancel** can be pressed deterministically: all rows end as `cancelled` (the running ones through the abort signal, the not-yet-started one by being marked after the pool stops), the summary shows no statistics rather than `NaN`, and the **Run** button is re-enabled.

# 8. Self-Assessment Answers

1. A `.then` callback is a microtask, which runs as soon as the current script ends; `setTimeout(fn, 0)` is a task and waits for the microtask queue to empty first.
2. `1`, `4`, `3`, `2`.
3. Pending, fulfilled, rejected. A settled promise never changes.
4. `undefined`.
5. `.catch` handles a rejection and, if it returns normally, turns the chain back to fulfilled. `.finally` runs for cleanup in both cases, takes no argument, and lets the original outcome continue.
6. A promise that fulfils with `5`. `await` pauses only the async function it is in.
7. Each `await` in the loop waits for the previous task, so delays add up; `Promise.all` starts them together. The sequential loop is still right when each step needs the previous result or the order of side effects matters.
8. `GET` is safe; `GET`, `PUT`, `DELETE` are idempotent. A retried `POST` can create duplicates.
9. 201 created, 204 no content, 400 bad request, 401 not authenticated, 403 forbidden, 404 not found, 429 too many requests, 503 service unavailable. Retry (carefully) 429 and 503; not 400, 401, 403 or 404 unchanged.
10. No; it resolves with `ok: false`. It rejects on network failure, CORS block, or abort.
11. The body is a stream that can be consumed once; read it once and keep the result (or `clone()` first).
12. `JSON.stringify` on the body and the header `Content-Type: application/json`.
13. By `error.name` and `error.status`: `TimeoutError`, `AbortError`, or a numeric HTTP status; a `TypeError` with no status is a network failure.
14. It rejects at once with the first reason. The other promises are not cancelled and keep running.
15. `allSettled` for partial results, `race` for "first to finish" such as timeouts, `any` for "first success" among alternatives.
16. Abort the previous request when a new one starts, or tag each request with a counter and ignore any answer that is not from the latest.
17. A closure holds the timer between calls; a new debounced function per event would have separate timers that never cancel each other.
18. The build copies it into the shipped JavaScript, which every user can read. Keep it on a server and call that server.
19. The browser enforces it; servers grant permission with headers. `mode: "no-cors"` only gives an unreadable opaque response.
20. Debounce and cache requests, honour `Retry-After`, back off between retries, and cap the number of retries.
