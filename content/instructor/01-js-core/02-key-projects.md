# 7. Mini Project Reference Implementations

Each project is split into a **logic module** (tested here, no input or output) and a **main program** (interactive). The build script can write all of these to real files (`python3 build.py emit`), and the interactive programs were run with scripted input to confirm they work. Students need `ask.mjs` from the student sheet in the same folder. In the tested listings, everything after the line `// --- self-test ---` is test code and is **not** part of the emitted module.

## Project 1: Number guessing game

```js file="guess-logic.mjs" run emit
export function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

export function checkGuess(secret, guess) {
  if (guess < secret) {
    return "low";
  }
  if (guess > secret) {
    return "high";
  }
  return "correct";
}

// --- self-test ---
console.log(checkGuess(50, 30), checkGuess(50, 70), checkGuess(50, 50));
let inRange = true;
for (let i = 0; i < 2000; i++) {
  const n = randomInt(1, 100);
  if (n < 1 || n > 100 || !Number.isInteger(n)) {
    inRange = false;
  }
}
console.log(inRange);
```

```output
low high correct
true
```

```js file="guess.mjs" emit
import { ask, closeInput } from "./ask.mjs";
import { randomInt, checkGuess } from "./guess-logic.mjs";

const MIN = 1;
const MAX = 100;
const MAX_ATTEMPTS = 7;

async function readGuess(number) {
  while (true) {
    const text = (await ask(`Guess #${number}: `)).trim();
    const value = Number(text);
    if (text !== "" && Number.isInteger(value) && value >= MIN && value <= MAX) {
      return value;
    }
    console.log(`Please enter a whole number from ${MIN} to ${MAX}.`);
  }
}

async function playRound() {
  const secret = randomInt(MIN, MAX);
  console.log(`I am thinking of a number from ${MIN} to ${MAX}.`);
  console.log(`You have ${MAX_ATTEMPTS} attempts.`);
  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    const guess = await readGuess(attempt);
    const verdict = checkGuess(secret, guess);
    if (verdict === "correct") {
      console.log(`Correct! You needed ${attempt} attempts.`);
      return;
    }
    const left = MAX_ATTEMPTS - attempt;
    console.log(`Too ${verdict}. ${left} attempts left.`);
  }
  console.log(`Out of attempts. The number was ${secret}.`);
}

let again;
do {
  await playRound();
  const answer = (await ask("Play again? (y/n) ")).trim().toLowerCase();
  again = answer === "y" || answer === "yes";
} while (again);
closeInput();
```

Marking notes: invalid input must not consume an attempt (the `while (true)` inside `readGuess` guarantees this); `checkGuess` is pure; no `var` or `==`.

## Project 2: Interactive calculator

```js file="calculator-logic.mjs" run emit
export function calculate(a, operator, b) {
  switch (operator) {
    case "+":
      return a + b;
    case "-":
      return a - b;
    case "*":
      return a * b;
    case "/":
      if (b === 0) {
        throw new Error("Cannot divide by zero.");
      }
      return a / b;
    case "%":
      if (b === 0) {
        throw new Error("Cannot take a remainder by zero.");
      }
      return a % b;
    case "**":
      return a ** b;
    default:
      throw new Error(`Unknown operator "${operator}".`);
  }
}

// --- self-test ---
console.log(calculate(6, "*", 7), calculate(2, "**", 10), calculate(7, "%", 3));
for (const [a, op, b] of [[1, "/", 0], [1, "?", 2]]) {
  try {
    calculate(a, op, b);
  } catch (error) {
    console.log(error.message);
  }
}
console.log(typeof calculate(1, "+", 2));
```

```output
42 1024 1
Cannot divide by zero.
Unknown operator "?".
number
```

```js file="calculator.mjs" emit
import { ask, closeInput } from "./ask.mjs";
import { calculate } from "./calculator-logic.mjs";

let previous = null;

