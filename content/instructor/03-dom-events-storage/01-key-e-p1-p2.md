# 6. Set E: Challenge Solutions

#### E1. Sortable table

```js file="sort-logic.js" bundle=e1
export function sortRows(rows, key, direction = "asc") {
  const sign = direction === "desc" ? -1 : 1;
  return [...rows].sort((a, b) => {
    const x = a[key];
    const y = b[key];
    const result =
      typeof x === "number" && typeof y === "number"
        ? x - y
        : String(x).localeCompare(String(y), undefined, { sensitivity: "base" });
    return sign * result;
  });
}
```

```js file="test-sort.mjs" run bundle=e1
import { sortRows } from "./sort-logic.js";

const rows = Object.freeze([
  { name: "Ann", age: 31 },
  { name: "bob", age: 9 },
  { name: "Cy", age: 25 },
  { name: "Dee", age: 10 },
]);
const names = (list) => list.map((r) => r.name).join(",");

console.log(names(sortRows(rows, "age")), names(sortRows(rows, "age", "desc")));
console.log(names(sortRows(rows, "name")), names(rows));
```

```output
bob,Dee,Cy,Ann Ann,Cy,Dee,bob
Ann,bob,Cy,Dee Ann,bob,Cy,Dee
```

Numbers sort numerically (`9` before `10`), text ignores case (`bob` between `Ann` and `Cy`), and the frozen input is untouched. `sort` is stable, so equal keys keep their previous order in both directions.

```html file="index.html" bundle=e1 page steps="click th[data-key=age] | eval names() | click th[data-key=age] | eval names() | click th[data-key=name] | eval names() | eval document.querySelector('th[data-key=name]').textContent"
<!DOCTYPE html>
<html lang="en">
  <body>
    <table>
      <thead>
        <tr>
          <th data-key="name">Name</th>
          <th data-key="age">Age</th>
        </tr>
      </thead>
      <tbody id="rows"></tbody>
    </table>
    <script type="module">
      import { sortRows } from "./sort-logic.js";

      const data = [
        { name: "Ann", age: 31 },
        { name: "bob", age: 9 },
        { name: "Cy", age: 25 },
        { name: "Dee", age: 10 },
      ];
      let sort = { key: null, direction: "asc" };

      function render() {
        const rows = sort.key ? sortRows(data, sort.key, sort.direction) : data;
        const body = document.getElementById("rows");
        body.replaceChildren();
        for (const row of rows) {
          const tr = document.createElement("tr");
          for (const value of [row.name, row.age]) {
            const td = document.createElement("td");
            td.textContent = value;
            tr.append(td);
          }
          body.append(tr);
        }
        for (const th of document.querySelectorAll("th")) {
          const base = th.dataset.key === "name" ? "Name" : "Age";
          const active = th.dataset.key === sort.key;
          th.textContent = active ? `${base} (${sort.direction})` : base;
        }
      }

      document.querySelector("thead").addEventListener("click", (event) => {
        const th = event.target.closest("th[data-key]");
        if (!th) {
          return;
        }
        const key = th.dataset.key;
        const same = sort.key === key;
        sort = { key, direction: same && sort.direction === "asc" ? "desc" : "asc" };
        render();
      });

      window.names = () =>
        [...document.querySelectorAll("tbody tr td:first-child")]
          .map((td) => td.textContent)
          .join(",");
      render();
    </script>
  </body>
</html>
```

```output
bob,Dee,Cy,Ann
Ann,Cy,Dee,bob
Ann,bob,Cy,Dee
Name (asc)
```

One delegated listener on `<thead>`; clicking another column starts ascending, clicking the same column toggles; `data` itself is never reordered.

#### E2. Undo and redo

```js file="history.js" bundle=e2
const LIMIT = 50;

export function createHistory(initial) {
  return { past: [], present: initial, future: [] };
}

export function push(history, value) {
  if (value === history.present) {
    return history;
  }
  return {
    past: [...history.past, history.present].slice(-LIMIT),
    present: value,
    future: [],
  };
}

export function undo(history) {
  if (history.past.length === 0) {
    return history;
  }
  return {
    past: history.past.slice(0, -1),
    present: history.past.at(-1),
    future: [history.present, ...history.future],
  };
}

export function redo(history) {
  if (history.future.length === 0) {
    return history;
  }
  return {
    past: [...history.past, history.present],
    present: history.future[0],
    future: history.future.slice(1),
  };
}

export const canUndo = (history) => history.past.length > 0;
export const canRedo = (history) => history.future.length > 0;
```

