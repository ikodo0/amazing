*This project has been created as part of the 42 curriculum by dchernyk, jrookyar.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator written in Python 3.10+.

The program reads a plain-text configuration file, generates a maze of the
requested size, solves it, and displays it in a graphical window built on
MiniLibX. The maze is also encoded in a hexadecimal wall format (one digit per
cell) for storage on disk. The generator can produce either a **perfect** maze
(exactly one path between any two cells) or an **imperfect** one (extra loops),
always keeps corridors at most 2 cells wide, and carves a visible **"42"
pattern** out of fully closed cells in the middle of the grid.

The project is split into two independent parts:

| Path | Purpose |
| --- | --- |
| [src/mazegen/](src/mazegen/) | The reusable, pip-installable generation library (`mazegen`). No rendering, no CLI. |
| [app/main/](app/main/) | Application logic: configuration parsing ([config.py](app/main/config.py)), shared state ([state.py](app/main/state.py)) and the three screens ([screens/](app/main/screens/)). |
| [app/renderer/](app/renderer/) | A from-scratch MLX rendering toolkit: render loop, screens, components, textures, fonts. |
| [a_maze_ing.py](a_maze_ing.py) | The entry point: config → maze → solution → graphical window. |

## Instructions

### Requirements

* Python 3.10 or later
* Linux/X11 with the MLX shared library available (the program opens a
  graphical window; the `mazegen` library on its own does not need it)

### Installation

```sh
make install
```

This creates a `.venv/` virtual environment, installs the dependencies from
[requirements.txt](requirements.txt) (`flake8`, `mypy`, `pydantic`, `build`,
`freetype-py`), installs the project itself in editable mode, and installs the
bundled `mlx-2.2-py3-none-any.whl` wheel.

### Running

```sh
make run                                      # uses config.txt
.venv/bin/python3 a_maze_ing.py config.txt    # or run it directly
```

