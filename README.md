*This project has been created as part of the 42 curriculum by <wabdella>.*

# Fly-in

## Description

Fly-in is a drone routing simulator whose objective is to transport a fleet of drones from a unique start hub to a unique end hub while minimizing the total number of simulation turns.

The environment is represented as a graph where:
- Vertices represent zones (normal, priority, restricted or blocked).
- Edges represent bidirectional connections between zones.
- Each zone and connection may have capacity constraints.
- Drones move simultaneously while respecting all movement and occupancy rules.

The project implements:
- A custom graph representation.
- A parser for the Fly-in map format.
- A pathfinding system based on Dijkstra and Yen's algorithm.
- A turn-based scheduler that manages conflicts and capacities.
- A graphical visualization of the simulation using Pygame.

---

# Project Architecture

```
             Map File
                 │
                 ▼
             Map Parser
                 │
                 ▼
             Graph Model
                 │
                 ▼
            Pathfinding
        (Dijkstra + Yen)
                 │
                 ▼
        Drone Assignment
                 │
                 ▼
             Scheduler
                 │
                 ▼
            Visualization
```

---

# Instructions

## Requirements

- Python 3.10+
- pygame

Install pygame:

```bash
pip install pygame
```

---

## Run

```bash
python main.py maps/example.txt
```

Example:

```bash
python main.py maps/easy_1.txt
```

---

## Input Format

Example:

```text
nb_drones: 5

start_hub: start 0 0 [color=green]

hub: zone1 2 0

hub: zone2 4 0 [zone=restricted]

end_hub: goal 6 0

connection: start-zone1

connection: zone1-zone2

connection: zone2-goal
```

---

# Algorithm Explanation

## 1. Parsing

The parser reads the map file and validates:

- number of drones
- unique start and end hubs
- unique zone names
- unique connections
- metadata
- capacities
- zone types
- syntax

The parser constructs a custom graph structure composed of:

- Graph
- Zone
- Connection

---

## 2. Pathfinding

The project combines two routing algorithms.

### Dijkstra

Dijkstra is used to compute the shortest path according to movement cost.

Zone costs are:

| Zone | Cost |
|------|-----:|
| Normal | 1 |
| Priority | 0.9 |
| Restricted | 2 |
| Blocked | ∞ |

Priority zones receive a slightly smaller cost to encourage the algorithm to choose them whenever possible.

---

### Yen's Algorithm

Instead of relying on only one shortest path, Yen's algorithm computes the two best loopless paths.

This allows the simulator to distribute drones over multiple routes when doing so decreases congestion.

---

## 3. Path Analysis

Each candidate path is analysed using four metrics:

- Total path cost
- Bottleneck delay
- Effective capacity
- Path geometry

The effective capacity is defined as the minimum capacity among every zone and every connection belonging to the path.

It estimates the maximum number of drones that can simultaneously progress through the entire path.

---

## 4. Drone Assignment Strategy

When two valid paths exist:

1. Both paths are analysed.
2. Their estimated completion time is evaluated according to:
   - travel cost,
   - bottleneck delay,
   - effective capacity.
3. The algorithm computes how many drones should be assigned to each path.
4. Drones are then alternately assigned to both paths to allow simultaneous progression from the beginning of the simulation.

If only one path exists, all drones use that path.

---

## 5. Scheduler

The scheduler executes the simulation turn by turn.

It guarantees:

- zone capacity constraints
- connection capacity constraints
- restricted movement
- simultaneous drone movement
- conflict avoidance

Restricted zones require two turns:

Turn 1:

```
Source -------- Connection
```

Turn 2:

```
Connection -------- Restricted Zone
```

During transit the drone occupies the connection but not the destination zone.

---

# Complexity

| Algorithm | Complexity |
|-----------|-----------:|
| Dijkstra | O((V + E) log V) |
| Yen (2 paths) | Approximately 2 × Dijkstra |
| Scheduler | O(D) per turn |

Where:

- V = number of zones
- E = number of connections
- D = number of drones

---

# Visual Representation

The project includes a graphical interface built with Pygame.

It displays:

- graph topology
- coloured zones
- connection capacities
- zone capacities
- drone identifiers
- drones travelling on connections
- current simulation turn
- delivered drones
- manual and automatic execution modes

Colours defined in the map are directly reflected in the visualization, making bottlenecks and zone types easy to identify during execution.

---

# Example

Input:

```text
nb_drones: 2

start_hub: start 0 0

hub: A 1 0

end_hub: goal 2 0

connection: start-A

connection: A-goal
```

Console output:

```text
D1-A D2-start
D1-goal D2-A
D2-goal
```

The graphical interface simultaneously displays the drone positions for every turn.

---

# Resources

## Documentation

- Python Documentation
  https://docs.python.org/3/

- Pygame Documentation
  https://www.pygame.org/docs/

- Dijkstra Algorithm
  https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm

- Yen's K Shortest Paths Algorithm
  https://en.wikipedia.org/wiki/Yen%27s_algorithm

---

## AI Usage

AI was used as a development assistant throughout the project.

It was primarily used for:

- discussing algorithmic strategies,
- reviewing code structure,
- identifying corner cases,
- improving the scheduling logic,
- evaluating design choices,
- refining the visualization.

All generated suggestions were reviewed, adapted, tested, and integrated manually before being included in the project.

---

# Future Improvements

Possible future optimizations include:

- Dynamic rerouting during simulation.
- More advanced scheduling heuristics.
- Improved edge-capacity handling for multi-turn restricted movements.
- Automatic graph scaling for very large maps.
- Additional performance metrics and benchmarking tools.