from collections import defaultdict


class Scheduler:

    def __init__(self, graph):

        self.graph = graph

        #
        # Persistent reservations
        #
        self.edge_reservations = defaultdict(int)

    def update_reservations(self):

        expired = []

        for edge in self.edge_reservations:

            self.edge_reservations[edge] -= 1

            if self.edge_reservations[edge] <= 0:
                expired.append(edge)

        for edge in expired:
            del self.edge_reservations[edge]

    def get_occupancy(self, drones):

        occupancy = defaultdict(int)

        for drone in drones:

            if drone["finished"]:
                continue

            if drone["travel_remaining"] > 0:
                continue

            current_zone = drone["path"][
                drone["position"]
            ]

            occupancy[current_zone] += 1

        return occupancy

    def get_edge_usage(self):

        return defaultdict(int)

    def can_enter_zone(
        self,
        destination,
        occupancy,
    ):

        if destination == self.graph.start:
            return True

        if destination == self.graph.end:
            return True

        zone = self.graph.zones[destination]

        return (
            occupancy[destination]
            < zone.max_drones
        )

    def can_use_edge(
        self,
        edge,
        connection,
        edge_usage,
    ):

        #
        # Persistent reservation
        #
        if edge in self.edge_reservations:
            return False

        return (
            edge_usage[edge]
            < connection.max_capacity
        )

    def move_drone(
        self,
        drone,
        occupancy,
        edge_usage,
    ):

        if drone["finished"]:
            return None

        #
        # Currently travelling
        #
        if drone["travel_remaining"] > 0:

            drone["travel_remaining"] -= 1

            if drone["travel_remaining"] == 0:

                drone["position"] += 1

                destination = drone["path"][
                    drone["position"]
                ]

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

        for neigh, conn in self.graph.adj[source]:

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

            drone["travel_remaining"] = 1

            self.edge_reservations[edge] = 1

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
        drones,
    ):

        self.update_reservations()

        occupancy = self.get_occupancy(
            drones
        )

        edge_usage = self.get_edge_usage()

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
