# Modular Matrix Workflows

The Modular Matrix Workflow(`trix`) is a layer based, modular, and extensible workflow system that works between project documents, source code, and agentic steerings tasks.

The core idea begind `trix` is to utilize Matrix frameworks, and full scope mathematics to create a management and dispatch system that agenticly coordinates and steers projects.

Each coding framework has its strengths, and weaknesses, but the Matrix(`trix`) is a hybrid of all of them. The matrix is the missing, unifying pice for agentic steering and project contextual management.

## Rules

- titles must be encased in square brackets `[]`
- Matrix can only have 3 nodes per row
- Each matrix box can only be a total of 9 nodes

## Design

The system is designed to be an optimal, centre hub to act as agentic systems multi layered database. It can be used to document, coordinate, share information, execute workflows, define tasks, and coordinate tasks.

### ABSOLUTE PURPOSE
`trix` acts as a full scope dispatch ecosystem that steers the project as a whole.

### Modulation features
- The Matrix(`trix`) blocks must be designed to interact, merge, integrate, and transform other matrix blocks.
- The Matrix(`trix`) blocks must be able to be “plugged in” to other Matrix(`trix`) blocks.


## DICTIONARY

### MODIFER DICTIONARY

- `block`, `bk`[MODIFIER]: a 3x3 matrix grouping of its `parent`(node block, 9ode block, super block).
- `cluster`, `cl`[MODIFIER]: is a 9x9 matrix grouping of its `parent`(node block, 9ode block, super block).
- `line`, `ln` [MODIFIER]: a 1x3 matrix grouping of its `parent`(node, 9ode, super).

### VALUE DICTIONARY
- `node`, `nd`[VALUE]: a single block of data that inside of a matrix.
- `9ode`, `9o`[VALUE]:is any grouping of node blocks that makes up another 3x3 matrix grouping of node blocks.
- `super`, `su`[VALUE]: is a 3x3 matrix grouping of 9odes.

### DESIGN DICTIONARY

- `hub`: a central `trix` module 9ode that serves as the central organizational matrix for all agentic services
- `titl`: a 4 letter title of the `trix` matrix block. Titles must adgere to a strict 4 letter specification.

## matrix examples

> Single Block Matrix
```
==[titl]=======
| [1] [2] [3] | 
| [4] [5] [6] |
| [7] [8] [9] | 
===============
```

---

> markdown files

- | [1](markddown/1.md) | [2](markddown/2.md) | [3](markddown/3.md) |
- | [4](markddown/4.md) | [5](markddown/5.md) | [6](markddown/6.md) |
- | [7](markddown/7.md) | [8](markddown/8.md) | [9](markddown/9.md) |

---

> matrix configs

[1](toml) [2](yaml) [3](json)
[4](toml) [5](yaml) [6](json)
[7](toml) [8](yaml) [9](json)

> source code

[1](code/1.cpp) [2](code/2.cpp) [3](code/3.cpp)
[4](code/4.cpp) [5](code/5.cpp) [6](code/6.cpp)
[7](code/7.cpp) [8](code/8.cpp) [9](code/9.cpp)

> agentic steerings

[1](steering/1.md) [2](codex/AGENTS.md) [3](claude-code/CLAUDE.md)
[4](steering/4.md) [5](codex/AGENTS.md) [6](claude-code/CLAUDE.md)
[7](steering/7.md) [8](codex/AGEBTS.md) [9](claude-code/CLAUDE.md)
