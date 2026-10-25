# 7. Mini Project Reference Implementations

Each project has a **logic module** (pure functions, tested in Node), and a **page** driven in headless Chromium against the mock server with scripted clicks and typing. The pages import the student sheet's `http.js` toolkit. Page code is shown in one `index.html` for brevity; students should split it as in the project template. The scripted steps are not shown; the text beside each output says what was done.

## Project 1: Weather dashboard

```js file="weather-logic.js" bundle=w1
export const toFahrenheit = (celsius) => (celsius * 9) / 5 + 32;

export function addRecent(list, city, max = 5) {
  const clean = city.trim();
  if (clean === "") {
    return list;
  }
  const key = clean.toLowerCase();
  return [clean, ...list.filter((c) => c.toLowerCase() !== key)].slice(0, max);
}

export function formatWeather(data, unit) {
  const value = unit === "F" ? toFahrenheit(data.temperatureC) : data.temperatureC;
  return `${data.city}: ${Math.round(value * 10) / 10} ${unit}, ${data.condition}`;
}
```

```js file="test-weather.mjs" run bundle=w1
import { toFahrenheit, addRecent, formatWeather } from "./weather-logic.js";

console.log(toFahrenheit(0), toFahrenheit(100), toFahrenheit(31));
console.log(addRecent(["Oslo", "Pune"], "pune"));
console.log(addRecent(["a", "b", "c", "d", "e"], "f"));
const same = ["Oslo"];
console.log(addRecent(same, "   ") === same);

const pune = { city: "Pune", temperatureC: 31, condition: "Sunny" };
console.log(formatWeather(pune, "C"), "|", formatWeather(pune, "F"));
```

```output
32 212 87.8
[ 'pune', 'Oslo' ]
[ 'f', 'a', 'b', 'c', 'd' ]
true
Pune: 31 C, Sunny | Pune: 87.8 F, Sunny
```

`formatWeather` rounds **only for display** (to one decimal), as the sheet recommends: the stored number is never rounded early. A repeated city moves to the front and keeps the newest spelling; the list never exceeds five.

```html file="index.html" bundle=w1,net page mock ignore="Failed to load resource" steps="fill #city Pune | click #search | wait 300 | print #result | click #unit | print #result | eval String(window.requestCount) | fill #city Atlantis | click #search | wait 300 | print #result | fill #city   | click #search | print #result | eval String(window.requestCount) | eval recent() | reload | eval recent()"
<!DOCTYPE html>
<html lang="en">
  <body>
    <form id="form">
      <input id="city" />
      <button id="search">Search</button>
      <button id="unit" type="button">Show Fahrenheit</button>
    </form>
    <p id="result"></p>
    <div id="recent"></div>
    <script type="module">
      import { getJSON } from "./http.js";
      import { addRecent, formatWeather } from "./weather-logic.js";

      const BASE = "http://localhost:3001";
      const $ = (id) => document.getElementById(id);
      window.requestCount = 0;

      function load() {
        try {
          const data = JSON.parse(localStorage.getItem("recent-v1"));
          return Array.isArray(data) ? data : [];
        } catch (error) {
          return [];
        }
      }

      let recent = load();
      let unit = "C";
      let current = null;
      let controller = null;

      function renderRecent() {
        $("recent").replaceChildren();
        for (const city of recent) {
          const button = document.createElement("button");
          button.type = "button";
          button.textContent = city;
          button.dataset.city = city;
          $("recent").append(button);
        }
        localStorage.setItem("recent-v1", JSON.stringify(recent));
      }

      function renderWeather() {
        if (current) $("result").textContent = formatWeather(current, unit);
      }

      async function search(city) {
        const clean = city.trim();
        if (clean === "") {
          $("result").textContent = "Please type a city name.";
          return;
        }
        controller?.abort();
        controller = new AbortController();
        window.requestCount++;
        $("result").textContent = "Loading...";
        const url = `${BASE}/weather?city=${encodeURIComponent(clean)}`;
        try {
          current = await getJSON(url, { signal: controller.signal });
          renderWeather();
        } catch (error) {
          if (error.name === "AbortError") return;
          current = null;
          $("result").textContent =
            error.status === 404
              ? "City not found. Check the spelling."
              : "Could not load the weather. Try again.";
        }
        recent = addRecent(recent, clean);
        renderRecent();
      }

      $("form").addEventListener("submit", (event) => {
        event.preventDefault();
        search($("city").value);
      });
      $("unit").addEventListener("click", () => {
        unit = unit === "C" ? "F" : "C";
        $("unit").textContent = unit === "C" ? "Show Fahrenheit" : "Show Celsius";
        renderWeather();
      });
      $("recent").addEventListener("click", (event) => {
        const button = event.target.closest("button[data-city]");
        if (button) search(button.dataset.city);
      });

      window.recent = () => {
        const buttons = [...document.querySelectorAll("#recent button")];
        return buttons.map((b) => b.textContent).join(", ");
      };
      renderRecent();
    </script>
  </body>
</html>
```

