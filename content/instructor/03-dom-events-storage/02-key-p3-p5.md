## Project 3: Kanban board

```js file="kanban-logic.js" bundle=p3
export function createBoard() {
  return {
    nextId: 1,
    columns: [
      { id: "todo", title: "To do", cardIds: [] },
      { id: "doing", title: "Doing", cardIds: [] },
      { id: "done", title: "Done", cardIds: [] },
    ],
    cards: {},
  };
}

export function addCard(board, columnId, text) {
  const clean = text.trim();
  if (clean === "" || !board.columns.some((c) => c.id === columnId)) {
    return board;
  }
  const id = String(board.nextId);
  return {
    ...board,
    nextId: board.nextId + 1,
    cards: { ...board.cards, [id]: { id, text: clean } },
    columns: board.columns.map((c) =>
      c.id === columnId ? { ...c, cardIds: [...c.cardIds, id] } : c
    ),
  };
}

export function moveCard(board, cardId, direction) {
  const from = board.columns.findIndex((c) => c.cardIds.includes(cardId));
  const to = from + direction;
  if (from === -1 || to < 0 || to >= board.columns.length) {
    return board;
  }
  return {
    ...board,
    columns: board.columns.map((c, i) => {
      if (i === from) return { ...c, cardIds: c.cardIds.filter((id) => id !== cardId) };
      if (i === to) return { ...c, cardIds: [...c.cardIds, cardId] };
      return c;
    }),
  };
}

export function editCard(board, cardId, text) {
  const clean = text.trim();
  if (clean === "" || !board.cards[cardId]) {
    return board;
  }
  return { ...board, cards: { ...board.cards, [cardId]: { id: cardId, text: clean } } };
}

export function deleteCard(board, cardId) {
  if (!board.cards[cardId]) {
    return board;
  }
  const cards = { ...board.cards };
  delete cards[cardId];
  return {
    ...board,
    cards,
    columns: board.columns.map((c) =>
      c.cardIds.includes(cardId)
        ? { ...c, cardIds: c.cardIds.filter((id) => id !== cardId) }
        : c
    ),
  };
}
```

```js file="test-kanban.mjs" run bundle=p3
import {
  createBoard, addCard, moveCard, editCard, deleteCard,
} from "./kanban-logic.js";

function deepFreeze(value) {
  for (const inner of Object.values(value)) {
    if (typeof inner === "object" && inner !== null) deepFreeze(inner);
  }
  return Object.freeze(value);
}

const start = deepFreeze(createBoard());
const sizes = (b) => b.columns.map((c) => c.cardIds.length).join("/");

const one = addCard(start, "todo", "  Write report ");
console.log(sizes(one), one.cards["1"].text, addCard(one, "todo", "   ") === one);
console.log(moveCard(one, "1", -1) === one, sizes(moveCard(one, "1", 1)));
const moved = moveCard(moveCard(one, "1", 1), "1", 1);
console.log(sizes(moved), moveCard(moved, "1", 1) === moved);
const step = moveCard(one, "1", 1);
console.log(step.columns[2] === one.columns[2], step.columns[0] === one.columns[0]);
const edited = editCard(one, "1", "Ship it");
console.log(edited.cards["1"].text, editCard(one, "1", " ") === one);
const gone = deleteCard(moved, "1");
const left = Object.keys(gone.cards).length;
console.log(sizes(gone), left, deleteCard(gone, "1") === gone);
```

```output
1/0/0 Write report true
true 0/1/0
0/0/1 true
true false
Ship it true
0/0/0 0 true
```

