from heapq import heappush, heappop
from copy import deepcopy
from visualizer import Visualizer
from scheduler import Scheduler
from models import Connection


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

    def dijkstra(self,graph, start, goal):

        heap = [(0, start, [start])]

        visited = {}

        while heap:

            cost, node, path = heappop(
                heap
            )

            if node == goal:
                return cost, path

            if (
                node in visited
                and visited[node] <= cost
            ):
                continue

            visited[node] = cost

            for (
                neighbor,
                _,
            ) in graph.adj.get(
                node,
                [],
            ):

                zone = graph.zones[
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


    def path_cost(self, path):
        return sum(
            self.zone_cost(node)
            for node in path[1:]
        )



    def yen_k_shortest_paths(self,graph, start, goal, k=2):

        first_cost, first_path = self.dijkstra(graph, start, goal)

        if not first_path:
            return []

        A = [(first_cost, first_path)]
        B = []

        for _ in range(1, k):

            
            _, previous_path = A[-1]
                

            for spur_index in range(len(previous_path) - 1):

                root_path = previous_path[: spur_index + 1]

                temp_graph = deepcopy(graph)

                #
                # Remove edges that would recreate
                # an already accepted path
                #
                for _, accepted_path in A:

                    if (
                        len(accepted_path) > spur_index
                        and accepted_path[: spur_index + 1]
                        == root_path
                    ):

                        u = accepted_path[spur_index]
                        v = accepted_path[spur_index + 1]

                        temp_graph.adj[u] = [
                            (n, w)
                            for n, w in temp_graph.adj[u]
                            if n != v
                        ]
                        temp_graph.adj[v] = [
                            (n, w)
                            for n, w in temp_graph.adj[v]
                            if n != u
                        ]

                #
                # Remove nodes of the root path
                # except the spur node
                #
                for node in root_path[:-1]:

                    temp_graph.adj.pop(node, None)

                    for key in temp_graph.adj:

                        temp_graph.adj[key] = [
                            (n, w)
                            for n, w in temp_graph.adj[key]
                            if n != node
                        ]

                

                

                _, spur_path = self.dijkstra(
                    temp_graph,
                    root_path[-1],
                    goal,
                )

                if not spur_path:
                    continue

                total_path = (
                    root_path[:-1]
                    + spur_path
                )

                total_cost = self.path_cost(total_path)

                candidate = (
                    total_cost,
                    total_path,
                )

                existing_paths = (
                    [path for _, path in A]
                    + [path for _, path in B]
                )

                if total_path not in existing_paths:
                    heappush(
                        B,
                        candidate,
                    )

            if not B:
                break

            A.append(heappop(B))

        return A


    def analyze_path(self, path):

        bottleneck_delay = 1

        min_zone_capacity = float("inf")
        min_edge_capacity = float("inf")

        for i in range(1, len(path)):

            zone = self.graph.zones[path[i]]

            if zone.zone_type == "restricted":
                bottleneck_delay = 2

            if path[i] not in (
                self.graph.start,
                self.graph.end,
            ):
                min_zone_capacity = min(
                    min_zone_capacity,
                    zone.max_drones,
                )

            source = path[i - 1]
            destination = path[i]

            for neigh, connection in self.graph.adj[source]:

                if neigh == destination:

                    min_edge_capacity = min(
                        min_edge_capacity,
                        connection.max_capacity,
                    )

                    break

        effective_capacity = min(
            min_zone_capacity,
            min_edge_capacity,
        )

        return {
            "cost": self.path_cost(path),
            "path": path,
            "bottleneck_delay": bottleneck_delay,
            "effective_capacity": effective_capacity,
        }

    def split_drones(
        self,
        path1,
        path2,
    ):

        #
        # If second path is much worse,
        # ignore it.
        #
        if path2["cost"] > path1["cost"] + 5:

            return (
                self.graph.drones,
                0,
            )

        total = self.graph.drones

        best_finish = float("inf")

        best_split = (
            total,
            0,
        )

        for drones_p2 in range(total + 1):

            drones_p1 = total - drones_p2

            finish_p1 = (
                path1["cost"]
                + max(
                    0,
                    drones_p1
                    - path1["effective_capacity"],
                )
                * path1["bottleneck_delay"]
            )

            finish_p2 = (
                path2["cost"]
                + max(
                    0,
                    drones_p2
                    - path2["effective_capacity"],
                )
                * path2["bottleneck_delay"]
            )

            finish = max(
                finish_p1,
                finish_p2,
            )

            if finish < best_finish:

                best_finish = finish

                best_split = (
                    drones_p1,
                    drones_p2,
                )

        return best_split

    
    def create_drones(self):

        paths = self.yen_k_shortest_paths(
            self.graph,
            self.graph.start,
            self.graph.end,
        )

        drones = []

        #
        # Only one path exists
        #
        if len(paths) == 1:

            _, path = paths[0]

            for drone_id in range(
                1,
                self.graph.drones + 1,
            ):

                drones.append(
                    {
                        "id": drone_id,
                        "position": 0,
                        "travel_remaining": 0,
                        "finished": False,
                        "path": path,
                    }
                )

            return drones

        #
        # Analyze both paths
        #
        path1 = self.analyze_path(
            paths[0][1]
        )

        path2 = self.analyze_path(
            paths[1][1]
        )

        drones_p1, drones_p2 = self.split_drones(
            path1,
            path2,
        )

        drone_id = 1
        remaining_p1 = drones_p1
        remaining_p2 = drones_p2

        while remaining_p1 > 0 or remaining_p2 > 0:

            if remaining_p1 > 0:

                drones.append(
                    {
                        "id": drone_id,
                        "position": 0,
                        "travel_remaining": 0,
                        "finished": False,
                        "path": path1["path"],
                    }
                )

                remaining_p1 -= 1
                drone_id += 1

            if remaining_p2 > 0:

                drones.append(
                    {
                        "id": drone_id,
                        "position": 0,
                        "travel_remaining": 0,
                        "finished": False,
                        "path": path2["path"],
                    }
                )

                remaining_p2 -= 1
                drone_id += 1

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