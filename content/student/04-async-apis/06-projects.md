# 12. Mini Projects

## Mini projects overview

Five browser applications, ordered from easier to harder. **Projects 1 to 3 are the core workload; projects 4 and 5 are extensions.** All of them talk to a web service. Develop **against the mock server first** (always available, predictable, can simulate failures), then optionally switch to the real service described in each project by changing one constant. Real services change, impose rate limits and may need accounts or keys: read the provider's current documentation before relying on any field name, and never put a private key in front-end code (Section 10).

```tree
project/
├── index.html
├── main.js        wiring, events, render
├── api.js         all requests: BASE constant, getJSON, one function per endpoint
├── logic.js       pure functions (sorting, formatting, converting)
└── http.js        the toolkit from Section 7 (plus debounce.js when needed)
```

[[widths 0.5 2.4 1.2 1.1]]
| # | Project | Difficulty | Scope |
|---|---|---|---|
| 1 | Weather dashboard | Easy | Core |
| 2 | GitHub profile explorer | Easy to medium | Core |
| 3 | Show and movie search | Medium | Core |
| 4 | Currency converter | Medium | Extension |
| 5 | Concurrent API data aggregator | Medium to hard | Extension |

::: note Rules for every project
All requests go through `api.js`; every screen has explicit **loading, success, empty and error** states; error messages are human-readable; user text is inserted with `textContent`; a `BASE` constant selects the mock server (`http://localhost:3001`) or a real service; the interface never freezes, never shows stale results, and never leaves a spinner running after a failure.
:::

:::: project Weather dashboard | Difficulty: Easy | Core
##### Objective
Practise a complete `fetch` flow: user input, a request with a query parameter, parsing, four interface states, and persistence of recent searches.

##### Problem statement
Build a page where the user types a city and sees its current weather. The page remembers the last five cities searched and lets the user click one to search again.

##### Required features
- A form with a city name; blank input is rejected with a message before any request is sent.
- Show loading text while waiting; show the city, temperature and condition on success.
- A `404` ("City not found") shows a friendly message; network failures and server errors show different friendly messages.
- A Celsius/Fahrenheit toggle that changes the displayed number **without** a new request.
- Keep recent searches (unique, newest first, at most five) in `localStorage` using safe load and save helpers, and show them as clickable buttons.
- Use `AbortController` so a second search cancels the first.

##### Technical constraints
- All requests live in `api.js` as `getWeather(city, signal)`.
- Build the URL with `URLSearchParams` or `encodeURIComponent`.
- A pure function `toFahrenheit(c)` and a pure function `addRecent(list, city)` live in `logic.js` and are tested in Node.
- Mock endpoint: `GET /weather?city=Pune` (cities `pune`, `oslo`, `lima`).

##### Expected behavior
```text file="Illustrative behaviour"
Search "Pune"      -> Loading... then "Pune: 31 C, Sunny"
Toggle to F        -> "Pune: 87.8 F, Sunny" (no new request)
Search "Atlantis"  -> "City not found. Check the spelling."
Stop the server    -> "Network problem. Check your connection."
Recent: Atlantis, Pune (click Pune to search it again)
```

##### Suggested milestones
1. `getWeather` and a hard-coded city, printing JSON to the console.
2. The form, loading and success states.
3. Error states using `describeError`.
4. Unit toggle and `toFahrenheit` tests.
5. Recent searches with storage, then abort on a new search.