```html file="index.html" bundle=p3 page steps="fill #text Write report | click #add | fill #text Review | click #add | eval heads() | click section:nth-of-type(1) li button[data-action=right] | eval heads() | click section:nth-of-type(2) button[data-action=right] | eval heads() | eval String(document.querySelector('section:nth-of-type(3) button[data-action=right]').disabled) | click section:nth-of-type(3) button[data-action=delete] | eval heads() | reload | eval heads()"
<!DOCTYPE html>
<html lang="en">
  <body>
    <form id="form">
      <input id="text" />
      <select id="column"></select>
      <button id="add">Add</button>
    </form>
    <div id="board"></div>
    <script type="module">
      import { createBoard, addCard, moveCard, deleteCard } from "./kanban-logic.js";

      const KEY = "kanban-v1";

      function load() {
        try {
          const data = JSON.parse(localStorage.getItem(KEY));
          const ok = data && Array.isArray(data.columns) && data.cards;
          return ok ? data : createBoard();
        } catch (error) {
          return createBoard();
        }
      }

      let board = load();

      function update(next) {
        board = next;
        localStorage.setItem(KEY, JSON.stringify(board));
        render();
      }

      function makeButton(label, action, disabled) {
        const button = document.createElement("button");
        button.textContent = label;
        button.dataset.action = action;
        button.disabled = disabled;
        return button;
      }

      function render() {
        const root = document.getElementById("board");
        root.replaceChildren();
        board.columns.forEach((column, index) => {
          const section = document.createElement("section");
          const heading = document.createElement("h2");
          heading.textContent = `${column.title} (${column.cardIds.length})`;
          const list = document.createElement("ul");
          for (const id of column.cardIds) {
            const card = board.cards[id];
            if (!card) continue;
            const li = document.createElement("li");
            li.dataset.cardId = id;
            const label = document.createElement("span");
            label.textContent = card.text;
            li.append(
              label, " ",
              makeButton("<", "left", index === 0),
              makeButton(">", "right", index === board.columns.length - 1),
              makeButton("x", "delete", false)
            );
            list.append(li);
          }
          section.append(heading, list);
          root.append(section);
        });
      }

      const select = document.getElementById("column");
      for (const column of board.columns) {
        const option = document.createElement("option");
        option.value = column.id;
        option.textContent = column.title;
        select.append(option);
      }

      document.getElementById("form").addEventListener("submit", (event) => {
        event.preventDefault();
        const input = document.getElementById("text");
        update(addCard(board, select.value, input.value));
        input.value = "";
      });

      document.getElementById("board").addEventListener("click", (event) => {
        const button = event.target.closest("button[data-action]");
        if (!button) return;
        const id = button.closest("li").dataset.cardId;
        const action = button.dataset.action;
        if (action === "delete") update(deleteCard(board, id));
        else update(moveCard(board, id, action === "right" ? 1 : -1));
      });

      window.heads = () => {
        const titles = [...document.querySelectorAll("section h2")];
        return JSON.stringify(titles.map((h) => h.textContent));
      };
      render();
    </script>
  </body>
</html>
```

```output
["To do (2)","Doing (0)","Done (0)"]
["To do (1)","Doing (1)","Done (0)"]
["To do (1)","Doing (0)","Done (1)"]
true
["To do (1)","Doing (0)","Done (0)"]
["To do (1)","Doing (0)","Done (0)"]
```

In the logic test, every call receives a **deeply frozen** board, so any mutation would throw. The page output lists the column headings after: adding two cards, moving the first card right, moving it right again, then checking that "move right" is disabled in the last column, deleting that card, and reloading (the saved board is restored). Every control works for cards that did not exist at page load because there is **one delegated listener** on the board.

## Project 4: Bookmark manager

```js file="bookmarks-logic.js" bundle=p4
export function parseTags(text) {
  const tags = text
    .split(",")
    .map((t) => t.trim().toLowerCase())
    .filter((t) => t !== "");
  return [...new Set(tags)];
}

export function normalizeUrl(text) {
  try {
    const url = new URL(text.trim());
    if (url.protocol !== "http:" && url.protocol !== "https:") {
      return null;
    }
    return url.href.replace(/\/$/, "");
  } catch (error) {
    return null;
  }
}

export function validateBookmark(list, data) {
  const errors = [];
  if (data.title.trim() === "") {
    errors.push("Title is required");
  }
  const url = normalizeUrl(data.url);
  if (url === null) {
    errors.push("URL must start with http:// or https://");
  } else if (list.some((b) => b.url === url)) {
    errors.push("That address is already saved");
  }
  return errors;
}

export function addBookmark(list, data) {
  const errors = validateBookmark(list, data);
  if (errors.length > 0) {
    throw new Error(errors.join("; "));
  }
  const id = Math.max(0, ...list.map((b) => b.id)) + 1;
  const bookmark = {
    id,
    title: data.title.trim(),
    url: normalizeUrl(data.url),
    tags: parseTags(data.tags ?? ""),
  };
  return [...list, bookmark];
}

export const removeBookmark = (list, id) => list.filter((b) => b.id !== id);
export const hostOf = (url) => new URL(url).hostname;
export const allTags = (list) => [...new Set(list.flatMap((b) => b.tags))].sort();

export function search(list, text, tag) {
  const needle = text.trim().toLowerCase();
  return list.filter((b) => {
    const textMatch =
      needle === "" ||
      b.title.toLowerCase().includes(needle) ||
      hostOf(b.url).includes(needle);
    return textMatch && (!tag || b.tags.includes(tag));
  });
}
```

