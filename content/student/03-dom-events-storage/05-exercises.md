# 12. Exercises

## Exercises overview and rules

Five sets, from recall to independent problem solving. Complete sets A to D in full; for set E complete at least one challenge. Solutions are in the instructor key. Use the acceptance criteria to check your own work: write down what you expect, then verify in the browser and in DevTools.

::: tip How to test a page without a solution
For each exercise, list three actions ("type X, click Y, reload") and the expected result of each. Perform them one by one with the Console and Elements panels open. When something differs, apply the debugging routine from Sheet 01.
:::

Work in `js-dom/exercises/`, one folder per exercise containing `index.html` and, where asked, separate script or module files. Remember that module pages need to be served over HTTP.

## Set A: Comprehension questions

1. What is the DOM, and how does it relate to the HTML file you wrote?
2. What is the difference between a node and an element? Why can `childNodes.length` differ from `children.length`?
3. What do `querySelector` and `querySelectorAll` return when nothing matches? What is the difference between a `NodeList` and an array?
4. Explain the difference between `textContent` and `innerHTML`. Which is safe for untrusted text, and why?
5. Why does `input.value` change as the user types while `input.getAttribute("value")` does not?
6. What are the three steps to add a new element to a page? What happens if you skip the last one?
7. What is the difference between `event.target` and `event.currentTarget`?
8. Describe the capture, target and bubble phases. In which phase do listeners run by default?
9. What is event delegation, and what two problems does it solve?
10. What does `preventDefault()` cancel? Name two events where you will use it.
11. Compare the `input` and `change` events. Which would you use for a live search box, and why?
12. What types can `localStorage` store? How do you store an object?
13. Name three kinds of values JSON cannot represent faithfully.
14. Explain stored XSS in your own words. Give one safe way and one unsafe way to display a user's comment.
15. Why must validation also happen on a server even if the page validates input?

## Set B: Syntax and output prediction

Each snippet is a full page. Write the **exact console output** before running. If a snippet involves clicking, the instructions say so.

**B1.**

```html file="b1.html"
<p class="n">1</p>
<p class="n">2</p>
<script>
  const a = document.querySelectorAll(".n");
  const b = document.getElementsByClassName("n");
  const extra = document.createElement("p");
  extra.className = "n";
  document.body.append(extra);
  console.log(a.length, b.length);
</script>
```

**B2.**

```html file="b2.html"
<script>
  const d = document.createElement("div");
  d.innerHTML = "<b>hi</b>";
  console.log(d.textContent, d.children.length, d.firstChild.tagName);
</script>
```

**B3.**

```html file="b3.html"
<div id="el" class="a b"></div>
<script>
  const el = document.getElementById("el");
  el.classList.toggle("a");
  el.classList.toggle("c");
  console.log(el.className);
</script>
```

**B4.** Click the button once.

```html file="b4.html"
<div id="outer"><button id="btn">Go</button></div>
<script>
  const outer = document.getElementById("outer");
  const btn = document.getElementById("btn");
  outer.addEventListener("click", () => console.log("1"), true);
  btn.addEventListener("click", (e) => {
    console.log("2");
    e.stopPropagation();
  });
  outer.addEventListener("click", () => console.log("3"));
</script>
```

**B5.**

```html file="b5.html"
<div id="u" data-user-id="7" data-role="admin"></div>
<script>
  const u = document.getElementById("u");
  console.log(Object.keys(u.dataset).join(","), typeof u.dataset.userId);
</script>
```

**B6.**

```html file="b6.html"
<script>
  const data = { a: undefined, b: [undefined], c: () => 1, d: NaN, e: new Date(0) };
  console.log(JSON.stringify(data));
</script>
```

**B7.**

```html file="b7.html"
<script>
  localStorage.clear();
  localStorage.setItem("n", 1);
  localStorage.setItem("n", Number(localStorage.getItem("n")) + 1);
  console.log(localStorage.getItem("n"), typeof localStorage.getItem("n"));
</script>
```

**B8.**

```html file="b8.html"
<form id="f">
  <input name="tag" value="a" />
  <input name="tag" value="b" />
</form>
<script>
  const fd = new FormData(document.getElementById("f"));
  console.log(Object.fromEntries(fd).tag, fd.getAll("tag").length);
</script>
```

## Set C: Small implementation exercises

Each is a single page. Keep data in JavaScript variables and write a `render` function where it helps.

#### C1. Counter with limits

**Problem.** A page with `+`, `-` and `Reset` buttons and a number display. The count must never go below `0` or above `10`; the `+` button is **disabled** at 10 and the `-` button at 0.

**Acceptance criteria.**

- Initial display `0`, with `-` disabled.
- After ten clicks on `+` the display is `10` and `+` is disabled; an eleventh click does nothing.
- `Reset` returns to `0` and re-enables the right buttons.
- Disabled state is set with the `disabled` **property**.

**Hint.** One `render()` function that sets the text and both `disabled` properties from the single `count` variable.

#### C2. Character counter

**Problem.** A `<textarea>` with a live counter `n / 100`. When the text exceeds 100 characters the counter gets the CSS class `over`.

**Acceptance criteria.**

- The counter updates on every keystroke (not only when leaving the field).
- At exactly 100 characters the class is **not** present; at 101 it is.
- Deleting characters removes the class again.

