# 10. Organising Browser Code: Data Logic Versus Interface

## Learning objectives for this section

- Explain why mixing data rules and DOM code in one place causes trouble.
- Split a small application into a data module, a storage module, an interface module and a wiring file.
- Describe the data flow: event, then new data, then save, then render.
- Test data logic without a browser.

## Conceptual explanation

So far each example has been one file where event handlers read the DOM, change data, update the DOM and save, all tangled together. That is fine for ten lines and miserable for two hundred. The fix is **separation of responsibilities**: give each kind of work its own place.

[[widths 1.1 2.6 2.4]]
| Layer | Responsibility | Knows about the DOM? |
|---|---|---|
| **Data logic** (`store.js`) | Rules for changing data: add, toggle, remove, filter. **Pure functions** that take data and return new data. | **No** |
| **Storage** (`storage.js`) | Loading and saving (safe JSON helpers). | No |
| **Interface** (`ui.js`) | Turning data into DOM elements (`render`). | Yes |
| **Wiring** (`main.js`) | Connecting events to data changes and calling `render`. | Yes |

```diagram
flow
User action (click, submit) -> Event handler in main.js -> *store.js returns NEW data -> storage.js saves -> ui.js renders
```

The most valuable consequence: the data layer has **no dependence on the browser**, so you can test it in Node.js in seconds, reuse it unchanged, and (as you will see in Sheet 06) lift the same functions straight into a React application, where only the interface layer changes.

## A complete multi-file application

```tree
js-todo/
├── index.html
├── main.js
├── store.js
├── storage.js
└── ui.js
```

```js file="store.js" bundle=todo
export function addTodo(todos, text) {
  const trimmed = text.trim();
  if (trimmed === "") {
    return todos;
  }
  const id = Math.max(0, ...todos.map((t) => t.id)) + 1;
  return [...todos, { id, text: trimmed, done: false }];
}

export function toggleTodo(todos, id) {
  return todos.map((t) => (t.id === id ? { ...t, done: !t.done } : t));
}

export function removeTodo(todos, id) {
  return todos.filter((t) => t.id !== id);
}

export function remaining(todos) {
  return todos.filter((t) => !t.done).length;
}
```

```js file="storage.js" bundle=todo
export function loadJSON(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw === null ? fallback : JSON.parse(raw);
  } catch (error) {
    return fallback;
  }
}

export function saveJSON(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (error) {
    return false;
  }
}
```

```js file="ui.js" bundle=todo
import { remaining } from "./store.js";

export function render(listEl, countEl, todos) {
  listEl.replaceChildren();
  for (const todo of todos) {
    const li = document.createElement("li");
    li.dataset.id = todo.id;
    li.classList.toggle("done", todo.done);

    const label = document.createElement("span");
    label.textContent = todo.text;

    const del = document.createElement("button");
    del.textContent = "Delete";
    del.dataset.action = "delete";

    li.append(label, " ", del);
    listEl.append(li);
  }
  countEl.textContent = `${remaining(todos)} left`;
}
```

```js file="main.js" bundle=todo
import { addTodo, toggleTodo, removeTodo } from "./store.js";
import { loadJSON, saveJSON } from "./storage.js";
import { render } from "./ui.js";

const KEY = "todos-v1";
const form = document.getElementById("form");
const input = document.getElementById("text");
const list = document.getElementById("list");
const count = document.getElementById("count");

let todos = loadJSON(KEY, []);

function update(nextTodos) {
  todos = nextTodos;
  saveJSON(KEY, todos);
  render(list, count, todos);
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  update(addTodo(todos, input.value));
  input.value = "";
});

list.addEventListener("click", (event) => {
  const li = event.target.closest("li");
  if (!li) {
    return;
  }
  const id = Number(li.dataset.id);
  if (event.target.dataset.action === "delete") {
    update(removeTodo(todos, id));
  } else {
    update(toggleTodo(todos, id));
  }
});

render(list, count, todos);
```

```html file="index.html" bundle=todo page steps="fill #text Read | click #add | fill #text Write | click #add | click li:nth-child(1) span | click li:nth-child(2) button | reload | print #list | print #count | eval document.querySelector('li').className"
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Todos</title>
  </head>
  <body>
    <form id="form">
      <input id="text" />
      <button id="add">Add</button>
    </form>
    <ul id="list"></ul>
    <p id="count"></p>
    <script type="module" src="main.js"></script>
  </body>
</html>
```

```output
Read Delete
0 left
done
```

