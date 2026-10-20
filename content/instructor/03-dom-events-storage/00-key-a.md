---
number: 03
title: Answer Key for DOM, Events, and Browser Storage
subtitle: Solutions, expected outputs, debugging explanations and reference implementations
track: instructor
kind: instructor
label: INSTRUCTOR ANSWER KEY - SHEET 03
time: Do not distribute to students
edition: Instructor edition
goals:
  - Check answers to comprehension and prediction exercises
  - Compare student pages with reference solutions that were run in a real browser
  - Use the debugging explanations when students are stuck
  - Run the reference applications for all five mini projects
---

# 1. How to Use This Key

Every page listed with an *Output* panel was **loaded in headless Chromium by the build validator**, driven by scripted actions (clicks, typing, reloads) exactly as the sheet describes, and the console output matches. Pure-logic modules were also run in Node.js. Reference solutions are one correct approach; grade against the acceptance criteria in the student sheet. Behaviour was verified in Chromium only, not in Firefox or Safari.

::: note Reading the test notation
The `steps` used to drive each page are not shown in the listings; where an output line comes from a page action, the text beside it says what was done. A line such as `true` or `0` usually reports an element property read after an action.
:::

# 2. Set A: Comprehension Answers

1. The DOM is the browser's in-memory tree of objects built by parsing the HTML. The page is drawn from the tree, not from the file; JavaScript changes the tree.
2. A node is any item in the tree (elements, text, comments); an element is an element node. Whitespace between tags becomes text nodes, so `childNodes` can be longer than `children`.
3. `querySelector` returns `null`; `querySelectorAll` returns an empty `NodeList`. A `NodeList` is array-like and static, with `forEach` but not `map`/`filter`/`reduce`; spread or `Array.from` converts it.
4. `textContent` treats the value as plain text (safe); `innerHTML` parses markup (unsafe for untrusted text).
5. The `value` attribute is the initial value from the HTML; the `value` property is the current content.
6. Create the element, fill it (text, classes, attributes), insert it (`append`). Without the third step nothing appears.
7. `target` is the innermost element where the event started; `currentTarget` is the element the listener is attached to.
8. Capture goes from `window` down to the target, then the target phase, then bubbling back up. Listeners run in the bubble phase by default.
9. One listener on an ancestor handles events for its descendants using `event.target`/`closest`. It needs one listener instead of many and works for elements added later.
10. It cancels the browser's default action (following a link, submitting a form, and others).
11. `input` fires on every edit, `change` when a value is committed (on leaving the field for text inputs). Use `input` for live search.
12. Strings only. Store objects with `JSON.stringify` and read them back with `JSON.parse`.
13. Any three of: `undefined`, functions, `Date` objects (become strings), `Map`/`Set`, `NaN` (becomes `null`), circular references.
14. Stored XSS: malicious markup is saved and then run each time it is shown. Safe: `textContent` or `createElement`. Unsafe: `innerHTML` with the comment.
15. Users and attackers can bypass browser checks (DevTools, direct requests), so the server cannot trust them.

# 3. Set B: Predicted Outputs

```html file="b1.html" page
<!DOCTYPE html>
<html lang="en">
  <body>
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
  </body>
</html>
```

```output
2 3
```

The `NodeList` is a snapshot (2); the `HTMLCollection` is live (3).

```html file="b2.html" page
<!DOCTYPE html>
<html lang="en">
  <body>
    <script>
      const d = document.createElement("div");
      d.innerHTML = "<b>hi</b>";
      console.log(d.textContent, d.children.length, d.firstChild.tagName);
    </script>
  </body>
</html>
```

```output
hi 1 B
```

`innerHTML` parsed the markup into a `<b>` element.

```html file="b3.html" page
<!DOCTYPE html>
<html lang="en">
  <body>
    <div id="el" class="a b"></div>
    <script>
      const el = document.getElementById("el");
      el.classList.toggle("a");
      el.classList.toggle("c");
      console.log(el.className);
    </script>
  </body>
</html>
```

```output
b c
```

The first toggle removes `a`, the second adds `c`.

```html file="b4.html" page steps="click #btn"
<!DOCTYPE html>
<html lang="en">
  <body>
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
  </body>
</html>
```

```output
1
2
```

Capture listener first (1), then the target (2). `stopPropagation` prevents the bubble phase, so `3` never prints.

