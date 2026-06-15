
*This project has been created as part of the 42 curriculum by login*

# Fly-in

Drone routing simulator.

## Architecture
- parser.py: parses maps
- models.py: graph entities
- simulator.py: routing engine
- main.py: entry point

## Recommended final implementation
For the full subject requirements, extend this baseline with:
- weighted pathfinding (Dijkstra/A*)
- restricted-zone 2-turn transitions
- capacities on nodes and edges
- multi-path scheduling
- deadlock avoidance
- colored terminal visualization

## Run
make run MAP=map.txt
