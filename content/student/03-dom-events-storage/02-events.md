# 6. Events

## Learning objectives for this section

- Explain event-driven programming and attach handlers with `addEventListener()`.
- Use the event object: `type`, `target`, `currentTarget`, `key`, `preventDefault()`.
- Choose the right event for typing, committing a value, submitting a form and keyboard input.
- Remove listeners correctly and use `once`.

## Conceptual explanation

A terminal program runs from start to finish. A web page does not: after your script finishes the first time, the page just *waits*. Things then happen to it: a click, a key press, a form submission, a timer. Each of these is an **event**. You tell the browser in advance, "when *this* happens to *that* element, run *this function*". That function is an **event handler** (or *listener*), and it is a callback in exactly the sense of Sheet 01: you hand it over and the browser calls it later, passing information about what happened. This style is called **event-driven programming**, and every interactive interface, including every React app, works this way.

## Function deep dive: `addEventListener()`

**What it is.** A method on elements (and on `document` and `window`) that registers a function to be called whenever a given type of event reaches that target.

**Why it exists.** It lets you attach any number of independent behaviours to the same event without changing the HTML, and without one behaviour replacing another.

**Syntax.** `target.addEventListener(type, fn, options)`

**Parameters.**

- `type`: a string naming the event, such as `"click"`, `"input"`, `"submit"` or `"keydown"`.
- `listener`: the function to call. It receives one argument, the **event object**.
- `options` (optional): `true` (shorthand for the capture phase, Section 7) or an object such as `{ once: true }` (run at most once, then remove itself), `{ capture: true }`, `{ passive: true }` (promise not to call `preventDefault`, which helps scrolling performance).

**Return value.** `undefined`.

**How it works, step by step.** (1) The browser stores `(type, listener)` in the element's list of listeners. (2) When a matching event occurs, the browser creates an event object. (3) It calls each registered listener, **in the order they were added**, passing that object. (4) Your listener runs to completion, then the next one runs. An error thrown in one listener is reported in the Console but does not stop the others.

**Removing a listener.** `target.removeEventListener(type, listener)` removes a listener, but only if you pass **the same function object** you added. An anonymous arrow function written a second time is a different object and removes nothing.

**Older style.** `element.onclick = fn` also works, but each element can have only one `onclick` handler (a second assignment replaces the first), so this curriculum always uses `addEventListener`.

## Worked example: a click counter

```html file="index.html" page steps="click #btn | click #btn | print #btn"
<!DOCTYPE html>
<html lang="en">
  <body>
    <button id="btn">Clicked 0 times</button>
    <script>
      const btn = document.querySelector("#btn");
      let count = 0;

      btn.addEventListener("click", (event) => {
        count++;
        btn.textContent = `Clicked ${count} times`;
        console.log(event.type, event.target === btn, count);
      });
    </script>
  </body>
</html>
```

```output
click true 1
click true 2
Clicked 2 times
```

**Line by line and data flow.** Line 7 holds the state in an ordinary variable, exactly as in the closure examples of Sheet 01. Line 9 registers the handler; nothing runs yet. Each click makes the browser call the arrow function with an **event object**. Inside, line 10 updates the data, line 11 updates the page, and line 12 logs three facts: the event's `type` is `"click"`, `event.target` (the element that was clicked) is the button, and the new count. The two scripted clicks give counts 1 and 2, and the button text ends as `Clicked 2 times`.

## The event object

Every listener receives an object describing what happened. These properties and methods cover most needs.

[[widths 1.3 3.6]]
| Member | Meaning |
|---|---|
| `event.type` | The event name, such as `"click"` |
| `event.target` | The **innermost element** where the event started (what was actually clicked) |
| `event.currentTarget` | The element **the listener is attached to** |
| `event.key` | For keyboard events: the key value, such as `"a"`, `"Enter"`, `"Escape"` |
| `event.preventDefault()` | Cancels the browser's default action (submitting a form, following a link) |
| `event.stopPropagation()` | Stops the event travelling to ancestors (Section 7) |
| `event.clientX`, `event.clientY` | Pointer position for mouse events |

