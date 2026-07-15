*This project has been created as part of the 42 curriculum by <kkhachat>, <vgurginy>.*

# A-Maze-ing

## Description

A-Maze-ing is a Python maze generator and solver. Given a configuration
file, it builds a rectangular maze — either a **perfect** maze (a single
path between entry and exit, no loops) or a **Pac-Man-ready** board (fully
connected, open corners and centre, at least two independent routes, rare
or zero dead-ends). The maze always carves a visible "42" pattern made of
fully-closed cells (unless the maze is too small to fit it, in which case
a warning is printed and the pattern is skipped). It exports the result to
a compact hex-encoded file (walls + entry/exit + shortest solution path),
and displays it live in the terminal with interactive controls (regenerate,
show/hide the solution path, rotate wall/pattern colours, replay the
generation as an animation).

The maze-building logic itself (`mazegen.py`) is written as a standalone,
pip-installable module so it can be reused in later projects independently
of this game/CLI.

## Instructions

### Requirements
- Python 3.10+
- Dependencies listed in `requirements.txt` (`pydantic`, plus `flake8`/
  `mypy`/`build` for development)

### Install
```bash
make install
```

### Run
```bash
make run
# equivalent to: python3 a_maze_ing.py config.txt
```
Any config filename is accepted:
```bash
python3 a_maze_ing.py my_other_config.txt
```

### Debug
```bash
make debug
```

### Lint / type-check
```bash
make lint          # flake8 + mypy (required flags)
make lint-strict    # flake8 + mypy --strict
```

### Clean
```bash
make clean
```

### Build the reusable `mazegen` package
The `Makefile` only automates the tasks required by the subject, so the
package build is run directly rather than through a `make` target:
```bash
python3 -m venv venv && source venv/bin/activate
pip install --upgrade build
python3 -m build
```
This produces `dist/mazegen-1.0.0-py3-none-any.whl` and
`dist/mazegen-1.0.0.tar.gz`, built from `pyproject.toml` and `mazegen.py`.
Install and test it in an isolated environment to confirm it works as a
standalone dependency:
```bash
pip install dist/mazegen-1.0.0-py3-none-any.whl
python3 -c "from mazegen import MazeGenerator; m = MazeGenerator(10, 10, (0,0), (9,9)); m.generate(); print(m.solve())"
```

### Verify an output file
An analyzer script provided with the subject can check wall coherence and
whether a maze matches the requested mode:
```bash
python3 maze_analyzer.py maze.txt --max-dead-ends 0
```

## Configuration file format

One `KEY=VALUE` pair per line. Lines starting with `#` are ignored.

| Key | Description | Mandatory | Example |
|---|---|---|---|
| `WIDTH` | Maze width in cells | yes | `WIDTH=25` |
| `HEIGHT` | Maze height in cells | yes | `HEIGHT=18` |
| `ENTRY` | Entry coordinates `x,y` | yes | `ENTRY=0,0` |
| `EXIT` | Exit coordinates `x,y` | yes | `EXIT=24,17` |
| `OUTPUT_FILE` | Path the hex maze is exported to | yes | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | `True` = single-path perfect maze, `False` = Pac-Man board | yes | `PERFECT=False` |
| `ALGORITHM` | `dfs` or `prim` | no (default `dfs`) | `ALGORITHM=prim` |
| `SEED` | Integer seed for reproducible generation | no | `SEED=50` |

Validation performed on load: positive width/height, entry/exit inside
bounds, entry different from exit, and no unknown keys.

## Maze generation algorithm

Two interchangeable carving algorithms are implemented, selected via
`ALGORITHM`:

- **DFS (recursive backtracker, default)** — a randomized depth-first walk
  that carves a spanning tree over the grid. Simple, fast, and naturally
  produces long, winding corridors.
- **Prim's algorithm** — grows the maze from a random cell by repeatedly
  picking a random cell on the frontier and connecting it to the already
  carved structure. Produces a visibly different texture: shorter, more
  branching corridors instead of DFS's long winding ones.

DFS is the default because it is the simplest to reason about and debug
(a single stack, no auxiliary frontier set), and it maps directly onto the
animation feature (each carve step is a stack push). Prim was added
second, as a bonus, specifically to show that the same post-processing
(corner/centre opening, dead-end removal, "42" pattern protection, the
3x3-open-area check) works identically regardless of which raw spanning
tree the maze started from.

Both algorithms respect the reserved "42" pattern cells (never carved
into) and, when `PERFECT=False`, are followed by the same shared steps:
opening the four corners and the centre, and iteratively removing
dead-ends without ever creating an illegal 3x3 open area.

## What is reusable, and how

`mazegen.py` is the standalone module: the `MazeGenerator` class and its
`Cell` grid have no CLI, no printing requirement, and no dependency on
`config_parser.py` or `a_maze_ing.py`. It is packaged separately via
`pyproject.toml` (see Instructions above) and can be installed with pip
independently of this repository's CLI game.

Minimal reuse example:
```python
from mazegen import MazeGenerator

maze = MazeGenerator(width=10, height=10, entry=(0, 0), exit=(9, 9))
maze.generate()
path = maze.solve()          # list of (x, y) from entry to exit
cell = maze.grid[0][0]       # direct access to wall booleans
```

`export_to_hex()`, `print_maze()`, `show_hide_shortest_path()`, and
`rotate_wall_colours()` remain available on the same class for convenience,
but a future project is free to ignore them entirely and only use
`.grid` / `.solve()` if it wants its own display or export format.

## Resources

- [Wikipedia — Maze generation algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
  (recursive backtracker and Prim's algorithm overviews)
- [Python Packaging User Guide](https://packaging.python.org/) — packaging
  a single-module project with `pyproject.toml`
- [pydantic documentation](https://docs.pydantic.dev/) — used for
  configuration validation
- [PEP 621](https://peps.python.org/pep-0621/) — `pyproject.toml` project
  metadata standard used to build `mazegen`

**AI usage:** an AI assistant was used throughout this project as
a code-review and design-discussion partner.

## Team and project management

| Member | Role |
|---|---|
| Khachik | <maze generation core, config parsing> |
| Vahan | <visual display, packaging/README> |

**Planning:** core generation first, then output format, then visuals,
then packaging/bonuses

**What worked well / what could be improved:** splitting generation
and rendering early made debugging the animation feature straightforward;
we underestimated how much of the Pac-Man mode (corners/centre, no dead
ends) needed a shared 3x3-open-area guard, which we only added once we
hit an actual failing case

**Tools used:** Python 3.10, pydantic, flake8, mypy, `build`/setuptools
for packaging, git for version control.