```js file="test-bookmarks.mjs" run bundle=p4
import {
  parseTags, normalizeUrl, validateBookmark, addBookmark, search, allTags,
} from "./bookmarks-logic.js";

console.log(parseTags("A, a, , b").join("|"), parseTags(",").length);
console.log(normalizeUrl("HTTPS://Example.com/"), normalizeUrl("http://a.com/x/"));
const bads = ["javascript:alert(1)", "data:text/html,x", "/relative", "not a url"];
for (const bad of bads) {
  console.log(normalizeUrl(bad));
}

const list = Object.freeze([]);
const mdn = { title: "MDN", url: "https://developer.mozilla.org/", tags: "docs, js" };
const one = addBookmark(list, mdn);
console.log(one[0].url, one[0].tags.join(), list.length);
const dup = { title: " ", url: "HTTPS://Developer.Mozilla.org" };
console.log(validateBookmark(one, dup).join("; "));

const ex = { title: "Example", url: "https://example.com/a", tags: "js" };
const two = addBookmark(one, ex);
const count = (text, tag) => search(two, text, tag).length;
console.log(count("mdn", ""), count("", "docs"), count("", "js"));
console.log(count("example", "docs"), allTags(two).join());
```

```output
a|b 0
https://example.com http://a.com/x
null
null
null
null
https://developer.mozilla.org docs,js 0
Title is required; That address is already saved
1 1 2
0 docs,js
```

```html file="index.html" bundle=p4 page steps="fill #title MDN | fill #url https://developer.mozilla.org/ | fill #tags docs, js | click #add | fill #title x | fill #url javascript:alert(1) | click #add | print #errors | fill #title MDN again | fill #url HTTPS://Developer.Mozilla.org | click #add | print #errors | fill #title Example | fill #url https://example.com/a | fill #tags js | click #add | eval count() | fill #search mdn | eval count() | fill #search | select #tagfilter docs | eval count() | select #tagfilter js | eval count() | select #tagfilter | fill #title <b>bold</b> | fill #url https://xss.test/ | fill #tags | click #add | eval String(document.querySelectorAll('b').length) | eval document.querySelector('a').rel | reload | eval count()"
<!DOCTYPE html>
<html lang="en">
  <body>
    <form id="form">
      <input id="title" placeholder="Title" />
      <input id="url" placeholder="URL" />
      <input id="tags" placeholder="tags, separated, by commas" />
      <button id="add">Save</button>
    </form>
    <p id="errors"></p>
    <input id="search" placeholder="Search" />
    <select id="tagfilter"></select>
    <ul id="list"></ul>
    <script type="module">
      import {
        addBookmark, removeBookmark, search, allTags, hostOf, normalizeUrl,
      } from "./bookmarks-logic.js";

      const KEY = "bookmarks-v1";

      function load() {
        try {
          const data = JSON.parse(localStorage.getItem(KEY));
          if (!Array.isArray(data)) return [];
          const valid = (b) => b && typeof b.title === "string" && normalizeUrl(b.url);
          return data.filter(valid);
        } catch (error) {
          return [];
        }
      }

      let bookmarks = load();
      const $ = (id) => document.getElementById(id);

      function renderTagFilter() {
        const current = $("tagfilter").value;
        $("tagfilter").replaceChildren(new Option("All tags", ""));
        for (const tag of allTags(bookmarks)) {
          $("tagfilter").append(new Option(tag, tag));
        }
        $("tagfilter").value = allTags(bookmarks).includes(current) ? current : "";
      }

      function render() {
        const items = search(bookmarks, $("search").value, $("tagfilter").value);
        $("list").replaceChildren();
        if (items.length === 0) {
          const li = document.createElement("li");
          li.textContent = "No bookmarks to show.";
          $("list").append(li);
          li.dataset.empty = "true";
        }
        for (const b of items) {
          const li = document.createElement("li");
          li.dataset.id = b.id;
          const a = document.createElement("a");
          a.href = normalizeUrl(b.url);
          a.target = "_blank";
          a.rel = "noopener noreferrer";
          a.textContent = b.title;
          const host = document.createElement("small");
          host.textContent = ` ${hostOf(b.url)} [${b.tags.join(", ")}] `;
          const del = document.createElement("button");
          del.textContent = "Delete";
          del.dataset.action = "delete";
          li.append(a, host, del);
          $("list").append(li);
        }
      }

      function save(next) {
        bookmarks = next;
        localStorage.setItem(KEY, JSON.stringify(bookmarks));
        renderTagFilter();
        render();
      }

      $("form").addEventListener("submit", (event) => {
        event.preventDefault();
        try {
          save(addBookmark(bookmarks, {
            title: $("title").value, url: $("url").value, tags: $("tags").value,
          }));
          $("errors").textContent = "";
          $("form").reset();
        } catch (error) {
          $("errors").textContent = error.message;
        }
      });

      $("search").addEventListener("input", render);
      $("tagfilter").addEventListener("change", render);
      $("list").addEventListener("click", (event) => {
        const button = event.target.closest("button[data-action=delete]");
        if (button) {
          const id = Number(button.closest("li").dataset.id);
          save(removeBookmark(bookmarks, id));
        }
      });

      window.count = () =>
        String(document.querySelectorAll("#list li:not([data-empty])").length);
      renderTagFilter();
      render();
    </script>
  </body>
</html>
```