```html file="b5.html" page
<!DOCTYPE html>
<html lang="en">
  <body>
    <div id="u" data-user-id="7" data-role="admin"></div>
    <script>
      const u = document.getElementById("u");
      console.log(Object.keys(u.dataset).join(","), typeof u.dataset.userId);
    </script>
  </body>
</html>
```

```output
userId,role string
```

Dashes become camelCase and dataset values are strings.

```html file="b6.html" page
<!DOCTYPE html>
<html lang="en">
  <body>
    <script>
      const data = { a: undefined, b: [undefined], c: () => 1, d: NaN, e: new Date(0) };
      console.log(JSON.stringify(data));
    </script>
  </body>
</html>
```

```output
{"b":[null],"d":null,"e":"1970-01-01T00:00:00.000Z"}
```

`undefined` and functions vanish from objects, `undefined` in an array and `NaN` become `null`, the date becomes an ISO string.

```html file="b7.html" page
<!DOCTYPE html>
<html lang="en">
  <body>
    <script>
      localStorage.clear();
      localStorage.setItem("n", 1);
      localStorage.setItem("n", Number(localStorage.getItem("n")) + 1);
      console.log(localStorage.getItem("n"), typeof localStorage.getItem("n"));
    </script>
  </body>
</html>
```

```output
2 string
```

The value is converted to a string on every write.

```html file="b8.html" page
<!DOCTYPE html>
<html lang="en">
  <body>
    <form id="f">
      <input name="tag" value="a" />
      <input name="tag" value="b" />
    </form>
    <script>
      const fd = new FormData(document.getElementById("f"));
      console.log(Object.fromEntries(fd).tag, fd.getAll("tag").length);
    </script>
  </body>
</html>
```

```output
b 2
```

`Object.fromEntries` keeps only the last value of a repeated name; `getAll` returns both.

# 4. Set C: Reference Solutions

#### C1. Counter with limits

```html file="c1.html" page steps="click #inc | click #inc | click #inc | click #inc | click #inc | click #inc | click #inc | click #inc | click #inc | click #inc | print #n | eval String(document.getElementById('inc').disabled) | click #reset | print #n | eval String(document.getElementById('dec').disabled) | eval String(document.getElementById('inc').disabled)"
<!DOCTYPE html>
<html lang="en">
  <body>
    <button id="dec">-</button>
    <span id="n"></span>
    <button id="inc">+</button>
    <button id="reset">Reset</button>
    <script>
      const MAX = 10;
      let count = 0;
      const n = document.getElementById("n");
      const inc = document.getElementById("inc");
      const dec = document.getElementById("dec");

      function render() {
        n.textContent = count;
        dec.disabled = count === 0;
        inc.disabled = count === MAX;
      }

      inc.addEventListener("click", () => {
        count = Math.min(MAX, count + 1);
        render();
      });
      dec.addEventListener("click", () => {
        count = Math.max(0, count - 1);
        render();
      });
      document.getElementById("reset").addEventListener("click", () => {
        count = 0;
        render();
      });
      render();
    </script>
  </body>
</html>
```

```output
10
true
0
true
false
```

Output lines: display after ten clicks, whether `+` is disabled, display after reset, whether `-` is disabled, whether `+` is disabled. One `render()` derives everything from `count`.

#### C2. Character counter

```html file="c2.html" page steps="eval (t.value = 'a'.repeat(100), t.dispatchEvent(new Event('input')), 'typed 100') | print #count | eval String(count.classList.contains('over')) | eval (t.value = 'a'.repeat(101), t.dispatchEvent(new Event('input')), 'typed 101') | print #count | eval String(count.classList.contains('over')) | eval (t.value = 'a'.repeat(50), t.dispatchEvent(new Event('input')), 'deleted') | eval String(count.classList.contains('over'))"
<!DOCTYPE html>
<html lang="en">
  <body>
    <textarea id="t"></textarea>
    <p id="count"></p>
    <script>
      const LIMIT = 100;
      const t = document.getElementById("t");
      const count = document.getElementById("count");

      function update() {
        count.textContent = `${t.value.length} / ${LIMIT}`;
        count.classList.toggle("over", t.value.length > LIMIT);
      }

      t.addEventListener("input", update);
      update();
    </script>
  </body>
</html>
```

```output
typed 100
100 / 100
false
typed 101
101 / 100
true
deleted
false
```