```js file="test-history.mjs" run bundle=e2
import { createHistory, push, undo, redo, canUndo, canRedo } from "./history.js";

let h = createHistory("");
console.log(canUndo(h), canRedo(h));
h = push(h, "a");
h = push(h, "ab");
h = push(h, "abc");
h = undo(undo(h));
console.log(h.present, canUndo(h), canRedo(h));
h = redo(h);
console.log(h.present);
h = undo(h);
h = push(h, "x");
console.log(h.present, canRedo(h), h.past.length);

let big = createHistory(0);
for (let i = 1; i <= 80; i++) {
  big = push(big, i);
}
console.log(big.past.length, big.past[0], big.present);

const frozen = Object.freeze(createHistory("start"));
console.log(undo(frozen) === frozen, redo(frozen) === frozen);
```

```output
false false
a true true
ab
x false 2
50 30 80
true true
```

Every function returns a **new** history (or the same object when nothing changes), so the past, present and future can be compared by reference. A new change after undoing clears `future` (the redo branch), and `slice(-LIMIT)` keeps only the latest 50 past states. The user interface is the textarea from Section 6 with a debounced `input` listener calling `push`, and two buttons whose `disabled` properties come from `canUndo` and `canRedo`.

# 7. Mini Project Reference Implementations

Each project has a **logic module** (no DOM), a Node test, and a **page** that was run in headless Chromium with scripted clicks and typing. Pages are single files with an inline module script for brevity; students should split them as described in Section 10. The test steps are not shown; the text beside each output explains what was done.

## Project 1: Habit tracker

```js file="habits-logic.js" bundle=p1
export function todayKey(date) {
  return date.toISOString().slice(0, 10);
}

export function shiftDay(key, delta) {
  const [y, m, d] = key.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d + delta)).toISOString().slice(0, 10);
}

export function currentStreak(doneDates, today) {
  const done = new Set(doneDates);
  let day = done.has(today) ? today : shiftDay(today, -1);
  let streak = 0;
  while (done.has(day)) {
    streak++;
    day = shiftDay(day, -1);
  }
  return streak;
}

export function validateName(habits, name) {
  const clean = name.trim();
  if (clean === "") {
    return "Name is required";
  }
  if (habits.some((h) => h.name.toLowerCase() === clean.toLowerCase())) {
    return "That habit already exists";
  }
  return "";
}

export function addHabit(habits, name) {
  if (validateName(habits, name) !== "") {
    return habits;
  }
  const id = Math.max(0, ...habits.map((h) => h.id)) + 1;
  return [...habits, { id, name: name.trim(), doneDates: [] }];
}

export function toggleToday(habits, id, today) {
  return habits.map((h) => {
    if (h.id !== id) {
      return h;
    }
    const has = h.doneDates.includes(today);
    const doneDates = has
      ? h.doneDates.filter((d) => d !== today)
      : [...h.doneDates, today];
    return { ...h, doneDates };
  });
}

export const removeHabit = (habits, id) => habits.filter((h) => h.id !== id);
export const doneCount = (habits, today) =>
  habits.filter((h) => h.doneDates.includes(today)).length;
```

```js file="test-habits.mjs" run bundle=p1
import {
  currentStreak, shiftDay, addHabit, toggleToday, validateName,
} from "./habits-logic.js";

console.log(currentStreak(["2026-03-12", "2026-03-13", "2026-03-14"], "2026-03-14"));
console.log(currentStreak(["2026-03-12", "2026-03-13"], "2026-03-14"));
console.log(currentStreak(["2026-03-10", "2026-03-11"], "2026-03-14"));
console.log(currentStreak([], "2026-03-14"));
console.log(shiftDay("2026-03-01", -1), shiftDay("2026-12-31", 1));

const habits = Object.freeze([]);
const one = addHabit(habits, "  Read  ");
console.log(one[0].name, addHabit(one, "read") === one, validateName(one, ""));
const done = toggleToday(one, 1, "2026-03-14");
const again = toggleToday(done, 1, "2026-03-14");
console.log(done[0].doneDates.join(), again[0].doneDates.length);
```

