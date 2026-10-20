---
number: 03
title: DOM, Events, and Browser Storage
subtitle: Making web pages react to people: selecting and changing elements, handling events and forms, and remembering data
track: js
time: Core path about 30-34 hours
edition: Student edition
goals:
  - Explain the DOM tree and select, create, change and remove elements with JavaScript
  - Handle clicks, typing, forms and keyboard input, including bubbling and event delegation
  - Validate forms and keep user input from becoming a security hole
  - Save and load data with localStorage and JSON, safely
  - Separate data logic from interface code, the habit that prepares you for React
---

# 1. Study Guide and Learning Objectives

Until now your programs lived in a terminal. This sheet moves JavaScript into the browser, where it finally touches what you already know well: HTML and CSS. The **DOM** (Document Object Model) is the bridge: the browser turns your HTML into objects that JavaScript can read and change. Everything React does later, it does to the DOM, so understanding the plain mechanism makes React much easier to learn.

## Learning objectives

By the end of this sheet you should be able to do each of the following without looking anything up.

- Draw the DOM tree for a small HTML page and explain the difference between a node and an element.
- Select elements with `getElementById`, `querySelector` and `querySelectorAll`, and explain what each returns when nothing matches.
- Change text, attributes, classes and styles, and explain why `textContent` is safer than `innerHTML`.
- Create, insert, move and remove elements, and navigate between related elements.
- Attach event listeners, use the event object, and explain bubbling, capturing, delegation and `preventDefault()`.
- Read, validate and reset form data, and show helpful error messages.
- Store data with `localStorage` and `sessionStorage` using `JSON.stringify()` and `JSON.parse()`, handling missing or corrupted data.
- Organise a page into data logic and interface code, and describe the main security risks of user input.

## Recommended workload

[[widths 1.2 3.4]]
| Item | Recommendation |
|---|---|
| **Essential topics** | Sections 2 to 10 except boxes marked *Optional deep dive*. |
| **Optional deep dives** | Capturing phase details, the constraint validation API in depth, `sessionStorage` use cases, `storage` events. |
| **Required exercises** | Sets A to D in full; at least one challenge from set E. |
| **Core projects (do these)** | Projects 1, 2 and 3. |
| **Extension projects** | Projects 4 and 5. |
| **Estimated study time** | Reading and experimenting: 13 to 15 hours. Exercises: 6 to 7 hours. Core projects: 10 to 12 hours. Extension projects add about 6 hours. |

::: warning Prerequisites
You need Sheets 01 and 02: functions and callbacks, arrays and objects, array methods, destructuring, and ES modules. Event handlers are callbacks, and almost every page you build will use `map`, `filter` and spread to manage its data.
:::

## Setup for browser work

- [ ] Create a folder `js-dom` and open it in your editor.
- [ ] For each example, save the HTML as `index.html` and open it in your browser (double-clicking the file works for plain scripts).
- [ ] Open DevTools with F12. You will use three panels constantly: **Elements** (the live DOM), **Console** (output and errors) and **Application** (storage).
- [ ] For module scripts (`type="module"`), serve the folder over HTTP, for example with `npx serve`, because browsers block modules on `file://` pages (see Sheet 02, Section 8).

::: note Every example here was run in a real browser
Each complete page in this sheet was loaded in a headless Chromium browser, scripted exactly as the text describes (clicks, typing, reloads), and its console output and page text were compared with the output panels printed here. Where an example says "Output", that is exactly what the console or page showed.
:::

# 2. The Document Object Model

## Learning objectives for this section

- Explain what the DOM is and how it relates to your HTML file.
- Describe the tree structure and the difference between nodes and elements.
- Explain when scripts run relative to page parsing, and use `DOMContentLoaded`.

## Conceptual explanation

An HTML file is just text. When the browser loads it, a **parser** reads the text and builds an in-memory structure of objects called the **Document Object Model**. Each tag becomes an **element object**, each run of text becomes a **text node**, and they are linked into a **tree**: every item has one parent and any number of children. The browser draws the page from this tree, not from your file. JavaScript can read and modify the tree through the global `document` object, and every change is reflected on screen immediately.

