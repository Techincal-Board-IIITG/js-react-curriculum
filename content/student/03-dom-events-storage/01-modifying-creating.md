# 4. Changing Content, Attributes, Classes and Styles

## Learning objectives for this section

- Change text with `textContent`, and explain how `innerHTML` differs and why it is riskier.
- Read and write attributes, `dataset` values, classes and inline styles.
- Read and write form control values.

## Conceptual explanation

Once you hold an element reference, its **properties** reflect its current state and assigning to them changes the page. There are two layers to keep apart. **Attributes** are what you write in HTML (`<a href="/a">`); **properties** are the live JavaScript values on the element object. They are usually linked but not identical: an `<input value="x">` starts with the attribute `x`, but as the user types, the **property** `input.value` changes while the attribute stays `x`.

## Text and HTML

[[widths 1.3 2.6 2.4]]
| Property | What it reads or writes | Parses HTML? |
|---|---|---|
| `textContent` | All text inside, as plain text | **No**: `<b>` stays literal text |
| `innerText` | Text as rendered (respects CSS visibility) | No |
| `innerHTML` | The HTML markup inside | **Yes**: tags become elements |

```html file="index.html" page
<!DOCTYPE html>
<html lang="en">
  <body>
    <h1 id="t">Old</h1>
    <a id="link" href="/a">link</a>
    <div id="box" class="card">Box</div>
    <input id="inp" value="x" />
    <script>
      const t = document.getElementById("t");
      t.textContent = "New <b>title</b>";
      console.log(t.innerHTML);
      t.innerHTML = "New <b>title</b>";
      console.log(t.textContent, t.children.length);

      const link = document.getElementById("link");
      link.setAttribute("href", "/b");
      console.log(link.getAttribute("href"), link.href.endsWith("/b"));

      const box = document.getElementById("box");
      box.classList.add("active");
      box.classList.toggle("card");
      console.log(box.className, box.classList.contains("card"));

      box.style.backgroundColor = "tomato";
      console.log(box.style.backgroundColor, box.getAttribute("style"));

      box.dataset.userId = "42";
      console.log(box.getAttribute("data-user-id"), box.dataset.userId);

      const inp = document.getElementById("inp");
      inp.value = "typed";
      console.log(inp.value, inp.getAttribute("value"));
    </script>
  </body>
</html>
```

```output
New &lt;b&gt;title&lt;/b&gt;
New title 1
/b true
active false
tomato background-color: tomato;
42 42
typed x
```

**Line by line.**

- Lines 10 to 13: assigning `textContent` treats the text literally, so the angle brackets are *escaped* when you read the markup back with `innerHTML` (`&lt;b&gt;`). Assigning the same string to `innerHTML` creates a real `<b>` element: `textContent` now reads `New title` and the heading has one child element.
- Lines 15 to 17: `setAttribute(name, value)` and `getAttribute(name)` work with the attribute exactly as written (`/b`), while the **property** `link.href` is the fully resolved address, so we test it with `endsWith`.
- Lines 19 to 22: the `classList` object has `add`, `remove`, `toggle` (add if absent, remove if present) and `contains`. After adding `active` and toggling `card` off, the class attribute is just `active`.
- Lines 24 and 25: the `style` property holds **inline** styles. CSS property names become camelCase (`background-color` becomes `backgroundColor`). Reading the `style` attribute shows the text the browser wrote.
- Lines 27 and 28: attributes beginning with `data-` are exposed through `dataset`, with dashes converted to camelCase: `data-user-id` is `dataset.userId`. Values are always strings.
- Lines 30 to 32: assigning `inp.value` changes what the user sees and what a form would submit, but the *attribute* still says `x`. Use the property for current state.

::: concept Prefer classes over inline styles
Change appearance by adding or removing a CSS **class** (`element.classList.toggle("done")`) and keep the actual colours and sizes in your stylesheet. It keeps style in one place, is easier to change, and supports hover states, media queries and animations that inline styles cannot.
:::

## Optional deep dive: `hidden`, `disabled` and other boolean properties

