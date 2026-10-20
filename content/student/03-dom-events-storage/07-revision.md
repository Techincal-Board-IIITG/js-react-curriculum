# 14. Revision and Assessment

## Summary of this sheet

The browser turns HTML into the **DOM**, a tree of node objects reachable through `document`. Select elements with `getElementById`, `querySelector` (first match or `null`) and `querySelectorAll` (static `NodeList`, convert with spread for array methods). Change content with `textContent` (safe) rather than `innerHTML` (parses markup), change state with properties (`value`, `checked`, `disabled`), appearance with `classList`, and read data attributes through `dataset`. Add elements by **creating, filling, then inserting** them (`createElement`, `append`), clear with `replaceChildren()`, remove with `remove()`, and find ancestors with `closest()`. Events are callbacks registered with `addEventListener`; the event object carries `target`, `currentTarget`, `key` and `preventDefault()`. Events travel through capture, target and bubble phases, which makes **delegation** possible: one listener on a parent handles current and future children. Forms: handle `submit`, call `preventDefault()`, read with `FormData` (all strings, unchecked boxes missing), validate with built-in attributes and your own pure `validate` function, and always validate again on the server. `localStorage` and `sessionStorage` hold **strings** per origin; use `JSON.stringify` and `JSON.parse` wrapped in safe helpers with fallbacks. Organise code into data logic (pure, testable in Node), storage, interface (`render`) and wiring. Never insert untrusted data with `innerHTML`, never trust `href` values without checking the scheme, and never keep secrets in the browser.

## Key syntax reference

[[widths 1.3 3.4 2.2]]
| Topic | Syntax | Notes |
|---|---|---|
| Select | `getElementById("id")`, `querySelector(css)`, `querySelectorAll(css)` | `null` or empty list when nothing matches |
| Text and HTML | `el.textContent = s`, `el.innerHTML = html` | Prefer `textContent` |
| Attributes | `el.setAttribute(n, v)`, `getAttribute(n)`, `el.dataset.userId` | `dataset` values are strings |
| Classes and style | `el.classList.add/remove/toggle/contains`, `el.style.backgroundColor` | Prefer classes |
| Create and insert | `document.createElement("li")`, `parent.append(el)`, `el.remove()` | `append` moves existing nodes |
| Clear | `parent.replaceChildren()` | First step of re-rendering |
| Navigate | `el.parentElement`, `el.children`, `el.closest(css)` | `closest` goes up |
| Listen | `el.addEventListener("click", fn, { once: true })` | Remove with the same function object |
| Event object | `e.target`, `e.currentTarget`, `e.key`, `e.preventDefault()` | `target` is the innermost element |
| Form data | `Object.fromEntries(new FormData(form))` | Values are strings |
| Validation | `input.checkValidity()`, `input.validity.valueMissing`, `setCustomValidity(msg)` | Not a security measure |
| Storage | `localStorage.setItem(k, v)`, `getItem(k)` (string or `null`), `removeItem(k)` | Strings only; per origin |
| JSON | `JSON.stringify(v)`, `JSON.parse(text)` | `parse` throws on bad text |
| URLs | `new URL(text).protocol` | Allow only `http:` and `https:` |

## Important terms and definitions

[[widths 1.2 4]]
| Term | Definition |
|---|---|
| DOM | The browser's in-memory tree of objects built from the HTML |
| Node / element | Any item in the tree / an item created by a tag |
| `NodeList` | An array-like collection returned by `querySelectorAll` (static) |
| Event | A signal that something happened (click, input, submit) |
| Listener / handler | A callback registered to run when an event reaches an element |
| Bubbling / capturing | Events travelling up / down the tree through ancestors |
| Delegation | Handling events for many elements with one listener on their ancestor |
| `preventDefault()` | Cancels the browser's built-in action for an event |
| Origin | Protocol, host and port; storage is separated by origin |
| JSON | A text format for data, used by storage and web APIs |
| XSS | Cross-site scripting: attacker's script running on your page |
| Sanitiser | A library that removes dangerous markup from HTML |
| Render function | A function that makes the DOM match the current data |

## Common mistakes checklist