```diagram
tree
document
  html
    head
      title
    body
      h1 | id="title"
      ul | id="menu"
        li | Home
        li | About
```

**Nodes and elements.** Everything in the tree is a **node**. There are several kinds: *element nodes* (tags such as `<ul>`), *text nodes* (the words inside), and *comment nodes*. An **element** is specifically an element node. The distinction matters because whitespace between tags becomes text nodes, which is why `childNodes` (all nodes) and `children` (elements only) can have different lengths.

[[widths 1.4 2.2 2.2]]
| Property | Includes | Typical use |
|---|---|---|
| `element.children` | child **elements** only | Looping over a list's items |
| `element.childNodes` | all child nodes, including text and comments | Rarely needed |
| `element.firstElementChild`, `lastElementChild` | first and last child element | Quick access to ends |
| `element.parentElement` | parent element | Walking up the tree |
| `element.nextElementSibling`, `previousElementSibling` | neighbouring elements | Walking sideways |
| `document.body`, `document.documentElement` | the `<body>` and `<html>` elements | Page-wide access |

The browser also provides the global object **`window`**, which represents the browser tab itself and holds things like `document`, `localStorage`, `setTimeout` and `fetch`. `window` is to the browser what `process` is to Node.js.

## Worked example: walking the tree

```html file="index.html" page
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>DOM tour</title>
  </head>
  <body>
    <h1 id="title">Hello</h1>
    <ul id="menu"><li>Home</li><li>About</li></ul>
    <script>
      console.log(document.title);
      console.log(document.body.children.length);

      const menu = document.getElementById("menu");
      console.log(menu.children.length, menu.firstElementChild.textContent);
      console.log(menu.parentElement.tagName, menu.childNodes.length);
      console.log(typeof window, window === globalThis, document.nodeType);
    </script>
  </body>
</html>
```

```output
DOM tour
3
2 Home
BODY 2
object true 9
```

**Line by line.** Line 10 reads the page title. Line 11: `<body>` has three child *elements*: the `<h1>`, the `<ul>` and the `<script>` itself, so `3`. Line 13 finds the list by its id (Section 3). Line 14: the list has two `<li>` children, and the first one's text is `Home`. Line 15: the list's parent element is the `<body>` (tag names are uppercase in HTML documents), and `childNodes.length` is `2` because there is no whitespace between the `<li>` tags; if the tags had been on separate lines, whitespace text nodes would raise it. Line 16: `window` is an object and is the same as the global object, and `document.nodeType` is `9`, the code for a *document node*.

## When does your script run?

The browser builds the DOM **while reading the file from top to bottom**. A script that runs before an element has been parsed cannot find it. There are three ways to solve this.

1. **Put the `<script>` at the end of `<body>`**, as above. Everything above it exists already.
2. **Add `defer` (or `type="module"`)** to the script tag. The script downloads while parsing continues and runs **after** parsing finishes. Module scripts are deferred automatically.
3. **Wait for the `DOMContentLoaded` event**, which fires when the DOM is fully built.

```html file="index.html" page
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Script timing</title>
    <script>
      console.log("head script: body is", document.body);
      document.addEventListener("DOMContentLoaded", () => {
        console.log("DOM ready:", document.body.tagName);
      });
    </script>
    <script type="module">
      console.log("module script: body is", document.body.tagName);
    </script>
  </head>
  <body>
    <p>Hello</p>
  </body>
</html>
```

```output
head script: body is null
module script: body is BODY
DOM ready: BODY
```

The classic script in `<head>` runs while the parser is still in the head, so `document.body` does not exist yet and prints `null`. The module script is deferred: it runs after parsing is complete, so the body exists. `DOMContentLoaded` fires last, after deferred scripts have run. In this curriculum, scripts normally go at the end of `<body>` or use `type="module"`; both avoid the problem without extra code.

# 3. Selecting Elements

## Learning objectives for this section

- Use `getElementById`, `querySelector` and `querySelectorAll`, and say what each returns.
- Explain static versus live collections and why a `NodeList` is not an array.
- Handle "element not found" correctly.

## Conceptual explanation

