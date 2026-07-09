import sys

from config_parser import load_config
from maze import MazeGenerator
import os


def choice() -> int:
    print("=== A-Maze-ing ===")
    print("1. Re-generate a new maze")
    print("2. Show / Hide the shortest path")
    print("3. Rotate the wall colours")
    print("4. Re-generate with animation")
    print("5. Quit")
    mode = input("\033[032mChoice? (1-5):\033[0m")
    while not (mode >= "1" and mode <= "5"):
        print("The choice must be between 1-5!")
        mode = input("\033[032mChoice? (1-5):\033[0m")
    return int(mode)


def start() -> None:
    config = load_config(sys.argv[1])
    print(config)

    try:
        maze = MazeGenerator(config.WIDTH, config.HEIGHT,
                             config.ENTRY, config.EXIT,
                             config.OUTPUT_FILE, config.PERFECT, config.SEED)
        maze.generate()
        maze.print_maze()
        maze.export_to_hex()

        while True:
            mode = choice()
            if mode == 1:
                os.system("cls" if os.name == "nt" else "clear")
                maze.generate()
                maze.print_maze()
                maze.export_to_hex()
            elif mode == 2:
                os.system("cls" if os.name == "nt" else "clear")
                maze.show_hide_shortest_path()
            elif mode == 3:
                os.system("cls" if os.name == "nt" else "clear")
                maze.rotate_wall_colours()
            elif mode == 4:
                maze.generate(animation=True)
                maze.print_maze()
                maze.export_to_hex()
            elif mode == 5:
                break
    except Exception as er:
        print(er)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return
    start()


if __name__ == "__main__":
    main()
