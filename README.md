*This project has been created as part of the 42 curriculum by papilaz.*

# Fly-In — Autonomous Drone Routing Simulation

## Description

**Fly-In** is a Python simulation that routes a fleet of autonomous drones from a
central base (`start_hub`) to a target location (`end_hub`) through a weighted,
constrained hub network.  
Each zone on the network has a type (`normal`, `priority`, `restricted`, `blocked`)
that affects movement cost, occupancy rules, and the number of turns required to
cross it. Connections between hubs can also carry a configurable capacity limit.

The simulator reads a plain-text map file, parses the graph, plans collision-free
paths for every drone using a **space-time A\*** algorithm backed by a
**reverse-Dijkstra heuristic**, then plays back the result in a **Pygame graphical
interface** while printing the standard turn-by-turn output to the terminal.

### Goals

- Route all drones from `start_hub` to `end_hub` in the minimum number of turns.
- Respect zone occupancy limits, link capacity limits, and movement costs.
- Output each simulation turn in the required `D<ID>-<zone>` format.
- Provide an interactive visual representation of the routing process.

---

## Algorithm Choices and Implementation Strategy

### Parsing (`parsing.py`)

The map file is read and stripped of comments (`#`), then validated in several
passes:

1. **Structural checks** — mandatory directives (`start_hub`, `end_hub`,
   `nb_drone`) must appear exactly once.
2. **Semantic checks** — hub names must be unique, coordinates must be unique,
   no dashes in names, no self-loops, no duplicate connections, no isolated
   start/end hubs.
3. **Hub and connection objects** are instantiated and wired as a bidirectional
   neighbour graph.

### Pathfinding (`algo/astar.py`)

**Reverse Dijkstra** is run once from `end_hub` across the entire graph to
compute an admissible, consistent heuristic (true cost to goal) for every hub.
Zone movement costs are:

| Zone type   | Move cost | Turns to cross |
|-------------|-----------|----------------|
| `priority`  | 0.5       | 1              |
| `normal`    | 1.0       | 1              |
| `restricted`| 2.0       | 2              |
| `blocked`   | —         | impassable     |

**Space-Time A\*** is then run sequentially for each drone. The search space is
`(hub, turn)` pairs. At each state a drone may:

- **Wait** at its current hub (+1 turn, cost 1.0) if the hub has remaining
  capacity.
- **Move** to a neighbour if both the link and the destination hub have remaining
  capacity at the relevant turns.

Reservations (hub slots and link slots) are updated after each drone is planned,
so later drones automatically route around earlier ones — a **Cooperative Pathfinding**
strategy that avoids conflicts without backtracking.

### Visual Representation (`py_game/scren.py`)

The Pygame interface provides two pages:

- **Start page** — left panel lists available map files per difficulty
  (Easy / Medium / Hard / Challenger); right panel shows map metadata or
  parsing error messages with word-wrapping.
- **Hub page** — hub graph is scaled to fit a central display zone using a
  uniform-scale, margin-aware projection. Connections are drawn as coloured lines,
  hubs as circles labelled with their names, drones as sprites (or red circles as
  fallback). Pressing **Space** triggers the A\* planner and starts the animation.

The colour scheme adapts to the selected difficulty:

| Difficulty  | Colour           |
|-------------|------------------|
| Easy        | Green `(80,220,130)` |
| Medium      | Blue `(70,140,255)`  |
| Hard        | Red `(235,75,85)`    |
| Challenger  | Gold `(255,195,50)`  |

---

## Instructions

### Requirements

- Python 3.10 or later
- [uv](https://github.com/astral-sh/uv) (recommended) **or** pip

### Installation

```bash
# Install dependencies (uses uv by default — see Makefile)
make install
```

### Running the Simulation

```bash
# Launch the interactive GUI (map-selection start page)
make run

# Launch directly on a specific map file
python main.py maps/easy/01_linear_path.txt

# Launch in debug mode (pdb)
make debug
```

### Controls

| Action | Effect |
|--------|--------|
| Click a map name | Load that map |
| Click Easy / Medium / Hard / Challenger | Switch difficulty folder |
| Click **Start** | Go to the hub page |
| Press **Space** | Run A\* and start drone animation |
| Click **Home** | Return to start page |
| Click **Quit** | Exit the application |

### Optional Flag

```bash
# Print per-turn link and zone capacity usage alongside the schedule
python main.py maps/hard/03_ultimate_challenge.txt --capacity-info
```

### Lint & Type Checking

```bash
make lint         # flake8 + mypy (standard flags)
make lint-strict  # flake8 + mypy --strict (optional)
```

### Clean

```bash
make clean  # removes __pycache__, .mypy_cache
```

---

## Example Input and Expected Output

### Input file (`maps/easy/01_linear_path.txt`)

```
nb_drones: 2
start_hub: hub 0 0 [color=green]
end_hub: goal 10 0 [color=yellow]
hub: mid 5 0
connection: hub-mid
connection: mid-goal
```

### Terminal output

```
Path of file : maps/easy/01_linear_path.txt

D1-mid D2-mid
D1-goal D2-goal
```

Each line represents one simulation turn. `D<ID>-<zone>` means drone `D<ID>`
arrived at `<zone>` during that turn. Drones that do not move are omitted.

---

## Resources

### References

- **A\* Search Algorithm** — Hart, P.E.; Nilsson, N.J.; Raphael, B. (1968).
  *A Formal Basis for the Heuristic Determination of Minimum Cost Paths.*
  IEEE Transactions on Systems Science and Cybernetics.
- **Cooperative Pathfinding** — Silver, D. (2005). *Cooperative Pathfinding.*
  AAAI Workshop on Multi-Agent Pathfinding.
- **Python `heapq` documentation** — <https://docs.python.org/3/library/heapq.html>
- **Pygame documentation** — <https://www.pygame.org/docs/>
- **PEP 257 — Docstring Conventions** — <https://peps.python.org/pep-0257/>
- **mypy documentation** — <https://mypy.readthedocs.io/>

### AI Usage

AI assistance (Claude) was used for the following tasks:

- **Docstrings and README** — generating PEP 257 compliant Google-style
  docstrings for all functions and classes, and drafting this README structure.
- **Debugging** — helping identify edge cases in the space-time A\* reservation
  logic (restricted-zone double-turn link booking).
- **Code review suggestions** — reviewing type hint completeness and flake8
  compliance.

All AI-generated content was reviewed, tested, and adapted by the author before
inclusion. The core algorithm design, architecture decisions, and validation logic
were developed independently.
