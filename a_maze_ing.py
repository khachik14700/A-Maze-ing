import sys
import os
from config_parser import load_config
from maze import MazeGenerator


def choice() -> int:
    """
    Displays the menu and prompts the user for a selection.

    Validates that the input is an integer between 1 and 5.

    Returns:
        int: The validated user choice.
    """
    print("=== A-Maze-ing ===")
    print("1. Re-generate a new maze")
    print("2. Show / Hide the shortest path")
    print("3. Rotate the wall colours")
    print("4. Rotate the 42 pattern colours")
    print("5. Re-generate with animation")
    print("6. Quit")
    mode = input("\033[032mChoice? (1-6):\033[0m")
    while not (mode >= "1" and mode <= "6"):
        print("The choice must be between 1-6!")
        mode = input("\033[032mChoice? (1-6):\033[0m")
    return int(mode)


def start() -> None:
    """
    Initializes the maze generation process and
    handles the user interaction loop.

    Loads configuration, generates the maze,
    and provides options to re-generate,
    show/hide the path, rotate colors, or quit the application.
    Handles potential errors during generation or execution gracefully.
    """
    config = load_config(sys.argv[1])

    try:
        maze = MazeGenerator(config.WIDTH, config.HEIGHT,
                             config.ENTRY, config.EXIT,
                             config.OUTPUT_FILE, config.ALGORITHM,
                             config.PERFECT, config.SEED)
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
                os.system("cls" if os.name == "nt" else "clear")
                maze.rotate_pattern_colours()
            elif mode == 5:
                maze.generate(animation=True)
                maze.print_maze()
                maze.export_to_hex()
            elif mode == 6:
                break
    except Exception as er:
        print(er)


def main() -> None:
    """
    The entry point of the application.

    Checks command-line arguments, validates the configuration file name,
    and initiates the maze generation process.
    """
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return

    config_file = sys.argv[1]
    if config_file != "config.txt":
        print("Error: The configuration file must be named 'config.txt'")
        sys.exit(1)

    if not os.path.exists(config_file):
        print(f"Error: The file '{config_file}' was not found.")
        sys.exit(1)

    if not os.path.isfile(config_file):
        print(f"Error: '{config_file}' is not a valid file.")
        sys.exit(1)

    start()


if __name__ == "__main__":
    main()