HTML boolean attributes (`hidden`, `disabled`, `checked`, `required`) are controlled with **properties holding `true` or `false`**: `button.disabled = true;`, `checkbox.checked = false`, `panel.hidden = true`. Do not set them with `setAttribute("disabled", "false")`: any value, even `"false"`, makes the attribute *present*, and a present boolean attribute means `true`.

## Common mistakes in this section

#### Mistake 1: Putting user text into `innerHTML`

**Why it is wrong.** `innerHTML` interprets markup. If the text came from a user or a server, it can contain tags that run code. Section 11 covers the attack in detail.

```html file="index.html" bad page
<!DOCTYPE html>
<html lang="en">
  <body>
    <p id="out"></p>
    <script>
      const userText =
        "<img src='data:image/png;base64,AAAA' " +
        `onerror="console.log('attacker code ran')">`;
      document.getElementById("out").innerHTML = userText;
    </script>
  </body>
</html>
```

```output
attacker code ran
```

```html file="index.html" good page
<!DOCTYPE html>
<html lang="en">
  <body>
    <p id="out"></p>
    <script>
      const userText =
        "<img src='data:image/png;base64,AAAA' " +
        `onerror="console.log('attacker code ran')">`;
      document.getElementById("out").textContent = userText;
      console.log(document.querySelectorAll("img").length);
    </script>
  </body>
</html>
```

```output
0
```

**Symptom.** Strange elements appear, or code you never wrote runs. **Diagnosis:** search your code for `innerHTML =` and ask where the string came from. If any part is not a constant you wrote yourself, use `textContent` or build elements with `createElement` (Section 5).

#### Mistake 2: Writing CSS property names with dashes

**Why it is wrong.** `box.style.background-color` is read as `box.style.background` minus `color`, which is not valid to assign to.

```js bad nocheck
box.style.background-color = "red";
```

**Symptom.** A `SyntaxError` about an invalid left-hand side in an assignment, and nothing on the page works because the whole script fails to parse.

```html file="index.html" good page
<!DOCTYPE html>
<html lang="en">
  <body>
    <div id="box">Box</div>
    <script>
      const box = document.getElementById("box");
      box.style.backgroundColor = "red";
      box.style["background-color"] = "blue";
      console.log(box.style.backgroundColor);
    </script>
  </body>
</html>
```

```output
blue
```

**Diagnosis.** Use camelCase (`backgroundColor`) or bracket notation with the dashed name. Better still: toggle a CSS class.

#### Mistake 3: Setting a boolean attribute to the text `"false"`

**Why it is wrong.** For boolean attributes, *presence* means true.

```html file="index.html" bad page
<!DOCTYPE html>
<html lang="en">
  <body>
    <button id="b">Save</button>
    <script>
      const b = document.getElementById("b");
      b.setAttribute("disabled", "false");
      console.log(b.disabled);
    </script>
  </body>
</html>
```

```output
true
```

```html file="index.html" good page
<!DOCTYPE html>
<html lang="en">
  <body>
    <button id="b" disabled>Save</button>
    <script>
      const b = document.getElementById("b");
      b.disabled = false;
      console.log(b.disabled, b.hasAttribute("disabled"));
    </script>
  </body>
</html>
```

```output
false false
```

**Symptom.** A button stays disabled although your code "set it to false". **Diagnosis:** log the **property** (`b.disabled`) rather than guessing from the markup.

#### Mistake 4: Using the `value` attribute to read what the user typed

**Why it is wrong.** The attribute is the *initial* value from the HTML; the property is the *current* value.

```html file="index.html" bad page steps="fill #name Asha | eval JSON.stringify(document.getElementById('name').getAttribute('value'))"
<!DOCTYPE html>
<html lang="en">
  <body>
    <input id="name" value="" />
  </body>
</html>
```

```output
""
```

```html file="index.html" good page steps="fill #name Asha | eval document.getElementById('name').value"
<!DOCTYPE html>
<html lang="en">
  <body>
    <input id="name" value="" />
  </body>
</html>
```

```output
Asha
```

**Symptom.** Your code always reads the original (often empty) text. **Diagnosis:** compare `input.value` with `input.getAttribute("value")` in the Console after typing.

# 5. Creating, Inserting, Removing and Navigating Elements

## Learning objectives for this section

- Create elements and put them into the page, and remove or replace them.
- Build lists from arrays of data using `createElement` and `append`.
- Move between related elements and find the right ancestor with `closest()`.