**Walking through a click on "Read".** (1) The click lands on the `<span>`. (2) It bubbles to the `<ul>`, whose single delegated listener runs (Section 7). (3) `closest("li")` finds the item and `Number(li.dataset.id)` recovers its id (dataset values are strings). (4) Because the clicked element is not the delete button, the handler calls `toggleTodo(todos, id)`, which **returns a new array** and changes nothing in place. (5) `update` stores the new array in `todos`, saves it, and calls `render`, which rebuilds the list from the data. The scripted run adds two todos, toggles the first, deletes the second, and reloads: the saved data restores a single, completed item, so the list shows `Read Delete`, the counter says `0 left`, and the item carries the `done` class.

Notice what each file does *not* know. `store.js` never touches `document`. `ui.js` never changes data. `main.js` contains no business rules, only wiring. That is the whole discipline.

## Testing the data layer without a browser

Because `store.js` imports nothing from the browser, Node.js can run it directly:

```js file="test-store.mjs" run bundle=todo
import { addTodo, toggleTodo, removeTodo, remaining } from "./store.js";

const empty = Object.freeze([]);
const one = addTodo(empty, "  Read  ");
const two = addTodo(one, "Write");

console.log(two.map((t) => `${t.id}:${t.text}`).join(" "));
console.log(addTodo(two, "   ") === two);

const toggled = toggleTodo(two, 1);
console.log(toggled[0].done, two[0].done, toggled[1] === two[1]);
console.log(remaining(toggled), removeTodo(toggled, 1).length);
```

```output
1:Read 2:Write
true
true false true
1 1
```

Each line checks one rule: ids increase and text is trimmed; blank text returns the **same** array unchanged; toggling produces a new object for the changed item while the original stays `false` and untouched items are shared; the remaining count and removal work. These few lines would have been awkward to test through a browser. Writing rules as pure functions makes tests trivial, which is exactly what Sheet 11 builds on.

## Common mistakes in this section

#### Mistake 1: Using the DOM as the source of truth

**Why it is wrong.** If the page is the only place the data lives, you cannot save it, filter it, or test it, and the page and the data drift apart.

```html file="index.html" bad page steps="click #del | eval document.querySelectorAll('li').length"
<!DOCTYPE html>
<html lang="en">
  <body>
    <ul id="list"><li>A</li><li>B</li></ul>
    <button id="del">Delete first</button>
    <script>
      const todos = ["A", "B"];
      document.getElementById("del").addEventListener("click", () => {
        document.querySelector("#list li").remove();
      });
      window.addEventListener("beforeunload", () => {});
      document.getElementById("del").addEventListener("click", () => {
        console.log("data still has", todos.length, "items");
      });
    </script>
  </body>
</html>
```

```output
data still has 2 items
1
```

**Symptom.** The screen shows one item while the `todos` array still has two; anything saved or counted from the array is wrong. **Fix:** change the **data**, then call `render`. **Diagnosis:** compare what the screen shows with `console.log(todos)`; if they differ, some code changed the DOM without changing the data.

#### Mistake 2: Changing data but forgetting to save

**Why it is wrong.** Memory and storage are separate. A change that is never written disappears on reload.

```html file="index.html" bad page steps="click #inc | reload | print #n"
<!DOCTYPE html>
<html lang="en">
  <body>
    <button id="inc">+1</button>
    <p id="n"></p>
    <script>
      let n = Number(localStorage.getItem("n") ?? 0);
      document.getElementById("n").textContent = n;
      document.getElementById("inc").addEventListener("click", () => {
        n++;
        document.getElementById("n").textContent = n;
      });
    </script>
  </body>
</html>
```

```output
0
```

**Symptom.** The counter works until the page reloads, then resets. **Fix:** route every change through one `update` function that saves and renders, as in `main.js`; then it is impossible to forget. **Diagnosis:** look in DevTools, Application, Local Storage, after a change. If the value is not updated, the save is missing.

#### Mistake 3: Attaching listeners inside `render`

**Why it is wrong.** `render` runs after every change. Each call adds *another* listener to an element that persists.

```html file="index.html" bad page steps="click #refresh | click #refresh | click #box"
<!DOCTYPE html>
<html lang="en">
  <body>
    <button id="refresh">Re-render</button>
    <div id="box">Box</div>
    <script>
      const box = document.getElementById("box");
      function render() {
        box.addEventListener("click", () => console.log("box clicked"));
      }
      render();
      document.getElementById("refresh").addEventListener("click", render);
    </script>
  </body>
</html>
```

```output
box clicked
box clicked
box clicked
```

**Symptom.** After two re-renders, one click runs the handler three times. **Fix:** register persistent listeners once, outside `render` (as `main.js` does); `render` should only create and update elements. **Diagnosis:** if a handler runs more times as the app is used, a listener is being added repeatedly.

#### Mistake 4: One giant file or function that does everything

**Why it is wrong.** It cannot be tested without a browser, and you cannot reuse any part. **Symptom:** you hesitate to change anything because you cannot predict what will break. **Fix:** extract each *rule* into a pure function first (the easiest part to separate), then the storage helpers, then rendering.

