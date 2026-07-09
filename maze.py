import random
from collections import deque
import os
import time


class Cell:
    """
    Represents a single cell in the maze grid.

    Attributes:
        north, east, south, west (bool): Indicates if the wall is closed.
        visited (bool): Tracks if the cell has been visited during generation.
        pattern (bool): Marks if the cell is part of the '42' pattern.
    """
    def __init__(self) -> None:
        self.north = True
        self.east = True
        self.south = True
        self.west = True
        self.visited = False
        self.pattern = False


class MazeGenerator:
    def __init__(self, width: int,
                 height: int, entry: tuple[int, int],
                 exit: tuple[int, int],
                 output_file: str,
                 algorithm: str = "dfs",
                 perfect: bool = False,
                 seed: int | None = None) -> None:
        """
        Initializes the maze generator with given dimensions and parameters.

        Args:
            width (int): Number of cells horizontally.
            height (int): Number of cells vertically.
            entry (tuple[int, int]): Start coordinates (x, y).
            exit (tuple[int, int]): End coordinates (x, y).
            output_file (str): Path to save the hexadecimal representation.
            algorithm (str): Generation algorithm ('dfs' or 'prim').
            perfect (bool): If True, generates a maze with a single path.
            seed (int | None): Optional seed for random number generation.
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.output_file = output_file
        self.perfect = perfect
        self.generation_steps: list[tuple[int, int, int, int, str]] = []

        self.show_path = False
        self.wall_colours = ["\033[37m", "\033[36m", "\033[35m",
                             "\033[33m", "\033[34m"]
        self.pattern_colours = ["\033[32m", "\033[36m", "\033[35m"]

        self.colour_index = 0
        self.pattern_colour_index = 0
        self.algorithm = algorithm

        if seed is not None:
            random.seed(seed)

    def get_unvisited_neighbours(
            self, x: int, y: int
            ) -> list[tuple[str, int, int]]:
        """
        Finds all unvisited neighbor cells for the given position.

        Args:
            x (int): X coordinate of the current cell.
            y (int): Y coordinate of the current cell.

        Returns:
            list[tuple[str, int, int]]: A list of (direction, nx, ny) tuples.
        """
        neighbours = []

        if y > 0:
            if not self.grid[y - 1][x].visited:
                neighbours.append(("N", x, y - 1))

        if x < self.width - 1:
            if not self.grid[y][x + 1].visited:
                neighbours.append(("E", x + 1, y))

        if y < self.height - 1:
            if not self.grid[y + 1][x].visited:
                neighbours.append(("S", x, y + 1))

        if x > 0:
            if not self.grid[y][x - 1].visited:
                neighbours.append(("W", x - 1, y))

        return neighbours

    def remove_wall(
            self, x1: int, y1: int, x2: int, y2: int, direction: str
            ) -> None:
        """
        Removes the shared wall between two adjacent cells.

        Args:
            x1, y1 (int): Coordinates of the current cell.
            x2, y2 (int): Coordinates of the neighbor cell.
            direction (str): The direction of the wall to
            remove ('N', 'E', 'S', 'W').
        """
        current = self.grid[y1][x1]
        neighbour = self.grid[y2][x2]

        if direction == "N":
            current.north = False
            neighbour.south = False
        elif direction == "E":
            current.east = False
            neighbour.west = False
        elif direction == "S":
            current.south = False
            neighbour.north = False
        elif direction == "W":
            current.west = False
            neighbour.east = False

    def _generate_dfs(self) -> None:
        """
        Generates the maze using the Depth-First Search (DFS) algorithm.

        Uses a stack to track the path and randomly selects unvisited
        neighbors to carve out corridors until the grid is filled.
        """
        self.generation_steps = []
        try:
            stack = []

            while True:
                start_x = random.randint(0, self.width - 1)
                start_y = random.randint(0, self.height - 1)

                current = self.grid[start_y][start_x]
                if current.visited is False:
                    break
            current.visited = True

            stack.append((start_x, start_y))

            while stack:
                x, y = stack[-1]

                neighbours = self.get_unvisited_neighbours(x, y)
                if neighbours:
                    direction, nx, ny = random.choice(neighbours)
                    self.remove_wall(x, y, nx, ny, direction)
                    self.grid[ny][nx].visited = True
                    stack.append((nx, ny))
                    self.generation_steps.append((x, y, nx, ny, direction))
                else:
                    stack.pop()
        except IndexError as er:
            print(f"Generation failed: Grid access error at ({x}, {y}) - {er}")
            raise
        except Exception as er:
            print(f"An unexpected error occurred "
                  f"during maze generation: {er}")
            raise

    def _get_all_neighbours(self, x: int,
                            y: int) -> list[tuple[str, int, int]]:
        """
        Returns all possible neighbors (N, E, S, W) for a given coordinate.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            list[tuple[str, int, int]]: List of (direction, nx, ny).
        """
        neighbours = []
        if y > 0:
            neighbours.append(("N", x, y - 1))
        if x < self.width - 1:
            neighbours.append(("E", x + 1, y))
        if y < self.height - 1:
            neighbours.append(("S", x, y + 1))
        if x > 0:
            neighbours.append(("W", x - 1, y))
        return neighbours

    def _generate_prim(self) -> None:
        """
        Generates the maze using Prim's algorithm.

        Maintains a frontier of cells adjacent to the growing maze and
        randomly connects them to the existing structure.
        """
        self.generation_steps = []
        try:
            frontier: list[tuple[int, int]] = []

            while True:
                start_x = random.randint(0, self.width - 1)
                start_y = random.randint(0, self.height - 1)

                current = self.grid[start_y][start_x]
                if current.visited is False:
                    break
            current.visited = True

            for _, nx, ny in self.get_unvisited_neighbours(start_x, start_y):
                if (nx, ny) not in frontier:
                    frontier.append((nx, ny))

            while frontier:
                fx, fy = random.choice(frontier)
                frontier.remove((fx, fy))

                if self.grid[fy][fx].visited:
                    continue

                visited_neighbours = [(direction, nx, ny)
                                      for direction, nx, ny in
                                      self._get_all_neighbours(fx, fy)
                                      if self.grid[ny][nx].visited
                                      and not self.grid[ny][nx].pattern
                                      ]

                if not visited_neighbours:
                    continue

                direction, vx, vy = random.choice(visited_neighbours)
                self.remove_wall(fx, fy, vx, vy, direction)
                self.generation_steps.append((fx, fy, vx, vy, direction))
                self.grid[fy][fx].visited = True

                for _, nx, ny in self.get_unvisited_neighbours(fx, fy):
                    if (nx, ny) not in frontier:
                        frontier.append((nx, ny))
        except IndexError as er:
            print(f"Generation failed: Grid access error - {er}")
            raise
        except Exception as er:
            print(f"An unexpected error occurred "
                  f"during maze generation: {er}")
            raise

    def get_valid_neighbors(self,
                            cord: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Returns accessible neighboring cells (where no wall exists).

        Args:
            cord (tuple[int, int]): The current cell coordinates.

        Returns:
            list[tuple[int, int]]: A list of valid neighboring coordinates.
        """
        x, y = cord
        current_cell = self.grid[y][x]
        neighbors = []

        if not current_cell.north and y > 0:
            neighbors.append((x, y - 1))

        if not current_cell.south and y < self.height - 1:
            neighbors.append((x, y + 1))

        if not current_cell.west and x > 0:
            neighbors.append((x - 1, y))

        if not current_cell.east and x < self.width - 1:
            neighbors.append((x + 1, y))

        return neighbors

    def _reconstruct_path(self, parent: dict,
                          exit: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Reconstructs the path from exit to entry using a parent dictionary.

        Args:
            parent (dict): Dictionary mapping cells to their predecessors.
            exit (tuple[int, int]): The exit coordinate.

        Returns:
            list[tuple[int, int]]: The path from entry to exit.
        """
        path = []
        current = exit

        while current is not None:
            path.append(current)
            current = parent[current]

        return path[::-1]

    def solve(self) -> list[tuple[int, int]]:
        """
        Finds the shortest path from the entry to the exit using BFS.

        Returns:
            list[tuple[int, int]]: A list of coordinates representing
             the shortest path.
        """
        entry = self.entry
        exit = self.exit
        queue = deque([entry])
        visited = {entry}
        parent: dict[tuple[int, int], tuple[int, int] | None] = {entry: None}

        while queue:
            current = queue.popleft()

            if current == exit:
                return self._reconstruct_path(parent, exit)

            for neighbor in self.get_valid_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)

        return []

    def _apply_pattern_42(self) -> None:
        """
        Applies the "42" pattern to the maze grid by marking specific
        cells as part of the visual pattern.
        """
        pattern_coords = [
            (-1, 0), (-1, 1), (-1, 2), (-2, 0), (-3, 0), (-3, -1), (-3, -2),
            (1, 0), (3, -1), (1, -2), (2, -2), (3, -2), (2, 0), (3, 0),
            (1, 1), (3, 2), (2, 2), (1, 2)
        ]

        center_y = self.height // 2
        center_x = self.width // 2

        dx_coords = [p[0] for p in pattern_coords]
        dy_coords = [p[1] for p in pattern_coords]

        min_dy, max_dy = min(dy_coords), max(dy_coords)
        min_dx, max_dx = min(dx_coords), max(dx_coords)

        if (center_y + min_dy < 0 or center_y + max_dy >= self.height or
           center_x + min_dx < 0 or center_x + max_dx >= self.width):
            raise ValueError("Maze is too small to fit the '42' pattern.")

        for dx, dy in pattern_coords:
            y, x = center_y + dy, center_x + dx
            if 0 <= x < self.width and 0 <= y < self.height:
                cell = self.grid[y][x]
                cell.north = cell.east = cell.south = cell.west = True
                cell.visited = True
                cell.pattern = True

    def export_to_hex(self) -> None:
        """
        Exports the current maze structure to the specified output file
        in a compact hexadecimal representation.
        """
        path = self.solve()
        if not path:
            raise ValueError("Cannot export: maze has no valid solution "
                             "path between entry and exit.")

        with open(self.output_file, 'w') as file:
            for y in range(0, self.height):
                row_string = ""
                for x in range(0, self.width):
                    cell = self.grid[y][x]
                    val = ((1 if cell.north else 0) + (2 if cell.east else 0) +
                           (4 if cell.south else 0) + (8 if cell.west else 0))
                    row_string += hex(val)[2:]
                file.write(f"{row_string}\n")

            file.write('\n')
            file.write(f"{self.entry[0]},{self.entry[1]}\n")
            file.write(f"{self.exit[0]},{self.exit[1]}\n")
            file.write(f"{self._path_to_directions(path)}\n")

    def _find_all_dead_ends(self) -> list[tuple[int, int]]:
        """
        Identifies all cells that have three walls closed (dead ends).

        Returns:
            list[tuple[int, int]]: List of (x, y) coordinates of dead ends.
        """
        result: list[tuple[int, int]] = []
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                walls_count = sum([cell.north, cell.east,
                                   cell.south, cell.west])
                if walls_count == 3:
                    result.append((x, y))
        return result

    def _break_one_wall(self, x: int, y: int) -> None:
        """
        Randomly breaks one wall of a given cell if possible.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.
        """
        cell = self.grid[y][x]

        candidates = []
        if y > 0 and cell.north and not self.grid[y-1][x].pattern:
            candidates.append("N")
        if x < self.width - 1 and cell.east and not self.grid[y][x+1].pattern:
            candidates.append("E")
        if (y < self.height - 1 and cell.south and not
           self.grid[y+1][x].pattern):
            candidates.append("S")
        if x > 0 and cell.west and not self.grid[y][x-1].pattern:
            candidates.append("W")

        safe_candidates = []
        if candidates:
            for direction in candidates:
                if direction == "N":
                    x2, y2 = x, y - 1
                elif direction == "E":
                    x2, y2 = x + 1, y
                elif direction == "S":
                    x2, y2 = x, y + 1
                else:
                    x2, y2 = x - 1, y
                if not self._creates_wide_open_area(x, y, x2, y2, direction):
                    safe_candidates.append((direction, x2, y2))

        if safe_candidates:
            direction, x2, y2 = random.choice(safe_candidates)
            self.remove_wall(x, y, x2, y2, direction)
            self.generation_steps.append((x, y, x2, y2, direction))

    def _validate_entry_exit(self) -> None:
        """
        Validates that entry and exit points are within bounds
        and not located within the "42" pattern.
        """
        entry_x, entry_y = self.entry
        exit_x, exit_y = self.exit

        if self.grid[entry_y][entry_x].pattern:
            raise ValueError("Entry point is inside the '42' pattern!")
        if self.grid[exit_y][exit_x].pattern:
            raise ValueError("Exit point is inside the '42' pattern!")

    def _ensure_no_dead_ends(self) -> None:
        """
        Iteratively removes dead ends to create a braided maze structure.
        """
        while True:
            dead_ends = self._find_all_dead_ends()
            if not dead_ends:
                return
            for x, y in dead_ends:
                self._break_one_wall(x, y)

            if self._find_all_dead_ends() == dead_ends:
                break

    def _safe_remove_wall(self, x: int, y: int, direction: str) -> None:
        """
        Removes a wall only if it does not create an illegal 3x3 open area.

        Args:
            x1, y1, x2, y2 (int): Coordinates of the cells.
            direction (str): Direction of the wall.

        Returns:
            bool: True if the wall was removed, False otherwise.
        """
        offsets = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
        if direction not in offsets:
            return

        dx, dy = offsets[direction]
        nx, ny = x + dx, y + dy

        if not (0 <= nx < self.width and 0 <= ny < self.height):
            return
        if self.grid[y][x].pattern or self.grid[ny][nx].pattern:
            return
        if self._creates_wide_open_area(x, y, nx, ny, direction):
            return

        self.remove_wall(x, y, nx, ny, direction)
        self.generation_steps.append((x, y, nx, ny, direction))

    def _open_corners_and_center(self) -> None:
        """
        Helper to clear specific cells in the center to accommodate
        the "42" visual pattern.
        """
        directions_by_corner = {
            (0, 0): ["E", "S"],
            (self.width - 1, 0): ["W", "S"],
            (0, self.height - 1): ["E", "N"],
            (self.width - 1, self.height - 1): ["W", "N"],
        }

        for (x, y), directions in directions_by_corner.items():
            for direction in directions:
                self._safe_remove_wall(x, y, direction)

        center_x, center_y = self.width // 2, self.height // 2
        for direction in ("N", "E", "S", "W"):
            self._safe_remove_wall(center_x, center_y, direction)

    def _is_3x3_block_fully_open(self, x0: int, y0: int) -> bool:
        """
        Checks if a 3x3 block starting at (x0, y0) is completely open.

        Args:
            x0 (int): Top-left X coordinate of the block.
            y0 (int): Top-left Y coordinate of the block.

        Returns:
            bool: True if the entire 3x3 area has no internal walls.
        """
        for dy in range(3):
            for dx in range(2):
                if self.grid[y0 + dy][x0 + dx].east:
                    return False
        for dx in range(3):
            for dy in range(2):
                if self.grid[y0 + dy][x0 + dx].south:
                    return False
        return True

    def _find_3x3_open_areas(self) -> list[tuple[int, int]]:
        """
        Scans the grid for 3x3 open areas.

        Returns:
            list[tuple[int, int]]: A list of coordinates (x, y)
            where a 3x3 open block starts.
        """
        result = []
        for y in range(self.height - 2):
            for x in range(self.width - 2):
                if self._is_3x3_block_fully_open(x, y):
                    result.append((x, y))
        return result

    def _close_wall(self, x1: int, y1: int, x2: int,
                    y2: int, direction: str) -> None:
        """
        Closes the wall in a specific direction for a given cell.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.
            direction (str): 'N', 'E', 'S', or 'W'.
        """
        current = self.grid[y1][x1]
        neighbour = self.grid[y2][x2]
        if direction == "N":
            current.north = True
            neighbour.south = True
        elif direction == "E":
            current.east = True
            neighbour.west = True
        elif direction == "S":
            current.south = True
            neighbour.north = True
        elif direction == "W":
            current.west = True
            neighbour.east = True

    def _creates_wide_open_area(self, x1: int, y1: int, x2: int,
                                y2: int, direction: str) -> bool:
        """
        Checks if removing a wall between two cells would create
        an invalid 3x3 open area.

        Returns:
            bool: True if it would create an invalid area.
        """
        self.remove_wall(x1, y1, x2, y2, direction)
        creates = bool(self._find_3x3_open_areas())
        self._close_wall(x1, y1, x2, y2, direction)
        return creates

    def generate(self, animation: bool = False) -> None:
        """
        Orchestrates the maze generation process.

        Initializes the grid, selects the algorithm, creates corridors,
        optionally applies the '42' pattern, and ensures no 3x3 areas exist.

        Args:
            animation (bool): If True, prints the maze state at each step.
        """
        self.grid = ([[Cell() for _ in range(self.width)]
                      for _ in range(self.height)])
        self._apply_pattern_42()
        self._validate_entry_exit()

        if self.algorithm == "dfs":
            self._generate_dfs()
        elif self.algorithm == "prim":
            self._generate_prim()
        else:
            raise ValueError(f"Unknown generation "
                             f"algorithm: '{self.algorithm}'")

        if self.perfect is False:
            self._open_corners_and_center()
            self._ensure_no_dead_ends()

        if self._find_3x3_open_areas():
            print("Warning: a 3x3 open area was detected after generation.")

        if animation:
            delay: float = 0.03
            self.grid = ([[Cell() for _ in range(self.width)]
                         for _ in range(self.height)])
            for x, y, nx, ny, direction in self.generation_steps:
                self.remove_wall(x, y, nx, ny, direction)
                os.system("cls" if os.name == "nt" else "clear")
                self.print_maze()
                time.sleep(delay)
            os.system("cls" if os.name == "nt" else "clear")

        if not self.solve():
            raise ValueError("Maze could not be solved "
                             "after pattern application.")

    def _path_to_directions(self, path: list[tuple[int, int]]) -> str:
        """
        Converts a list of path coordinates into a string of directions.

        Args:
            path (list[tuple[int, int]]): Ordered list of path cells.

        Returns:
            str: Direction sequence (e.g., "NSWE").
        """
        directions = ""
        for (x1, y1), (x2, y2) in zip(path, path[1:]):
            if x2 == x1 + 1 and y2 == y1:
                directions += "E"
            elif x2 == x1 - 1 and y2 == y1:
                directions += "W"
            elif y2 == y1 + 1 and x2 == x1:
                directions += "S"
            elif y2 == y1 - 1 and x2 == x1:
                directions += "N"
            else:
                raise ValueError(f"Non-adjacent path cells: "
                                 f"({x1},{y1}) -> ({x2},{y2})")
        return directions

    def show_hide_shortest_path(self) -> None:
        """
        Toggles the visibility of the shortest path calculation
        and updates the display.
        """
        self.show_path = not self.show_path
        self.print_maze()

    def rotate_wall_colours(self) -> None:
        """
        Cycles to the next available colour index for wall rendering.
        """
        self.colour_index = (self.colour_index + 1) % len(self.wall_colours)
        self.print_maze()

    def rotate_pattern_colours(self) -> None:
        """
        Cycles to the next available colour index for "42" pattern rendering.
        """
        self.pattern_colour_index = ((self.pattern_colour_index +
                                      1) % len(self.pattern_colours))
        self.print_maze()

    def print_maze(self) -> None:
        """
        Displays the current maze state in the terminal using ANSI colors.

        Visualizes walls, the entry/exit points, the optional shortest path,
        and the '42' pattern.
        """
        center_y, center_x = self.height // 2, self.width // 2
        pattern_coords = [
            (-1, 0), (-1, 1), (-1, 2), (-2, 0), (-3, 0), (-3, -1), (-3, -2),
            (1, 0), (3, -1), (1, -2), (2, -2), (3, -2), (2, 0), (3, 0),
            (1, 1), (3, 2), (2, 2), (1, 2)
        ]

        reset = "\033[0m"
        wall_colour = self.wall_colours[self.colour_index]
        pattern_colour = self.pattern_colours[self.pattern_colour_index]
        entry_colour = "\033[44m"
        exit_colour = "\033[41m"
        path_colour = "\033[43m"
        wall_block = f"{wall_colour}\u2588{reset}"

        path_cells: set[tuple[int, int]] = set()
        path_edges = set()
        if self.show_path:
            solution = self.solve()
            path_cells = set(solution)
            for a, b in zip(solution, solution[1:]):
                path_edges.add((a, b))
                path_edges.add((b, a))

        print(wall_block * (self.width * 2 + 1))
        for y in range(self.height):
            row = wall_block
            for x in range(self.width):
                is_42 = (x - center_x, y - center_y) in pattern_coords
                if (x, y) == self.entry:
                    floor = f"{entry_colour} {reset}"
                elif (x, y) == self.exit:
                    floor = f"{exit_colour} {reset}"
                elif (x, y) in path_cells:
                    floor = f"{path_colour} {reset}"
                elif is_42:
                    floor = f"{pattern_colour}\u2588{reset}"
                else:
                    floor = " "

                if self.grid[y][x].east:
                    side = wall_block
                elif ((x, y), (x + 1, y)) in path_edges:
                    side = f"{path_colour} {reset}"
                else:
                    side = " "
                row += floor + side
            print(row)

            row_bottom = wall_block
            for x in range(self.width):
                if self.grid[y][x].south:
                    below = wall_block
                elif ((x, y), (x, y + 1)) in path_edges:
                    below = f"{path_colour} {reset}"
                else:
                    below = " "
                row_bottom += below + wall_block
            print(row_bottom)