## Conceptual explanation

A page that reacts to people usually has to add things the HTML file did not contain: a new to-do item, a search result, an error message. The plan is always the same: **create** an element, **fill** it (text, classes, attributes), then **insert** it into the tree. Nothing appears until step three.

## Function deep dives: `createElement()`, `append()`, `remove()`

**`document.createElement(tagName)`** takes a tag name such as `"li"` and returns a **new element that is not yet part of the page**. It has no parent and is invisible until inserted.

**`parent.append(...nodesOrStrings)`** inserts one or more nodes (or plain strings, which become text nodes) as the **last children** of `parent`. It returns `undefined`. If a node already lives elsewhere in the page, `append` **moves** it rather than copying it. Siblings: `prepend` (as first children), `before` and `after` (next to an element), and `replaceWith`.

**`element.remove()`** removes the element from its parent. It returns `undefined`. The element object still exists as long as you hold a reference to it, so you can re-insert it later.

**`parent.replaceChildren(...nodes)`** removes all current children and inserts the new ones; with no arguments it **clears** the element, which is the standard first step of re-rendering a list.

**`element.cloneNode(deep)`** copies an element; pass `true` to include descendants. Event listeners are *not* copied.

```html file="index.html" page
<!DOCTYPE html>
<html lang="en">
  <body>
    <ul id="list"></ul>
    <script>
      const todos = [
        { id: 1, text: "Read", done: true },
        { id: 2, text: "Write", done: false },
        { id: 3, text: "Test", done: false },
      ];

      const list = document.getElementById("list");

      function renderTodos(items) {
        list.replaceChildren();
        for (const todo of items) {
          const li = document.createElement("li");
          li.textContent = todo.text;
          li.dataset.id = todo.id;
          if (todo.done) {
            li.classList.add("done");
          }
          list.append(li);
        }
      }

      renderTodos(todos);
      console.log(list.children.length, list.firstElementChild.className);
      console.log(list.innerHTML);

      list.children[1].remove();
      console.log(list.children.length);

      renderTodos(todos.filter((t) => !t.done));
      console.log(list.textContent);
    </script>
  </body>
</html>
```

```output
3 done
<li data-id="1" class="done">Read</li><li data-id="2">Write</li><li data-id="3">Test</li>
2
WriteTest
```

**Line by line.** `renderTodos` is the key pattern: it takes **data** (an array) and makes the page match it. Line 15 clears the list first so that calling it again does not duplicate items. Lines 17 to 22 create one `<li>` per todo: `textContent` for the text (safe), `dataset.id` to remember which todo it belongs to, a CSS class for completed items. Line 23 inserts it. After the first call (line 27) the list has three items and the first has the class `done`. Line 31 removes the second `<li>` directly from the page (the `todos` array is untouched, which is why the data and the page can drift apart). Line 34 re-renders from only the unfinished todos (`Write` and `Test`). Reading `textContent` of the list joins the text of the two items with no separator, so it prints `WriteTest`.

| Step | Operation | List now shows | `todos` array |
|---|---|---|---|
| 1 | `renderTodos(todos)` | Read, Write, Test | 3 items |
| 2 | `children[1].remove()` | Read, Test | 3 items (unchanged) |
| 3 | `renderTodos(todos.filter(...))` | Write, Test | 3 items (filter made a new array) |

::: concept The render function pattern
Keep your data in a variable, and write a function that makes the DOM match the data. When anything changes, update the data and call the function again. This one idea, "the page is a function of the data", is what React automates for you. Sections 9 and 10 build on it.
:::

## Navigating: `closest()`, parents and siblings

`element.closest(selector)` starts at the element and walks **up** the tree, returning the first ancestor (or the element itself) that matches the selector, or `null`. It is what you use inside an event handler to answer "which card was this button in?".

```html file="index.html" page
<!DOCTYPE html>
<html lang="en">
  <body>
    <div class="card" data-id="7">
      <h2>Title</h2>
      <button class="del">Delete</button>
    </div>
    <script>
      const button = document.querySelector(".del");
      const card = button.closest(".card");
      console.log(card.dataset.id, button.parentElement === card);
      console.log(button.previousElementSibling.tagName, button.nextElementSibling);
      console.log(button.closest(".nothing"));
    </script>
  </body>
</html>
```