async function readOperand(label) {
  while (true) {
    const text = (await ask(label)).trim().toLowerCase();
    if (text === "q") {
      return null;
    }
    if (text === "ans") {
      if (previous === null) {
        console.log("No previous result yet.");
        continue;
      }
      return previous;
    }
    const value = Number(text);
    if (text !== "" && !Number.isNaN(value)) {
      return value;
    }
    console.log("Please enter a number, ans, or q.");
  }
}

while (true) {
  const a = await readOperand("First number (or ans/q): ");
  if (a === null) break;
  const op = (await ask("Operator (+ - * / % **): ")).trim();
  if (op.toLowerCase() === "q") break;
  const b = await readOperand("Second number (or ans/q): ");
  if (b === null) break;
  try {
    const result = calculate(a, op, b);
    console.log(`${a} ${op} ${b} = ${result}`);
    previous = result;
  } catch (error) {
    console.log(`Error: ${error.message}`);
  }
}
console.log("Goodbye!");
closeInput();
```

Marking notes: no `eval`; results are numbers; `null` is used as the quit signal because it can never be a valid operand.

## Project 3: Student grade calculator

```js file="grade-logic.mjs" run emit
export function letterGrade(percentage) {
  if (percentage >= 90) return "A";
  if (percentage >= 80) return "B";
  if (percentage >= 70) return "C";
  if (percentage >= 60) return "D";
  if (percentage >= 40) return "E";
  return "F";
}

// --- self-test ---
for (const p of [90, 89.99, 80, 70, 60, 59.99, 40, 39.9, 0]) {
  console.log(p, letterGrade(p));
}
```

```output
90 A
89.99 B
80 B
70 C
60 D
59.99 E
40 E
39.9 F
0 F
```

```js file="grades.mjs" emit
import { ask, closeInput } from "./ask.mjs";
import { letterGrade } from "./grade-logic.mjs";

async function readNumber(label, min, max, wholeOnly) {
  while (true) {
    const text = (await ask(label)).trim();
    const value = Number(text);
    const ok = text !== "" && !Number.isNaN(value) && value >= min && value <= max;
    if (ok && (!wholeOnly || Number.isInteger(value))) {
      return value;
    }
    console.log(`Enter a ${wholeOnly ? "whole " : ""}number from ${min} to ${max}.`);
  }
}

const name = (await ask("Student name: ")).trim() || "Student";
const count = await readNumber("Number of subjects: ", 1, 10, true);

let total = 0;
let highest = 0;
let lowest = 100;
let failed = 0;
for (let i = 1; i <= count; i++) {
  const mark = await readNumber(`Mark for subject ${i}: `, 0, 100, false);
  total += mark;
  if (mark > highest) highest = mark;
  if (mark < lowest) lowest = mark;
  if (mark < 40) failed++;
}

const percentage = total / count;
const plural = failed === 1 ? "" : "s";
const result = failed === 0 ? "PASS" : `FAIL (${failed} subject${plural} below 40)`;

console.log(`\n----- Report for ${name} -----`);
console.log(`Total:      ${total} / ${count * 100}`);
console.log(`Average:    ${percentage.toFixed(2)}`);
console.log(`Percentage: ${percentage.toFixed(2)}%`);
console.log(`Grade:      ${letterGrade(percentage)}`);
console.log(`Highest:    ${highest}`);
console.log(`Lowest:     ${lowest}`);
console.log(`Result:     ${result}`);
closeInput();
```

Marking notes: because each subject is out of 100, average and percentage coincide; accept an implementation that shows both. Check the "100, 100, 39" case (average 79.67, grade `C`, result **FAIL**). Highest and lowest initial values work for any valid mark because marks are confined to 0 to 100.

## Project 4: Quiz application

```js file="quiz-logic.mjs" run emit
export function isCorrect(question, letter) {
  return letter.trim().toUpperCase() === question.answer;
}

export function ratingFor(percentage) {
  if (percentage >= 80) return "Excellent work!";
  if (percentage >= 50) return "Keep practising!";
  return "Review the material and try again.";
}

