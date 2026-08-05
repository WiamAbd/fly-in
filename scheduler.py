"""Turn-based scheduler for drone movement and conflict resolution."""
from collections import defaultdict
from models import Graph, Connection


class Scheduler:
    """Schedule drone movements while respecting movement constraints."""
    def __init__(self, graph: Graph) -> None:
        """Initialize the scheduler for the given graph."""
        self.graph = graph

    def get_occupancy(
        self,
        drones: list[dict],
    ) -> defaultdict[str, int]:
        """Compute the current occupancy of every zone."""

        occupancy: defaultdict[str, int] = defaultdict(int)

        for drone in drones:

            if drone["finished"]:
                continue

            if drone["on_connection"]:
                continue

            current_zone = drone["path"][
                drone["position"]
            ]

            occupancy[current_zone] += 1

        return occupancy

    def can_enter_zone(
        self,
        destination: str,
        occupancy: defaultdict[str, int],
    ) -> bool:
        """Check whether a drone may enter the destination zone."""

        if destination == self.graph.end:
            return True

        zone = self.graph.zones[destination]

        return (
            occupancy[destination]
            < zone.max_drones
        )

    def can_use_edge(
        self,
        edge: tuple[str, str],
        connection: Connection,
        edge_usage: defaultdict[tuple[str, str], int],
    ) -> bool:
        """Check whether a connection can be used this turn."""

        return (
            edge_usage[edge]
            < connection.max_capacity
        )

    def move_drone(
        self,
        drone: dict,
        occupancy: defaultdict[str, int],
        edge_usage: defaultdict[tuple[str, str], int],
    ) -> tuple[int, str] | None:
        """Attempt to move a drone according to the scheduling rules."""

        if drone["finished"]:
            return None

        if drone["on_connection"]:
            destination = drone["path"][drone["position"]+1]

            if self.can_enter_zone(destination, occupancy):
                drone["on_connection"] = False

                drone["position"] += 1

                if destination == self.graph.end:
                    drone["finished"] = True

                return (
                    drone["id"],
                    destination,
                )
            return None

        current_idx = drone["position"]

        if (
            current_idx
            >= len(drone["path"]) - 1
        ):
            drone["finished"] = True
            return None

        source = drone["path"][
            current_idx
        ]

        destination = drone["path"][
            current_idx + 1
        ]

        connection = None

        for neigh, conn in self.graph.neighbors[source]:

            if neigh == destination:
                connection = conn
                break

        if connection is None:
            return None

        edge = tuple(
            sorted(
                (
                    source,
                    destination,
                )
            )
        )

        if not self.can_enter_zone(
            destination,
            occupancy,
        ):
            return None

        if not self.can_use_edge(
            edge,
            connection,
            edge_usage,
        ):
            return None

        zone = self.graph.zones[
            destination
        ]

        #
        # Restricted movement
        #
        occupancy[source] -= 1

        edge_usage[edge] += 1

        if zone.zone_type == "restricted":

            drone["on_connection"] = True

            return (
                drone["id"],
                f"{source}-{destination}",
            )

        occupancy[destination] += 1

        drone["position"] += 1

        if destination == self.graph.end:
            drone["finished"] = True

        return (
            drone["id"],
            destination,
        )

    def schedule_turn(
        self,
        drones: list[dict],
    ) -> list[tuple[int, str]]:
        """Execute one simulation turn for all drones."""

        occupancy = self.get_occupancy(
            drones
        )

        edge_usage: defaultdict[
            tuple[str, str],
            int,
        ] = defaultdict(int)

        moves = []

        for drone in drones:

            result = self.move_drone(
                drone,
                occupancy,
                edge_usage,
            )

            if result:
                moves.append(result)

        return moves