`classList.toggle(name, force)` with a boolean adds or removes in one call. Exactly 100 characters is allowed; 101 is over; deleting removes the class again. (Element ids such as `t` and `count` become globals in a page, which is why the test can refer to them; do not rely on that in real code.)

#### C3. Show/hide password

```html file="c3.html" page steps="fill #pw secret | check #show | eval document.getElementById('pw').type | eval document.getElementById('pw').value | click label | eval document.getElementById('pw').type"
<!DOCTYPE html>
<html lang="en">
  <body>
    <input id="pw" type="password" />
    <label><input id="show" type="checkbox" /> Show password</label>
    <script>
      const pw = document.getElementById("pw");
      document.getElementById("show").addEventListener("change", (event) => {
        pw.type = event.target.checked ? "text" : "password";
      });
    </script>
  </body>
</html>
```

```output
text
secret
password
```

The typed text survives because only the `type` property changes. Clicking the label text unchecks the box because the input is nested inside the label.

#### C4. Live filter

```html file="c4.html" page steps="fill #q AN | print #list | eval String(document.getElementById('empty').hidden) | fill #q zzz | eval String(document.getElementById('empty').hidden) | fill #q   hannah   | print #list | fill #q | eval String(document.querySelectorAll('li:not([hidden])').length)"
<!DOCTYPE html>
<html lang="en">
  <body>
    <input id="q" placeholder="Search" />
    <ul id="list">
      <li>Anna</li>
      <li>Brian</li>
      <li>Hannah</li>
      <li>Carlos</li>
      <li>Diana</li>
      <li>Ethan</li>
      <li>Fiona</li>
      <li>George</li>
    </ul>
    <p id="empty" hidden>No matches</p>
    <script>
      const items = document.querySelectorAll("#list li");
      const q = document.getElementById("q");
      const empty = document.getElementById("empty");

      q.addEventListener("input", () => {
        const needle = q.value.trim().toLowerCase();
        let visible = 0;
        for (const li of items) {
          const match = li.textContent.toLowerCase().includes(needle);
          li.hidden = !match;
          if (match) {
            visible++;
          }
        }
        empty.hidden = visible > 0;
      });
    </script>
  </body>
</html>
```

```output
Anna / Brian / Hannah / Diana / Ethan
true
false
Hannah
8
```

Outputs, in order: the visible names for `AN` (case-insensitive, matches inside names), whether the message is hidden, then (after typing `zzz`) whether it is hidden, the single match for `  hannah  ` (spaces trimmed), and the number of visible items after clearing. Elements are hidden, never deleted, so clearing restores them.

#### C5. Tabs

```html file="c5.html" page steps="eval String(document.querySelector('.active').dataset.tab) | click button[data-tab=b] | print #panels | eval String(document.querySelector('.active').dataset.tab) | click #tabs | eval String(document.querySelectorAll('.active').length)"
<!DOCTYPE html>
<html lang="en">
  <body>
    <div id="tabs">
      <button class="active" data-tab="a">A</button>
      <button data-tab="b">B</button>
      <button data-tab="c">C</button>
    </div>
    <div id="panels">
      <section data-panel="a">Panel A</section>
      <section data-panel="b" hidden>Panel B</section>
      <section data-panel="c" hidden>Panel C</section>
    </div>
    <script>
      document.getElementById("tabs").addEventListener("click", (event) => {
        const button = event.target.closest("button[data-tab]");
        if (!button) {
          return;
        }
        for (const b of document.querySelectorAll("#tabs button")) {
          b.classList.toggle("active", b === button);
        }
        for (const panel of document.querySelectorAll("#panels section")) {
          panel.hidden = panel.dataset.panel !== button.dataset.tab;
        }
      });
    </script>
  </body>
</html>
```

```output
a
Panel B
b
1
```

One delegated listener; the last step clicks the container itself (not a button), which `closest` ignores, so exactly one tab stays active.

#### C6. Remembered theme

