from collections import defaultdict


class Scheduler:

    def __init__(self, graph):

        self.graph = graph

    def get_occupancy(self, drones):

        occupancy = defaultdict(int)

        for drone in drones:

            if drone["finished"]:
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
        # Drone already travelling through
        # a restricted zone
        #
        if drone["travel_remaining"] > 0:

            drone["travel_remaining"] -= 1

            if drone["travel_remaining"] == 0:

                drone["position"] += 1

                destination = drone["path"][
                    drone["position"]
                ]

                if (
                    destination
                    == self.graph.end
                ):
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

        #
        # Capacity checks
        #
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

        #
        # Reserve destination
        #
        occupancy[destination] += 1

        #
        # Drone leaves source
        #
        occupancy[source] -= 1

        #
        # Reserve edge
        #
        edge_usage[edge] += 1

        zone = self.graph.zones[
            destination
        ]

        #
        # Restricted zone
        #
        if zone.zone_type == "restricted":

            drone["travel_remaining"] = 1

            return (
                drone["id"],
                f"{source}-{destination}",
            )

        #
        # Normal movement
        #
        drone["position"] += 1

        if destination == self.graph.end:

            drone["finished"] = True

        return (
            drone["id"],
            destination,
        )

    def schedule_turn(
        self,
        drones_p1,
        drones_p2,
        turn,
    ):

        all_drones = (
            drones_p1 + drones_p2
        )

        occupancy = self.get_occupancy(
            all_drones
        )

        edge_usage = self.get_edge_usage()

        moves = []

        #
        # Path 1 priority
        #
        for drone in drones_p1:

            result = self.move_drone(
                drone,
                occupancy,
                edge_usage,
            )

            if result:
                moves.append(result)

        #
        # Path 2 second
        #
        for drone in drones_p2:

            result = self.move_drone(
                drone,
                occupancy,
                edge_usage,
            )

            if result:
                moves.append(result)

        return moves