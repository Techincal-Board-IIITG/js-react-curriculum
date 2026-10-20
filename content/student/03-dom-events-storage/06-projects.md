# 13. Mini Projects

## Mini projects overview

Five browser applications, ordered from easier to harder. **Projects 1 to 3 are the core workload; projects 4 and 5 are extensions.** Every project follows the architecture from Section 10: a **pure data module** you can test in Node, a small **storage** layer using the safe JSON helpers, a **`render`** function, and a **wiring** file with delegated listeners. Starter structure for every project:

```tree
project/
├── index.html
├── style.css      (yours)
├── main.js        wiring: events, update(), initial render
├── logic.js       pure functions, no DOM, exported by name
├── storage.js     loadJSON / saveJSON
└── ui.js          render(...) and DOM helpers
```

[[widths 0.5 2.2 1.2 1.1]]
| # | Project | Difficulty | Scope |
|---|---|---|---|
| 1 | Habit tracker | Easy | Core |
| 2 | Pomodoro timer | Easy to medium | Core |
| 3 | Kanban board | Medium | Core |
| 4 | Bookmark manager | Medium | Extension |
| 5 | Markdown editor with live preview | Medium to hard | Extension |

::: note Rules for every project
No `innerHTML` with data that did not come from your own constants. Pure logic in `logic.js`, tested from Node with `console.log` checks. Survive empty storage, corrupted storage and a reload. Use `type="module"` and serve the folder over HTTP.
:::

:::: project Habit tracker | Difficulty: Easy | Core
##### Objective
Practise rendering a list from data, delegated listeners, date handling with strings, and persistence.

##### Problem statement
Build a page where the user lists habits (such as "Read 20 pages") and ticks off each one for today. Each habit shows its current **streak**: the number of consecutive days, ending today or yesterday, on which it was completed.

##### Required features
- Add a habit with a form; reject blank names and duplicates (ignoring case).
- Each habit has a checkbox or button "Done today"; clicking again un-ticks it.
- Store each habit as `{ id, name, doneDates: ["2026-03-14", ...] }` where dates are `YYYY-MM-DD` strings.
- Show the current streak for each habit, and a summary "x of y done today".
- Delete a habit.
- Everything persists across reloads.

