import re

from models import Graph, Zone, Connection


VALID_ZONE_TYPES = {
    "normal",
    "priority",
    "restricted",
    "blocked",
}

VALID_ZONE_METADATA = {
    "color",
    "zone",
    "max_drones"

}
VALID_CONNECTION_METADATA = {
    "max_link_capacity"
}


class MapParser:

    def parse(self, filename: str) -> Graph:

        graph = Graph()
        seen_connections = set()
        nb_drones_check = False

        with open(filename, "r", encoding="utf-8") as file:

            for line_num, raw_line in enumerate(file):

                line = raw_line.strip()

                if not line or line.startswith("#"):
                    continue

                if not nb_drones_check:
                    nb_drones_check = True

                    if not line.startswith("nb_drones:"):
                        raise ValueError(
                            "nb_drones must be the first directive"
                        )
                try:

                    if line.startswith("nb_drones:"):

                        if graph.drones != 0:
                            raise ValueError(
                                "nb_drones defined multiple times"
                            )

                        graph.drones = int(
                            line.split(":", 1)[1].strip()
                        )

                        if graph.drones <= 0:
                            raise ValueError(
                                "number of drones must be positive"
                            )

                    elif (
                        line.startswith("start_hub:")
                        or line.startswith("end_hub:")
                        or line.startswith("hub:")
                    ):

                        self._parse_zone(
                            line,
                            graph,
                        )

                    elif line.startswith("connection:"):

                        self._parse_connection(
                            line,
                            graph,
                            seen_connections,
                        )

                    else:

                        raise ValueError(
                            "unknown directive"
                        )

                except ValueError as exc:

                    raise ValueError(
                        f"Line {line_num + 1}: {exc}"
                    ) from exc

        self._validate_graph(graph)

        return graph

    def _parse_zone(
        self,
        line: str,
        graph: Graph,
    ) -> None:

        metadata = {}

        meta_match = re.search(
            r"\[(.*?)\]",
            line,
        )
        

        if meta_match:

            if (line[meta_match.end():].strip()):
                raise ValueError(
                "unexpected content after metadata"
            )

            metadata_text = meta_match.group(1)

            for token in metadata_text.split():

                if "=" not in token:
                    raise ValueError(
                        f"invalid metadata '{token}'"
                    )

                key, value = token.split(
                    "=",
                    1,
                )
                if key in metadata:
                    raise ValueError(
                        f"duplicate metadata '{key}'"
                    )
                if key not in VALID_ZONE_METADATA:
                    raise ValueError(
                        f"invalid zone metadata '{key}'"
                    )

                metadata[key] = value

            line = line[: meta_match.start()].strip()

        parts = line.split()

        if len(parts) != 4:
            raise ValueError(
                "invalid zone declaration"
            )

        zone_kind = parts[0].replace(
            ":",
            "",
        )

        name = parts[1]

        if "-" in name:
            raise ValueError(
                "zone names cannot contain '-'"
            )

        if name in graph.zones:
            raise ValueError(
                f"duplicate zone '{name}'"
            )

        try:
            x = int(parts[2])
            y = int(parts[3])
        except ValueError:
            raise ValueError(
                "zone coordinates must be integers"
            )

        zone_type = metadata.get(
            "zone",
            "normal",
        )

        if zone_type not in VALID_ZONE_TYPES:
            raise ValueError(
                f"invalid zone type '{zone_type}'"
            )

        color = metadata.get(
            "color",
            "none",
        )

        max_drones = int(
            metadata.get(
                "max_drones",
                1,
            )
        )

        if max_drones <= 0:
            raise ValueError(
                "max_drones must be positive"
            )

        zone = Zone(
            name=name,
            x=x,
            y=y,
            zone_type=zone_type,
            color=color,
            max_drones=max_drones,
        )

        graph.zones[name] = zone

        if zone_kind == "start_hub":

            if graph.start:
                raise ValueError(
                    "multiple start_hub definitions"
                )

            graph.start = name

        elif zone_kind == "end_hub":

            if graph.end:
                raise ValueError(
                    "multiple end_hub definitions"
                )

            graph.end = name

    def _parse_connection(
        self,
        line: str,
        graph: Graph,
        seen_connections: set,
    ) -> None:

        metadata = {}

        meta_match = re.search(
            r"\[(.*?)\]",
            line,
        )

        if meta_match:

            if line[meta_match.end():].strip():
                raise ValueError(
                    "unexpected content after metadata"
                )

            metadata_text = meta_match.group(1)

            for token in metadata_text.split():

                if "=" not in token:
                    raise ValueError(
                        f"invalid metadata '{token}'"
                    )

                key, value = token.split(
                    "=",
                    1,
                )
                if key in metadata:
                    raise ValueError(
                        f"duplicate metadata '{key}'"
                    )
                if key not in VALID_CONNECTION_METADATA:
                    raise ValueError(
                        f"invalid connection metadata '{key}'"
                    )

                metadata[key] = value

            line = line[: meta_match.start()].strip()

        pair = line.split(
            ":",
            1,
        )[1].strip()

        if "-" not in pair:
            raise ValueError(
                "invalid connection syntax"
            )

        source, destination = pair.split(
            "-",
            1,
        )

        if source not in graph.zones:
            raise ValueError(
                f"unknown zone '{source}'"
            )

        if destination not in graph.zones:
            raise ValueError(
                f"unknown zone '{destination}'"
            )

        connection_key = tuple(
            sorted(
                (
                    source,
                    destination,
                )
            )
        )

        if connection_key in seen_connections:
            raise ValueError(
                f"duplicate connection {source}-{destination}"
            )

        seen_connections.add(
            connection_key
        )

        max_capacity = int(
            metadata.get(
                "max_link_capacity",
                1,
            )
        )

        if max_capacity <= 0:
            raise ValueError(
                "max_link_capacity must be positive"
            )

        connection = Connection(
            source=source,
            destination=destination,
            max_capacity=max_capacity,
        )

        graph.adj.setdefault(
            source,
            [],
        ).append(
            (
                destination,
                connection,
            )
        )

        graph.adj.setdefault(
            destination,
            [],
        ).append(
            (
                source,
                connection,
            )
        )

    def _validate_graph(
        self,
        graph: Graph,
    ) -> None:

        if graph.drones <= 0:
            raise ValueError(
                "missing nb_drones"
            )

        if not graph.start:
            raise ValueError(
                "missing start_hub"
            )

        if not graph.end:
            raise ValueError(
                "missing end_hub"
            )