**Diagnosis.** A good test of a function: can you call it from Node with plain data and check the result? If it needs `document`, it is interface code; if it does not, it belongs in the data layer.

# 11. Security: Handling User Input Safely

## Learning objectives for this section

- Explain cross-site scripting (XSS) and how `innerHTML` can cause it.
- Choose safe ways to put untrusted text and URLs into a page.
- Know what must never be stored in browser storage, and why validation must also happen on a server.

## Conceptual explanation

Everything a user types, everything loaded from a URL, and everything fetched from a server is **untrusted input**. If your page treats it as *code* instead of *text*, an attacker can make your page run their JavaScript in other people's browsers. That script runs with your page's full privileges: it can read your storage, send requests as the user, and rewrite the page. This class of attack is **cross-site scripting (XSS)**.

Forms of XSS you should recognise:

- **Stored XSS**: malicious text is saved (in a database, or in `localStorage`) and executed every time it is displayed.
- **Reflected XSS**: text from the URL or a form is echoed straight into the page.
- **DOM-based XSS**: your own client-side code takes untrusted text and inserts it with `innerHTML`, `insertAdjacentHTML`, or similar.

## Safe and unsafe ways to put data into a page

[[widths 2.6 1.1 2.5]]
| Way of inserting data | Safe for untrusted text? | Notes |
|---|---|---|
| `element.textContent = text` | **Yes** | Always treated as text |
| `document.createElement` plus `textContent`, then `append` | **Yes** | The recommended way to build structure |
| `input.value = text`, `element.setAttribute("title", text)` | Yes for these attributes | Not for URL or event attributes (below) |
| `element.innerHTML = text` | **No** | Parses markup; scripts in event attributes run |
| `insertAdjacentHTML`, `document.write` | **No** | Same problem |
| `a.href = text` | **Only if the scheme is checked** | `javascript:` URLs run code |
| `eval(text)`, `new Function(text)` | **Never** | Executes arbitrary code |

If you *must* display rich HTML that came from outside (for example Markdown rendered to HTML, Project 5), it has to pass through a proper **sanitizer** library such as DOMPurify before it reaches `innerHTML`. Writing your own filter with a few string replacements is a well-known way to be hacked.

## Escaping text when you must build an HTML string

Sometimes you do need a string of markup (an email, a server template). Then **escape** the five special characters so the text can never become tags.

```js file="escape.js" run
function escapeHTML(text) {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

const hostile = `<img src=x onerror="steal()"> & "quotes"`;
console.log(escapeHTML(hostile));
console.log(escapeHTML("Tom & Jerry"));
```

```output
&lt;img src=x onerror=&quot;steal()&quot;&gt; &amp; &quot;quotes&quot;
Tom &amp; Jerry
```

The ampersand must be replaced **first**; otherwise the `&` in the entities produced by the later replacements would be escaped a second time. After escaping, the browser shows the hostile text literally rather than running it. In browser code, `textContent` does this for you automatically and is preferable.

## URLs are code too

A link whose address starts with `javascript:` runs script when clicked. If users can supply a link (a profile website, a bookmark in Project 4), check the **scheme** with the built-in `URL` class instead of guessing with string tests.

```js file="safe-url.js" run
function safeUrl(text) {
  try {
    const url = new URL(text);
    return url.protocol === "http:" || url.protocol === "https:" ? url.href : null;
  } catch (error) {
    return null;
  }
}

console.log(safeUrl("https://developer.mozilla.org/en-US/"));
console.log(safeUrl("javascript:alert(1)"));
console.log(safeUrl("JAVASCRIPT:alert(1)"));
console.log(safeUrl("data:text/html,<script>1</script>"));
console.log(safeUrl("not a url"));
console.log(safeUrl("//evil.example/x"));
```

```output
https://developer.mozilla.org/en-US/
null
null
null
null
null
```

`new URL(text)` parses the string and throws a `TypeError` if it is not an absolute URL, which the `catch` turns into `null`. The `protocol` property is normalised to lower case (`JAVASCRIPT:` becomes `javascript:`), so the allow-list check cannot be bypassed by changing capitalisation. An **allow-list** (accept only `http:` and `https:`) is safer than a block-list (reject `javascript:`), because there are other dangerous schemes such as `data:`.

Links that open a new tab should also carry `rel="noopener noreferrer"`: it stops the opened page from getting a handle on yours (`window.opener`) and from learning which page linked to it. Current browsers already apply `noopener` by default for `target="_blank"`, but writing it explicitly documents the intent and covers older browsers.

## Other rules you should follow now