```output
Pune: 31 C, Sunny
Pune: 87.8 F, Sunny
1
City not found. Check the spelling.
Please type a city name.
2
Atlantis, Pune
Atlantis, Pune
```

The page output, in order: the weather after searching Pune; the same city after toggling the unit (computed locally); the request count after those two steps (one, since toggling does not fetch); the not-found message for `Atlantis`; the message for a blank entry; the request count again (two: the blank search never reached the network); the recent list (newest first); and the recent list after a reload (restored from storage). A second search always aborts the first, so a slow earlier answer can never overwrite a newer one.

## Project 2: GitHub profile explorer

```js file="github-logic.js" bundle=w2
export function isValidUsername(name) {
  return /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$/.test(name);
}

export function sortByStars(repos) {
  return [...repos].sort((a, b) => b.stargazers_count - a.stargazers_count);
}

export function describeRepo(repo) {
  return `${repo.name} (${repo.language ?? "unknown"}) ${repo.stargazers_count} stars`;
}
```

```js file="test-github.mjs" run bundle=w2
import { isValidUsername, sortByStars, describeRepo } from "./github-logic.js";

console.log(isValidUsername("octocat"), isValidUsername("asha-dev"));
console.log(isValidUsername("bad name!"), isValidUsername(""), isValidUsername("-x"));

const repos = Object.freeze([
  { name: "a", stargazers_count: 5, language: null },
  { name: "b", stargazers_count: 50, language: "JS" },
  { name: "c", stargazers_count: 5, language: "CSS" },
]);
console.log(sortByStars(repos).map((r) => r.name).join(""), repos[0].name);
console.log(describeRepo(repos[0]), "|", describeRepo(repos[1]));
```

```output
true true
false false false
bac a
a (unknown) 5 stars | b (JS) 50 stars
```

The sort is stable, so the equal-star repositories `a` and `c` keep their original order, and the frozen input is untouched. A missing language prints as `unknown`.

```html file="index.html" bundle=w2,net page mock ignore="Failed to load resource" steps="fill #name octocat | click #go | wait 300 | print #profile | print #repos | fill #name nobody | click #go | wait 300 | print #profile | eval String(document.querySelectorAll('#repos li').length) | eval String(window.requestCount) | fill #name octocat | click #go | wait 300 | eval String(window.requestCount) | fill #name bad name! | click #go | print #profile | eval String(window.requestCount)"
<!DOCTYPE html>
<html lang="en">
  <body>
    <form id="form">
      <input id="name" />
      <button id="go">Search</button>
    </form>
    <p id="profile"></p>
    <ul id="repos"></ul>
    <script type="module">
      import { getJSON } from "./http.js";
      import { isValidUsername, sortByStars, describeRepo } from "./github-logic.js";

      const BASE = "http://localhost:3001/github/users";
      const $ = (id) => document.getElementById(id);
      const cache = new Map();
      const TTL = 60000;
      window.requestCount = 0;

      function cachedGet(url) {
        const hit = cache.get(url);
        if (hit && Date.now() - hit.at < TTL) return hit.promise;
        window.requestCount++;
        const promise = getJSON(url);
        cache.set(url, { promise, at: Date.now() });
        promise.catch(() => cache.delete(url));
        return promise;
      }

      async function search(rawName) {
        const name = rawName.trim();
        $("repos").replaceChildren();
        if (!isValidUsername(name)) {
          $("profile").textContent = "Enter a valid GitHub username.";
          return;
        }
        $("profile").textContent = "Loading...";
        const path = `${BASE}/${encodeURIComponent(name)}`;
        const [profile, repos] = await Promise.allSettled([
          cachedGet(path),
          cachedGet(`${path}/repos`),
        ]);

        if (profile.status === "rejected") {
          const notFound = profile.reason.status === 404;
          const message = notFound ? "User not found" : "Could not load the profile.";
          $("profile").textContent = message;
          return;
        }
        const p = profile.value;
        const line = `${p.name}, ${p.followers} followers, ${p.public_repos} repos`;
        $("profile").textContent = line;
        if (repos.status === "rejected") {
          const li = document.createElement("li");
          li.textContent = "Could not load repositories.";
          $("repos").append(li);
          return;
        }
        for (const repo of sortByStars(repos.value)) {
          const li = document.createElement("li");
          li.textContent = describeRepo(repo);
          $("repos").append(li);
        }
      }

      $("form").addEventListener("submit", (event) => {
        event.preventDefault();
        search($("name").value);
      });
    </script>
  </body>
</html>
```

```output
The Octocat, 20 followers, 2 repos
hello-world (JavaScript) 80 stars / spoon-knife (HTML) 12 stars
User not found
0
4
4
Enter a valid GitHub username.
4
```

In order: the profile and the star-sorted repositories for `octocat`; the not-found message for `nobody` with an empty repository list; the request count (four: two per fresh search); the count after repeating `octocat` (still four: both answers came from the 60-second cache); and the message for an invalid username, with the count unchanged (it never reached the network). The two requests are started together and combined with `Promise.allSettled`, so a failing repository list cannot hide a good profile. Failed requests are removed from the cache so they can be retried.

