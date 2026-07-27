from heapq import heappush, heappop

from visualizer import Visualizer
from scheduler import Scheduler


class Simulator:

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

    def dijkstra(self):

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

                new_cost = (
                    cost
                    + self.zone_cost(
                        neighbor
                    )
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


    def create_drones(self):

        _, path = self.dijkstra()

        drones = []

        for drone_id in range(
            1,
            self.graph.drones + 1,
        ):

            drone = {
                "id": drone_id,
                "position": 0,
                "travel_remaining": 0,
                "finished": False,
                "path": path,
            }

            drones.append(drone)

        return drones

    def run(self):

        drones = self.create_drones()

        scheduler = Scheduler(
            self.graph
        )

        visualizer = Visualizer(
            self.graph
        )

        #
        # Initial state
        #
        visualizer.draw_turn(
            0,
            drones,
        )

        visualizer.wait_for_next_turn()

        turn = 1

        while True:

            visualizer.process_events()

            moves = scheduler.schedule_turn(
                drones,
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
                drones,
            )

            all_finished = all(
                drone["finished"]
                for drone in drones
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