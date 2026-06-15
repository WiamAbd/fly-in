
from parser import MapParser
from simulator import Simulator
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <map_file>")
        return
    graph = MapParser().parse(sys.argv[1])
    sim = Simulator(graph)
    sim.run()

if __name__ == "__main__":
    main()