Before you can change an element you must get a **reference** to its object. These methods search the DOM and hand you that reference. Because you already know CSS selectors (`#id`, `.class`, `tag`, `parent > child`), `querySelector` lets you reuse that knowledge directly.

## Function deep dive: `querySelector()` and `querySelectorAll()`

**What they are.** Methods of `document` (and of every element) that search for elements using a **CSS selector string**.

**Why they exist.** Pages are built from many elements; JavaScript needs a flexible, familiar way to point at "the submit button" or "every card in the sidebar".

**Syntax.** `document.querySelector(selector)` returns one element; `document.querySelectorAll(selector)` returns a list.

**Parameter.** `selector`: any valid CSS selector string, such as `"#menu"`, `".item.active"`, `"ul > li"`, `"input[type='text']"`, `"li:not(.active)"`.

**Return values.**

- `querySelector` returns the **first** matching element in document order, or **`null`** if there is none.
- `querySelectorAll` returns a **`NodeList`** of all matches, which is **empty** (never `null`) when nothing matches. The list is **static**: it is a snapshot, and does not change if the page changes later.

**How it works.** The browser walks the DOM tree in document order and tests each element against the selector, stopping at the first match for `querySelector`. When called on an element rather than on `document`, the search covers only that element's descendants, which is both faster and more precise.

**Edge cases and errors.** An invalid selector (for example `"##menu"`) throws a `SyntaxError`. Selecting by id with `querySelector("#menu")` and with `getElementById("menu")` gives the same element, but `getElementById` takes the bare id **without** the `#`, and is slightly faster.

```html file="index.html" page
<!DOCTYPE html>
<html lang="en">
  <body>
    <ul id="menu">
      <li class="item">Home</li>
      <li class="item active">About</li>
      <li class="item">Contact</li>
    </ul>
    <script>
      const menu = document.getElementById("menu");
      const first = document.querySelector(".item");
      const all = document.querySelectorAll(".item");
      const live = document.getElementsByClassName("item");

      console.log(menu.tagName, first.textContent, all.length, live.length);
      console.log(document.querySelector(".missing"), document.getElementById("nope"));
      console.log(Array.isArray(all), Array.isArray([...all]), all instanceof NodeList);

      const extra = document.createElement("li");
      extra.className = "item";
      menu.append(extra);
      console.log(all.length, live.length);

      console.log([...all].map((li) => li.textContent).join(","));
      console.log(document.querySelector("#menu > .active").textContent);
      console.log(menu.querySelectorAll("li:not(.active)").length);
    </script>
  </body>
</html>
```

```output
UL Home 3 3
null null
false true true
3 4
Home,About,Contact
About
3
```

**Line by line.** Lines 10 to 13 collect references four ways. `getElementsByClassName` returns an **`HTMLCollection`**, which is *live*. Line 15 prints the list's tag, the first item's text, and the two counts (both `3`). Line 16: no match gives `null` for both single-element methods. Line 17: a `NodeList` is **not** an array (`Array.isArray` is `false`), but spreading it into a real array works. Lines 19 to 21 add a fourth `<li>`. Line 22 proves the difference: the static `NodeList` still says `3`, the live collection now says `4`. Line 24 builds a real array with spread so `map` can be used (Sheet 02). Line 25 uses a child selector. Line 26 searches only inside `menu`, and counts the three items without the `active` class (Home, Contact and the new empty one).

**Rule of thumb.** Use `querySelector` and `querySelectorAll` for almost everything, use `getElementById` when you have an id, and convert with `[...nodeList]` or `Array.from(nodeList)` when you need `map`, `filter` or `reduce`. (`NodeList` does have `forEach`.)

| Method | Returns | When nothing matches | Live? |
|---|---|---|---|
| `getElementById(id)` | one element | `null` | n/a |
| `querySelector(css)` | first match | `null` | n/a |
| `querySelectorAll(css)` | `NodeList` | empty `NodeList` | No (static) |
| `getElementsByClassName(name)` | `HTMLCollection` | empty collection | **Yes** |
| `getElementsByTagName(name)` | `HTMLCollection` | empty collection | **Yes** |

## Common mistakes in this section

#### Mistake 1: Selecting before the element exists