##### Technical constraints
- `logic.js` exports `addHabit`, `toggleToday`, `removeHabit`, `currentStreak(doneDates, todayKey)` and `todayKey(date)`; none of them touches the DOM or reads the clock (pass today's key in, so tests are deterministic).
- Calculate dates with string keys and `new Date(...)` only inside small helpers; do not compare date objects with `===`.
- One delegated listener for the list.

##### Expected behavior
```text file="Illustrative behaviour"
Add "Read 20 pages"        -> list shows it, streak 0, "0 of 1 done today"
Click "Done today"         -> streak 1, "1 of 1 done today"
(next day) Click again     -> streak 2
(skip a day) open the page -> streak 0 or restarts, per your rule
Reload                     -> everything is still there
```

##### Suggested milestones
1. `todayKey` and `currentStreak`, tested in Node with hand-made date lists.
2. Add, toggle and remove functions (immutable).
3. `render` and the form.
4. Delegated listener for toggle and delete.
5. Persistence with safe load and save.

##### Edge cases
- No completed dates; a single date that is today or yesterday; a gap of one day; duplicate dates in the list.
- Midnight rollover while the page is open (document how you handle it).
- Names with only spaces, very long names, names containing `<` or `&`.
- Corrupted stored data.

##### Acceptance criteria
- [ ] `currentStreak(["2026-03-12", "2026-03-13", "2026-03-14"], "2026-03-14")` is `3`.
- [ ] `currentStreak(["2026-03-12", "2026-03-13"], "2026-03-14")` is `2` (streak still alive until the day ends); with a gap before yesterday it is `0`.
- [ ] A habit named `<img src=x onerror=alert(1)>` is displayed as text and runs nothing.
- [ ] Toggling twice on the same day returns to the original data.
- [ ] Reload keeps habits; corrupted storage shows an empty list without errors.

##### Stretch goals
- A seven-day history strip per habit.
- Weekly goals ("3 times a week").
- Export and import the data as a JSON file.

##### Concepts practiced
Sections 3 to 5, 7, 9 and 10: rendering, delegation, immutable updates, storage, separation of logic.
::::

:::: project Pomodoro timer | Difficulty: Easy to medium | Core
##### Objective
Practise timers, state machines, formatting numbers, and keeping logic separate from an interval that updates the screen.

##### Problem statement
Build a focus timer that alternates between a work session (default 25 minutes) and a break (default 5 minutes), with start, pause and reset controls and a large `mm:ss` countdown.

##### Required features
- Display remaining time as `mm:ss` with leading zeros, and show the current mode ("Focus" or "Break").
- Start, pause and reset buttons; buttons are disabled when they make no sense.
- When a session reaches zero, switch modes automatically and show how many focus sessions have been completed today.
- Settings for the two durations (whole minutes from 1 to 90), saved in storage.
- Update `document.title` with the remaining time.

##### Technical constraints
- State is a plain object `{ mode, remainingSeconds, running, completed }`; `logic.js` exports `formatTime(seconds)`, `tick(state, settings)`, `start`, `pause` and `reset` as **pure functions**.
- Use `setInterval` for the screen refresh, but compute elapsed time from `Date.now()` (not by counting ticks) so that a throttled background tab stays accurate.
- Always `clearInterval` when pausing or resetting; never create two intervals.

##### Expected behavior
```text file="Illustrative behaviour"
Focus 25:00 -> Start -> 24:59, 24:58 ...
Pause       -> time freezes; Start resumes from the same value
00:00       -> "Break" 05:00 begins; completed = 1
Reset       -> back to Focus 25:00, timer stopped
```

##### Suggested milestones
1. `formatTime` with tests (`0`, `59`, `60`, `3599`).
2. A `tick` function that moves a state one second forward and switches modes at zero.
3. Interval wiring with start, pause, reset.
4. Settings form with validation and persistence.
5. Title updates and the completed-sessions counter.

##### Edge cases
- Pause and resume rapidly; pressing Start twice.
- Changing durations while running.
- Background-tab throttling (many seconds pass between ticks).
- Invalid durations: empty, `0`, `91`, `2.5`, text.

##### Acceptance criteria
- [ ] `formatTime(0)` is `"00:00"`, `formatTime(65)` is `"01:05"`, `formatTime(1500)` is `"25:00"`.
- [ ] A tick on `remainingSeconds: 1` switches mode and loads the other duration.
- [ ] Only one interval ever exists (verify by logging in the interval callback).
- [ ] After a reload the saved durations are used.
- [ ] Elapsed time is correct after the tab is hidden for a minute.

##### Stretch goals
- A sound or notification when a session ends (research the Notifications API and permission rules).
- A long break after every fourth focus session.
- A daily statistics view.

##### Concepts practiced
`setInterval`/`clearInterval`, `Date.now()`, pure state transitions, formatting, validation, storage.
::::

:::: project Kanban board | Difficulty: Medium | Core
##### Objective
Practise a nested data model, rendering several lists from one object, moving items between lists, and delegation across a larger interface.

##### Problem statement
Build a board with three columns, **To do**, **Doing** and **Done**. Cards can be added to any column, moved between columns, edited and deleted.

##### Required features
- Data model: `{ columns: [{ id, title, cardIds: [] }], cards: { [id]: { id, text } } }`; cards live in one lookup object and columns reference them by id.
- Add a card to a column (form per column or a single form with a column choice); reject blank text.
- Move a card to the previous or next column with buttons; buttons are disabled at the ends.
- Edit a card's text inline (double-click or an Edit button) and delete a card.
- Show the card count in each column heading.
- Persist the whole board.

##### Technical constraints
- `logic.js` exports `addCard`, `moveCard(board, cardId, direction)`, `editCard`, `deleteCard`; all are pure and return **new** board objects; unchanged columns keep their identity.
- One delegated listener on the board for every button; buttons carry `data-action` and `data-card-id` attributes.
- Cards are inserted with `textContent` only.

##### Expected behavior
```text file="Illustrative behaviour"
Add "Write report" to To do          -> To do (1)
Move right                           -> To do (0), Doing (1)
Move right                           -> Doing (0), Done (1); "move right" disabled
Delete                               -> Done (0)
Reload                               -> board restored exactly
```

##### Suggested milestones
1. The data model and a hand-written starting board.
2. `render` for columns and cards.
3. `addCard`, `deleteCard` and their listeners.
4. `moveCard` with end-of-board rules.
5. Inline editing and persistence.

##### Edge cases
- Moving the first card left or the last card right.
- Deleting a card that is already gone; editing to blank text.
- An orphan card id stored in a column but missing from `cards` (corrupted data).
- Very long card text; 200 cards.

##### Acceptance criteria
- [ ] `moveCard` on a card in the first column with direction `-1` returns the board unchanged.
- [ ] After a move, the card id appears in exactly one column.
- [ ] The old board object is unchanged after every operation (test with frozen data).
- [ ] Every control works for cards added after page load (delegation).
- [ ] Corrupted data falls back to an empty starting board.

##### Stretch goals
- Drag and drop using the HTML Drag and Drop API.
- Reorder cards inside a column.
- A column to create and rename columns.

##### Concepts practiced
Normalised data (lookup by id), immutable nested updates, delegation with `data-*` attributes, rendering from one source of truth.
::::

:::: project Bookmark manager | Difficulty: Medium | Extension
##### Objective
Practise validation, safe handling of untrusted URLs, searching, filtering and tags in a persistent application.

##### Problem statement
Build a page that saves bookmarks (title, address, tags), lets the user search and filter them, and opens them safely.

##### Required features
- A form with title, URL and a comma-separated tag list. Validate: title required; URL must be an `http:` or `https:` address (use the `new URL()` allow-list from Section 11); tags are trimmed, lower-cased, de-duplicated and may be empty.
- A list showing title, host name (such as `developer.mozilla.org`), tags and a delete button.
- Live search by title or host (ignoring case) combined with a tag filter built from all tags in use.
- Reject duplicate URLs (compare normalised addresses) with a clear message.
- Links open in a new tab with `rel="noopener noreferrer"`.
- Persist all bookmarks; show an empty-state message when there are none or no matches.

##### Technical constraints
- `logic.js` exports `validateBookmark`, `addBookmark`, `removeBookmark`, `search(list, text, tag)` and `allTags(list)`.
- The URL is set as the `href` only after passing the allow-list check.
- No `innerHTML` anywhere.

##### Expected behavior
```text file="Illustrative behaviour"
Add "MDN", https://developer.mozilla.org/, tags "docs, js"
   -> appears with host developer.mozilla.org
Add "x" javascript:alert(1)           -> error "URL must start with http:// or https://"
Add MDN again                          -> error "That address is already saved"
Search "mdn"                           -> only MDN visible
Tag filter "docs"                      -> only bookmarks tagged docs
```

##### Suggested milestones
1. `validateBookmark` using `URL`, with a table of valid and invalid examples.
2. Add and remove, immutable.
3. Rendering and delegated delete.
4. Search plus tag filtering and the dynamic tag list.
5. Persistence, empty states and error messages.

##### Edge cases
- `HTTPS://Example.com/` versus `https://example.com` (duplicates?).
- Trailing slashes, query strings, a URL with a username; a very long URL.
- Tags such as `"A, a, , b"`; no tags; a single comma.
- A stored bookmark whose URL no longer passes validation (corrupted or edited storage).

##### Acceptance criteria
- [ ] `validateBookmark` rejects `javascript:`, `data:`, relative paths and empty titles, and accepts normal web addresses.
- [ ] Duplicate detection ignores case in the host and a trailing slash.
- [ ] A title containing `<script>` is displayed as text.
- [ ] Search and tag filter combine (both must match).
- [ ] After reload, bookmarks are restored and any invalid stored entries are skipped.

##### Stretch goals
- Import and export as JSON with validation of every entry.
- Sort by date added, title, or host.
- A favicon next to each bookmark (research how, and what privacy cost it has).

##### Concepts practiced
`URL`, allow-list validation, XSS-safe rendering, filtering, tag normalisation, storage.
::::

:::: project Markdown editor with live preview | Difficulty: Medium to hard | Extension
##### Objective
Practise parsing text into structure, building DOM safely without `innerHTML`, debouncing input, and persistence.

##### Problem statement
Build a two-pane page: a `<textarea>` on the left and a live preview on the right. The preview shows the text rendered from a small subset of Markdown.

##### Required features
- Supported syntax: headings `#` to `###`, paragraphs, bold `**text**`, italic `*text*`, inline code with backticks, unordered lists (`- item`), ordered lists (`1. item`), and links `[label](url)`.
- The preview updates while the user types, but the rendering work runs at most once per 200 ms of silence (debounce).
- The draft is saved and restored.
- A word and character count below the editor.
- Links only become clickable for `http:` and `https:` addresses; other targets are shown as plain text.

##### Technical constraints
- **No `innerHTML`.** `logic.js` exports `parseMarkdown(text)`, which returns a **data structure** (for example `[{ type: "heading", level: 2, children: [...] }]`) and has no DOM code; `ui.js` turns that structure into elements with `createElement` and `textContent`.
- Implement the parser yourself with string methods; do not use a library for this exercise.
- Debounce is a small reusable function you write (a closure around `setTimeout`/`clearTimeout`).

##### Expected behavior
```text file="Illustrative behaviour"
Type:  # Title            -> preview shows an <h1> "Title"
Type:  **bold** and *it*   -> bold and italic text
Type:  - a / - b           -> a bulleted list with two items
Type:  <script>alert(1)</script> -> shown literally as text
Type:  [x](javascript:alert(1)) -> shown as plain text "x", not a link
```

##### Suggested milestones
1. Block parsing: headings, paragraphs, lists (as data), tested in Node.
2. Inline parsing: bold, italic, code, links, as nested data.
3. `ui.js`: convert the data structure to elements.
4. Wire the textarea with a debounce and persist the draft.
5. Counts, link safety checks and unusual-input tests.

##### Edge cases
- Empty text; only blank lines; a heading with no text; `#` without a space.
- Unclosed `**` or backticks; `**bold *and italic***`; characters such as `<`, `&`, quotes.
- A very long document (10,000 lines): the preview must not freeze the page.
- Mixed list types and blank lines between list items.

##### Acceptance criteria
- [ ] `parseMarkdown("# Hi")` returns a single heading block of level 1 with the text `Hi`.
- [ ] The output for `<script>` and `<img onerror>` in the source contains no script or image elements.
- [ ] A `javascript:` link target never becomes an `<a href>`.
- [ ] The debounce renders at most once for twenty keystrokes typed quickly (log to verify).
- [ ] After reload the draft is restored and rendered.

##### Stretch goals
- Code blocks fenced with triple backticks, blockquotes and horizontal rules.
- A synchronised scroll between editor and preview.
- Export the rendered result as a standalone HTML file with correct escaping.

##### Concepts practiced
String processing, recursive data, `createElement` rendering, debounce with closures, XSS-safe design, storage.
::::
