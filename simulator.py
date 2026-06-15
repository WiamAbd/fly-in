from heapq import heappush, heappop

from visualizer import Visualizer
from scheduler import Scheduler


class Simulator:

    EDGE_PENALTY = 10

    def __init__(self, graph):
        self.graph = graph

    def zone_cost(self, zone_name):

        zone = self.graph.zones[zone_name]

        if zone.zone_type == "blocked":
            return float("inf")

        if zone.zone_type == "restricted":
            return 2

        if zone.zone_type == "priority":
            return 0.9

        return 1

    def dijkstra(
        self,
        edge_penalties=None,
    ):

        if edge_penalties is None:
            edge_penalties = {}

        heap = [
            (
                0,
                self.graph.start,
                [self.graph.start],
            )
        ]

        visited = {}

        while heap:

            cost, node, path = heappop(
                heap
            )

            if node == self.graph.end:
                return cost, path

            if (
                node in visited
                and visited[node] <= cost
            ):
                continue

            visited[node] = cost

            for (
                neighbor,
                connection,
            ) in self.graph.adj.get(
                node,
                [],
            ):

                zone = self.graph.zones[
                    neighbor
                ]

                if (
                    zone.zone_type
                    == "blocked"
                ):
                    continue

                edge = tuple(
                    sorted(
                        (
                            node,
                            neighbor,
                        )
                    )
                )

                penalty = edge_penalties.get(
                    edge,
                    0,
                )

                new_cost = (
                    cost
                    + self.zone_cost(
                        neighbor
                    )
                    + penalty
                )

                heappush(
                    heap,
                    (
                        new_cost,
                        neighbor,
                        path + [neighbor],
                    ),
                )

        return float("inf"), []

    def two_best_paths(self):

        cost1, path1 = self.dijkstra()

        penalties = {}

        for i in range(
            len(path1) - 1
        ):

            edge = tuple(
                sorted(
                    (
                        path1[i],
                        path1[i + 1],
                    )
                )
            )

            penalties[
                edge
            ] = self.EDGE_PENALTY

        cost2, path2 = self.dijkstra(
            penalties
        )

        if not path2:
            path2 = path1
            cost2 = cost1

        return (
            (cost1, path1),
            (cost2, path2),
        )

    def create_drones(self):

        (
            (cost1, path1),
            (cost2, path2),
        ) = self.two_best_paths()

        drones_p1 = []
        drones_p2 = []

        load1 = 0
        load2 = 0

        for drone_id in range(
            1,
            self.graph.drones + 1,
        ):

            score1 = (
                cost1
                + load1 * 2
            )

            score2 = (
                cost2
                + load2 * 2
            )

            drone = {
                "id": drone_id,
                "position": 0,
                "travel_remaining": 0,
                "finished": False,
            }

            if score1 <= score2:

                drone["path"] = path1

                drones_p1.append(
                    drone
                )

                load1 += 1

            else:

                drone["path"] = path2

                drones_p2.append(
                    drone
                )

                load2 += 1

        return (
            drones_p1,
            drones_p2,
        )

    def run(self):

        drones_p1, drones_p2 = (
            self.create_drones()
        )

        scheduler = Scheduler(
            self.graph
        )

        visualizer = Visualizer(
            self.graph
        )

        #
        # INITIAL STATE
        #
        visualizer.draw_turn(
            0,
            drones_p1 + drones_p2,
        )

        visualizer.wait_for_next_turn()

        turn = 1

        while True:

            visualizer.process_events()

            moves = scheduler.schedule_turn(
                drones_p1,
                drones_p2,
                turn,
            )

            if moves:

                print(
                    " ".join(
                        f"D{drone_id}-{destination}"
                        for (
                            drone_id,
                            destination,
                        )
                        in moves
                    )
                )

            visualizer.draw_turn(
                turn,
                drones_p1 + drones_p2,
            )

            all_finished = all(
                drone["finished"]
                for drone in (
                    drones_p1 + drones_p2
                )
            )

            if all_finished:

                print(
                    f"\nSimulation finished in {turn} turns"
                )

                while True:

                    try:

                        visualizer.wait_for_next_turn()

                    except SystemExit:

                        return

            visualizer.wait_for_next_turn()

            turn += 1