## Choosing the right event

[[widths 1.2 3.4 2.3]]
| Event | Fires when | Typical use |
|---|---|---|
| `click` | An element is clicked, or activated by keyboard (Enter or Space on a button) | Buttons, links, cards |
| `input` | The value of an input changes, **on every keystroke or edit** | Live search, character counters, previews |
| `change` | A value is **committed**: when the field loses focus after a change, or immediately for checkboxes and selects | Settings, dropdowns, checkboxes |
| `submit` | A form is submitted (button click or Enter in a field) | Form handling |
| `keydown`, `keyup` | A key is pressed or released | Shortcuts, Enter to add, Escape to close |
| `focus`, `blur` | An element gains or loses keyboard focus | Validation on leaving a field |
| `DOMContentLoaded`, `load` | The DOM is built / all resources have loaded | Start-up code |

```html file="index.html" page steps="fill #t hello | press #t Tab"
<!DOCTYPE html>
<html lang="en">
  <body>
    <input id="t" />
    <script>
      const field = document.getElementById("t");
      field.addEventListener("input", (e) => console.log("input:", e.target.value));
      field.addEventListener("change", (e) => console.log("change:", e.target.value));
      field.addEventListener("blur", () => console.log("blur"));
    </script>
  </body>
</html>
```

```output
input: hello
change: hello
blur
```

Typing fires `input`. Pressing Tab moves focus away, which commits the edit (`change`) and then fires `blur`. In current Chromium the order is `change` then `blur`; do not write code that depends on the order of those two. (When you type character by character, `input` fires for each character; the scripted test fills the whole value at once, which fires it once.) For a **live** preview or search box use `input`; `change` would update only after the user leaves the field.

## Keyboard events

```html file="index.html" page steps="fill #name Asha | press #name Enter | print #greeting"
<!DOCTYPE html>
<html lang="en">
  <body>
    <input id="name" />
    <p id="greeting"></p>
    <script>
      const name = document.getElementById("name");
      const greeting = document.getElementById("greeting");

      name.addEventListener("input", () => {
        greeting.textContent = `Hello, ${name.value}!`;
      });

      name.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
          console.log("Enter pressed with", JSON.stringify(name.value));
        }
      });
    </script>
  </body>
</html>
```

```output
Enter pressed with "Asha"
Hello, Asha!
```

The `input` handler keeps the greeting synchronised with the field as the user types. The `keydown` handler checks `event.key` and acts only on `"Enter"`. Use `event.key` (the character or key name) rather than the old numeric `keyCode`, which is deprecated.

## Removing a listener and `once`

```html file="index.html" page steps="click #btn | click #btn | click #btn"
<!DOCTYPE html>
<html lang="en">
  <body>
    <button id="btn">Go</button>
    <script>
      const btn = document.getElementById("btn");

      function onClick() {
        console.log("clicked");
        btn.removeEventListener("click", onClick);
      }

      btn.addEventListener("click", onClick);
      btn.addEventListener("click", () => console.log("once only"), { once: true });
    </script>
  </body>
</html>
```

```output
clicked
once only
```

Three clicks produce only two lines. On the first click both listeners run, in the order they were registered; `onClick` removes itself (it passes the *same function object* it was registered with), and the second listener, registered with `{ once: true }`, removes itself automatically. The later clicks find no listeners.

## Common mistakes in this section

#### Mistake 1: Calling the handler instead of passing it

**Why it is wrong.** `handle()` runs the function **now** and registers its return value (`undefined`) as the listener (Sheet 01, Section 9).

```html file="index.html" bad page steps="click #btn"
<!DOCTYPE html>
<html lang="en">
  <body>
    <button id="btn">Go</button>
    <script>
      function handle() {
        console.log("handled");
      }
      document.getElementById("btn").addEventListener("click", handle());
    </script>
  </body>
</html>
```

```output
handled
```

