# 12. Revision and Assessment

## Summary of this sheet

Arrays are ordered lists indexed from zero; objects are collections of named properties. Both are **reference values**: `const b = a` shares one value, and spread (`[...a]`, `{ ...o }`) makes only a **shallow** copy, so nested data stays shared. `push`, `pop`, `shift`, `unshift`, `splice`, `sort` and `reverse` **mutate**; `slice`, `map`, `filter`, `concat` and spread do not. The callback methods share one pattern, `callback(value, index, array)`: `map` returns a transformed array of the same length, `filter` keeps elements whose callback is truthy, `find`/`findIndex` return the first match (`undefined`/`-1` if none), `some`/`every` return booleans, and `reduce` folds everything into one value, always with an initial value. `sort` needs a comparator for numbers. Destructuring unpacks, spread expands, rest gathers, template literals embed expressions, `?.` avoids errors on missing data, and `??` supplies defaults only for `null`/`undefined`. `Set` stores unique values and `Map` stores key-value pairs with any key type. **Pure functions** and **immutable updates** keep data predictable, and are the foundation for React state. ES modules split code into files with named and default exports.

## Key syntax reference

[[widths 1.3 3.2 2.2]]
| Topic | Syntax | Notes |
|---|---|---|
| Array literal | `[1, 2, 3]`, `list[0]`, `list.at(-1)`, `list.length` | Last index is `length - 1` |
| Add / remove | `push`, `pop`, `unshift`, `shift`, `splice(i, n, ...items)` | All mutate |
| Copy / slice | `[...list]`, `list.slice(a, b)` | `b` is excluded |
| Search | `includes(x)`, `indexOf(x)`, `find(fn)`, `findIndex(fn)` | `-1` / `undefined` when absent |
| Transform | `map(fn)`, `filter(fn)`, `reduce(fn, init)` | Never forget `return` in a block body |
| Test | `some(fn)`, `every(fn)` | `every` on `[]` is `true` |
| Order | `[...list].sort((a, b) => a - b)` | Copy first; comparator for numbers |
| Object | `{ a: 1 }`, `o.a`, `o["a"]`, `delete o.a`, `"a" in o` | Variable keys need brackets |
| Object helpers | `Object.keys`, `Object.values`, `Object.entries`, `Object.fromEntries` | Return arrays (or an object) |
| Destructure | `const { a, b: c = 1, ...rest } = o`, `const [x, ...ys] = list` | Defaults apply to `undefined` only |
| Spread / rest | `[...a, ...b]`, `{ ...o, k: v }`, `fn(...args)`, `function f(...rest)` | Later properties override |
| Safe access | `a?.b`, `a?.[0]`, `a.fn?.()`, `a ?? b` | `??` keeps `0`, `""`, `false` |
| Collections | `new Set(list)`, `new Map(entries)`, `.size`, `.has`, `.get`, `.set` | Not JSON-serialisable directly |
| Copying deeply | `structuredClone(value)` | Cannot copy functions |
| Modules | `export const x`, `export default f`, `import { x } from "./f.js"`, `import f from "./f.js"` | Include extension and `./` |

## Important terms and definitions

[[widths 1.2 4]]
| Term | Definition |
|---|---|
| Index | Zero-based position of an element in an array |
| Property / key | A named value stored in an object |
| Mutation | Changing an existing array or object in place |
| Shallow copy | A copy of only the top level; nested values are still shared |
| Deep copy | A copy that duplicates nested values too |
| Predicate | A function that returns true or false, such as a `filter` callback |
| Accumulator | The running value carried between `reduce` callback calls |
| Comparator | A function `(a, b)` returning negative, zero or positive, used by `sort` |
| Destructuring | Unpacking array elements or object properties into variables |
| Spread / rest | `...` used to expand a collection / to gather leftovers |
| Nullish | The values `null` and `undefined` |
| Pure function | Same input gives same output, with no side effects |
| Immutability | Updating by creating new values instead of changing existing ones |
| Module | A file with private scope that shares code via `export` and `import` |

## Common mistakes checklist

- [ ] No `sort`, `reverse`, `splice`, `push` or `pop` is applied to data I did not mean to change.
- [ ] Every `map` or `reduce` with a block body has a `return`.
- [ ] Every `reduce` call has an initial value.
- [ ] Every `find` result is checked for `undefined` before use.
- [ ] Numbers are sorted with a comparator.
- [ ] Nested data is copied at **every level I change**.
- [ ] I used `??` rather than `||` where `0`, `""` or `false` are valid values.
- [ ] Functions return new values instead of editing their arguments.
- [ ] Imports use braces for named exports, none for defaults, and include `./` and the extension.
- [ ] I tested every function with an empty array and a single-element array.

## Self-assessment questions

1. What are `[1, 2, 3].at(-1)` and `[1, 2, 3][3]`? (Section 2)
2. What does `push` return, and what does `splice(1, 1)` return? (Section 2)
3. After `const a = [1]; const b = a; b.push(2);`, what is `a`? Why? (Section 2)
4. After `const c = { ...o }`, can changing `c.address.city` affect `o`? When? (Section 3)
5. Write one expression turning `[1, 2, 3]` into `[2, 4, 6]` and one keeping only the odd numbers. (Section 4)
6. What does the `reduce` callback return on each step, and what happens to it? (Section 4)
7. Why does `["10", "9", "1"].map(parseInt)` not return `[10, 9, 1]`? (Section 4)
8. How would you sort `[10, 9, 1]` ascending without changing the original? (Section 4)
9. Rewrite `const name = user.name; const age = user.age;` with destructuring and a default age of `18`. (Section 5)
10. What do `0 ?? 5`, `0 || 5`, `null ?? 5` and `user?.address?.city` give for a user with no address? (Section 5)
11. Which dots are spread and which are rest in `const f = (...args) => [...args, ...args]`? (Section 5)
12. How do you remove duplicates from an array? How do you count word frequencies? (Section 6)
13. Why can a `Map` have an object as a key but a plain object cannot? (Section 6)
14. Is `Math.max(...[])` a safe expression? Why or why not? (Section 9)
15. Rewrite `function add(list, x) { list.push(x); return list; }` as a pure function. (Section 7)
16. Why does React need updates that create new arrays and objects? (Section 7)
17. How do `import { f } from "./a.js"` and `import f from "./a.js"` differ? (Section 8)

## Practical completion checklist

- [ ] I typed and ran every worked example and compared my predictions with the output.
- [ ] I completed exercise sets A to D and at least one challenge from set E.
- [ ] I completed core projects 1, 2 and 3, and my functions pass their acceptance criteria without mutating input.
- [ ] I can explain shallow versus deep copies to a classmate with an example.
- [ ] I can write `map`, `filter`, `find`, `some`, `every` and `reduce` calls from memory and say what the callback returns.
- [ ] I can run a three-file module program in Node.js.
- [ ] (Optional) I completed one or both extension projects.

## Official documentation

- [MDN: Indexed collections (arrays)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Indexed_collections)
- [MDN: Keyed collections (Map and Set)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Keyed_collections)
- [MDN: Working with objects](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Working_with_objects)
- [MDN: JavaScript modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)
- [MDN: Array reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array)
- [MDN: Object reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object)
- [MDN: Set reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Set)
- [MDN: Map reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map)
- [MDN: Destructuring assignment](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment)
- [MDN: Spread syntax](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax)
- [MDN: Optional chaining](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining)
- [MDN: Nullish coalescing](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing)
