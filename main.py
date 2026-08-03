
from parser import MapParser
from simulator import Simulator
import sys


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python main.py <map_file>")
        return
    try:
        graph = MapParser().parse(sys.argv[1])
        sim = Simulator(graph)
        sim.run()
    except ValueError as e:
        print("ERROR:", e)


if __name__ == "__main__":
    main()