**Why it is wrong.** The script runs while the parser is still above the element, so the search finds nothing and returns `null`.

```html file="index.html" bad page throws
<!DOCTYPE html>
<html lang="en">
  <head>
    <script>
      const title = document.getElementById("title");
      title.textContent = "Welcome";
    </script>
  </head>
  <body>
    <h1 id="title">Hello</h1>
  </body>
</html>
```

```output
Uncaught TypeError: Cannot read properties of null (reading 'textContent')
```

**Symptom.** In the Console: a `TypeError` saying it cannot read properties of `null`. The word `null` is the clue: your selector returned `null`.

```html file="index.html" good page
<!DOCTYPE html>
<html lang="en">
  <head>
    <script type="module">
      const title = document.getElementById("title");
      title.textContent = "Welcome";
      console.log(title.textContent);
    </script>
  </head>
  <body>
    <h1 id="title">Hello</h1>
  </body>
</html>
```

```output
Welcome
```

**How to diagnose it yourself.** `console.log` the result of the selector. If it prints `null`, either the id or selector is wrong, or the element did not exist yet when the script ran. Check the script's position (or use `defer`/`type="module"`).

#### Mistake 2: Calling array methods on a `NodeList`

**Why it is wrong.** `NodeList` has `forEach` but not `map`, `filter` or `reduce`.

```html file="index.html" bad page throws
<!DOCTYPE html>
<html lang="en">
  <body>
    <p class="note">One</p>
    <p class="note">Two</p>
    <script>
      const notes = document.querySelectorAll(".note");
      const texts = notes.map((n) => n.textContent);
    </script>
  </body>
</html>
```

```output
Uncaught TypeError: notes.map is not a function
```

```html file="index.html" good page
<!DOCTYPE html>
<html lang="en">
  <body>
    <p class="note">One</p>
    <p class="note">Two</p>
    <script>
      const notes = document.querySelectorAll(".note");
      const texts = [...notes].map((n) => n.textContent);
      console.log(texts.join(" + "));
    </script>
  </body>
</html>
```

```output
One + Two
```

**Symptom.** `notes.map is not a function`. **Diagnosis:** `console.log(notes)` shows `NodeList(2)` instead of `Array(2)`. Convert with spread or `Array.from`.

#### Mistake 3: Forgetting the `#` or `.` in a selector

**Why it is wrong.** In `querySelector`, `"menu"` means "an element whose **tag** is `<menu>`", not an id.

```html file="index.html" bad page
<!DOCTYPE html>
<html lang="en">
  <body>
    <ul id="menu"></ul>
    <script>
      console.log(document.querySelector("menu"));
      console.log(document.querySelector("#menu").tagName);
    </script>
  </body>
</html>
```

```output
null
UL
```

**Symptom.** `null` with no error until you use the result. **Diagnosis:** remember the CSS rules: `#` for ids, `.` for classes, bare words for tags.

#### Mistake 4: Expecting a snapshot but holding a live collection

**Why it is wrong.** `getElementsByClassName` and `getElementsByTagName` return live collections, so a loop that removes matching elements skips some of them.

```html file="index.html" bad page
<!DOCTYPE html>
<html lang="en">
  <body>
    <p class="old">1</p><p class="old">2</p><p class="old">3</p><p class="old">4</p>
    <script>
      const items = document.getElementsByClassName("old");
      for (let i = 0; i < items.length; i++) {
        items[i].classList.remove("old");
      }
      console.log(items.length);
    </script>
  </body>
</html>
```

```output
2
```

```html file="index.html" good page
<!DOCTYPE html>
<html lang="en">
  <body>
    <p class="old">1</p><p class="old">2</p><p class="old">3</p><p class="old">4</p>
    <script>
      for (const item of document.querySelectorAll(".old")) {
        item.classList.remove("old");
      }
      console.log(document.querySelectorAll(".old").length);
    </script>
  </body>
</html>
```

```output
0
```

**Symptom.** Only half the elements change: removing the class makes an element leave the live collection, which shifts the remaining ones down and the index jumps over them. **Diagnosis:** prefer the static `querySelectorAll` whenever your loop changes the thing you are searching for.