```output
URL must start with http:// or https://
That address is already saved
2
1
1
2
0
noopener noreferrer
3
```

In order, the page output shows: the validation message for a `javascript:` address; the duplicate message when the same address is entered with different capitalisation; the bookmark count after the second save (2); after searching `mdn` (1); with tag filter `docs` (1) and `js` (2); after saving a bookmark titled `<b>bold</b>` there are zero `<b>` elements (the title is text) and the link's `rel` attribute; and the count after a reload (3, restored from storage). Links are only given an `href` after `normalizeUrl` has accepted the address.

## Project 5: Markdown editor with live preview

```js file="markdown-logic.js" bundle=p5
export function parseInline(text) {
  const nodes = [];
  let buffer = "";
  let i = 0;
  const flush = () => {
    if (buffer !== "") {
      nodes.push({ type: "text", value: buffer });
      buffer = "";
    }
  };

  while (i < text.length) {
    if (text.startsWith("**", i)) {
      const end = text.indexOf("**", i + 2);
      if (end !== -1) {
        flush();
        nodes.push({ type: "strong", children: parseInline(text.slice(i + 2, end)) });
        i = end + 2;
        continue;
      }
      buffer += "**";
      i += 2;
      continue;
    }
    if (text[i] === "`") {
      const end = text.indexOf("`", i + 1);
      if (end !== -1) {
        flush();
        nodes.push({ type: "code", value: text.slice(i + 1, end) });
        i = end + 1;
        continue;
      }
    }
    if (text[i] === "*" && text[i + 1] !== "*") {
      const end = text.indexOf("*", i + 1);
      if (end !== -1) {
        flush();
        nodes.push({ type: "em", children: parseInline(text.slice(i + 1, end)) });
        i = end + 1;
        continue;
      }
    }
    if (text[i] === "[") {
      const mid = text.indexOf("](", i);
      let close = -1;
      if (mid !== -1) {
        let depth = 1;
        let j = mid + 2;
        while (j < text.length && depth > 0) {
          if (text[j] === "(") depth++;
          else if (text[j] === ")") depth--;
          j++;
        }
        close = depth === 0 ? j - 1 : -1;
      }
      if (mid !== -1 && close !== -1) {
        flush();
        const href = text.slice(mid + 2, close);
        const children = parseInline(text.slice(i + 1, mid));
        nodes.push({ type: "link", href, children });
        i = close + 1;
        continue;
      }
    }
    buffer += text[i];
    i++;
  }
  flush();
  return nodes;
}

