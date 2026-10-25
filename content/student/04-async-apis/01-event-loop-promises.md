# 2. Synchronous and Asynchronous Execution

## Learning objectives for this section

- Explain what blocking means and why waiting must not block JavaScript.
- Describe the call stack, the task queue, the microtask queue and the event loop.
- Predict the output order of code that mixes synchronous code, timers and promise callbacks.

## Conceptual explanation

JavaScript runs your code on **one thread**: it can do exactly one thing at a time. Code that does its work from start to finish before the next line begins is **synchronous**. That is fine for arithmetic, but a network request can take a second or more. If JavaScript simply stood still waiting, everything else would freeze: the page could not respond to clicks, scroll smoothly, or run animations. To avoid this, anything slow is handed to the **environment** (the browser or Node.js), which does the waiting in the background. When the work is finished, the environment puts a **callback** in a queue, and JavaScript runs it when it is free. Code that starts something now and finishes it later is **asynchronous**.

Three machines cooperate:

1. The **call stack** is the list of functions currently running. Calling a function pushes a frame; returning pops it. Only the top frame runs.
2. The **environment** (Web APIs in a browser) handles timers, network requests and events outside your code.
3. The **event loop** is a loop that watches the call stack and two queues, and feeds the stack when it is empty.

```diagram
flow
Your code runs on the call stack -> Slow work is handed to the environment -> *Environment queues a callback when done -> Event loop moves it to the stack when the stack is empty
```

## The two queues and the loop

There are **two** queues, and their priority is the key to predicting order.

[[widths 1.3 2.6 2.6]]
| Queue | What goes in it | When it runs |
|---|---|---|
| **Microtask queue** | Promise callbacks (`.then`, `.catch`, `.finally`, code after `await`) and `queueMicrotask()` | **As soon as the call stack is empty, all of them**, before anything else |
| **Task queue** (macrotasks) | Timer callbacks (`setTimeout`, `setInterval`), user events (click, input), network completion events | **One task at a time**, only when the stack **and** the microtask queue are empty |

The event loop follows this cycle, forever:

1. Run the current script (or task) until the call stack is empty.
2. Run **every** microtask in the microtask queue (including any new ones added meanwhile) until it is empty.
3. (In a browser, the page may now be redrawn.)
4. Take **one** task from the task queue and run it. Go back to step 2 after it finishes.

```js file="order-basic.js" run
console.log("1 sync start");

setTimeout(() => console.log("5 timeout 0"), 0);

Promise.resolve().then(() => console.log("3 promise then"));
queueMicrotask(() => console.log("4 microtask"));

console.log("2 sync end");
```

```output
1 sync start
2 sync end
3 promise then
4 microtask
5 timeout 0
```

**Explanation.** Lines 1 and 8 are plain synchronous code, so they run first, in order. During the script, line 3 handed a timer to the environment (its callback will go to the **task** queue), while lines 5 and 6 placed callbacks in the **microtask** queue. When the script ends and the stack is empty, the loop empties the microtask queue (promise callback first, because it was queued first), and only then takes the timer task. That is why `setTimeout(..., 0)` loses to every promise callback: **a delay of 0 does not mean "now", it means "as a later task"**.

```js file="order-nested.js" run
setTimeout(() => console.log("timeout A"), 0);

setTimeout(() => {
  console.log("timeout B");
  Promise.resolve().then(() => console.log("microtask from B"));
}, 0);

setTimeout(() => console.log("timeout C"), 0);
```

```output
timeout A
timeout B
microtask from B
timeout C
```

Each timer callback is a separate **task**. After task B finishes and the stack is empty, the loop empties the microtask queue (running the microtask B created) *before* it takes task C. The rule "microtasks run after every task" explains the order.

| Step | What runs | Stack | Microtask queue | Task queue |
|---|---|---|---|---|
| 1 | Script schedules three timers, then ends | empty | empty | A, B, C |
| 2 | Task A: prints `timeout A` | empty after | empty | B, C |
| 3 | Task B: prints `timeout B`, queues a microtask | empty after | microtask B | C |
| 4 | Microtask checkpoint: prints `microtask from B` | empty | empty | C |
| 5 | Task C: prints `timeout C` | empty | empty | empty |

## The call stack in action

Each function call pushes a frame; each return pops it. A function that calls another waits (stays on the stack) until the inner one returns.

```js file="call-stack.js" run
function third() {
  console.log("  third runs");
}

function second() {
  console.log(" second starts");
  third();
  console.log(" second ends");
}

function first() {
  console.log("first starts");
  second();
  console.log("first ends");
}

first();
```

```output
first starts
 second starts
  third runs
 second ends
first ends
```