```output
7 true
H2 null
null
```

The button's parent is the card, and `closest(".card")` finds the same element. The button's previous sibling is the `<h2>`; it has no next sibling element, so `nextElementSibling` is `null`. `closest` with a selector that matches no ancestor returns `null`.

## Common mistakes in this section

#### Mistake 1: Creating an element and forgetting to insert it

**Why it is wrong.** An element that is not in the tree is not on the page.

```html file="index.html" bad page
<!DOCTYPE html>
<html lang="en">
  <body>
    <ul id="list"></ul>
    <script>
      const li = document.createElement("li");
      li.textContent = "New item";
      console.log(document.getElementById("list").children.length);
    </script>
  </body>
</html>
```

```output
0
```

**Symptom.** No error, nothing appears. **Diagnosis:** count the children of the parent, or look in the Elements panel; add `list.append(li)`.

#### Mistake 2: Re-rendering without clearing

**Why it is wrong.** Appending the whole list again adds a second copy of every item.

```html file="index.html" bad page
<!DOCTYPE html>
<html lang="en">
  <body>
    <ul id="list"></ul>
    <script>
      const list = document.getElementById("list");
      function render(items) {
        for (const text of items) {
          const li = document.createElement("li");
          li.textContent = text;
          list.append(li);
        }
      }
      render(["a", "b"]);
      render(["a", "b"]);
      console.log(list.children.length);
    </script>
  </body>
</html>
```

```output
4
```

```html file="index.html" good page
<!DOCTYPE html>
<html lang="en">
  <body>
    <ul id="list"></ul>
    <script>
      const list = document.getElementById("list");
      function render(items) {
        list.replaceChildren();
        for (const text of items) {
          const li = document.createElement("li");
          li.textContent = text;
          list.append(li);
        }
      }
      render(["a", "b"]);
      render(["a", "b"]);
      console.log(list.children.length);
    </script>
  </body>
</html>
```

```output
2
```

**Symptom.** Duplicated items after every change. **Diagnosis:** a growing child count tells you the render function adds without clearing.

#### Mistake 3: Using `innerHTML +=` to add one item

**Why it is wrong.** `innerHTML +=` re-parses **every** existing child into brand-new elements, so any references you held to the old elements (and any event listeners attached to them) are lost.

```html file="index.html" bad page
<!DOCTYPE html>
<html lang="en">
  <body>
    <ul id="list"><li id="first">One</li></ul>
    <script>
      const first = document.getElementById("first");
      const list = document.getElementById("list");
      list.innerHTML += "<li>Two</li>";
      console.log(first.isConnected, list.children.length);
    </script>
  </body>
</html>
```

```output
false 2
```

**Symptom.** The reference `first` is now "disconnected" (no longer in the page) and listeners attached to the original elements stop working, though the screen looks right. **Fix:** `list.append(newElement)`, or `insertAdjacentElement`. **Diagnosis:** check `element.isConnected`.

#### Mistake 4: Expecting `append` to copy an element

**Why it is wrong.** An element can only be in one place, so `append` **moves** an element that is already in the page.

```html file="index.html" bad page
<!DOCTYPE html>
<html lang="en">
  <body>
    <ul id="a"><li>Item</li></ul>
    <ul id="b"></ul>
    <script>
      const item = document.querySelector("#a li");
      document.getElementById("b").append(item);
      console.log(document.getElementById("a").children.length);
      console.log(document.getElementById("b").children.length);
    </script>
  </body>
</html>
```

```output
0
1
```

```html file="index.html" good page
<!DOCTYPE html>
<html lang="en">
  <body>
    <ul id="a"><li>Item</li></ul>
    <ul id="b"></ul>
    <script>
      const item = document.querySelector("#a li");
      document.getElementById("b").append(item.cloneNode(true));
      console.log(document.getElementById("a").children.length);
      console.log(document.getElementById("b").children.length);
    </script>
  </body>
</html>
```

```output
1
1
```

**Symptom.** The item disappears from its original place. **Diagnosis:** use `cloneNode(true)` when you want a copy.
