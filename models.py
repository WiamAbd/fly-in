from dataclasses import dataclass, field


@dataclass
class Zone:
    name: str
    x: int
    y: int
    zone_type: str = "normal"
    color: str = "none"
    max_drones: int = 1


@dataclass
class Connection:
    source: str
    destination: str
    max_capacity: int = 1


@dataclass
class Graph:
    drones: int = 0
    start: str = ""
    end: str = ""

    zones: dict[str, Zone] = field(default_factory=lambda: {})

    adj: dict[str, list[tuple[str, Connection]]] = field(default_factory=lambda: {})