// --- self-test ---
const sample = { prompt: "?", options: ["a", "b", "c"], answer: "C" };
console.log(isCorrect(sample, "C"), isCorrect(sample, "c "), isCorrect(sample, "A"));
console.log(ratingFor(100), "|", ratingFor(50), "|", ratingFor(49));
```

```output
true true false
Excellent work! | Keep practising! | Review the material and try again.
```

```js file="questions.mjs" emit
export const questions = [
  {
    prompt: "Which keyword declares a variable that cannot be reassigned?",
    options: ["var", "let", "const", "static"],
    answer: "C",
  },
  {
    prompt: "What does typeof null return?",
    options: ["null", "object", "undefined", "number"],
    answer: "B",
  },
  {
    prompt: "Which operator checks equality without type conversion?",
    options: ["=", "==", "===", "=>"],
    answer: "C",
  },
  {
    prompt: "What does a function return when it has no return statement?",
    options: ["null", "0", "undefined", "an error"],
    answer: "C",
  },
  {
    prompt: "Which loop visits the values of an array?",
    options: ["for...in", "for...of", "while", "switch"],
    answer: "B",
  },
];
```

```js file="quiz.mjs" emit
import { ask, closeInput } from "./ask.mjs";
import { questions } from "./questions.mjs";
import { isCorrect, ratingFor } from "./quiz-logic.mjs";

const LETTERS = ["A", "B", "C", "D"];

async function readAnswer(question) {
  while (true) {
    const text = (await ask("Your answer: ")).trim().toUpperCase();
    const index = LETTERS.indexOf(text);
    if (index !== -1 && index < question.options.length) {
      return text;
    }
    console.log("Please answer with one of the letters shown.");
  }
}

async function runQuiz() {
  let score = 0;
  let number = 0;
  for (const question of questions) {
    number++;
    console.log(`\nQ${number}. ${question.prompt}`);
    for (let i = 0; i < question.options.length; i++) {
      console.log(`  ${LETTERS[i]}) ${question.options[i]}`);
    }
    const letter = await readAnswer(question);
    if (isCorrect(question, letter)) {
      score++;
      console.log("Correct!");
    } else {
      const right = LETTERS.indexOf(question.answer);
      const text = question.options[right];
      console.log(`Wrong. The correct answer was ${question.answer}) ${text}.`);
    }
  }
  const percentage = Math.round((score / questions.length) * 100);
  const rating = ratingFor(percentage);
  console.log(`\nScore: ${score} / ${questions.length} (${percentage}%) - ${rating}`);
}

let again;
do {
  await runQuiz();
  const answer = (await ask("Retake? (y/n) ")).trim().toLowerCase();
  again = answer === "y";
} while (again);
closeInput();
```

## Project 5: Banking simulator

```js file="bank-logic.mjs" run emit
export function formatMoney(cents) {
  const dollars = Math.floor(cents / 100);
  const rest = cents % 100;
  return "$" + dollars + "." + (rest < 10 ? "0" : "") + rest;
}

export function createAccount(owner, openingBalanceCents = 0) {
  let balance = openingBalanceCents;
  const history = [];

  function checkAmount(cents) {
    if (!Number.isInteger(cents) || cents <= 0) {
      throw new Error("Amount must be a positive whole number of cents.");
    }
  }

  return {
    owner,
    deposit(cents) {
      checkAmount(cents);
      balance += cents;
      history.push({ type: "deposit", cents, balance });
      return balance;
    },
    withdraw(cents) {
      checkAmount(cents);
      if (cents > balance) {
        throw new Error(`Insufficient funds. Balance is ${formatMoney(balance)}.`);
      }
      balance -= cents;
      history.push({ type: "withdraw", cents, balance });
      return balance;
    },
    getBalance() {
      return balance;
    },
    getHistory() {
      const copy = [];
      for (const entry of history) {
        copy.push({ type: entry.type, cents: entry.cents, balance: entry.balance });
      }
      return copy;
    },
  };
}