**Symptom.** `handled` is logged **once at page load**, and clicking does nothing. **Fix:** `addEventListener("click", handle)`. To pass arguments, wrap: `() => handle(id)`. **Diagnosis:** if code runs at load time instead of on the event, look for stray parentheses after the function name.

#### Mistake 2: Removing a listener with a different function object

**Why it is wrong.** Two identical-looking arrow functions are two distinct objects.

```html file="index.html" bad page steps="click #btn"
<!DOCTYPE html>
<html lang="en">
  <body>
    <button id="btn">Go</button>
    <script>
      const btn = document.getElementById("btn");
      btn.addEventListener("click", () => console.log("still here"));
      btn.removeEventListener("click", () => console.log("still here"));
    </script>
  </body>
</html>
```

```output
still here
```

**Symptom.** The listener cannot be removed. **Fix:** store the function in a variable (`const onClick = () => ...`) and pass that variable to both calls, or use the `once` option or an `AbortController` signal.

#### Mistake 3: Confusing `target` with `currentTarget`

**Why it is wrong.** `target` is the innermost element that was clicked, which may be a child of the element your listener is on.

```html file="index.html" page steps="click #icon"
<!DOCTYPE html>
<html lang="en">
  <body>
    <button id="save" data-action="save"><span id="icon">Disk</span> Save</button>
    <script>
      document.getElementById("save").addEventListener("click", (event) => {
        console.log("target:", event.target.tagName, event.target.dataset.action);
        console.log("currentTarget:", event.currentTarget.tagName);
        console.log(event.currentTarget.dataset.action);
      });
    </script>
  </body>
</html>
```

```output
target: SPAN undefined
currentTarget: BUTTON
save
```

**Symptom.** Reading `event.target.dataset.action` gives `undefined` when the user clicks the icon inside the button. **Fix:** use `event.currentTarget` (the element the listener is on) or `event.target.closest("[data-action]")`. **Diagnosis:** log both and compare.

#### Mistake 4: Using `change` when you wanted live updates

**Why it is wrong.** `change` waits until the field loses focus.

```html file="index.html" bad page steps="fill #q hello | print #out"
<!DOCTYPE html>
<html lang="en">
  <body>
    <input id="q" />
    <p id="out"></p>
    <script>
      const q = document.getElementById("q");
      q.addEventListener("change", () => {
        document.getElementById("out").textContent = q.value.toUpperCase();
      });
    </script>
  </body>
</html>
```

```output

```

```html file="index.html" good page steps="fill #q hello | print #out"
<!DOCTYPE html>
<html lang="en">
  <body>
    <input id="q" />
    <p id="out"></p>
    <script>
      const q = document.getElementById("q");
      q.addEventListener("input", () => {
        document.getElementById("out").textContent = q.value.toUpperCase();
      });
    </script>
  </body>
</html>
```

```output
HELLO
```

**Symptom.** The preview stays empty until the user clicks elsewhere. **Diagnosis:** ask "should this react while typing or after leaving the field?" and pick `input` or `change` accordingly.

# 7. Bubbling, Capturing, Delegation and `preventDefault()`

## Learning objectives for this section

- Explain the three phases of event propagation and predict the order listeners run in.
- Use event delegation to handle many (including future) elements with one listener.
- Use `preventDefault()` and `stopPropagation()` appropriately.

## Conceptual explanation

When you click a button, you are also clicking the `<div>` that contains it, and the `<body>`, and the whole page. The browser reflects this: an event does not only visit the element where it started. It **travels through the tree** in three phases.

1. **Capture phase**: from the top (`window`, `document`) **down** towards the target.
2. **Target phase**: the event arrives at the element where it started.
3. **Bubble phase**: from the target **back up** to the top.

```diagram
flow
Capture: document -> body -> outer div -> inner div -> *button (target) -> Bubble: inner div -> outer div -> body -> document
```

By default `addEventListener` listens in the **bubble** phase, so a click on the button is also seen by listeners on its ancestors, from the inside out. Passing `true` (or `{ capture: true }`) as the third argument listens in the **capture** phase instead.