- [ ] My script runs after the elements it selects exist (`defer`, `type="module"`, or at the end of `<body>`).
- [ ] I convert `NodeList` to an array before using `map`, `filter` or `reduce`.
- [ ] I never put untrusted text into `innerHTML`; I use `textContent` or `createElement`.
- [ ] Every `submit` handler calls `event.preventDefault()`.
- [ ] I pass handler functions without parentheses (`handle`, not `handle()`).
- [ ] I resolve clicked elements with `closest()` when delegating.
- [ ] Form values are converted with `Number` before arithmetic.
- [ ] Anything read from storage goes through safe parsing with a fallback.
- [ ] Every data change goes through one function that saves and re-renders.
- [ ] Listeners are registered once, never inside `render`.
- [ ] URLs from users are checked with an allow-list before use.
- [ ] No secrets in front-end code or browser storage.

## Self-assessment questions

1. For `<ul id="m"><li>A</li><li>B</li></ul>`, what are `m.children.length`, `m.firstElementChild.textContent`, and `m.parentElement.tagName` if the `<ul>` is the only child of `<body>`? (Section 2)
2. When does a `<script>` in `<head>` run relative to the page content, and how do you avoid the problem? (Section 2)
3. What does `document.querySelector(".x")` return if no element matches? What does `querySelectorAll`? (Section 3)
4. Why does `nodeList.map(...)` fail, and what are two fixes? (Section 3)
5. After `el.textContent = "<b>x</b>"`, what does `el.children.length` return? After `el.innerHTML = "<b>x</b>"`? (Section 4)
6. Why does `box.style.background-color = "red"` not work? (Section 4)
7. Write the three steps to add an `<li>` to a list. How do you clear a list before re-rendering? (Section 5)
8. What is wrong with `list.innerHTML += "<li>x</li>"` for adding one item? (Section 5)
9. What is the difference between `target` and `currentTarget`? (Section 6)
10. When does `change` fire compared with `input`? (Section 6)
11. Click a button inside nested `div`s with listeners on each. In which order do bubble listeners run? What does `true` as the third argument change? (Section 7)
12. Why does delegation work for elements created after the listener was added? (Section 7)
13. What does `preventDefault()` do on a form submit, and what happens if you forget it? (Sections 7, 8)
14. Why does `Object.fromEntries(new FormData(form))` give `{ age: "20" }` for a number field? Why is an unchecked checkbox missing? (Section 8)
15. Why can browser validation not protect a server? (Section 8)
16. What does `localStorage.getItem("missing")` return? What happens to `true` stored with `setItem`? (Section 9)
17. What does `JSON.stringify` do with `undefined`, functions, and `Date`s? What does `JSON.parse` do with invalid text? (Section 9)
18. Which of `store.js`, `ui.js` can be tested in Node, and why? (Section 10)
19. Why is `innerHTML` with stored user text dangerous? Name a safe alternative. (Section 11)
20. Why is `javascript:alert(1)` dangerous in an `href`, and how do you check a URL safely? (Section 11)

## Practical completion checklist

- [ ] I ran every worked example in a browser and compared the output with the output panels.
- [ ] I completed exercise sets A to D and at least one challenge from set E.
- [ ] I completed core projects 1, 2 and 3, and can explain every line aloud.
- [ ] My projects keep data logic in a separate module that I tested in Node.
- [ ] My projects survive an empty storage, a corrupted storage and a reload.
- [ ] I can find and read data in DevTools: Elements, Console and Application, Local Storage.
- [ ] I can explain XSS and show a safe way to display user text.
- [ ] (Optional) I completed one or both extension projects.

## Official documentation

- [MDN: Introduction to the DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction)
- [MDN: Document reference](https://developer.mozilla.org/en-US/docs/Web/API/Document)
- [MDN: Element reference](https://developer.mozilla.org/en-US/docs/Web/API/Element)
- [MDN: Introduction to events](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Building_blocks/Events)
- [MDN: EventTarget.addEventListener()](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener)
- [MDN: FormData](https://developer.mozilla.org/en-US/docs/Web/API/FormData)
- [MDN: Client-side form validation](https://developer.mozilla.org/en-US/docs/Learn/Forms/Form_validation)
- [MDN: Web Storage API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API)
- [MDN: JSON](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON)
- [MDN glossary: Cross-site scripting](https://developer.mozilla.org/en-US/docs/Glossary/Cross-site_scripting)
- [MDN: URL](https://developer.mozilla.org/en-US/docs/Web/API/URL)