```output
3
2
0
0
2026-02-28 2027-01-01
Read true Name is required
2026-03-14 0
```

A streak is still alive if yesterday was completed (so it counts until the day ends); one missed day resets it to `0`. Dates are handled as `YYYY-MM-DD` strings and only converted inside `shiftDay`, using UTC to avoid daylight-saving surprises. Pass the day in as an argument so tests never depend on the clock.

```html file="index.html" bundle=p1 page steps="fill #name Read | click #add | fill #name read | click #add | print #error | click button[data-action=toggle] | print #summary | print .streak | click button[data-action=toggle] | print #summary | fill #name <img src=x onerror=alert(1)> | click #add | eval String(document.querySelectorAll('img').length) | reload | eval String(document.querySelectorAll('li').length)"
<!DOCTYPE html>
<html lang="en">
  <body>
    <form id="form">
      <input id="name" />
      <button id="add">Add</button>
    </form>
    <p id="error"></p>
    <ul id="list"></ul>
    <p id="summary"></p>
    <script type="module">
      import {
        todayKey, addHabit, toggleToday, removeHabit,
        currentStreak, validateName, doneCount,
      } from "./habits-logic.js";

      const KEY = "habits-v1";
      const today = todayKey(new Date());

      function load() {
        try {
          const data = JSON.parse(localStorage.getItem(KEY));
          return Array.isArray(data) ? data : [];
        } catch (error) {
          return [];
        }
      }

      let habits = load();

      function update(next) {
        habits = next;
        localStorage.setItem(KEY, JSON.stringify(habits));
        render();
      }

      function render() {
        const list = document.getElementById("list");
        list.replaceChildren();
        for (const habit of habits) {
          const li = document.createElement("li");
          li.dataset.id = habit.id;
          const name = document.createElement("span");
          name.textContent = habit.name;
          const streak = document.createElement("span");
          streak.className = "streak";
          streak.textContent = `Streak: ${currentStreak(habit.doneDates, today)}`;
          const toggle = document.createElement("button");
          toggle.dataset.action = "toggle";
          toggle.textContent = habit.doneDates.includes(today) ? "Undo" : "Done today";
          const del = document.createElement("button");
          del.dataset.action = "delete";
          del.textContent = "Delete";
          li.append(name, " ", streak, " ", toggle, " ", del);
          list.append(li);
        }
        const summary = `${doneCount(habits, today)} of ${habits.length} done today`;
        document.getElementById("summary").textContent = summary;
      }

      document.getElementById("form").addEventListener("submit", (event) => {
        event.preventDefault();
        const input = document.getElementById("name");
        const error = validateName(habits, input.value);
        document.getElementById("error").textContent = error;
        if (error === "") {
          update(addHabit(habits, input.value));
          input.value = "";
        }
      });

      document.getElementById("list").addEventListener("click", (event) => {
        const button = event.target.closest("button[data-action]");
        if (!button) {
          return;
        }
        const id = Number(button.closest("li").dataset.id);
        if (button.dataset.action === "delete") {
          update(removeHabit(habits, id));
        } else {
          update(toggleToday(habits, id, today));
        }
      });

      render();
    </script>
  </body>
</html>
```

```output
That habit already exists
1 of 1 done today
Streak: 1
0 of 1 done today
0
2
```

Reading the output in order: the duplicate name is rejected with a message; ticking the habit gives `1 of 1 done today` and a streak of 1; ticking again undoes it; a habit named like an `<img onerror>` tag is added as text (zero image elements exist); after a reload both habits are restored from storage.

## Project 2: Pomodoro timer