```html file="index.html" page steps="click #btn"
<!DOCTYPE html>
<html lang="en">
  <body>
    <div id="outer">
      <div id="inner">
        <button id="btn">Go</button>
      </div>
    </div>
    <script>
      const outer = document.getElementById("outer");
      const inner = document.getElementById("inner");
      const btn = document.getElementById("btn");

      outer.addEventListener("click", () => console.log("outer bubble"));
      inner.addEventListener("click", () => console.log("inner bubble"));
      btn.addEventListener("click", () => console.log("button"));
      outer.addEventListener("click", () => console.log("outer capture"), true);
    </script>
  </body>
</html>
```

```output
outer capture
button
inner bubble
outer bubble
```

**Reading the order.** The click starts at the top and **captures** downward, so the capture listener on `outer` runs first. At the **target** the button's own listener runs. Then the event **bubbles** upward: `inner`, then `outer`. The registration order in the source (lines 13 to 16) does not matter between phases; it only decides the order among listeners on the *same* element in the *same* phase.

**`event.stopPropagation()`** stops the event from going any further along the path. Use it rarely: it hides events from every other listener above, including ones you or a library added for good reasons (analytics, closing menus).

## Event delegation

Because events bubble, **one listener on a parent can handle events for all its descendants**, and `event.target` tells you which descendant was involved. This pattern is called **delegation**, and it has two big advantages: you attach one listener instead of hundreds, and it keeps working for elements **added later**, because the listener belongs to the parent, which never changes.

```html file="index.html" page steps="click #add | click li:nth-child(2) | click li:nth-child(1)"
<!DOCTYPE html>
<html lang="en">
  <body>
    <button id="add">Add</button>
    <ul id="list">
      <li data-id="1">Item 1</li>
    </ul>
    <script>
      const list = document.getElementById("list");
      let nextId = 2;

      document.getElementById("add").addEventListener("click", () => {
        const li = document.createElement("li");
        li.dataset.id = nextId;
        li.textContent = `Item ${nextId}`;
        nextId++;
        list.append(li);
      });

      list.addEventListener("click", (event) => {
        const li = event.target.closest("li");
        if (!li) {
          return;
        }
        li.classList.toggle("done");
        console.log("toggled", li.dataset.id, li.classList.contains("done"));
      });
    </script>
  </body>
</html>
```

```output
toggled 2 true
toggled 1 true
```

**Line by line.** There is **one** listener on the `<ul>` (line 20). When something inside it is clicked, line 21 uses `closest("li")` to find the list item that contains the click (even if the user clicked a child element of the `<li>`), and line 22 ignores clicks on the list's padding where no item was hit. Item 2 did not exist when the listener was registered, yet clicking it works, because the click bubbles up to the `<ul>`. Each handled click toggles the `done` class and logs the item's id.

## `preventDefault()`

Many events have a **default action** built into the browser: clicking a link navigates, submitting a form reloads the page, pressing Space scrolls. `event.preventDefault()` cancels that default action while leaving the event propagating. It works only on **cancelable** events and only if called before the handler returns.

```html file="index.html" page steps="click #link | eval location.pathname"
<!DOCTYPE html>
<html lang="en">
  <body>
    <a id="link" href="/other-page">Go</a>
    <script>
      document.getElementById("link").addEventListener("click", (event) => {
        event.preventDefault();
        console.log("handled", event.defaultPrevented);
      });
    </script>
  </body>
</html>
```

```output
handled true
/index.html
```

Without line 7 the browser would navigate to `/other-page`. With it, the page stays where it is (the last line of output shows the path is unchanged) and your code decides what happens next. The same call is essential on form `submit` events (Section 8), and it is how single-page applications and React Router (Sheet 08) handle links without reloading.

## Common mistakes in this section

#### Mistake 1: Forgetting `preventDefault()` on a form submit

**Why it is wrong.** The browser's default is to send the form and load a new page, wiping your JavaScript state.