```html file="c6.html" page steps="eval String(document.body.classList.contains('dark')) | click #toggle | reload | eval String(document.body.classList.contains('dark')) | eval (localStorage.setItem('theme', '{bad'), 'corrupted') | reload | eval String(document.body.classList.contains('dark'))"
<!DOCTYPE html>
<html lang="en">
  <body>
    <button id="toggle">Toggle theme</button>
    <script>
      function loadJSON(key, fallback) {
        try {
          const raw = localStorage.getItem(key);
          return raw === null ? fallback : JSON.parse(raw);
        } catch (error) {
          return fallback;
        }
      }
      function saveJSON(key, value) {
        try {
          localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
          /* storage unavailable: the theme just will not persist */
        }
      }

      const saved = loadJSON("theme", "light");
      document.body.classList.toggle("dark", saved === "dark");

      document.getElementById("toggle").addEventListener("click", () => {
        const isDark = document.body.classList.toggle("dark");
        saveJSON("theme", isDark ? "dark" : "light");
      });
    </script>
  </body>
</html>
```

```output
false
true
corrupted
false
```

Light on first load; dark after toggling and reloading; light again when the stored value is corrupted. The stored theme is applied by the first script that runs, before the user can interact.

# 5. Set D: Debugging Explanations

**D1.** `sayHi()` was *called* while registering the listener, so it ran at load and registered `undefined`. Pass the function itself. (`alert` is replaced by `console.log` so the check can be automated; the nothing-at-load behaviour is visible because the output has exactly one line, from the click.)

```html file="d1-fixed.html" page steps="click #b"
<!DOCTYPE html>
<html lang="en">
  <body>
    <button id="b">Say hi</button>
    <script>
      function sayHi() {
        console.log("hi");
      }
      document.getElementById("b").addEventListener("click", sayHi);
    </script>
  </body>
</html>
```

```output
hi
```



**D2.** `innerHTML` parses the typed text as markup. Use `textContent`. After typing `<b>hi</b>` the heading shows the characters, and no `<b>` element exists (`null`).

```html file="d2-fixed.html" page steps="fill #name <b>hi</b> | print #title | eval String(document.querySelector('#title b'))"
<!DOCTYPE html>
<html lang="en">
  <body>
    <h1 id="title"></h1>
    <input id="name" />
    <script>
      const input = document.getElementById("name");
      input.addEventListener("input", () => {
        document.getElementById("title").textContent = input.value;
      });
    </script>
  </body>
</html>
```

```output
<b>hi</b>
null
```



**D3.** The form's default submit reloads the page, wiping the list. Call `event.preventDefault()`.

```html file="d3-fixed.html" page steps="fill #note Buy | click #save | fill #note Cook | click #save | print #list"
<!DOCTYPE html>
<html lang="en">
  <body>
    <form id="f">
      <input id="note" name="note" />
      <button id="save">Save</button>
    </form>
    <ul id="list"></ul>
    <script>
      document.getElementById("f").addEventListener("submit", (event) => {
        event.preventDefault();
        const li = document.createElement("li");
        li.textContent = document.getElementById("note").value;
        document.getElementById("list").append(li);
      });
    </script>
  </body>
</html>
```

```output
Buy / Cook
```



**D4.** The script ran before the paragraph existed, so `getElementById` returned `null`. Move the script below the element (or use `type="module"`).

```html file="d4-fixed.html" page steps="print #greeting"
<!DOCTYPE html>
<html lang="en">
  <body>
    <p id="greeting"></p>
    <script>
      document.getElementById("greeting").textContent = "Hello!";
    </script>
  </body>
</html>
```

```output
Hello!
```



**D5.** `getItem` returns `null` on the first visit and `JSON.parse` throws on corrupted text. Use a safe loader with a fallback. Output lines: items on first visit, items with corrupted text, then the items after valid data is stored.

```html file="d5-fixed.html" page steps="eval String(document.querySelectorAll('li').length) | eval (localStorage.setItem('items', '{bad'), 'corrupted') | reload | eval String(document.querySelectorAll('li').length) | eval (localStorage.setItem('items', JSON.stringify(['a','b'])), 'saved') | reload | print #list"
<!DOCTYPE html>
<html lang="en">
  <body>
    <ul id="list"></ul>
    <script>
      function loadJSON(key, fallback) {
        try {
          const raw = localStorage.getItem(key);
          return raw === null ? fallback : JSON.parse(raw);
        } catch (error) {
          return fallback;
        }
      }
      const items = loadJSON("items", []);
      for (const item of items) {
        const li = document.createElement("li");
        li.textContent = item;
        document.getElementById("list").append(li);
      }
    </script>
  </body>
</html>
```

```output
0
corrupted
0
saved
a / b
```


