"""Data models used by the Fly-in simulator."""

from dataclasses import dataclass, field
from typing import TypedDict


@dataclass
class Zone:
    """Represents a zone of the graph."""

    name: str
    x: int
    y: int
    zone_type: str = "normal"
    color: str = "none"
    max_drones: int = 1


@dataclass
class Connection:
    """Represents a bidirectional connection between two zones."""

    source: str
    destination: str
    max_capacity: int = 1


@dataclass
class Graph:
    """Represents the complete map used during the simulation."""

    drones: int = 0
    start: str = ""
    end: str = ""

    zones: dict[str, Zone] = field(default_factory=dict)

    adj: dict[str, list[tuple[str, Connection]]] = field(
        default_factory=dict
    )


class PathInfo(TypedDict):
    """Stores heuristic information about a candidate path."""

    cost: float
    path: list[str]
    bottleneck_delay: int
    effective_capacity: float