| Step | Event | Call stack (top at right) |
|---|---|---|
| 1 | `first()` called | `first` |
| 2 | `second()` called | `first`, `second` |
| 3 | `third()` called | `first`, `second`, `third` |
| 4 | `third` returns | `first`, `second` |
| 5 | `second` returns | `first` |
| 6 | `first` returns | empty |

This stack is what you see in a stack trace (Sheet 01, Section 10), and it is why an infinite recursion ends in a `RangeError: Maximum call stack size exceeded`: the stack has a size limit.

## Blocking: why timers are only "at least"

Because there is one thread, a long synchronous task delays everything queued behind it, including timers and clicks.

```js file="blocking.js" run
const start = Date.now();

setTimeout(() => {
  const elapsed = Date.now() - start;
  console.log("timer asked for 10 ms, ran after 60+ ms:", elapsed >= 60);
}, 10);

while (Date.now() - start < 60) {
  // busy-wait: nothing else can run during this loop
}
console.log("busy loop finished");
```

```output
busy loop finished
timer asked for 10 ms, ran after 60+ ms: true
```

The timer was due after 10 ms, but the loop held the call stack for 60 ms, so the callback had to wait. In a browser the same loop would freeze the page: no clicks, no scrolling. **The delay in `setTimeout` is a minimum, never a promise.** The raw millisecond count is not printed because it varies from run to run; the comparison with 60 does not.

## Callbacks, and why promises were invented

Early asynchronous JavaScript used **callbacks** only. Doing three things in sequence meant nesting:

```js file="callback-pyramid.js" run
function step(name, done) {
  setTimeout(() => {
    console.log("finished", name);
    done();
  }, 10);
}

step("A", () => {
  step("B", () => {
    step("C", () => {
      console.log("all done");
    });
  });
});
```

```output
finished A
finished B
finished C
all done
```

Each step starts only inside the callback of the previous one. With error handling at every level this "pyramid of doom" becomes unreadable, and errors cannot be caught with a single `try/catch` (Sheet 01, Section 10, Mistake 4). **Promises** (Section 3) give the same ordering as a flat chain with one error path, and `async/await` (Section 4) makes it read like ordinary code.

## Common mistakes in this section

#### Mistake 1: Expecting `setTimeout(fn, 0)` to run immediately

**Why it is wrong.** The callback is a task; it waits for the current script and all microtasks.

```js bad run
let ready = false;
setTimeout(() => {
  ready = true;
}, 0);
console.log("ready right after setTimeout:", ready);
```

```output
ready right after setTimeout: false
```

```js good run
let ready = false;
setTimeout(() => {
  ready = true;
  console.log("ready inside the callback:", ready);
}, 0);
console.log("ready right after setTimeout:", ready);
```

```output
ready right after setTimeout: false
ready inside the callback: true
```

**Symptom.** Code that depends on the result runs too early. **Fix:** put the dependent code *inside* the callback (or use promises, Section 3). **Diagnosis:** number your `console.log` lines to see the real order.

#### Mistake 2: Reading a result before the async code has produced it

**Why it is wrong.** The value is assigned later, but the reading line runs now.

```js bad run
let user;
setTimeout(() => {
  user = { name: "Asha" };
}, 10);
console.log(user);
```

```output
undefined
```

```js good run
function loadUser(callback) {
  setTimeout(() => callback({ name: "Asha" }), 10);
}
loadUser((user) => {
  console.log(user);
});
```

```output
{ name: 'Asha' }
```

**Symptom.** `undefined`, or `Cannot read properties of undefined` one line later. **Diagnosis:** ask "when is this variable assigned, and when is it read?" If the assignment is inside an asynchronous callback, everything that needs the value must run *after* it.

#### Mistake 3: Busy-waiting instead of scheduling

**Why it is wrong.** A loop that waits for time to pass blocks everything, including the thing you are waiting for (in a browser, even the rendering).

```js bad run
function sleepBlocking(ms) {
  const end = Date.now() + ms;
  while (Date.now() < end) {}
}

setTimeout(() => console.log("timer"), 0);
sleepBlocking(30);
console.log("after blocking sleep");
```

```output
after blocking sleep
timer
```

**Symptom.** The page freezes; timers and clicks respond late. **Fix:** use a timer or a promise-based `wait` function (Section 3), which hands the waiting to the environment.

#### Mistake 4: Assuming two asynchronous operations finish in the order they started

**Why it is wrong.** Completion order depends on how long each takes, not on the order you started them.

```js bad run
setTimeout(() => console.log("first request (slow) finished"), 30);
setTimeout(() => console.log("second request (fast) finished"), 5);
```

```output
second request (fast) finished
first request (slow) finished
```