The program parses the configuration, generates and solves the maze, and opens
the graphical window described in [Visual representation](#visual-representation).
Note that the maze parameters are read from the `CONFIG` environment variable
(defaulting to `config.txt`), which is what `make run` sets; the command-line
argument is currently only checked for presence.

Any error — missing file, bad syntax, out-of-bounds entry/exit, unsolvable maze
— is reported on `stderr` with exit code 1, never as a traceback.

### Other Makefile targets

| Target | Effect |
| --- | --- |
| `make install` | Create the venv and install everything. |
| `make run` | Run the generator on `config.txt`. |
| `make debug` | Run the generator under `pdb`. |
| `make lint` | `flake8 .` + `mypy .` with the subject's flags. |
| `make lint-strict` | `flake8 .` + `mypy --strict .`. |
| `make build` | Build the `mazegen` wheel and sdist into `dist/`. |
| `make clean` | Remove `__pycache__`, `.mypy_cache`, `.pytest_cache`. |
| `make fclean` | `clean` + remove the venv. |
| `make re` | `fclean` + `install`. |

Linting is also enforced on every pull request by
[.github/workflows/lint.yml](.github/workflows/lint.yml).

## Configuration file format

The configuration file contains one `KEY=VALUE` pair per line. Blank lines and
lines starting with `#` are ignored. Any line that is not a comment and does
not contain `=` is a fatal error. Values are parsed and validated with
`pydantic` in [app/main/config.py](app/main/config.py).

### Required keys

| Key | Type | Constraint | Example |
| --- | --- | --- | --- |
| `WIDTH` | int | `> 0` | `WIDTH=20` |
| `HEIGHT` | int | `> 0` | `HEIGHT=15` |
| `ENTRY` | `x,y` | inside the grid, `!= EXIT` | `ENTRY=0,0` |
| `EXIT` | `x,y` | inside the grid, `!= ENTRY` | `EXIT=19,14` |
| `PERFECT` | bool | `True` / `False` | `PERFECT=True` |
| `OUTPUT_FILE` | str | — | `OUTPUT_FILE=maze.txt` |

These are exactly the six keys the subject requires; everything else has a
default, so a configuration file containing only these will run.

### Optional keys

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `SEED` | int | `None` | Seed for the RNG. Same seed + same settings ⇒ identical maze. Omitted ⇒ non-reproducible. |
| `PATTERN` | bool | `True` | Carve the "42" pattern of closed cells. |
| `MODE` | `dfs` \| `dfs_gt` | `dfs` | Generation algorithm (see below). Any other value is rejected. |
| `WINDOW_WIDTH` | int | `1000` | Window width in pixels, `> 0`. |
| `WINDOW_HEIGHT` | int | `950` | Window height in pixels, `> 0`. A taller window allows a larger maze to be drawn without being clipped. |

### Example ([config.txt](config.txt))

```ini
WIDTH=25
HEIGHT=25
ENTRY=0,0
EXIT=24,24
#IGNORAR_PLEASE
#SEED=1
OUTPUT_FILE=maze.txt
PERFECT=False
PATTERN=True
MODE=dfs_gt
WINDOW_HEIGHT=950
WINDOW_WIDTH=1000
```

## Output file format

The maze is serialised to the file named by `OUTPUT_FILE` by
`mazegen.txt_generate()`. Each cell is written as one uppercase hexadecimal
digit encoding its **closed** walls (bit set = wall present):

| Bit | Value | Direction |
| --- | --- | --- |
| 0 (LSB) | 1 | North |
| 1 | 2 | East |
| 2 | 4 | South |
| 3 | 8 | West |

So `F` is a fully closed cell, `3` has walls only to the north and east, and
`A` has walls to the east and west.

Cells are written row by row, one row per line. After the grid comes an empty
line, then the entry coordinates, the exit coordinates, and — after another
empty line — the shortest path from entry to exit as a string of `N`, `E`, `S`,
`W` letters.

```
97911111117
856AC2EEC07
83FAFAFFF83
AAFEF857FAE
AAFFFAFFFAB
A857FEFD546
A853FBFFFD3
AC3C545397A
850795502BA
C7C5457EC46

0,0
10,2

SEENEEEEEESESE
```

Wall data is always coherent between neighbours: carving goes through
`Maze.carve()`, which clears the wall bit on both cells at once, so a cell can
never have an east wall while its eastern neighbour has no west wall.

## Maze generation algorithm

### The algorithms

Both modes are randomized spanning-tree carvers over the grid graph, sharing
one loop in `MazeGenerator.generate()`:

* **`dfs` — recursive backtracker (iterative).** Always expands from the *last*
  cell on the stack. Produces long, winding corridors and few junctions.
* **`dfs_gt` — Growing Tree.** Picks a *random* cell from the stack instead of
  the last one. This is the Growing Tree algorithm with a uniformly random
  selection rule, which behaves close to Prim's algorithm: many short branches
  and frequent junctions.

The loop starts from `(0, 0)`, repeatedly picks an unvisited neighbour of the
current cell, carves the wall between them, and marks it visited; when a cell
has no unvisited neighbours it is removed from the stack. Because every cell is
reached exactly once, the result is a spanning tree — a **perfect maze**, fully
connected with no isolated cells and exactly one path between any two cells.

### Imperfect mazes

When `PERFECT=False`, `knock_walls()` collects every remaining interior wall
(scanning only the north and west wall of each cell, so each wall is considered
once), randomly samples 10% of them, and carves them. Each carve is immediately
tested by `creates_open_area()`; if it would create a fully open 3×3 block, the
wall is put straight back with `uncarve()`. That keeps corridors at most 2
cells wide while adding loops. `find_open_areas()` is exported so the whole
grid can be re-checked afterwards.

### The "42" pattern

Before carving starts, the cells of the `PATTERN` bitmap are computed at the
centre of the grid, added to a *protected* set and pre-marked as visited, so
the carving loop never enters them and they stay fully closed (`F`). They are
also excluded from `knock_walls()`. The pattern needs at least a 10×7 grid
(an 8×5 glyph plus a 1-cell margin); on a smaller maze the pattern is skipped
and a message is printed to `stderr`, as the subject requires.

### Solving

`solve()` is a breadth-first search from entry to exit over the carved graph,
reconstructing the route through a parent map. BFS is used rather than DFS
because BFS is guaranteed to return the **shortest** path, which matters for
imperfect mazes where several routes exist. It raises `ValueError` if entry and
exit are equal or if no path exists.

### Why these choices

* **The randomized backtracker** is simple, allocation-light, needs no
  union-find or priority queue, and cannot produce an invalid maze: it is a
  spanning tree by construction, so connectivity and perfection come for free
  rather than being something to verify afterwards.
* **Growing Tree** was added as a second mode because it reuses the exact same
  loop with a one-line change to the cell-selection rule, and gives a visibly
  different maze texture — a cheap way to satisfy the "multiple algorithms"
  bonus.
* **Carving from a fully closed grid** (rather than adding walls) makes the
  neighbour-coherence requirement structurally impossible to violate.
* **Post-processing for imperfection** keeps the perfect maze as the trusted
  base case, so the 3×3 open-area rule only has to be enforced in one place.

## Visual representation

The maze is displayed in a graphical window, drawn with MiniLibX. There is no
terminal renderer.

[app/renderer/](app/renderer/) is a small rendering toolkit written from
scratch on top of MLX: a render loop, a screen/scene factory, components
(tiles, text, buttons), an XPM texture loader, and a TrueType font rasterizer
via `freetype-py`. It knows nothing about mazes — it only draws components.
[app/main/screens/](app/main/screens/) builds the three actual screens on top
of it, and [a_maze_ing.py](a_maze_ing.py) registers them with the
`ScreenFactory` and starts the loop.

### Screens and interactions

Everything is driven with the mouse (left click).

| Screen | Controls |
| --- | --- |
| **Main menu** ([MainMenu.py](app/main/screens/MainMenu.py)) | **Start** — open the maze. **Reload** — re-read the configuration file and rebuild the generator, so a new size, mode or seed can be applied without restarting the program. The title cycles through hues each time the screen is left, and Mario hops back and forth along the bottom — `on_enter()` is called once per frame, so it drives the sprite from elapsed time rather than a frame count, keeping the speed the same on any machine. |
| **Maze** ([Maze.py](app/main/screens/Maze.py)) | The maze itself, plus a burger button in the corner that opens the in-game menu. |
| **In-game menu** ([GameMenu.py](app/main/screens/GameMenu.py)) | **Redraw** — generate a new maze with a fresh random seed and return to it. **Color** — apply a random colour offset to the wall texture. **Path** — show or hide the shortest path from entry to exit. **Animate** — generate a new maze, but carved step by step so the algorithm is visible. **Exit** — back to the main menu. |

### How the maze is drawn

Each cell is expanded into a 3×3 block of tiles, so the whole grid becomes a
`(2·width + 3) × (2·height + 3)` tile field: the corners and the wall segments
that are still closed are painted, the cell centre and every carved wall are
left empty. Rather than submitting thousands of draw calls per frame,
`bake_maze_walls()` blits the wall texture into one `MemoryTexture` once and
hands the renderer a single `Tile` — the maze is one image from then on, which
is what makes the colour offset and the redraw cheap.

The shortest path is drawn on top as red connector rectangles between cell
centres, and it is revealed **progressively**: `on_enter()` appends one segment
per frame, so the solution animates from the entry to the exit rather than
appearing at once.

The path is hidden on start and toggled by **Path** in the in-game menu. The
button flips `show_path` on the shared state and re-enters the maze screen;
`on_mount()` rebuilds the components, so hiding drops the segments and showing
replays the animation. The solution is always computed regardless of
visibility, so the output file is unaffected.

The entry and exit are marked by 16×16 sprites drawn in the centre tile of
their cell — Mario at the entry, a gold coin at the exit — so both stay
identifiable even when they are interior cells rather than corners.
`cell_rect()` converts cell coordinates into that centre tile, using the same
grid arithmetic as `bake_maze_walls()`, which is why the markers line up
exactly with the ends of the drawn path. Both sprites are XPM files in
[assets/textures/](assets/textures/) and use `c None` for their transparent
pixels, which land on the empty cell centre the wall baking leaves behind.

### Animated generation

`MazeGenerator.generate_steps()` is the generation algorithm as a generator: it
yields the maze after every carve, and `generate()` just runs it to completion,
so both give an identical maze for a given seed. Because `carve()` mutates the
maze in place, every step yields the *same* object — no copying, no extra
memory.

**Animate** stores that generator on the shared state instead of a finished
maze, which is the only difference from **Redraw**. MLX owns the event loop, so
the animation cannot sleep; `on_enter()` — called once per frame — advances the
generator 8 carves and re-bakes the walls.
When it raises `StopIteration` the screen solves the maze and writes the output
file, then falls back to revealing the solution path one segment per frame. A
25×25 maze is 605 carves, so it animates over about 76 frames.

Solving is deferred deliberately: a partly carved maze still has isolated
cells, so the breadth-first search would find no path.

## Reusable module: `mazegen`

Everything needed to generate and solve a maze lives in
[src/mazegen/](src/mazegen/) and has no dependency on the rendering or CLI
code. It is packaged as `mazegen` and can be installed into any other project:

```sh
pip install mazegen-1.0.0-py3-none-any.whl
```

To rebuild the package from source:

```sh
make build          # or: python3 -m build
```

### Instantiating the generator

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

### Accessing the structure

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

### Getting a solution

```python
from mazegen import solve

path = solve(maze, (0, 0), (19, 14))   # [(0, 0), (1, 0), ...] shortest route
```

`solve()` raises `ValueError` when start equals end or when no path exists.
To turn the cell list into direction letters, use the exported `STEP` mapping:

```python
from mazegen import STEP

letters = {1: "N", 2: "E", 4: "S", 8: "W"}
moves = "".join(
    letters[STEP[path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]]]
    for i in range(len(path) - 1)
)
```

### Other exported helpers

| Symbol | Purpose |
| --- | --- |
| `to_text(maze)` | The hexadecimal grid as a string, one row per line. |
| `txt_generate(config, maze, path)` | Write the full output file (grid, entry, exit, path). |
| `find_open_areas(maze)` | Top-left corners of every fully open 3×3 block; an empty list means the corridor-width rule holds. |
| `Maze`, `Cell` | The data types, for type annotations. |

### Full example

```python
from mazegen import MazeGenerator, solve, to_text, find_open_areas

maze = MazeGenerator(20, 15, seed=42, is_perfect=False, mode="dfs_gt").generate()
print(to_text(maze))
print(solve(maze, (0, 0), (19, 14)))
assert find_open_areas(maze) == []
```

## Team and project management

### Roles

| Member | Responsibility |
| --- | --- |
| **dchernyk** | Maze domain: the `mazegen` package (grid, wall model, DFS/Growing Tree generation, imperfect-maze pass, open-area detection, "42" pattern, BFS solver), the `pydantic` configuration parser and validation, the output file writer, packaging, Makefile and CI lint setup. |
| **jrookyar** | Rendering: the MLX renderer library (render loop, screens, components, XPM textures, TrueType fonts), the graphical front-end and its assets, MLX packaging in the Makefile, the file-format specification document. |

The split was deliberate: one clean interface (`MazeGenerator` → `Maze`)
between the two halves meant we could work in parallel with almost no merge
conflicts, and it is the same boundary the subject asks for in the
reusable-module requirement.

### Planning

Work was organised as milestones M0–M6 in
[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md), each split into a *blue*
(maze/logic) and an *orange* (rendering/UI) track, with a pull request onto
`main` at the end of each milestone. The architecture diagram was drawn on
Miro.

How it evolved: the logic track ran roughly to plan — the perfect maze (M2.1),
imperfect maze (M3.1), "42" pattern (M3.2), output file (M3.3) and BFS solver
(M4.1) all landed in order. The rendering track turned out to be much larger
than estimated, because building a component system, a texture loader and a
font rasterizer on top of raw MLX is a project in itself, so it stayed a
standalone prototype for most of the project and was only folded into
`a_maze_ing.py` late, together with the menus (M3.4) and the rendered solution
(M4.3). The show/hide toggle (M4.4) is still open. Two requirements also
surfaced later than planned and forced rework of finished code: the "no
corridor wider than 2 cells" rule (which added the open-area detection and the
uncarve step) and entry/exit validation.

