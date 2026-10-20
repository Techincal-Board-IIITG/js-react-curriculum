# 12. Mini Projects

## Mini projects overview

Five console programs, ordered from easier to harder. **Projects 1 to 3 are the core workload; projects 4 and 5 are extensions.** None needs anything beyond this sheet plus the toolbox below. Each specification tells you what to build, how to break it into milestones, and how to verify that you are finished. Resist looking for finished solutions online: the learning is in the struggle.

[[widths 0.5 2 1.1 1.1]]
| # | Project | Difficulty | Scope |
|---|---|---|---|
| 1 | Number guessing game | Easy | Core |
| 2 | Interactive calculator | Easy to medium | Core |
| 3 | Student grade calculator | Medium | Core |
| 4 | Quiz application | Medium | Extension |
| 5 | Banking simulator | Medium to hard | Extension |

## Toolbox: reading input in a console program

Console programs need to *ask* the user things. Save this helper as `ask.mjs` in your project folder and treat it as a black box for now: it uses `async` functions and Promises, which Sheet 04 explains. All you need to know is that `await ask("text")` pauses, shows the text, and gives back whatever line the user typed, **as a string**.

```js file="ask.mjs"
import readline from "node:readline";

const reader = readline.createInterface({ input: process.stdin });
const lines = reader[Symbol.asyncIterator]();

export async function ask(question) {
  process.stdout.write(question);
  const { value, done } = await lines.next();
  return done ? "" : value;
}

export function closeInput() {
  process.stdin.pause();
}
```

```js file="demo.mjs"
import { ask, closeInput } from "./ask.mjs";

const name = await ask("Your name? ");
const age = Number(await ask("Your age? "));
console.log(`Hello ${name}, next year you will be ${age + 1}.`);
closeInput();
```

Name your program files with the **`.mjs`** extension so Node treats them as ES modules, which allows `import` and top-level `await`. Run with `node demo.mjs`. The helper returns an empty string when input ends, so a program reading piped input never hangs. Browser alternative: `prompt("text")` returns a string (or `null` if cancelled) and works in the console.

## Function deep dive: `Math.random()` and `Math.floor()`

**What they are.** Functions on the built-in `Math` object, available in browsers and Node.js.

**`Math.random()`** takes no parameters and returns a number **at least 0 and strictly less than 1**, such as `0.7312...`. The sequence is pseudo-random: good for games, not for security.

**`Math.floor(x)`** takes one number and returns the largest whole number not greater than `x`: `Math.floor(3.9)` is `3`, and `Math.floor(-3.1)` is `-4`. Related: `Math.round` (nearest), `Math.ceil` (round up), `Math.trunc` (drop the decimals).

**Combining them: a random whole number from `min` to `max` inclusive.** `Math.random()` gives `[0, 1)`. Multiplying by the count of possible values (`max - min + 1`) gives `[0, count)`. `Math.floor` turns that into `0 ... count - 1`. Adding `min` shifts the range.

```js file="random-int.js" run
function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

let allValid = true;
for (let i = 0; i < 1000; i++) {
  const roll = randomInt(1, 6);
  if (roll < 1 || roll > 6 || !Number.isInteger(roll)) {
    allValid = false;
  }
}
console.log(allValid);
```

```output
true
```

Because the output is random, the example does not print rolls; it checks 1000 of them against the rule and prints `true` if all are whole numbers from 1 to 6. For `randomInt(1, 6)`, the pieces are: `Math.random() * 6` is in `[0, 6)`, `Math.floor` gives `0` to `5`, and `+ 1` gives `1` to `6`. The common mistake is writing `Math.round(Math.random() * 5) + 1`: `round` makes the first and last values half as likely as the others.

:::: project Number guessing game | Difficulty: Easy | Core
##### Objective
Practise loops, conditionals, input validation and small functions in the simplest complete interactive program.

##### Problem statement
The computer secretly picks a whole number from 1 to 100. The player tries to guess it. After each guess the program says whether the guess was too low or too high. The player has 7 attempts. After the game ends, the program offers another round.

##### Required features
- Pick the secret with a `randomInt(min, max)` function like the one above.
- Read guesses with `ask()`, convert them with `Number()`, and reject anything that is not a whole number from 1 to 100 *without* using up an attempt.
- Report "too low", "too high" or success, and show the attempts remaining.
- End on a correct guess (show how many attempts it took) or after 7 failed attempts (reveal the secret).
- Ask "Play again? (y/n)" and repeat or quit accordingly.