**Symptom.** Results appear in the wrong order, or an older response overwrites a newer one (a real bug in search boxes; Section 9 solves it). **Diagnosis:** log when each operation *starts* and *finishes*.

# 3. Promises

## Learning objectives for this section

- Explain what a promise is and name its three states.
- Create promises with `new Promise`, `Promise.resolve` and `Promise.reject`.
- Use `.then()`, `.catch()` and `.finally()`, and explain what each returns.
- Explain how values, thrown errors and returned promises flow along a chain.

## Conceptual explanation

A **promise** is an object that stands for a value that is not available *yet*. Instead of waiting for the value, you receive the promise immediately, and attach callbacks that will run when the value arrives or when the operation fails. A promise is always in exactly one of three states.

[[widths 1.1 3.0 2.4]]
| State | Meaning | Can change? |
|---|---|---|
| **pending** | The operation has not finished yet | Yes, to one of the two below |
| **fulfilled** | The operation succeeded and the promise holds a **value** | No, never again |
| **rejected** | The operation failed and the promise holds a **reason** (normally an `Error`) | No, never again |

A fulfilled or rejected promise is **settled**. Once settled, a promise never changes state or value. This is what makes promises dependable: no matter how many times or how late you ask, you get the same answer.

## Creating a promise

**Syntax.** `new Promise((resolve, reject) => { ... })`. The function you pass is the **executor**. It runs **immediately and synchronously**, receiving two functions: call `resolve(value)` to fulfil the promise, or `reject(reason)` to reject it. Only the **first** call counts; later calls are ignored. If the executor throws, the promise is rejected with that error. Two shortcuts exist: `Promise.resolve(value)` makes an already fulfilled promise and `Promise.reject(reason)` an already rejected one.

```js file="promise-create.js" run
const p = new Promise((resolve) => {
  console.log("executor runs now");
  resolve("done");
});

console.log("after constructor:", p);

p.then((value) => console.log("then received:", value));

console.log("end of script");
```

```output
executor runs now
after constructor: Promise { 'done' }
end of script
then received: done
```

**Line by line.** The executor on lines 1 to 4 runs **synchronously** during `new Promise`, so line 2 prints first. `resolve("done")` makes the promise fulfilled at once, which `console.log` shows on line 6 as `Promise { 'done' }`. Line 8 registers a callback with `.then()`, **but even though the promise is already fulfilled, the callback does not run immediately**: it is placed in the microtask queue and runs after the synchronous script finishes, which is why `end of script` prints before `then received: done`. Promise callbacks are **always asynchronous**.

## Function deep dive: `.then()`, `.catch()` and `.finally()`

**What they are.** Methods on every promise that register callbacks for its outcome.

**Syntax.** `promise.then(onFulfilled, onRejected)`, `promise.catch(onRejected)`, `promise.finally(onFinally)`.

**Parameters.**

- `onFulfilled(value)`: called with the promise's value if it fulfils.
- `onRejected(reason)`: called with the reason if it rejects. `.catch(fn)` is shorthand for `.then(undefined, fn)`.
- `onFinally()`: called with **no arguments** whether the promise fulfilled or rejected, for cleanup (hiding a spinner).

**Return value, the most important point.** Each of these methods returns a **new promise**. That is what makes **chaining** possible. The new promise settles according to what your callback does:

[[widths 2.6 3.4]]
| Your callback... | The new promise... |
|---|---|
| returns a normal value `v` | fulfils with `v` |
| returns another promise | **adopts** it: waits, then fulfils or rejects the same way |
| throws an error | rejects with that error |
| is skipped (no matching handler for the outcome) | passes the original outcome along unchanged |

`.catch()` therefore **recovers**: if its callback returns normally, the chain continues as fulfilled. `.finally()` is different: its return value is ignored (unless it throws), and the original outcome continues through it.

**How it works.** When the promise settles, the engine puts the matching callback into the microtask queue. The callback runs with the value or reason, and whatever it does settles the next promise in the chain.

```js file="promise-chain.js" run
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

Promise.resolve(2)
  .then((n) => n * 3)
  .then((n) => wait(10).then(() => n + 1))
  .then((n) => {
    throw new Error("boom " + n);
  })
  .then(() => console.log("skipped"))
  .catch((error) => {
    console.log("caught:", error.message);
    return "recovered";
  })
  .finally(() => console.log("finally runs"))
  .then((value) => console.log("final value:", value));
```

```output
caught: boom 7
finally runs
final value: recovered
```

