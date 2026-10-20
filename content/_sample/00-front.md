---
number: 00
title: Engine Smoke Test
subtitle: Checking every block type renders
track: js
time: test
goals:
  - See highlighted code with line numbers
  - See callouts, tables, diagrams
---

# 1. Everything at once

Intro paragraph with `inline code`, **bold**, *italic* and a [link](https://developer.mozilla.org/en-US/docs/Web/JavaScript). Check marks ✓ and arrows → work.

## A code block

```js file="demo.js" run
const prices = [100, 200, 300];
const discounted = prices.map(price => price * 0.9);
console.log(discounted);
```

```output
[ 90, 180, 270 ]
```

```js bad
const x = 1
x = 2;
```

```tree
src/
├── App.jsx
└── main.jsx
```

::: tip Short tip
Callouts split by row and keep their colour bar.
:::

::: mistake Careless loops
- First bullet in callout
- Second bullet
:::

| Step | Operation | State |
|---|---|---|
| 1 | Initial | `count = 0` |
| 2 | Click | `count = 1` |

```diagram
flow
Source file -> *Parser -> Flowables -> PDF
```

```diagram
tree
App
  Header
  Main
    Card | props: title
    Card
```

```diagram
sequence
actors: Browser | Server
Browser -> Server: GET /data
Server --> Browser: 200 JSON
note: The response is a Promise result
```

:::: project Tiny project | Easy | Core
##### Objective
Do the thing.
- [ ] first checkbox
- [ ] second checkbox
::::