- **Never store secrets in `localStorage` or `sessionStorage`.** Any script that runs on your page, including injected ones, can read all of it. This includes passwords, long-lived access tokens and API keys.
- **Never put private API keys in front-end code.** Anyone can open DevTools and read your JavaScript. Sheet 04 covers this in detail.
- **Validate on the server as well.** Browser-side checks are for user experience (Section 8, Mistake 4).
- **Do not `eval`.** If you think you need it, you almost certainly need a `switch`, a lookup table or `JSON.parse`.
- **Treat every third-party script as having full access to your page.** Add only the ones you trust.
- **Keep dependencies updated** when you start using packages (Sheet 05 onward), because attackers target known flaws in old versions.

## Common mistakes in this section

#### Mistake 1: Rendering stored data with `innerHTML`

**Why it is wrong.** Stored XSS: data saved once (here in `localStorage`) runs again on **every** load, for every viewer of that data.

```html file="index.html" bad page steps="reload | reload"
<!DOCTYPE html>
<html lang="en">
  <body>
    <div id="comments"></div>
    <script>
      const evil =
        "<img src='data:image/png;base64,AAAA' " +
        `onerror="console.log('attacker code ran')">`;
      localStorage.setItem("comments", JSON.stringify([evil]));

      const comments = JSON.parse(localStorage.getItem("comments"));
      const html = comments.map((c) => `<p>${c}</p>`).join("");
      document.getElementById("comments").innerHTML = html;
    </script>
  </body>
</html>
```

```output
attacker code ran
attacker code ran
attacker code ran
```

**Symptom.** The attacker's code runs on each page load (three loads here, three lines). In reality it would send the user's data elsewhere, silently. **Fix:** build elements with `createElement` and `textContent`.

```html file="index.html" good page steps="reload | reload"
<!DOCTYPE html>
<html lang="en">
  <body>
    <div id="comments"></div>
    <script>
      const evil =
        "<img src='data:image/png;base64,AAAA' " +
        `onerror="console.log('attacker code ran')">`;
      localStorage.setItem("comments", JSON.stringify([evil]));

      const box = document.getElementById("comments");
      for (const text of JSON.parse(localStorage.getItem("comments"))) {
        const p = document.createElement("p");
        p.textContent = text;
        box.append(p);
      }
      console.log("images created:", document.querySelectorAll("img").length);
    </script>
  </body>
</html>
```

```output
images created: 0
images created: 0
images created: 0
```

**Diagnosis.** Search for `innerHTML` and template strings that contain `${...}` inside HTML. Ask of each `${...}`: could that value ever come from outside the code?

#### Mistake 2: Putting an unchecked URL into `href`

**Why it is wrong.** A `javascript:` link runs code when clicked.

```html file="index.html" bad page steps="click #link"
<!DOCTYPE html>
<html lang="en">
  <body>
    <a id="link">My website</a>
    <script>
      const userWebsite = "javascript:console.log('script from a link ran')";
      document.getElementById("link").href = userWebsite;
    </script>
  </body>
</html>
```

```output
script from a link ran
```

**Symptom.** Clicking the profile link runs the attacker's script. **Fix:** pass the text through the `safeUrl` allow-list above, and only set `href` when it returns a URL. **Diagnosis:** any `href` or `src` assigned from non-constant data needs a scheme check.

#### Mistake 3: Hand-written "sanitising" with a couple of replacements

**Why it is wrong.** Browsers accept dozens of ways to start a script, and an incomplete filter misses some.

```js file="weak-filter.js" run
function weakFilter(html) {
  return html.replaceAll("<script>", "").replaceAll("</script>", "");
}

console.log(weakFilter("<script>steal()</script>"));
console.log(weakFilter("<scr<script>ipt>steal()</scr</script>ipt>"));
console.log(weakFilter(`<img src=x onerror="steal()">`));
```

```output
steal()
<script>steal()</script>
<img src=x onerror="steal()">
```

**Symptom.** The filter removes the obvious attack but the second input *rebuilds* a script tag after the removal, and the third attack never used a script tag at all. **Fix:** do not filter by hand. Use `textContent`, or a maintained sanitizer library for rich HTML. **Diagnosis:** if you find yourself writing a list of "bad strings to remove", stop: allow-lists (escape everything, then permit known-safe markup through a library) are the only approach that holds.

#### Mistake 4: Keeping secrets in browser storage or front-end code

**Why it is wrong.** The user (and any injected script) can read everything the browser holds for your page.

**Symptom.** An API key or token shows up in someone else's repository, a stranger uses your paid service, or a stolen login token is reused. There is often no visible error at all until the bill or the incident report arrives.

**Fix and diagnosis.** Keep secrets on a server you control, and let the front end call *that* server. If something must be in the browser, assume the world can read it. Open the Application tab for your own site and read what is stored; if you would not print it on a poster, it should not be there.
