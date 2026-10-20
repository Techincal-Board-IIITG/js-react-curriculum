# 8. Forms and Validation

## Learning objectives for this section

- Read values from text inputs, checkboxes, selects and radio groups, remembering that they are strings.
- Handle the `submit` event correctly and collect values with `FormData`.
- Validate input with the built-in HTML rules, the constraint validation API, and your own functions.
- Show clear error messages and reset a form.

## Conceptual explanation

A form is the main way people give your page information. The browser provides a lot for free: Enter submits, `required` blocks empty fields, `type="email"` checks the shape of an address. Your job is to *intercept* the submission (so the page is not reloaded), read the values, check them properly, and respond.

Remember three facts from the start. First, **every value you read from a form is a string**, even for `type="number"` (Sheet 01's string-versus-number trap). Second, **validating in the browser is a courtesy to the user, not a security measure**: anyone can bypass it, so a real server must validate again. Third, use `<label>` elements so that fields have accessible names (Sheet 11 returns to this).

## Reading control values

[[widths 1.4 2.4 2.5]]
| Control | Read with | Value you get |
|---|---|---|
| Text, email, number, date, textarea | `input.value` | a **string** (empty string if blank) |
| Checkbox | `input.checked` | `true` or `false` |
| Radio group | `form.elements["group"].value` | the chosen option's value, or `""` |
| Select | `select.value` | the selected option's value (string) |
| Whole form | `new FormData(form)` | all named fields (see below) |

## Function deep dive: `FormData`

**What it is.** A built-in object that collects the current values of a form's **named** controls.

**Why it exists.** Reading ten fields one by one is repetitive and easy to get wrong. `FormData` reads everything in one call, and uses the same rules the browser uses when it really submits a form.

**Syntax and parameters.** `new FormData(formElement)`. The only parameter is the form element.

**Methods.** `get(name)` returns the first value for a name (or `null`); `getAll(name)` returns an array of all values for that name; `has(name)`; and the object is iterable, yielding `[name, value]` pairs. `Object.fromEntries(new FormData(form))` turns it into a plain object.

**How it works.** It walks the form's controls and records `(name, value)` for each control that has a `name` attribute, is not disabled, and (for checkboxes and radios) is **checked**. Controls without a `name` are ignored.

**Edge cases.** An **unchecked checkbox is simply missing** from the data. A checked checkbox without a `value` attribute gives the string `"on"`. If several controls share a name, `Object.fromEntries` keeps only the **last** one, so use `getAll` for those.

```html file="index.html" page steps="fill [name=name] Asha | fill [name=age] 20 | check [name=agree] | click #go"
<!DOCTYPE html>
<html lang="en">
  <body>
    <form id="signup">
      <label>Name <input name="name" /></label>
      <label>Age <input name="age" type="number" /></label>
      <label><input name="agree" type="checkbox" /> I agree</label>
      <button id="go">Join</button>
    </form>
    <script>
      const form = document.getElementById("signup");

      form.addEventListener("submit", (event) => {
        event.preventDefault();
        const data = Object.fromEntries(new FormData(form));
        console.log(JSON.stringify(data));
        console.log(typeof data.age, data.age + 1);
      });
    </script>
  </body>
</html>
```

```output
{"name":"Asha","age":"20","agree":"on"}
string 201
```

**Line by line.** The `submit` handler is registered on the **form** (not on the button), so it also runs when the user presses Enter in a field. Line 13 cancels the default page reload. Line 14 reads all fields into a plain object. The printed JSON demonstrates the rules above: `age` is the **string** `"20"` (so `data.age + 1` concatenates to `"201"`), and the checked checkbox became `"on"`. If the box were unchecked, the `agree` key would be absent altogether.

## Validation with built-in HTML rules

HTML provides attributes that the browser enforces *before* the `submit` event fires: `required`, `minlength`, `maxlength`, `min`, `max`, `pattern` (a regular expression), and the `type` itself (`email`, `url`, `number`). If a rule fails the browser shows its own message and **does not fire** `submit`.

The **constraint validation API** lets your code ask the same questions:

```html file="index.html" page
<!DOCTYPE html>
<html lang="en">
  <body>
    <form>
      <input id="email" type="email" required />
    </form>
    <script>
      const email = document.getElementById("email");
      console.log(email.checkValidity(), email.validity.valueMissing);

      email.value = "nope";
      console.log(email.validity.typeMismatch, email.checkValidity());

      email.value = "a@b.co";
      console.log(email.checkValidity());

      email.setCustomValidity("Not allowed");
      console.log(email.checkValidity(), email.validationMessage);
      email.setCustomValidity("");
    </script>
  </body>
</html>
```

```output
false true
true false
true
false Not allowed
```

`checkValidity()` returns `true` if the control satisfies all its rules. `validity` is an object of booleans naming the reason: `valueMissing`, `typeMismatch`, `patternMismatch`, `tooShort`, `rangeUnderflow` and others. `setCustomValidity(message)` marks the field invalid with **your** message (an empty string clears it again, which you must remember to do).

## Custom validation functions

Built-in rules cannot express "the end date must be after the start date" or friendly wording in your own language. The robust pattern, and the one React uses, is a **pure function** that takes the values and returns an object of error messages, separate from any DOM code.

```html file="index.html" page steps="fill [name=age] 15 | click #go | print #errors | fill [name=name] Asha | fill [name=age] 21 | click #go"
<!DOCTYPE html>
<html lang="en">
  <body>
    <form id="signup" novalidate>
      <label>Name <input name="name" /></label>
      <label>Age <input name="age" /></label>
      <button id="go">Join</button>
    </form>
    <ul id="errors"></ul>
    <script>
      function validate(values) {
        const errors = {};
        if (values.name.trim() === "") {
          errors.name = "Name is required";
        }
        const age = Number(values.age);
        if (values.age.trim() === "" || Number.isNaN(age)) {
          errors.age = "Age must be a number";
        } else if (age < 18) {
          errors.age = "You must be 18 or older";
        }
        return errors;
      }

      const form = document.getElementById("signup");
      const errorList = document.getElementById("errors");

      form.addEventListener("submit", (event) => {
        event.preventDefault();
        const values = Object.fromEntries(new FormData(form));
        const errors = validate(values);

        errorList.replaceChildren();
        for (const message of Object.values(errors)) {
          const li = document.createElement("li");
          li.textContent = message;
          errorList.append(li);
        }

        if (Object.keys(errors).length === 0) {
          console.log("valid:", values.name, Number(values.age));
          form.reset();
        }
      });
    </script>
  </body>
</html>
```

```output
Name is required / You must be 18 or older
valid: Asha 21
```

**How the pieces fit.** `validate` knows nothing about the page: it receives plain values and returns an object such as `{ name: "...", age: "..." }`, which makes it easy to test (you can paste it into Node and call it). The `novalidate` attribute on the form turns off the browser's own messages so that **your** messages are the only ones. The submit handler reads values, calls `validate`, **clears the old messages** (`replaceChildren`), renders the new ones with `textContent`, and proceeds only if the error object is empty. The first scripted submit has an empty name and age `15`, so both errors are shown. After the user fixes both fields, the second submit finds no errors, logs the cleaned values (converting the age with `Number`), and calls `form.reset()`, which restores every field to its initial value.

## Common mistakes in this section

#### Mistake 1: Doing arithmetic on form values without converting

**Why it is wrong.** Values are strings; `+` concatenates.

```html file="index.html" bad page steps="fill #a 2 | fill #b 3 | click #sum | print #out"
<!DOCTYPE html>
<html lang="en">
  <body>
    <input id="a" type="number" /> + <input id="b" type="number" />
    <button id="sum">Add</button>
    <p id="out"></p>
    <script>
      document.getElementById("sum").addEventListener("click", () => {
        const a = document.getElementById("a").value;
        const b = document.getElementById("b").value;
        document.getElementById("out").textContent = a + b;
      });
    </script>
  </body>
</html>
```

```output
23
```

**Symptom.** `2 + 3` shows `23`. **Fix:** `Number(a) + Number(b)` (or the input's `valueAsNumber` property), and check for `NaN` when the field is empty. **Diagnosis:** `typeof input.value` is always `"string"`.

#### Mistake 2: Expecting an unchecked checkbox in `FormData`

**Why it is wrong.** Unchecked controls are not submitted at all.

```html file="index.html" bad page steps="click #go"
<!DOCTYPE html>
<html lang="en">
  <body>
    <form id="f">
      <input name="agree" type="checkbox" />
      <button id="go">Go</button>
    </form>
    <script>
      const form = document.getElementById("f");
      form.addEventListener("submit", (event) => {
        event.preventDefault();
        const data = Object.fromEntries(new FormData(form));
        console.log(data.agree, data.agree === false);
        console.log(form.elements.agree.checked);
      });
    </script>
  </body>
</html>
```

```output
undefined false
false
```

**Symptom.** `data.agree` is `undefined`, not `false`, so code testing `=== false` never matches. **Fix:** read `form.elements.agree.checked` (always a boolean), or test `data.agree === "on"`.

#### Mistake 3: A label not connected to its input

**Why it is wrong.** An unassociated label is just text: clicking it does not focus the field, and assistive technology cannot name the field.

```html file="index.html" bad page steps="click #lbl | eval document.activeElement.tagName"
<!DOCTYPE html>
<html lang="en">
  <body>
    <span id="lbl">Email</span>
    <input id="email" />
  </body>
</html>
```

```output
BODY
```

```html file="index.html" good page steps="click #lbl | eval document.activeElement.tagName"
<!DOCTYPE html>
<html lang="en">
  <body>
    <label id="lbl" for="email">Email</label>
    <input id="email" />
  </body>
</html>
```

```output
INPUT
```

**Symptom.** Clicking the text does nothing; screen readers announce an unnamed text box. **Fix:** use `<label for="id">` with a matching `id`, or wrap the input inside the label.

#### Mistake 4: Trusting browser-side validation alone

**Why it is wrong.** Anyone can remove `required` in DevTools or send a request without using your page at all.

```html file="index.html" bad page steps="eval (document.getElementById('name').removeAttribute('required'), 'required removed') | click #go"
<!DOCTYPE html>
<html lang="en">
  <body>
    <form id="f">
      <input id="name" name="name" required />
      <button id="go">Save</button>
    </form>
    <script>
      document.getElementById("f").addEventListener("submit", (event) => {
        event.preventDefault();
        const name = document.getElementById("name").value;
        console.log("saving name:", JSON.stringify(name));
      });
    </script>
  </body>
</html>
```

```output
required removed
saving name: ""
```

**Symptom.** An "impossible" empty value arrives. **Fix:** validate again inside your own handler (as in the `validate` function above) and, for real applications, on the server. **Diagnosis:** remember the rule: *HTML validation guides honest users; it never stops dishonest ones.*

# 9. Browser Storage and JSON

## Learning objectives for this section

- Save, read and delete data with `localStorage` and `sessionStorage`.
- Convert data to and from text with `JSON.stringify()` and `JSON.parse()`, and know what JSON cannot represent.
- Write load and save helpers that survive missing, corrupted or blocked storage.

## Conceptual explanation

Variables vanish when the page reloads. To remember a to-do list, a theme choice or a half-written draft, you need somewhere that **outlives the page**. Browsers provide two small key-value stores for this.

[[widths 1.3 2.6 2.6]]
| | `localStorage` | `sessionStorage` |
|---|---|---|
| Lifetime | Stays until your code or the user clears it | Cleared when the **tab** is closed |
| Shared between tabs | Yes (same origin) | No (each tab has its own) |
| Typical use | Saved lists, preferences, drafts | Temporary wizard state, per-tab data |
| Capacity | About 5 MB per origin | About 5 MB per origin |

Both share the same rules, which you must learn once.

- **Strings only.** Keys and values are converted to strings. Objects and arrays must be converted to text first (JSON, below).
- **Per origin.** Data belongs to the combination of protocol, host and port. `http://localhost:3000` and `http://localhost:5173` are different origins with separate storage.
- **Synchronous.** Reading and writing block the page, so keep stored data small.
- **Not private or secure.** Any script running on the page, including injected malicious scripts, can read it. Never store passwords or secret tokens here.

## The storage API

| Call | Does | Returns |
|---|---|---|
| `setItem(key, value)` | Stores `String(value)` under `key` | `undefined` (can **throw** if full or blocked) |
| `getItem(key)` | Reads the stored text | the string, or **`null`** if the key does not exist |
| `removeItem(key)` | Deletes one key | `undefined` |
| `clear()` | Deletes everything for this origin | `undefined` |
| `length`, `key(i)` | Number of stored keys, and the name of key *i* | number, string or `null` |

```html file="index.html" page
<!DOCTYPE html>
<html lang="en">
  <body>
    <script>
      localStorage.setItem("theme", "dark");
      console.log(localStorage.getItem("theme"), localStorage.getItem("missing"));
      console.log(typeof localStorage.getItem("theme"), localStorage.length);

      localStorage.setItem("count", 5);
      console.log(localStorage.getItem("count") + 1);

      localStorage.removeItem("theme");
      console.log(localStorage.getItem("theme"), localStorage.length);
    </script>
  </body>
</html>
```

```output
dark null
string 1
51
null 1
```

Line 5 reads back `"dark"`, and a missing key gives `null`, not `undefined`. Line 9 stores the number `5`, but it is converted to the text `"5"`, which is why adding `1` on line 10 gives `"51"`. After `removeItem`, the `theme` key is gone but `count` remains, so the length is `1`.

**It survives reloads.** This page counts how many times it has been loaded:

```html file="index.html" page steps="reload | reload"
<!DOCTYPE html>
<html lang="en">
  <body>
    <script>
      const visits = Number(localStorage.getItem("visits") ?? 0) + 1;
      localStorage.setItem("visits", visits);
      console.log("visits", visits);
    </script>
  </body>
</html>
```

```output
visits 1
visits 2
visits 3
```

The `?? 0` supplies a starting value when the key does not exist yet (the first visit); `Number(...)` converts the stored text back to a number; the new total is stored again.

## Function deep dive: `JSON.stringify()` and `JSON.parse()`

**What they are.** **JSON** (JavaScript Object Notation) is a plain-text format for data that looks like JavaScript literals. `JSON.stringify` converts a value **to** JSON text; `JSON.parse` converts JSON text **back** into a value.

**Why they exist.** Storage, files and web APIs carry only text. JSON is the agreed format for turning objects and arrays into text and back, and it is what almost every web API speaks (Sheet 04).

**Syntax.** `JSON.stringify(value, replacer, space)` and `JSON.parse(text, reviver)`. Only the first parameter of each is needed day to day. `space` (for example `2`) pretty-prints with indentation.

**Return values.** `stringify` returns a **string** (or `undefined` for values such as a bare function). `parse` returns the reconstructed value: an object, array, string, number, boolean or `null`.

**What JSON can represent.** Objects, arrays, strings (double quotes only), numbers, booleans and `null`. Therefore:

- `undefined` and functions are **dropped** from objects and become `null` inside arrays.
- A `Date` becomes an ISO **string**, and comes back as a string, not a `Date`.
- A `Map` or `Set` becomes `{}` (convert them first; see Sheet 02).
- Circular references make `stringify` throw a `TypeError`.

**Errors.** `JSON.parse` **throws a `SyntaxError`** if the text is not valid JSON (single quotes, trailing commas, truncated text). It does not return `null` for bad input.

```js file="json-demo.js" run
const todo = {
  id: 1,
  text: "Read",
  done: false,
  due: new Date("2026-03-01T00:00:00Z"),
  note: undefined,
  run() {},
};

const text = JSON.stringify(todo);
console.log(text);

const back = JSON.parse(text);
console.log(typeof back.due, back.note, "run" in back);

console.log(JSON.stringify([1, "a", null, undefined, () => 1]));
console.log(JSON.stringify({ a: 1, b: [1, 2] }, null, 2));

try {
  JSON.parse("{'single': 'quotes'}");
} catch (error) {
  console.log(error.name);
}
```

```output
{"id":1,"text":"Read","done":false,"due":"2026-03-01T00:00:00.000Z"}
string undefined false
[1,"a",null,null,null]
{
  "a": 1,
  "b": [
    1,
    2
  ]
}
SyntaxError
```

**Explanation.** The `note` property (`undefined`) and the `run` method disappear from the text, and the `Date` is turned into an ISO string. After `JSON.parse`, `back.due` has type `"string"`: you would have to rebuild a `Date` yourself. In arrays, unsupported values become `null` so that positions are preserved. The pretty-printed form uses two spaces per level. Invalid JSON, here because of single quotes, throws a `SyntaxError`, which you catch.

## Safe load and save helpers

Real stored data can be missing (first visit), corrupted (hand-edited, or saved by an older version of your code) or inaccessible (private browsing modes, full storage, blocked by user settings). Wrap both operations once, and use the wrappers everywhere.

```html file="index.html" page
<!DOCTYPE html>
<html lang="en">
  <body>
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
          return true;
        } catch (error) {
          return false;
        }
      }

      console.log(JSON.stringify(loadJSON("todos", [])));
      console.log(saveJSON("todos", [{ id: 1, text: "Read" }]));
      console.log(JSON.stringify(loadJSON("todos", [])));

      localStorage.setItem("broken", "{not json");
      console.log(JSON.stringify(loadJSON("broken", ["default"])));
    </script>
  </body>
</html>
```

```output
[]
true
[{"id":1,"text":"Read"}]
["default"]
```

`loadJSON` handles all three failure modes with one `fallback` value: the missing key returns the fallback directly, corrupted text makes `JSON.parse` throw and the `catch` returns the fallback, and blocked storage throws from `getItem` and is caught too. `saveJSON` reports success with a boolean so the caller can warn the user if saving failed.

## A complete example: a to-do list that survives reloads

```html file="index.html" page steps="fill #text Read | click #add | fill #text Write | click #add | reload | print #list"
<!DOCTYPE html>
<html lang="en">
  <body>
    <form id="form">
      <input id="text" />
      <button id="add">Add</button>
    </form>
    <ul id="list"></ul>
    <script>
      const KEY = "todos-v1";

      function loadJSON(key, fallback) {
        try {
          const raw = localStorage.getItem(key);
          return raw === null ? fallback : JSON.parse(raw);
        } catch (error) {
          return fallback;
        }
      }

      let todos = loadJSON(KEY, []);
      console.log("loaded", todos.length);

      function render() {
        const list = document.getElementById("list");
        list.replaceChildren();
        for (const todo of todos) {
          const li = document.createElement("li");
          li.textContent = todo.text;
          list.append(li);
        }
      }

      document.getElementById("form").addEventListener("submit", (event) => {
        event.preventDefault();
        const input = document.getElementById("text");
        if (input.value.trim() === "") {
          return;
        }
        todos = [...todos, { id: Date.now(), text: input.value.trim() }];
        localStorage.setItem(KEY, JSON.stringify(todos));
        console.log("saved", todos.length);
        input.value = "";
        render();
      });

      render();
    </script>
  </body>
</html>
```

```output
loaded 0
saved 1
saved 2
loaded 2
Read / Write
```

**Data flow.** On load, `loadJSON` reads the saved array (empty the first time). `render` draws the page from the `todos` array (the render pattern from Section 5). On submit, the handler creates a **new** array with spread (Sheet 02's immutable update), writes it to storage as JSON, and re-renders. After the scripted reload the page logs `loaded 2` and `render()` immediately shows `Read` and `Write` again. Notice the key name `todos-v1`: putting a version in the key lets you change the data format later without crashing on old saved data.

## Common mistakes in this section

#### Mistake 1: Storing an object without converting it

**Why it is wrong.** `setItem` turns the value into a string with `String(value)`.

```html file="index.html" bad page
<!DOCTYPE html>
<html lang="en">
  <body>
    <script>
      localStorage.setItem("user", { name: "Asha" });
      console.log(localStorage.getItem("user"));
      console.log(localStorage.getItem("user").name);
    </script>
  </body>
</html>
```

```output
[object Object]
undefined
```

**Symptom.** You saved an object and got the useless text `[object Object]` back. **Fix:** `setItem("user", JSON.stringify(user))` and `JSON.parse(getItem("user"))`. **Diagnosis:** look at the stored value in DevTools, Application tab, Local Storage.

#### Mistake 2: Expecting numbers or booleans back

**Why it is wrong.** Everything read from storage is a string, including `"false"`, which is **truthy**.

```html file="index.html" bad page
<!DOCTYPE html>
<html lang="en">
  <body>
    <script>
      localStorage.setItem("darkMode", false);
      if (localStorage.getItem("darkMode")) {
        console.log("dark mode ON (wrong)");
      }
      console.log(localStorage.getItem("darkMode") === false);
    </script>
  </body>
</html>
```

```output
dark mode ON (wrong)
false
```

**Symptom.** A setting that was turned off behaves as on. **Fix:** store with JSON (`JSON.stringify(false)` is `"false"`, and `JSON.parse("false")` is the real `false`) or compare to the string explicitly.

#### Mistake 3: Letting `JSON.parse` crash the page

**Why it is wrong.** Corrupted or hand-edited data throws a `SyntaxError`, which stops the script before the page is even drawn.

```html file="index.html" bad page throws
<!DOCTYPE html>
<html lang="en">
  <body>
    <script>
      localStorage.setItem("todos", "[{broken");
      const todos = JSON.parse(localStorage.getItem("todos"));
      console.log(todos.length);
    </script>
  </body>
</html>
```

```output
Uncaught SyntaxError: Expected property name or '}' in JSON at position 2
```

**Symptom.** A blank page and a `SyntaxError` in the Console, and it **stays** broken on every reload because the bad data is still stored. **Fix:** use the `loadJSON` helper with a fallback. **Diagnosis:** open Application, Local Storage, and inspect the stored text; clear the key to recover during development. (The wording of the message varies between browsers.)

#### Mistake 4: Assuming the key exists

**Why it is wrong.** The first time a user visits, nothing has been saved: `getItem` returns `null`.

```html file="index.html" bad page throws
<!DOCTYPE html>
<html lang="en">
  <body>
    <script>
      const todos = JSON.parse(localStorage.getItem("todos"));
      console.log(todos.length);
    </script>
  </body>
</html>
```

```output
Uncaught TypeError: Cannot read properties of null (reading 'length')
```

**Symptom.** Works on your machine (where you saved data during testing) and crashes for every new user. `JSON.parse(null)` quietly returns `null` and the crash comes one line later. **Fix:** `loadJSON("todos", [])`. **Diagnosis:** test with storage cleared (DevTools, Application, Clear site data) as well as with saved data.