##### Technical constraints
- Plain JavaScript in Node.js, `.mjs` files, no external packages.
- Keep *logic* and *input/output* separate: a pure function `checkGuess(secret, guess)` returns `"low"`, `"high"` or `"correct"` and never prints.
- Use `const` unless a variable must change. No `var`.

##### Expected behavior
```text file="Sample session"
I am thinking of a number from 1 to 100. You have 7 attempts.
Guess #1: 50
Too low. 6 attempts left.
Guess #2: abc
Please enter a whole number from 1 to 100.
Guess #2: 75
Too high. 5 attempts left.
Guess #3: 62
Correct! You needed 3 attempts.
Play again? (y/n) n
```

##### Suggested milestones
1. Hard-code the secret as `42`; accept one guess; print the verdict.
2. Add a loop so the player can guess repeatedly until correct.
3. Add input validation and the attempt limit.
4. Replace `42` with the random secret.
5. Add the replay question using a `do...while` loop.

##### Edge cases
- Empty input, text, `3.5`, `0`, `101`, negative numbers.
- Entering the same guess twice.
- Winning on the very last attempt versus losing on it.
- Answering the replay question with `Y`, `yes`, or an empty line.

##### Acceptance criteria
- [ ] Invalid input never costs an attempt and always produces a clear message.
- [ ] `checkGuess(50, 30)` returns `"low"`, `checkGuess(50, 70)` returns `"high"`, `checkGuess(50, 50)` returns `"correct"` (verify with `console.log` lines).
- [ ] The game ends after exactly 7 wrong valid guesses.
- [ ] The secret is always between 1 and 100 across 20 test games.
- [ ] No variable is declared with `var`; no `==` appears in the code.

##### Stretch goals
- Three difficulty levels with different ranges and attempt limits.
- Track and display the best (fewest-attempts) score across rounds.
- After a win, print the *optimal* number of guesses for the range (hint: halving).

##### Concepts practiced
Sections 3 to 7 and 10 (validation, `Number()`, `Math.random`, loops, functions, `Number.isInteger`).
::::

:::: project Interactive calculator | Difficulty: Easy to medium | Core
##### Objective
Practise `switch`, functions that return values, error handling with `throw` and `try/catch`, and numeric input handling.

##### Problem statement
Build a command-line calculator that repeatedly asks for two numbers and an operator, prints the result, and continues until the user types `q`.

##### Required features
- Supported operators: `+`, `-`, `*`, `/`, `%`, `**`.
- A `calculate(a, operator, b)` function that **returns** the result, and **throws** an `Error` for division or remainder by zero and for unknown operators.
- Accept the word `ans` in place of a number to reuse the previous result.
- Handle invalid numbers with a message, then ask again.
- Type `q` at any prompt to quit with a goodbye message.

##### Technical constraints
- Use `switch` inside `calculate`. Do **not** use `eval()` or `new Function()`: they execute arbitrary text as code and are a security risk.
- Call `calculate` inside `try/catch` in the main loop; the catch prints `error.message` and the loop continues.
- Convert input with `Number()` after trimming; reject empty strings explicitly.

##### Expected behavior
```text file="Sample session"
First number (or ans/q): 12
Operator (+ - * / % **): /
Second number (or ans/q): 4
12 / 4 = 3
First number (or ans/q): ans
Operator (+ - * / % **): *
Second number (or ans/q): 0
3 * 0 = 0
First number (or ans/q): 5
Operator (+ - * / % **): /
Second number (or ans/q): 0
Error: Cannot divide by zero.
First number (or ans/q): q
Goodbye!
```

##### Suggested milestones
1. `calculate()` alone, tested with `console.log` calls.
2. Read two numbers and an operator once; print the result.
3. Wrap in a loop; add `q` to quit.
4. Add `try/catch` and error messages.
5. Add `ans` memory.

##### Edge cases
- Division and remainder by zero; `0 / 5`; negative numbers; very large powers (`2 ** 1024` is `Infinity`).
- Operator typed with spaces or an unsupported symbol.
- `ans` used before any calculation exists.
- Floating-point results such as `0.1 + 0.2`: decide how to display them (for example `toFixed` only for display).

##### Acceptance criteria
- [ ] `calculate(6, "*", 7)` returns `42`; `calculate(2, "**", 10)` returns `1024`; `calculate(7, "%", 3)` returns `1`.
- [ ] `calculate(1, "/", 0)` throws an `Error` (check with `try/catch`).
- [ ] Bad input never crashes the program.
- [ ] Results from `calculate` are numbers, not strings (check with `typeof`).
- [ ] The code contains no `eval`.

##### Stretch goals
- Support a one-line expression such as `12 / 4` by splitting the input on spaces.
- Keep a history of the last five calculations and show it when the user types `h`.
- Format very large and very small results sensibly.