##### Edge cases
- Blank or whitespace-only city; city names with spaces, accents or `&`.
- The user searches twice quickly (the first answer must not overwrite the second).
- Corrupted recent-search data; the same city typed in different capitalisation.
- Slow responses (use `/slow` or edit the mock's delay) and server stopped.

##### Acceptance criteria
- [ ] `toFahrenheit(0)` is `32`, `toFahrenheit(100)` is `212`, `toFahrenheit(31)` is about `87.8`.
- [ ] `addRecent(["Oslo", "Pune"], "pune")` returns `["pune", "Oslo"]` or equivalent with no duplicate (decide on casing and document it), never longer than five.
- [ ] Each of the four failure types produces a different, understandable message.
- [ ] Rapid double searches always end showing the **last** city typed.
- [ ] Reloading the page restores the recent list; corrupted storage does not break the page.

##### Stretch goals
- Use the real Open-Meteo service: a geocoding request turns the city into coordinates, then a forecast request returns current conditions (read both pages of its documentation for current URLs and fields).
- Show a five-day forecast from a second endpoint.
- Detect the browser's language for units.

##### Concepts practiced
`fetch` with query parameters, loading/error states, `AbortController`, `localStorage` with JSON, pure helper functions.
::::

:::: project GitHub profile explorer | Difficulty: Easy to medium | Core
##### Objective
Practise path parameters, two dependent requests, sorting and caching, and handling a service that rate-limits you.

##### Problem statement
Given a username, show the profile (name, followers, public repository count) and a list of that user's repositories sorted by stars, with a link to each.

##### Required features
- A search form for a username (trimmed, validated against letters, digits and `-`).
- Fetch the profile and the repository list **in parallel** and render both; if the repositories fail, still show the profile with an inline error for the list.
- Repositories sorted by stars (highest first), showing name, language and star count; show a message for users with no repositories.
- A `404` shows "User not found"; a rate-limit response (`403` or `429` from the real service) shows a "Try again later" message that includes the wait time if the server provides one.
- Cache results per username in a `Map` for 60 seconds so repeated searches do not use up the limit.

##### Technical constraints
- `api.js` exports `getProfile(name)` and `getRepos(name)`; the username is placed in the path with `encodeURIComponent`.
- Sorting is a pure function `sortByStars(repos)` that does not mutate its input.
- Mock endpoints: `GET /github/users/octocat`, `GET /github/users/octocat/repos` (users `octocat` and `asha-dev`).
- Links open with `rel="noopener noreferrer"`, and the address is only used after an `http:`/`https:` check.

##### Expected behavior
```text file="Illustrative behaviour"
Search "octocat" -> "The Octocat, 20 followers, 2 repos"
                    hello-world (JavaScript) 80 stars
                    spoon-knife (HTML) 12 stars
Search "nobody"  -> "User not found"
Search "octocat" again within a minute -> served from cache (no new request)
```

##### Suggested milestones
1. `getProfile` and rendering the profile alone.
2. `getRepos` and `sortByStars`.
3. Run both requests with `Promise.allSettled` and show partial results.
4. Error messages for 404 and rate limiting.
5. The `Map` cache with expiry.

##### Edge cases
- Usernames with invalid characters, or leading/trailing spaces and capital letters.
- A user with zero repositories; repositories with a missing language (`null`).
- Equal star counts (keep original order); very long names.
- The profile succeeds but the repositories fail (and the reverse).

##### Acceptance criteria
- [ ] `sortByStars` returns a new array ordered by `stargazers_count` descending and leaves the input unchanged.
- [ ] The two requests start together (verify in the Network tab: overlapping bars).
- [ ] A second search for the same user within 60 seconds sends no request.
- [ ] A missing `language` renders as "unknown", not `null`.
- [ ] Invalid usernames never reach the network.

##### Stretch goals
- Real service: the GitHub REST API (`/users/{name}` and `/users/{name}/repos`); unauthenticated requests are rate-limited per IP, so your cache and error handling matter. Read the current documentation, including pagination.
- A language filter built from the repositories you received.
- Pagination of the repository list.

##### Concepts practiced
Path parameters, `Promise.allSettled`, caching with `Map`, sorting without mutation, rate-limit awareness.
::::

:::: project Show and movie search | Difficulty: Medium | Core
##### Objective
Practise search-as-you-type done correctly: debounce, abort, stale-response protection, results, pagination and a details view.

##### Problem statement
Build a search box that finds shows as the user types, lists the results with name, genres and rating, and shows details when one is chosen.

##### Required features
- Debounce input (about 300 ms) and send **one** request for a burst of typing; abort the previous request when a new one starts.
- Distinct states: idle (empty box), loading, results, **no results**, and error (with a Retry button).
- Show name, genres and rating (a missing rating shows "No rating").
- Client-side pagination: five results per page with Previous and Next buttons that disable at the ends.
- Clicking a result shows its details in a panel without a new search; Escape closes the panel.

##### Technical constraints
- `searchShows(term, signal)` in `api.js`; `debounce` created **once**; `paginate(items, page, size)` is a pure function.
- Ignore `AbortError`; never display results for text that is no longer in the box.
- Mock endpoint: `GET /shows?q=space` (one-letter searches are deliberately slow). Real alternative: the TVMaze search endpoint, which needs no key; check its documentation for the current response shape.

##### Expected behavior
```text file="Illustrative behaviour"
Type "s", then quickly "space c" -> only one request completes; shows "1 result"
Clear the box                    -> idle message, results removed
Type "zzz"                       -> "No results"
Stop the server, type "space"    -> error message with a Retry button
```

##### Suggested milestones
1. A fixed search triggered by a button, results rendered.
2. Debounce and the four states.
3. Abort previous requests; prove the stale-response bug is fixed with a slow mock endpoint.
4. `paginate` and the buttons.
5. Details panel and keyboard handling.

##### Edge cases
- A rating of `null`; shows with no genres; very long names.
- Typing, deleting everything and typing again within the debounce window.
- A response that arrives after the user cleared the box.
- Changing the search term while on page 3 (the page must reset to 1).

##### Acceptance criteria
- [ ] `paginate([1, 2, 3, 4, 5, 6, 7], 2, 5)` returns `[6, 7]`; page 0 or a page past the end returns `[]`.
- [ ] A burst of ten keystrokes sends exactly one request (count in the Network tab).
- [ ] Late answers for old terms never replace newer results.
- [ ] `AbortError` never appears on screen.
- [ ] Retry re-runs the last search without retyping.

##### Stretch goals
- Remember the last search in `sessionStorage` and restore it on reload.
- Keyboard navigation of the result list (arrow keys and Enter).
- Highlight the matching part of each name safely (without `innerHTML`).

##### Concepts practiced
Debounce, `AbortController`, stale-response protection, pure pagination, explicit interface states.
::::

:::: project Currency converter | Difficulty: Medium | Extension
##### Objective
Practise validated numeric input, a request with a base parameter, time-limited caching, and floating-point-safe presentation.

##### Problem statement
Build a converter: the user enters an amount, chooses a "from" and "to" currency, and sees the converted value using rates fetched from a service.

##### Required features
- An amount field validated as a positive number (reject empty, text, negative and `0`), and two currency selectors populated from the fetched rates (plus the base currency itself).
- A **Swap** button.
- Fetch rates for the chosen base; cache each base for 10 minutes in memory and show "rates as of <date>" from the response.
- Convert with a pure function `convert(amount, from, to, ratesTable)` that handles conversion through the base currency; show the result rounded to two decimals, and the rate used (for example `1 USD = 0.92 EUR`).
- Loading, error and retry behaviour as in the other projects; the last used pair is remembered in `localStorage`.

##### Technical constraints
- Request only when the base changes (not on every keystroke).
- Validation is a pure function returning an error message or an empty string.
- Never use `toFixed` for intermediate math; round only for display. Keep the amount as typed text until validated.
- Mock endpoint: `GET /rates?base=USD` (bases `USD`, `EUR`, `GBP`). Real alternative: the Frankfurter service (key-free); confirm its current address and response shape in its documentation, because it has changed before.

##### Expected behavior
```text file="Illustrative behaviour"
100 USD -> EUR      = 92.00 EUR   (1 USD = 0.92 EUR, rates as of 2026-03-14)
Swap                = 100 EUR -> USD, new rates fetched for EUR (or derived and shown)
Amount "abc"        = "Enter a positive number" (no request)
Same currency       = result equals the amount
```

##### Suggested milestones
1. `convert` and `validateAmount` with Node tests.
2. Fetch and display rates for one base.
3. Selectors, swap, and the result line.
4. Rates cache with expiry.
5. Remembered pair, error states and retry.

##### Edge cases
- `0.1 + 0.2`-style rounding (`convert(0.1, ...)`); very large amounts; many decimals typed.
- `from === to`; a currency missing from the table; a base the server does not know (`404`).
- Rates that arrive late after the user changed the pair.
- Comma used as a decimal separator in the input.

##### Acceptance criteria
- [ ] `convert(100, "USD", "EUR", { base: "USD", rates: { EUR: 0.92 } })` is `92`.
- [ ] `convert(50, "EUR", "EUR", table)` is `50` for any table.
- [ ] Invalid amounts never trigger a request and show a specific message.
- [ ] Switching selectors within ten minutes re-uses cached rates.
- [ ] The displayed result is rounded to two decimals but the stored number is not rounded early.

##### Stretch goals
- A list of the five most recent conversions.
- Convert one amount into every available currency in a table.
- A rate history chart using a service's time-series endpoint, drawn with plain SVG.

##### Concepts practiced
Input validation, query parameters, caching with expiry, numeric formatting, pure conversion logic.
::::

:::: project Concurrent API data aggregator | Difficulty: Medium to hard | Extension
##### Objective
Combine concurrency limits, retries, timeouts, partial results, progress reporting and cancellation in one tool.

##### Problem statement
Given a list of cities (typed or pasted, one per line), fetch their weather concurrently and display a summary table, tolerating failures, with a Cancel button and a progress indicator.

##### Required features
- Parse the textarea into a clean list (trimmed, non-empty, unique, at most 30 entries).
- Fetch with **at most three requests in flight**, each with a 3-second timeout and up to two retries for retryable failures only.
- Update a progress indicator (`done / total`) as each request finishes.
- A table in the **original input order** with columns city, temperature, condition and a status (ok, not found, failed after retries, cancelled).
- A summary: how many succeeded, average temperature of the successes, hottest and coldest city; computed only from successes.
- A **Cancel** button that aborts all in-flight and queued requests immediately and marks the rest as "cancelled".

##### Technical constraints
- Reuse `withRetry` and the concurrency-limited runner from Sections 7 and 8; one `AbortController` per run, with a timeout signal per request.
- The statistics are pure functions in `logic.js` tested in Node.
- Mock endpoints: `/weather?city=...` (cities `pune`, `oslo`, `lima` exist; others return `404`), `/flaky` and `/slow` for failure and timing experiments.

##### Expected behavior
```text file="Illustrative behaviour"
Input: Pune, Oslo, Atlantis, Lima, Pune
Cleaned list: Pune, Oslo, Atlantis, Lima
Progress: 1/4 ... 4/4
Table: Pune 31 Sunny ok | Oslo 4 Cloudy ok | Atlantis - - not found | Lima 19 Fog ok
Summary: 3 of 4 succeeded, average 18 C, hottest Pune, coldest Oslo
Cancel pressed at 2/4 -> remaining rows show "cancelled"
```

##### Suggested milestones
1. Parsing and cleaning input; a table rendered from fake results.
2. Concurrent fetching with `allSettled` (no limit yet).
3. The concurrency limit and progress counter.
4. Timeouts and retries by error type.
5. Cancellation and the statistics summary.

##### Edge cases
- Empty input; one city; all cities failing; 30 cities; duplicate names in different capitalisation.
- Cancel pressed before the first request finishes, and after all are done.
- A request that times out and is retried successfully.
- Statistics when there are zero successes (no division by zero).

##### Acceptance criteria
- [ ] Never more than three requests are active at once (prove it with a counter shown in the page).
- [ ] The table order always equals the cleaned input order.
- [ ] A `404` city is **not** retried; the `/flaky` endpoint is retried and succeeds.
- [ ] After Cancel, no further requests are started and no row stays "loading".
- [ ] Statistics ignore failures; with zero successes they show a dash, not `NaN`.

##### Stretch goals
- Show a per-request timeline (start and end times) as a simple bar chart in HTML.
- Export the table as CSV, escaping commas and quotes correctly.
- A "retry failed only" button.

##### Concepts practiced
Concurrency limiting, `Promise.allSettled`, retry with backoff, `AbortController` and timeout signals, aggregation, progress reporting.
::::
