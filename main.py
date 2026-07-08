import sys

from config_parser import load_config
from maze import MazeGenerator, Cell

import os
import time





def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return

    config = load_config(sys.argv[1])
    print(config)

    try:
        maze = MazeGenerator(config.WIDTH, config.HEIGHT,
                             config.ENTRY, config.EXIT,
                             config.OUTPUT_FILE, config.PERFECT,
                             config.SEED)
        maze.generate(True)
    except Exception as er:
        print(er)


if __name__ == "__main__":
    main()