##### Concepts practiced
`switch`, functions, `throw`/`try`/`catch`, `Number()` and `NaN`, loops, the string-versus-number trap.
::::

:::: project Student grade calculator | Difficulty: Medium | Core
##### Objective
Combine accumulating variables, validated loops, `if/else if` chains and well-separated functions into a small report generator.

##### Problem statement
Ask for a student's name and how many subjects they took. Then read one mark (0 to 100) per subject. Print a report with the total, average, percentage, overall letter grade, highest mark, lowest mark and pass/fail result.

##### Required features
- Validate the subject count (a whole number from 1 to 10) and every mark (a number from 0 to 100); re-ask on invalid input.
- Track the total, highest mark, lowest mark and number of failed subjects **while reading**, using variables updated in the loop.
- A function `letterGrade(percentage)` returning `"A"` (90 or more), `"B"` (80 to 89.99), `"C"` (70 to 79.99), `"D"` (60 to 69.99), `"E"` (40 to 59.99) or `"F"` (below 40).
- Overall result is **Pass** only if no subject is below 40; otherwise **Fail**, even if the average is high.
- Display averages with two decimal places.

##### Technical constraints
- No arrays are required (they arrive in Sheet 02): use running variables.
- `letterGrade` and a `readMark(promptText)` helper must be separate functions; `letterGrade` must not print.
- Do not hard-code the number of subjects.

##### Expected behavior
```text file="Sample report"
Student name: Meera
Number of subjects: 3
Mark for subject 1: 82
Mark for subject 2: 35
Mark for subject 3: 90

----- Report for Meera -----
Total:      207 / 300
Average:    69.00
Percentage: 69.00%
Grade:      D
Highest:    90
Lowest:     35
Result:     FAIL (1 subject below 40)
```

##### Suggested milestones
1. Implement and test `letterGrade` with `console.log` calls at the boundaries (39, 40, 59.99, 60, 89.99, 90).
2. Read exactly three marks and total them.
3. Generalise to *n* subjects and add validation.
4. Track highest, lowest and failures.
5. Format the report.

##### Edge cases
- A single subject; marks of exactly `0`, `40` and `100`.
- Marks such as `85.5` (decide whether decimals are allowed; document your decision).
- All marks identical; the failing subject also being the lowest mark.
- Initialising highest and lowest correctly (what start values work for any valid mark?).

##### Acceptance criteria
- [ ] `letterGrade(90)` is `"A"`, `letterGrade(89.99)` is `"B"`, `letterGrade(40)` is `"E"`, `letterGrade(39.9)` is `"F"`.
- [ ] The example session above produces exactly that report.
- [ ] A student with marks 100, 100, 39 receives a **Fail** result despite an average above 79.
- [ ] Invalid marks (`-5`, `101`, `abc`, empty) are rejected and re-asked.
- [ ] Highest and lowest are correct when the first mark is the highest or the lowest.

##### Stretch goals
- Support weighted subjects (each subject has a credit weight).
- After the report, offer to enter another student and show the class average of all entered students.
- Replace the `if/else if` chain with a lookup table and compare the two designs.

##### Concepts practiced
Accumulator pattern, `for` loops, `if/else if` ordering, validation helpers, `toFixed` for display, returning versus printing.
::::

:::: project Quiz application | Difficulty: Medium | Extension
##### Objective
Practise iterating over structured data, scoring logic and feedback using the language features of this sheet.

##### Problem statement
Run a multiple-choice quiz of at least five questions in the terminal, give feedback after each answer, and show a final score with a rating.

##### Required features
- Store the questions in the data structure provided below; do not hard-code each question into separate statements.
- Show each question with lettered options (`A`, `B`, `C`, `D`), accept an answer in either case, and reject invalid letters without penalty.
- Tell the player whether the answer was right and, if wrong, what the correct answer was.
- Show the final score as `x / n` and a percentage, plus a rating chosen with a `switch` or `if` chain.
- Offer to retake the quiz.

##### Technical constraints
- Loop over the questions with `for...of`.
- A pure function `isCorrect(question, letter)` decides correctness; a function `ratingFor(percentage)` returns the rating text.
- Starter data (you extend it to at least five questions of your own on a topic you know well):

```js file="questions.mjs"
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
];
```

##### Expected behavior
```text file="Sample session"
Q1. Which keyword declares a variable that cannot be reassigned?
  A) var
  B) let
  C) const
  D) static
Your answer: c
Correct!

Q2. What does typeof null return?
  A) null
  B) object
  C) undefined
  D) number
Your answer: a
Wrong. The correct answer was B) object.

Score: 1 / 2 (50%) - Keep practising!
```