```html file="index.html" bad page steps="fill #q Asha | click #go | eval location.search"
<!DOCTYPE html>
<html lang="en">
  <body>
    <form id="f">
      <input id="q" name="q" />
      <button id="go">Go</button>
    </form>
    <script>
      document.getElementById("f").addEventListener("submit", () => {
        console.log("submitted");
      });
    </script>
  </body>
</html>
```

```output
submitted
?q=Asha
```

```html file="index.html" good page steps="fill #q Asha | click #go | eval JSON.stringify(location.search)"
<!DOCTYPE html>
<html lang="en">
  <body>
    <form id="f">
      <input id="q" name="q" />
      <button id="go">Go</button>
    </form>
    <script>
      document.getElementById("f").addEventListener("submit", (event) => {
        event.preventDefault();
        console.log("submitted", document.getElementById("q").value);
      });
    </script>
  </body>
</html>
```

```output
submitted Asha
""
```

**Symptom.** In the bad version your handler runs, but then the page **reloads** with `?q=Asha` appended to the address, and everything in memory is lost. (DevTools clears the Console on a reload unless *Preserve log* is ticked, so the `submitted` message vanishes too.) **Diagnosis:** if your page flashes and resets when you submit, you forgot `preventDefault()`. Look at the address bar for `?name=value` text.

#### Mistake 2: Attaching listeners to elements and expecting new ones to be covered

**Why it is wrong.** A listener belongs to the specific element it was attached to. Elements created later have none.

```html file="index.html" bad page steps="click #add | click li:nth-child(2) | click li:nth-child(1)"
<!DOCTYPE html>
<html lang="en">
  <body>
    <button id="add">Add</button>
    <ul id="list"><li>One</li></ul>
    <script>
      for (const li of document.querySelectorAll("li")) {
        li.addEventListener("click", () => console.log("clicked", li.textContent));
      }
      document.getElementById("add").addEventListener("click", () => {
        const li = document.createElement("li");
        li.textContent = "Two";
        document.getElementById("list").append(li);
      });
    </script>
  </body>
</html>
```

```output
clicked One
```

**Symptom.** New items do nothing when clicked, while the original ones work. **Fix:** delegate from the parent (see the worked example) or attach a listener when you create each element. **Diagnosis:** compare working and non-working elements: if only the dynamically added ones fail, you need delegation.

#### Mistake 3: Reading `event.target` when the user clicked a child element

**Why it is wrong.** `target` is the *innermost* element. If your list item contains a `<span>` and the user clicks it, `target` is the span.

```html file="index.html" bad page steps="click #label"
<!DOCTYPE html>
<html lang="en">
  <body>
    <ul id="list">
      <li data-id="5"><span id="label">Buy milk</span></li>
    </ul>
    <script>
      document.getElementById("list").addEventListener("click", (event) => {
        console.log(event.target.dataset.id, event.target.closest("li").dataset.id);
      });
    </script>
  </body>
</html>
```

```output
undefined 5
```

**Symptom.** `undefined` when reading data from the clicked element. **Fix:** always resolve with `closest(selector)` (as shown above) when delegating. **Diagnosis:** log `event.target` to see which element was really hit.

#### Mistake 4: Overusing `stopPropagation()`

**Why it is wrong.** It silently hides the event from all listeners higher up, including ones that other code relies on.

```html file="index.html" bad page steps="click #btn"
<!DOCTYPE html>
<html lang="en">
  <body>
    <button id="btn">Go</button>
    <script>
      document.body.addEventListener("click", () => console.log("analytics: click"));
      document.getElementById("btn").addEventListener("click", (event) => {
        event.stopPropagation();
        console.log("button handled");
      });
    </script>
  </body>
</html>
```

```output
button handled
```

**Symptom.** A listener on an ancestor (menu-closing, logging, a library) mysteriously never runs for clicks on certain elements. **Fix:** remove `stopPropagation()` and test `event.target` in the ancestor's listener instead. **Diagnosis:** search the code for `stopPropagation`; it is almost always the cause of "my other listener doesn't fire".