## Project 3: Show search

```js file="shows-logic.js" bundle=w3
export function paginate(items, page, size) {
  if (page < 1) {
    return [];
  }
  return items.slice((page - 1) * size, page * size);
}

export function pageCount(total, size) {
  return Math.max(1, Math.ceil(total / size));
}

export function describeShow(show) {
  const genres = show.genres.length > 0 ? show.genres.join(", ") : "no genres";
  const rating = show.rating?.average ?? "No rating";
  return `${show.name} (${genres}, ${rating})`;
}
```

```js file="test-shows.mjs" run bundle=w3
import { paginate, pageCount, describeShow } from "./shows-logic.js";

const seven = [1, 2, 3, 4, 5, 6, 7];
console.log(paginate(seven, 1, 5), paginate(seven, 2, 5));
console.log(paginate(seven, 0, 5), paginate(seven, 3, 5));
console.log(pageCount(7, 5), pageCount(0, 5));
console.log(describeShow({ name: "A", genres: ["Comedy"], rating: { average: 7.8 } }));
console.log(describeShow({ name: "B", genres: [], rating: { average: null } }));
console.log(describeShow({ name: "C", genres: ["Drama"] }));
```

```output
[ 1, 2, 3, 4, 5 ] [ 6, 7 ]
[] []
2 1
A (Comedy, 7.8)
B (no genres, No rating)
C (Drama, No rating)
```

```html file="index.html" bundle=w3,net page mock steps="fill #q s | fill #q sp | fill #q s | wait 1000 | print #status | print #results | eval String(window.requestCount) | click #next | print #results | eval String(document.getElementById('next').disabled) | click #results li | print #details | press #q Escape | eval String(document.getElementById('details').hidden) | fill #q zzz | wait 1000 | print #status"
<!DOCTYPE html>
<html lang="en">
  <body>
    <input id="q" placeholder="Search shows" />
    <p id="status"></p>
    <ul id="results"></ul>
    <button id="prev">Previous</button>
    <button id="next">Next</button>
    <p id="details" hidden></p>
    <script type="module">
      import { getJSON } from "./http.js";
      import { debounce } from "./debounce.js";
      import { paginate, pageCount, describeShow } from "./shows-logic.js";

      const BASE = "http://localhost:3001";
      const SIZE = 2;
      const $ = (id) => document.getElementById(id);
      window.requestCount = 0;
      let shows = [];
      let page = 1;
      let controller = null;

      function render() {
        const pages = pageCount(shows.length, SIZE);
        page = Math.min(page, pages);
        $("results").replaceChildren();
        for (const show of paginate(shows, page, SIZE)) {
          const li = document.createElement("li");
          li.textContent = describeShow(show);
          li.dataset.id = show.id;
          $("results").append(li);
        }
        $("prev").disabled = page <= 1;
        $("next").disabled = page >= pages;
      }

      async function search(term) {
        controller?.abort();
        $("details").hidden = true;
        const clean = term.trim();
        if (clean === "") {
          shows = [];
          $("status").textContent = "Type to search.";
          render();
          return;
        }
        controller = new AbortController();
        window.requestCount++;
        $("status").textContent = "Searching...";
        try {
          const url = `${BASE}/shows?q=${encodeURIComponent(clean)}`;
          const hits = await getJSON(url, { signal: controller.signal });
          shows = hits.map((hit) => hit.show);
          page = 1;
          const count = shows.length;
          $("status").textContent = count === 0 ? "No results" : `${count} results`;
          render();
        } catch (error) {
          if (error.name === "AbortError") return;
          $("status").textContent = "Could not search. Try again.";
        }
      }

      const searchLater = debounce(search, 250);
      $("q").addEventListener("input", (event) => searchLater(event.target.value));
      $("prev").addEventListener("click", () => {
        page--;
        render();
      });
      $("next").addEventListener("click", () => {
        page++;
        render();
      });
      $("results").addEventListener("click", (event) => {
        const li = event.target.closest("li[data-id]");
        const show = shows.find((s) => String(s.id) === li?.dataset.id);
        if (show) {
          const rating = show.rating?.average ?? "No rating";
          const genres = show.genres.join(", ");
          $("details").textContent = `${show.name}: ${genres}. ${rating}`;
          $("details").hidden = false;
        }
      });
      document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") $("details").hidden = true;
      });
      render();
    </script>
  </body>
</html>
```

```output
3 results
Space Cats (Comedy, 7.8) / Space Station (Drama, Sci-Fi, 8.4)
1
Spaced Out (Comedy, No rating)
true
Spaced Out: Comedy. No rating
true
No results
```

In order: after three quick edits (`s`, `sp`, `s`) the status shows three results; the first page of two; the request count (one: the debounce collapsed the burst); the second page; whether **Next** is now disabled (it is); the details of the clicked result; whether Escape hid the details panel; and the empty-state message for `zzz`. The page size is two here so that the mock's three results demonstrate pagination; the project asks for five.