**Hint.** The `input` event and `classList.toggle(name, force)` with a boolean second argument.

#### C3. Show/hide password

**Problem.** A password field and a checkbox "Show password". Checking the box makes the characters visible; unchecking hides them again.

**Acceptance criteria.**

- The typed text is preserved when toggling.
- The field's `type` property switches between `password` and `text`.
- The label is correctly associated with the checkbox (clicking the label text toggles it).

**Hint.** The `change` event on the checkbox, and the `type` property of the input.

#### C4. Live filter

**Problem.** A list of at least eight names and a search box. Typing filters the list: only names containing the typed text (ignoring case) stay visible. An empty box shows everything. If nothing matches, show the message "No matches".

**Acceptance criteria.**

- Filtering is case-insensitive and matches anywhere in the name.
- Items are hidden with the `hidden` property, not deleted (clearing the box restores all of them).
- The "No matches" message appears only when zero items are visible.
- Leading and trailing spaces in the search text are ignored.

**Hint.** `querySelectorAll("li")`, `toLowerCase()`, `includes`, `trim`.

#### C5. Tabs

**Problem.** Three tab buttons and three panels. Clicking a tab shows its panel and hides the others, and marks the active tab with the class `active`. Use **one** delegated listener on the container of the tab buttons.

**Acceptance criteria.**

- Exactly one panel is visible at a time; the first tab is active on load.
- The listener is attached once, to the container, and ignores clicks that are not on a tab button.
- Tabs and panels are linked with a `data-tab` attribute (no hard-coded ids in the script).

**Hint.** `closest("button[data-tab]")` and `dataset`.

#### C6. Remembered theme

**Problem.** A button "Toggle theme" switches the page between light and dark by toggling the class `dark` on `<body>`. The choice is saved and applied again on the next visit, before the user sees the page flash the wrong theme.

**Acceptance criteria.**

- After toggling to dark and reloading, the page is dark.
- If storage contains invalid text, the page falls back to light without errors.
- Reading and writing use the safe `loadJSON` and `saveJSON` helper pattern.
- No flash of the wrong theme: the class is applied by the very first script that runs.

**Hint.** Put the script at the end of `<body>` (or in `<head>` using `document.documentElement` instead of `body`) and apply the stored class immediately.

## Set D: Debugging exercises

Each page is broken. State the **evidence**, your **hypothesis**, the **fix** and *why* it was wrong.

**D1. It runs at load time.**

```html file="d1.html"
<button id="b">Say hi</button>
<script>
  function sayHi() {
    alert("hi");
  }
  document.getElementById("b").addEventListener("click", sayHi());
</script>
```

*Expected:* nothing happens at load; `hi` appears only when clicking.

**D2. The title is full of tags.**

```html file="d2.html"
<h1 id="title"></h1>
<input id="name" />
<script>
  const input = document.getElementById("name");
  input.addEventListener("input", () => {
    document.getElementById("title").innerHTML = input.value;
  });
</script>
```

*Expected:* if the user types `<b>hi</b>`, the heading must show the characters literally.

**D3. The page flashes and resets.**

```html file="d3.html"
<form id="f">
  <input id="note" name="note" />
  <button>Save</button>
</form>
<ul id="list"></ul>
<script>
  document.getElementById("f").addEventListener("submit", () => {
    const li = document.createElement("li");
    li.textContent = document.getElementById("note").value;
    document.getElementById("list").append(li);
  });
</script>
```

*Expected:* each saved note stays in the list.

**D4. Cannot read properties of null.**

```html file="d4.html"
<script>
  document.getElementById("greeting").textContent = "Hello!";
</script>
<p id="greeting"></p>
```

*Expected:* the paragraph shows `Hello!`.

**D5. Works for me, crashes for new users.**

```html file="d5.html"
<ul id="list"></ul>
<script>
  const items = JSON.parse(localStorage.getItem("items"));
  for (const item of items) {
    const li = document.createElement("li");
    li.textContent = item;
    document.getElementById("list").append(li);
  }
</script>
```

*Expected:* an empty list on the first visit, and also if the stored text is corrupted.

## Set E: Challenges

#### E1. Sortable table

**Problem.** Render a table from an array of at least six objects (`name`, `age`, `city`). Clicking a column header sorts by that column ascending; clicking it again reverses the order. Numbers must sort numerically (`9` before `10`), text alphabetically without case sensitivity, and the header shows an arrow for the current sort.

**Acceptance criteria.**

- One delegated listener on the `<thead>`; data and DOM stay separate (a `sortRows(rows, key, direction)` pure function exists).
- Clicking a different column starts ascending; clicking the same one toggles.
- The original array is never mutated.
- Sorting is stable: rows with equal keys keep their previous relative order.

#### E2. Undo and redo

**Problem.** A `<textarea>` with **Undo** and **Redo** buttons (also bound to `Ctrl+Z` and `Ctrl+Y`). Each change is recorded after the user pauses typing for 400 ms (not on every keystroke).

**Acceptance criteria.**

- A pure module `history.js` with `createHistory(initial)`, `push(history, value)`, `undo(history)` and `redo(history)` that return **new** history objects (no mutation).
- Undo and redo buttons are disabled when there is nothing to undo or redo.
- A new change after undoing discards the redo branch.
- The history is limited to the latest 50 states.