##### Suggested milestones
1. Print one question and read one answer from the starter data.
2. Loop through all questions.
3. Add scoring and feedback.
4. Add validation and the rating.
5. Add the retake loop.

##### Edge cases
- Lowercase answers, answers with spaces, empty input, a letter beyond the available options (a question with only three options).
- A quiz where the player gets every answer right or every answer wrong.
- Percentages that are not whole numbers (1 of 3 correct).

##### Acceptance criteria
- [ ] At least five questions, all stored in the data array.
- [ ] `isCorrect(questions[0], "C")` is `true` and `isCorrect(questions[0], "A")` is `false`.
- [ ] Answers are accepted case-insensitively.
- [ ] Invalid input does not skip or penalise a question.
- [ ] The final percentage is rounded to a whole number for display only.

##### Stretch goals
- Shuffle the order of the questions on each attempt without repeating any.
- Add a timer message showing how many seconds the whole quiz took (research `Date.now()`).
- Track the best score across retakes.

##### Concepts practiced
`for...of`, property access with dot and bracket notation, string methods, functions with distinct responsibilities, `switch`.
::::

:::: project Banking simulator | Difficulty: Medium to hard | Extension
##### Objective
Use closures to keep private state, throw and catch meaningful errors, and design a menu-driven program with clean separation between logic and interface.

##### Problem statement
Simulate a bank account in the terminal. The user can deposit, withdraw, check the balance and view the transaction history. Money is stored as whole **cents** to avoid floating-point rounding problems.

##### Required features
- `createAccount(owner, openingBalanceCents)` returns an object of functions: `deposit(cents)`, `withdraw(cents)`, `getBalance()`, `getHistory()`. The balance and history must be **private** (kept in the closure), not directly accessible.
- `deposit` and `withdraw` throw an `Error` for amounts that are not positive whole numbers; `withdraw` also throws when funds are insufficient.
- Every successful transaction is recorded with its type, amount and the balance afterwards.
- A menu loop (`switch`) offers deposit, withdraw, balance, history and quit. User input in dollars (like `12.50`) is converted to cents once, at the boundary.
- Errors from the account are caught in the menu loop and shown as friendly messages; they never crash the program.

##### Technical constraints
- The account logic file must not use `console.log` or `ask`; it only returns values or throws. The menu file does all the printing.
- Convert dollars to cents with `Math.round(Number(text) * 100)`; display cents as dollars with a helper `formatMoney(cents)`.
- Use `const` wherever possible, and `let` only for the private balance and menu state.

##### Expected behavior
```text file="Sample session"
Account owner: Ravi
1) Deposit  2) Withdraw  3) Balance  4) History  5) Quit
Choose: 1
Amount in dollars: 100.50
Deposited $100.50. New balance: $100.50
Choose: 2
Amount in dollars: 500
Error: Insufficient funds. Balance is $100.50.
Choose: 4
1. deposit   $100.50  balance $100.50
Choose: 5
Goodbye, Ravi!
```

##### Suggested milestones
1. Implement `createAccount` with `getBalance` and `deposit`; test with `console.log` lines.
2. Add `withdraw` with validation and errors.
3. Add history recording.
4. Build `formatMoney` and the dollars-to-cents conversion.
5. Build the menu loop with `try/catch`.

##### Edge cases
- Deposit or withdraw of `0`, a negative amount, `abc`, an empty string, `1.999` (rounds to `200` cents, which you must decide how to handle) and a huge number.
- Withdrawing exactly the whole balance; withdrawing one cent more than the balance.
- Creating two accounts and confirming they do not share balances.
- Trying to read `account.balance` directly (must be `undefined`).

##### Acceptance criteria
- [ ] After `createAccount("Ravi", 1000)`, `deposit(500)` then `getBalance()` returns `1500`.
- [ ] `withdraw(2000)` on a balance of `1500` throws an `Error` and leaves the balance at `1500`.
- [ ] `account.balance` is `undefined`; the only way to change money is via the functions.
- [ ] `formatMoney(1050)` returns `"$10.50"`, `formatMoney(5)` returns `"$0.05"`.
- [ ] Two accounts are fully independent.

##### Stretch goals
- Add `transfer(otherAccount, cents)` between two accounts, ensuring either both changes happen or neither does.
- Add an overdraft limit option, chosen when the account is created.
- Print the history as an aligned table.

##### Concepts practiced
Closures and private state, `throw`/`try`/`catch`/`finally`, separation of logic from I/O, integer arithmetic for money, `switch`.
::::
