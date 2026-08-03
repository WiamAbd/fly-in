import pygame


class Visualizer:

    NODE_RADIUS = 22

    MIN_GRID_X = 60
    MIN_GRID_Y = 70
    MAX_GRID_X = 120
    MAX_GRID_Y = 140

    COLORS = {
        "red": (220, 50, 50),
        "green": (50, 180, 50),
        "blue": (50, 50, 220),
        "yellow": (230, 230, 50),
        "gray": (120, 120, 120),
        "orange": (255, 165, 0),
        "purple": (128, 0, 128),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
        "brown": (139, 69, 19),
        "gold": (255, 215, 0),
        "black": (0, 0, 0),
        "none": (200, 200, 200),
    }

    def __init__(self, graph):

        pygame.init()
        self.screen_info = pygame.display.Info()

        self.screen_width = self.screen_info.current_w
        self.screen_height = self.screen_info.current_h
        self.graph = graph

        self.auto_mode = False

        self.compute_layout()

        self.screen = pygame.display.set_mode(
            (
                self.width,
                self.height,
            )
        )

        pygame.display.set_caption(
            "Fly-In Drone Simulator"
        )

        self.font = pygame.font.SysFont(
            "Arial",
            14,
        )

    def compute_layout(self):

        xs = sorted(
            {
                zone.x
                for zone in self.graph.zones.values()
            }
        )

        ys = sorted(
            {
                zone.y
                for zone in self.graph.zones.values()
            }
        )

        self.x_index = {
            x: i
            for i, x in enumerate(xs)
        }

        self.y_index = {
            y: i
            for i, y in enumerate(ys)
        }

        self.width = self.screen_width - 40
        self.height = self.screen_height - 80

        usable_width = self.width - 250
        usable_height = self.height - 250

        cols = max(1, len(xs) - 1)
        rows = max(1, len(ys) - 1)

        self.grid_x = max(
            self.MIN_GRID_X,
            min(
                self.MAX_GRID_X,
                usable_width // cols,
            ),
        )

        self.grid_y = max(
            self.MIN_GRID_Y,
            min(
                self.MAX_GRID_Y,
                usable_height // rows,
            ),
        )

        graph_width = cols * self.grid_x
        graph_height = rows * self.grid_y

        self.offset_x = (self.width - graph_width) // 2
        self.offset_y = (self.height - graph_height) // 2

    def graph_position(self, zone):

        x = (
            self.offset_x
            + self.x_index[zone.x]
            * self.grid_x
        )

        y = (
            self.offset_y
            + self.y_index[zone.y]
            * self.grid_y
        )

        return x, y

    def process_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                raise SystemExit

    def wait_for_next_turn(self):

        if self.auto_mode:

            pygame.time.wait(500)
            return

        while True:

            event = pygame.event.wait()

            if event.type == pygame.QUIT:

                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    pygame.quit()
                    raise SystemExit

                if event.key == pygame.K_a:

                    self.auto_mode = True
                    return

                if event.key in (
                    pygame.K_SPACE,
                    pygame.K_RETURN,
                ):
                    return

    def draw_edges(self):

        drawn = set()

        for source, neighbors in self.graph.adj.items():

            zone1 = self.graph.zones[source]

            x1, y1 = self.graph_position(zone1)

            for destination, connection in neighbors:

                edge = tuple(
                    sorted(
                        (
                            source,
                            destination,
                        )
                    )
                )

                if edge in drawn:
                    continue

                drawn.add(edge)

                zone2 = self.graph.zones[destination]

                x2, y2 = self.graph_position(zone2)

                pygame.draw.line(
                    self.screen,
                    (120, 120, 120),
                    (x1, y1),
                    (x2, y2),
                    2,
                )
                mid_x = (x1 + x2) // 2
                mid_y = (y1 + y2) // 2

                capacity = self.font.render(
                    f"{connection.max_capacity}",
                    True,
                    (0, 0, 255),
                )

                self.screen.blit(
                    capacity,
                    (
                        mid_x - capacity.get_width() // 2,
                        mid_y - capacity.get_height() // 2,
                    ),
                )

    def draw_nodes(self):

        for zone in self.graph.zones.values():

            color = self.COLORS.get(
                zone.color.lower(),
                self.COLORS["none"],
            )

            x, y = self.graph_position(zone)

            pygame.draw.circle(
                self.screen,
                color,
                (x, y),
                self.NODE_RADIUS,
            )

            pygame.draw.circle(
                self.screen,
                (30, 30, 30),
                (x, y),
                self.NODE_RADIUS,
                2,
            )

            zone_type = zone.zone_type[0].upper()

            label = self.font.render(
                f"{zone.name} ({zone_type},{zone.max_drones})",
                True,
                (0, 0, 0),
            )
                    
            self.screen.blit(
                    label,
                    (
                        x - label.get_width() // 2,
                        y - 42,
                    ),
                )

    def draw_drones(self, drones):

        offsets = {}

        for drone in drones:

            if drone["finished"]:

                zone_name = self.graph.end
                position_key = zone_name

                zone = self.graph.zones[zone_name]

                x, y = self.graph_position(zone)

                color = (0, 220, 0)

            elif drone["travel_remaining"] > 0:

                source_name = drone["path"][
                    drone["position"]
                ]

                destination_name = drone["path"][
                    drone["position"] + 1
                ]

                position_key = (
                    f"{source_name}->{destination_name}"
                )

                source = self.graph.zones[
                    source_name
                ]

                destination = self.graph.zones[
                    destination_name
                ]

                x1, y1 = self.graph_position(
                    source
                )

                x2, y2 = self.graph_position(
                    destination
                )

                x = (x1 + x2) //2
                y = (y1 + y2) //2

                color = (255, 255, 255)

            else:

                zone_name = drone["path"][
                    drone["position"]
                ]

                position_key = zone_name

                zone = self.graph.zones[
                    zone_name
                ]

                x, y = self.graph_position(
                    zone
                )

                color = (255, 255, 255)

            count = offsets.get(
                position_key,
                0,
            )

            offsets[position_key] = count + 1

            #
            # Better distribution around node/connection
            #
            if count == 0:
                dx = 0
                dy = 0
            else:
                offsets_pos = [
                    (-12, 0),
                    (12, 0),
                    (0, -12),
                    (0, 12),
                    (-12, -12),
                    (12, -12),
                    (-12, 12),
                    (12, 12),
                ]

                dx, dy = offsets_pos[
                    (count - 1) % len(offsets_pos)
                ]
            pygame.draw.circle(
                self.screen,
                color,
                (
                    x + dx,
                    y + dy,
                ),
                8,
            )

            text = self.font.render(
                str(drone["id"]),
                True,
                (0, 0, 0),
            )

            self.screen.blit(
                text,
                (
                    x + dx - text.get_width() // 2,
                    y + dy - text.get_height() // 2,
                ),
            )

    def draw_turn(
        self,
        turn,
        drones,
    ):

        self.screen.fill(
            (240, 240, 240)
        )

        self.draw_edges()

        self.draw_nodes()

        self.draw_drones(
            drones
        )

        finished = sum(
            1
            for d in drones
            if d["finished"]
        )

        total = len(drones)

        title = self.font.render(
            (
                f"Turn {turn} | "
                f"Finished {finished}/{total}"
            ),
            True,
            (0, 0, 0),
        )

        self.screen.blit(
            title,
            (20, 20),
        )

        mode = (
            "AUTO"
            if self.auto_mode
            else "MANUAL"
        )

        mode_text = self.font.render(
            f"Mode: {mode}",
            True,
            (0, 0, 0),
        )

        self.screen.blit(
            mode_text,
            (20, 50),
        )

        help_text = self.font.render(
            (
                "SPACE/ENTER = Next Turn | "
                "A = Autoplay | ESC = Quit"
            ),
            True,
            (0, 0, 0),
        )

        self.screen.blit(
            help_text,
            (20, 80),
        )

        pygame.display.flip()
