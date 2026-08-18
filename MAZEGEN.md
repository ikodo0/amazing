# mazegen

A standalone maze generator and solver. Generates rectangular mazes — perfect
(exactly one path between any two cells) or with loops — and returns the wall
structure as a grid of cells. No dependency on any rendering or CLI code.

## Installation

```sh
pip install mazegen-1.0.0-py3-none-any.whl
```

To rebuild the package from source:

```sh
make build          # or: python3 -m build
```

## Instantiating the generator

```python
from mazegen import MazeGenerator

generator = MazeGenerator(
    width=20,
    height=15,
    seed=42,          # int | None — omit or None for a non-reproducible maze
    is_perfect=True,  # False adds loops (10% of walls knocked down)
    has_pattern=True, # carve the "42" pattern of closed cells
    mode="dfs",       # "dfs" (backtracker) or "dfs_gt" (Growing Tree)
)
maze = generator.generate()
```

`generate()` returns a fresh `Maze` and can be called repeatedly on the same
generator; with a fixed `seed`, every call returns an identical maze.

### Watching it build

`generate_steps()` is the same algorithm as `generate()`, but it is a generator
that yields the maze after every carve. `generate()` simply runs it to the end,
so both produce an identical maze for a given seed.

```python
for maze in generator.generate_steps():
    draw(maze)          # called once per carved wall
```

The yielded object is always the *same* `Maze`, mutated in place — so there is
no copying, and iteration costs no extra memory. If you need snapshots of
earlier states, copy the grid yourself.

`mode` accepts only `"dfs"` or `"dfs_gt"`; anything else raises `ValueError`.
If `has_pattern` is set but the maze is too small to hold the "42" pattern
(minimum 10x7), a message is printed to stderr and the maze is generated
without it.

## Accessing the structure

`Maze` holds `grid`, a list of rows of `Cell`. Each `Cell` has `x`, `y`, and
`walls` — a bitmask of the **closed** walls, built from the exported constants
`N = 1`, `E = 2`, `S = 4`, `W = 8`.

```python
from mazegen import N, E, S, W

maze.width, maze.height          # dimensions
cell = maze.cell(3, 4)           # or: maze[3, 4]
cell.walls                       # e.g. 0b1010 -> east and west closed
maze.has_wall(3, 4, N)           # True if the north wall is closed
maze.in_bounds(3, 4)             # bounds check
list(maze.neighbors(3, 4))       # [(x, y, direction), ...] in-bounds only
maze.carve(3, 4, N)              # open a wall on both sides at once
maze.uncarve(3, 4, N)            # close it again on both sides
```

`carve()` and `uncarve()` always update both adjacent cells, so the grid can
never end up with a wall that exists on one side only.

## Getting a solution

```python
from mazegen import solve

path = solve(maze, (0, 0), (19, 14))   # [(0, 0), (1, 0), ...] shortest route
```

`solve()` runs a breadth-first search, so the returned path is always a
shortest one. It raises `ValueError` when start equals end or when no path
exists.

To turn the cell list into direction letters, use the exported `STEP` mapping:

```python
from mazegen import STEP

letters = {1: "N", 2: "E", 4: "S", 8: "W"}
moves = "".join(
    letters[STEP[path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]]]
    for i in range(len(path) - 1)
)
```

## Other exported helpers

| Symbol | Purpose |
| --- | --- |
| `to_text(maze)` | The hexadecimal grid as a string, one row per line. |
| `txt_generate(config, maze, path)` | Write the full output file (grid, entry, exit, path). |
| `find_open_areas(maze)` | Top-left corners of every fully open 3x3 block; an empty list means the corridor-width rule holds. |
| `Maze`, `Cell` | The data types, for type annotations. |

`txt_generate()` takes any object exposing `ENTRY`, `EXIT` and `OUTPUT_FILE`
attributes, so it does not tie the module to a particular config class.

## Full example

```python
from mazegen import MazeGenerator, solve, to_text, find_open_areas

maze = MazeGenerator(20, 15, seed=42, is_perfect=False, mode="dfs_gt").generate()
print(to_text(maze))
print(solve(maze, (0, 0), (19, 14)))
assert find_open_areas(maze) == []
```

## Requirements

Python 3.10 or later. No third-party dependencies.