```js file="pomodoro-logic.js" bundle=p2
export function initialState(settings) {
  return {
    mode: "focus",
    remainingSeconds: settings.focusMinutes * 60,
    running: false,
    completed: 0,
  };
}

export function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

export function tick(state, settings) {
  if (!state.running) {
    return state;
  }
  if (state.remainingSeconds > 1) {
    return { ...state, remainingSeconds: state.remainingSeconds - 1 };
  }
  if (state.mode === "focus") {
    return {
      ...state,
      mode: "break",
      remainingSeconds: settings.breakMinutes * 60,
      completed: state.completed + 1,
    };
  }
  return { ...state, mode: "focus", remainingSeconds: settings.focusMinutes * 60 };
}

export const start = (state) => ({ ...state, running: true });
export const pause = (state) => ({ ...state, running: false });
export const reset = (settings) => initialState(settings);

export function parseMinutes(text) {
  const n = Number(text);
  return text.trim() !== "" && Number.isInteger(n) && n >= 1 && n <= 90 ? n : null;
}
```

```js file="test-pomodoro.mjs" run bundle=p2
import {
  initialState, formatTime, tick, start, pause, reset, parseMinutes,
} from "./pomodoro-logic.js";

const settings = { focusMinutes: 25, breakMinutes: 5 };
console.log(formatTime(0), formatTime(59), formatTime(65));
console.log(formatTime(1500), formatTime(3599));

let s = initialState(settings);
console.log(tick(s, settings) === s);
s = start(s);
s = tick(s, settings);
console.log(s.remainingSeconds, s.mode);

const last = { ...s, remainingSeconds: 1 };
const next = tick(last, settings);
console.log(next.mode, formatTime(next.remainingSeconds), next.completed);
const back = tick({ ...next, remainingSeconds: 1 }, settings);
console.log(back.mode, formatTime(back.remainingSeconds), back.completed);

console.log(pause(s).running, reset(settings).running);
console.log(parseMinutes("25"), parseMinutes("0"), parseMinutes("91"));
console.log(parseMinutes("2.5"), parseMinutes(""), parseMinutes("abc"));
```

```output
00:00 00:59 01:05
25:00 59:59
true
1499 focus
break 05:00 1
focus 25:00 1
false false
25 null null
null null null
```

```html file="index.html" bundle=p2 page steps="print #mode | print #time | click #start | wait 1200 | print #time | click #pause | wait 1200 | print #time | click #reset | print #time | eval document.title"
<!DOCTYPE html>
<html lang="en">
  <body>
    <p id="mode"></p>
    <p id="time"></p>
    <button id="start">Start</button>
    <button id="pause">Pause</button>
    <button id="reset">Reset</button>
    <script type="module">
      import {
        initialState, formatTime, tick, start, pause, reset,
      } from "./pomodoro-logic.js";

      const settings = { focusMinutes: 25, breakMinutes: 5 };
      let state = initialState(settings);
      let timerId = null;
      let lastTick = 0;

      function render() {
        const label = state.mode === "focus" ? "Focus" : "Break";
        const time = formatTime(state.remainingSeconds);
        document.getElementById("mode").textContent = label;
        document.getElementById("time").textContent = time;
        document.getElementById("start").disabled = state.running;
        document.getElementById("pause").disabled = !state.running;
        document.title = `${time} ${label}`;
      }

      function stopTimer() {
        clearInterval(timerId);
        timerId = null;
      }

      function loop() {
        const now = Date.now();
        while (now - lastTick >= 1000) {
          state = tick(state, settings);
          lastTick += 1000;
        }
        render();
      }

      document.getElementById("start").addEventListener("click", () => {
        if (timerId !== null) {
          return;
        }
        state = start(state);
        lastTick = Date.now();
        timerId = setInterval(loop, 250);
        render();
      });

      document.getElementById("pause").addEventListener("click", () => {
        stopTimer();
        state = pause(state);
        render();
      });

      document.getElementById("reset").addEventListener("click", () => {
        stopTimer();
        state = reset(settings);
        render();
      });

      render();
    </script>
  </body>
</html>
```

```output
Focus
25:00
24:59
24:59
25:00
25:00 Focus
```

The page shows `Focus` and `25:00`, then after about 1.2 seconds of running `24:59`, then the same value after pausing for another second (frozen), then `25:00` after reset, and the document title always mirrors the display. The interval refreshes every 250 ms, but the number of seconds to apply is computed from `Date.now()`, so a throttled background tab catches up correctly. `timerId !== null` guarantees at most one interval. This reference page keeps the durations in a constant; the settings form and its persistence (using `parseMinutes` and the safe `loadJSON` pattern) are left to the student and are part of the acceptance criteria.