export function parseMarkdown(text) {
  const blocks = [];
  let paragraph = [];
  let list = null;
  const flushParagraph = () => {
    if (paragraph.length > 0) {
      blocks.push({ type: "paragraph", children: parseInline(paragraph.join(" ")) });
      paragraph = [];
    }
  };
  const flushList = () => {
    if (list) {
      blocks.push(list);
      list = null;
    }
  };

  for (const line of text.split("\n")) {
    const heading = line.match(/^(#{1,3}) (.+)$/);
    const bullet = line.match(/^- (.+)$/);
    const numbered = line.match(/^\d+\. (.+)$/);
    if (heading) {
      flushParagraph();
      flushList();
      const children = parseInline(heading[2]);
      blocks.push({ type: "heading", level: heading[1].length, children });
    } else if (bullet || numbered) {
      flushParagraph();
      const ordered = Boolean(numbered);
      if (!list || list.ordered !== ordered) {
        flushList();
        list = { type: "list", ordered, items: [] };
      }
      list.items.push(parseInline((bullet ?? numbered)[1]));
    } else if (line.trim() === "") {
      flushParagraph();
      flushList();
    } else {
      flushList();
      paragraph.push(line.trim());
    }
  }
  flushParagraph();
  flushList();
  return blocks;
}

export function safeUrl(text) {
  try {
    const url = new URL(text);
    return url.protocol === "http:" || url.protocol === "https:" ? url.href : null;
  } catch (error) {
    return null;
  }
}

export function debounce(fn, delay) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}
```

```js file="test-markdown.mjs" run bundle=p5
import { parseMarkdown, parseInline, safeUrl } from "./markdown-logic.js";

function show(nodes) {
  return nodes
    .map((n) => {
      if (n.type === "text") return JSON.stringify(n.value);
      if (n.type === "code") return `code(${JSON.stringify(n.value)})`;
      const label = n.type === "link" ? `link[${n.href}]` : n.type;
      return `${label}(${show(n.children)})`;
    })
    .join(" ");
}

console.log(JSON.stringify(parseMarkdown("# Hi")));
console.log(show(parseInline("**b** *i* `c`")));
console.log(show(parseMarkdown("<script>x</script>")[0].children));
const doc = parseMarkdown("- a\n- b\n\n1. one");
const kinds = doc.map((b) => b.type + (b.ordered ? ":ol" : ""));
console.log(kinds);
console.log(parseMarkdown("").length, parseMarkdown("\n\n").length);
console.log(parseMarkdown("#nospace")[0].type);
console.log(show(parseInline("**unclosed and `tick")));
console.log(show(parseInline("[x](javascript:alert(1)) end")));
console.log(safeUrl("javascript:alert(1)"), safeUrl("https://a.com"));
```

```output
[{"type":"heading","level":1,"children":[{"type":"text","value":"Hi"}]}]
strong("b") " " em("i") " " code("c")
"<script>x</script>"
[ 'list', 'list:ol' ]
0 0
paragraph
"**unclosed and `tick"
link[javascript:alert(1)]("x") " end"
null https://a.com/
```

```html file="index.html" bundle=p5 page steps="eval (src.value = '# Title\n\n**bold** and *it* and `code`\n\n- a\n- b\n\n1. one\n2. two\n\n[MDN](https://developer.mozilla.org/) and [bad](javascript:alert(1))', src.dispatchEvent(new Event('input')), 'typed') | wait 400 | eval Array.from(preview.children).map((e) => e.tagName).join(' ') | eval preview.querySelector('p').innerHTML | eval String(preview.querySelectorAll('a').length) | eval preview.lastElementChild.textContent | eval (src.value = '<script>alert(1)</script> <img src=x onerror=alert(1)>', src.dispatchEvent(new Event('input')), 'typed hostile') | wait 400 | eval String(preview.querySelectorAll('script, img').length) | eval preview.textContent | eval (() => { window.renderCount = 0; for (let i = 0; i < 20; i++) { src.value = 'x' + i; src.dispatchEvent(new Event('input')); } return 'burst'; })() | wait 400 | eval String(window.renderCount) | reload | wait 100 | eval preview.textContent"
<!DOCTYPE html>
<html lang="en">
  <body>
    <textarea id="src" rows="8" cols="60"></textarea>
    <div id="preview"></div>
    <p id="counts"></p>
    <script type="module">
      import { parseMarkdown, safeUrl, debounce } from "./markdown-logic.js";

      const src = document.getElementById("src");
      const preview = document.getElementById("preview");
      window.renderCount = 0;

      function inline(nodes) {
        return nodes.flatMap((node) => {
          if (node.type === "text") return [node.value];
          const tag = { strong: "strong", em: "em", code: "code" }[node.type];
          if (node.type === "code") {
            const el = document.createElement("code");
            el.textContent = node.value;
            return [el];
          }
          if (node.type === "link") {
            const href = safeUrl(node.href);
            if (!href) return inline(node.children);
            const a = document.createElement("a");
            a.href = href;
            a.target = "_blank";
            a.rel = "noopener noreferrer";
            a.append(...inline(node.children));
            return [a];
          }
          const el = document.createElement(tag);
          el.append(...inline(node.children));
          return [el];
        });
      }

      function toDom(blocks) {
        return blocks.map((block) => {
          if (block.type === "heading") {
            const h = document.createElement("h" + block.level);
            h.append(...inline(block.children));
            return h;
          }
          if (block.type === "list") {
            const list = document.createElement(block.ordered ? "ol" : "ul");
            for (const item of block.items) {
              const li = document.createElement("li");
              li.append(...inline(item));
              list.append(li);
            }
            return list;
          }
          const p = document.createElement("p");
          p.append(...inline(block.children));
          return p;
        });
      }

      function render() {
        window.renderCount++;
        preview.replaceChildren(...toDom(parseMarkdown(src.value)));
        const text = src.value.trim();
        const words = text === "" ? 0 : text.split(/\s+/).length;
        document.getElementById("counts").textContent =
          `${words} words, ${src.value.length} characters`;
      }

      const renderLater = debounce(() => {
        render();
        try {
          localStorage.setItem("draft-v1", src.value);
        } catch (error) {
          /* storage unavailable */
        }
      }, 200);

      src.addEventListener("input", renderLater);
      try {
        src.value = localStorage.getItem("draft-v1") ?? "";
      } catch (error) {
        src.value = "";
      }
      render();
      window.renderCount = 0;
    </script>
  </body>
</html>
```

```output
typed
H1 P UL OL P
<strong>bold</strong> and <em>it</em> and <code>code</code>
1
MDN and bad
typed hostile
0
<script>alert(1)</script> <img src=x onerror=alert(1)>
burst
1
x19
```

The page output lists, in order: the preview's HTML for a document using every supported construct (the `javascript:` link has become plain text and only the safe link is an `<a>`); the number of `script` or `img` elements created from hostile input (zero) and the literal text shown instead; how many times `render` ran for a burst of twenty rapid edits (once, thanks to the debounce); and the restored draft after a reload. No part of the page uses `innerHTML` to build content (the test only *reads* `innerHTML` to show the result). A known limit of this small parser: `**bold *and italic***` leaves a stray `*`; accept this, and discuss how a real parser would handle nesting.

# 8. Self-Assessment Answers

1. `m.children.length` is `2`, `m.firstElementChild.textContent` is `A`, `m.parentElement.tagName` is `BODY`.
2. A classic script in `<head>` runs while the parser is still in the head, so the body does not exist yet. Use `defer`, `type="module"`, or place the script at the end of `<body>`.
3. `querySelector` returns `null`; `querySelectorAll` returns an empty `NodeList`.
4. `NodeList` is not an array. Convert with `[...list]` or `Array.from(list)`.
5. After `textContent`, `children.length` is `0` (the tags are literal text). After `innerHTML`, it is `1`.
6. `background-color` is parsed as subtraction. Use `style.backgroundColor` or toggle a class.
7. Create, fill, insert (`append`). Clear a list with `replaceChildren()`.
8. It re-parses and replaces every existing child, which discards references and listeners held by the old elements.
9. `target` is the innermost element where the event started; `currentTarget` is the element the listener belongs to.
10. `input` fires on every edit; `change` fires when a value is committed (for text inputs, when focus leaves).
11. Bubble listeners run from the target upward: inner first, then outer. `true` registers the listener for the capture phase, so it runs first on the way down.
12. The listener is on the parent, which exists before and after children are added, and events bubble up to it.
13. It cancels the form submission and page reload; without it the page reloads and in-memory state is lost.
14. Form values are strings. Unchecked checkboxes are not submitted, so they are absent from the data.
15. A user can disable or bypass the browser checks, or send requests directly.
16. `null`. `true` is stored as the string `"true"`.
17. `undefined` and functions are dropped from objects (and become `null` in arrays); a `Date` becomes an ISO string. Invalid text makes `JSON.parse` throw a `SyntaxError`.
18. `store.js` (pure data functions) can be tested in Node; `ui.js` needs `document`.
19. It parses markup, so stored text containing event attributes runs script on every load. Use `textContent` or `createElement`.
20. A `javascript:` URL runs script when clicked. Parse with `new URL()` and allow only `http:` and `https:`.