| Link | Receives | Does | Next promise |
|---|---|---|---|
| start | n/a | `Promise.resolve(2)` | fulfilled with `2` |
| `.then` 1 | `2` | returns `2 * 3` | fulfilled with `6` |
| `.then` 2 | `6` | returns a promise that waits 10 ms and then gives `6 + 1` | adopts it: fulfilled with `7` |
| `.then` 3 | `7` | throws `Error("boom 7")` | **rejected** |
| `.then` 4 | (skipped) | rejection passes through; callback never runs | rejected |
| `.catch` | the error | logs, returns `"recovered"` | fulfilled with `"recovered"` |
| `.finally` | nothing | logs; its return value is ignored | fulfilled with `"recovered"` (passed through) |
| `.then` 5 | `"recovered"` | logs `final value: recovered` | fulfilled with `undefined` |

The helper on line 1, `wait(ms)`, is worth memorising: it **wraps a callback-style timer in a promise**. It calls `resolve` after the delay, with no value. You will use the same pattern throughout the sheet.

## Converting callback code to a promise

```js file="promisify.js" run
function loadUserCallback(id, callback) {
  setTimeout(() => {
    if (id === 0) {
      callback(new Error("No such user"));
    } else {
      callback(null, { id, name: "User " + id });
    }
  }, 10);
}

function loadUser(id) {
  return new Promise((resolve, reject) => {
    loadUserCallback(id, (error, user) => {
      if (error) {
        reject(error);
      } else {
        resolve(user);
      }
    });
  });
}

loadUser(7)
  .then((user) => console.log("loaded:", user.name))
  .then(() => loadUser(0))
  .catch((error) => console.log("failed:", error.message));
```

```output
loaded: User 7
failed: No such user
```

This is the standard recipe for wrapping an old callback API (in which the first callback argument is an error, the style used by many Node.js functions): create the promise, call the old function, and call `resolve` or `reject` from its callback. The chain at the bottom has **one** `.catch()` that handles failure from either call.

## Common mistakes in this section

#### Mistake 1: Forgetting to `return` inside `.then()`

**Why it is wrong.** The next link receives whatever the callback returns. A block body without `return` returns `undefined`.

```js bad run
Promise.resolve(5)
  .then((n) => {
    n * 2;
  })
  .then((value) => console.log("received:", value));
```

```output
received: undefined
```

```js good run
Promise.resolve(5)
  .then((n) => {
    return n * 2;
  })
  .then((value) => console.log("received:", value));
```

```output
received: 10
```

**Symptom.** `undefined` further down the chain. This is the same mistake as the `map` callback without `return` in Sheet 02. **Diagnosis:** log inside each `.then` and check what it returns. For promises it matters even more: forgetting to return a **promise** makes the chain stop waiting for it.

#### Mistake 2: No `.catch()`: the unhandled rejection

**Why it is wrong.** A rejection nobody handles is an error nobody sees. In Node.js it terminates the program; in a browser it appears as an *Uncaught (in promise)* error in the Console, and the interface may be left stuck in a loading state.

```js bad run throws
Promise.reject(new Error("request failed"));
console.log("script finished normally");
```

```output
script finished normally
Error: request failed
```

```js good run
Promise.reject(new Error("request failed")).catch((error) => {
  console.log("handled:", error.message);
});
```

```output
handled: request failed
```

**Symptom.** Silent failure in a browser (a spinner that never stops), or a crash in Node.js with `unhandledRejection`. **Fix:** end every chain with `.catch()` (or use `try/catch` with `await`, Section 4). **Diagnosis:** look for *Uncaught (in promise)* messages in the browser Console.

#### Mistake 3: Calling a function instead of passing it to `.then()`

**Why it is wrong.** `.then(f())` runs `f` **now** and passes its return value; `.then` ignores values that are not functions.

```js bad run
function sayDone() {
  console.log("done (printed immediately!)");
}
Promise.resolve("x").then(sayDone());
console.log("script end");
```

```output
done (printed immediately!)
script end
```

```js good run
function sayDone() {
  console.log("done (printed after the promise)");
}
Promise.resolve("x").then(sayDone);
console.log("script end");
```

```output
script end
done (printed after the promise)
```

**Symptom.** The code runs before the promise settles. This is the same trap as `setTimeout(greet(), 1000)` in Sheet 01 and `addEventListener("click", handler())` in Sheet 03. **Diagnosis:** parentheses after a function name mean "call it now".

#### Mistake 4: Expecting `resolve` and `reject` to be usable more than once

**Why it is wrong.** A promise settles exactly once; later calls are silently ignored.

```js bad run
const p = new Promise((resolve, reject) => {
  resolve("first");
  resolve("second");
  reject(new Error("too late"));
});
p.then((value) => console.log("value:", value));
```

```output
value: first
```

**Symptom.** A later result or error vanishes without any message. **Diagnosis:** if a promise seems to ignore a rejection, check whether code ran `resolve` earlier. Settle exactly once, normally by `return`ing right after calling `resolve` or `reject`.