### What worked well

* The `MazeGenerator` → `Maze` interface was agreed early and never changed, so
  the two tracks really were independent.
* Carving from a fully closed grid made most of the subject's validity rules
  hold by construction instead of by checking.
* `flake8` + `mypy` in CI on every pull request kept the standard from
  drifting.
* Short-lived `feature/*` branches merged into `dev`, with `main` updated only
  per milestone.

### What could be improved

* Estimate unfamiliar work more conservatively — the renderer was budgeted like
  the generator and was several times larger.
* Read the whole subject for constraints *before* implementing, rather than
  discovering the corridor-width rule after the generator was done.
* Automated tests were pushed to the last milestone (M6.2) instead of being
  written alongside each feature; validation was mostly manual against the
  provided checker script.

### Tools

Git with a `main` ← `dev` ← `feature/*` branch model and pull requests; GitHub
Actions for lint CI; Miro for the architecture diagram and milestone board;
`pydantic` for declarative config validation; `flake8` and `mypy` for the
coding standard; `venv` + `setuptools`/`build` for packaging; MLX with
`freetype-py` for the graphical layer.

## Resources

### Maze generation and graph theory

* [Maze generation algorithm — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
* Jamis Buck, *Maze Generation: Growing Tree algorithm* —
  [weblog.jamisbuck.org](https://weblog.jamisbuck.org/2011/1/27/maze-generation-growing-tree-algorithm.html);
  the reference explanation of how the selection rule turns one loop into a
  whole family of algorithms.
* Jamis Buck, *Mazes for Programmers* (Pragmatic Bookshelf) — grid
  representation and the wall-bitmask idea.
* [Spanning tree — Wikipedia](https://en.wikipedia.org/wiki/Spanning_tree), for
  why a randomized traversal yields a perfect maze.
* [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search),
  for the shortest-path guarantee on unweighted graphs.
* [Think Labyrinth: Maze Algorithms](https://www.astrolog.org/labyrnth/algrithm.htm)

### Python and tooling

* [PEP 8](https://peps.python.org/pep-0008/) and
  [PEP 257](https://peps.python.org/pep-0257/)
* [`typing`](https://docs.python.org/3/library/typing.html) and
  [mypy](https://mypy.readthedocs.io/) documentation
* [pydantic v2 documentation](https://docs.pydantic.dev/latest/) — validators
  and model validation
* [Python Packaging User Guide](https://packaging.python.org/) —
  `pyproject.toml`, `src/` layout, building wheels
* [`random.Random`](https://docs.python.org/3/library/random.html) — seeding
  for reproducibility
* [MiniLibX documentation](https://harm-smits.github.io/42docs/libs/minilibx)
* [freetype-py](https://freetype-py.readthedocs.io/)

### Use of AI

AI assistants were used as a research and review aid, not as a code generator
for the core of the project. Concretely:

* **Explaining algorithms.** Comparing the recursive backtracker, Prim's,
  Kruskal's and Growing Tree, and understanding why a randomized spanning tree
  is exactly a perfect maze. The implementations in
  [src/mazegen/maze.py](src/mazegen/maze.py) were written by hand from that
  understanding.
* **Tooling and boilerplate.** `pyproject.toml` and `src/`-layout packaging
  questions, `mypy`/`flake8` configuration, Makefile and GitHub Actions syntax
  — the tedious configuration work the subject encourages offloading.
* **Debugging aid.** Talking through type errors reported by `mypy --strict`
  and reasoning about edge cases in the open-area detection.
* **Documentation.** Drafting and structuring this README from the actual
  source files, which we then reviewed and corrected.

Everything produced with AI assistance was read, tested and reviewed by both of
us before being merged, and reviewed again by the other member in the pull
request; nothing was merged that we could not explain in full.
