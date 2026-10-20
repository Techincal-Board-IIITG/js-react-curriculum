# 6. Set E: Challenge Solutions

#### E1. Password strength checker

```js file="e1-password.js" run
function checkPassword(password) {
  let hasLower = false;
  let hasUpper = false;
  let hasDigit = false;
  let hasSymbol = false;

  for (const ch of password) {
    if (ch >= "a" && ch <= "z") {
      hasLower = true;
    } else if (ch >= "A" && ch <= "Z") {
      hasUpper = true;
    } else if (ch >= "0" && ch <= "9") {
      hasDigit = true;
    } else {
      hasSymbol = true;
    }
  }

  const rules = [
    [password.length >= 8, "Use at least 8 characters"],
    [hasLower, "Add a lowercase letter"],
    [hasUpper, "Add an uppercase letter"],
    [hasDigit, "Add a digit"],
    [hasSymbol, "Add a symbol"],
  ];

  let score = 0;
  const problems = [];
  for (const rule of rules) {
    if (rule[0]) {
      score++;
    } else {
      problems.push(rule[1]);
    }
  }
  return { score, problems };
}

for (const pw of ["abc", "Abcdef12!", ""]) {
  const result = checkPassword(pw);
  console.log(JSON.stringify(pw), result.score, result.problems.length);
}
```

```output
"abc" 1 4
"Abcdef12!" 5 0
"" 0 5
```

Look for: all five rules implemented with loops and conditions (no regular expressions), `problems` containing one message per failed rule, and the empty string handled without special-casing.

#### E2. Decimal to binary

```js file="e2-binary.js" run
function toBinary(n) {
  if (!Number.isInteger(n) || n < 0) {
    throw new Error("Expected a non-negative whole number");
  }
  if (n === 0) {
    return "0";
  }
  let result = "";
  let rest = n;
  while (rest > 0) {
    result = (rest % 2) + result;
    rest = Math.floor(rest / 2);
  }
  return result;
}

console.log(toBinary(0), toBinary(1), toBinary(5), toBinary(255));

let firstMismatch = null;
for (let n = 0; n <= 100; n++) {
  if (toBinary(n) !== n.toString(2) && firstMismatch === null) {
    firstMismatch = n;
  }
}
console.log(firstMismatch === null ? "all correct" : firstMismatch);

try {
  toBinary(-1);
} catch (error) {
  console.log(error.message);
}
```

```output
0 1 101 11111111
all correct
Expected a non-negative whole number
```

Point out to students that `(rest % 2) + result` works because `result` starts as a *string*, so `+` concatenates. If `result` started as a number the digits would be added instead.