// --- self-test ---
const account = createAccount("Ravi", 1000);
account.deposit(500);
console.log(account.getBalance());
try {
  account.withdraw(2000);
} catch (error) {
  console.log(error.message);
}
console.log(account.getBalance(), account.balance);
console.log(formatMoney(1050), formatMoney(5), formatMoney(0));
const second = createAccount("Mira");
second.deposit(250);
console.log(account.getBalance(), second.getBalance());
console.log(account.getHistory().length);
```

```output
1500
Insufficient funds. Balance is $15.00.
1500 undefined
$10.50 $0.05 $0.00
1500 250
1
```

```js file="bank.mjs" emit
import { ask, closeInput } from "./ask.mjs";
import { createAccount, formatMoney } from "./bank-logic.mjs";

function toCents(text) {
  return Math.round(Number(text) * 100);
}

const owner = (await ask("Account owner: ")).trim() || "Customer";
const account = createAccount(owner, 0);
let running = true;

while (running) {
  console.log("1) Deposit  2) Withdraw  3) Balance  4) History  5) Quit");
  const choice = (await ask("Choose: ")).trim();
  try {
    switch (choice) {
      case "1": {
        const cents = toCents(await ask("Amount in dollars: "));
        const balance = account.deposit(cents);
        console.log(`Deposited ${formatMoney(cents)}.`);
        console.log(`New balance: ${formatMoney(balance)}`);
        break;
      }
      case "2": {
        const cents = toCents(await ask("Amount in dollars: "));
        const balance = account.withdraw(cents);
        console.log(`Withdrew ${formatMoney(cents)}.`);
        console.log(`New balance: ${formatMoney(balance)}`);
        break;
      }
      case "3":
        console.log(`Balance: ${formatMoney(account.getBalance())}`);
        break;
      case "4": {
        let n = 0;
        for (const entry of account.getHistory()) {
          n++;
          const amount = formatMoney(entry.cents);
          const after = formatMoney(entry.balance);
          console.log(`${n}. ${entry.type}  ${amount}  balance ${after}`);
        }
        break;
      }
      case "5":
        running = false;
        console.log(`Goodbye, ${owner}!`);
        break;
      default:
        console.log("Please choose 1 to 5.");
    }
  } catch (error) {
    console.log(`Error: ${error.message}`);
  }
}
closeInput();
```

Marking notes: confirm the balance is not reachable (`account.balance` is `undefined`), that conversion to cents happens once at the boundary, and that errors never crash the menu. A student who stores dollars as decimals should be shown `0.1 + 0.2` and asked to fix it.

# 8. Self-Assessment Answers

1. A browser tab: the browser's engine. `node app.js`: Node.js's engine (also V8). Same language, different environments.
2. `console.log(x)` throws `ReferenceError: Cannot access 'x' before initialization` (temporal dead zone).
3. `"object"`, `"object"`, `"number"`, `"function"`.
4. `0`, `NaN`, `12`, `3.5`.
5. Binary floating-point cannot store 0.1 or 0.2 exactly. Store money as whole cents and format at the end.
6. `null || "x"` is `"x"`; `0 || "x"` is `"x"`. The second is a bug when `0` is a legitimate value (a volume setting, a count).
7. `0 == ""`, `0 == "0"`, `[] == false` are all `true`, yet `"" == "0"` is `false`.
8. Initialisation once; test; body; update; back to the test. The update runs after each body execution, before the next test.
9. `for...of` for values of an array; `for...in` for the keys of an object.
10. `undefined`.
11. After `=>` the braces open a *block body*, so `x, y` is an expression statement and nothing is returned. Wrap the object in parentheses.
12. Each call to `makeCounter` creates a new scope with its own `count`; each returned function closes over its own scope.
13. `var` has one function-wide binding that holds `3` by the time the callbacks run; `let` creates a new binding per iteration.
14. In `forEach`, `return` only ends one callback call (like `continue`) and `break` is impossible; in `for` and `for...of` both work as expected.
15. `a`, `c`, `b`. The timer callback only runs after the current script finishes.
16. `finally` always runs, even after `return`. A thrown string has no `message`, no `name` and no stack trace.
17. Reproduce; read the evidence; form one hypothesis; test by observing; isolate; fix one thing; understand why and prevent recurrence.
