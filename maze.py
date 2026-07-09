import random
from collections import deque
import os
import time


class Cell:
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
                 perfect: bool = False,
                 seed: int | None = None) -> None:
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

        self.colour_index = 0

        if seed is not None:
            random.seed(seed)

    def get_unvisited_neighbours(
            self, x: int, y: int
            ) -> list[tuple[str, int, int]]:
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

    def _generate_prim(self) -> None:
        pass

    def get_valid_neighbors(self,
                            cord: tuple[int, int]) -> list[tuple[int, int]]:
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
        path = []
        current = exit

        while current is not None:
            path.append(current)
            current = parent[current]

        return path[::-1]

    def solve(self) -> list[tuple[int, int]]:
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

        if candidates:
            direction = random.choice(candidates)
            if direction == "N":
                x2, y2 = x, y - 1
            elif direction == "E":
                x2, y2 = x + 1, y
            elif direction == "S":
                x2, y2 = x, y + 1
            else:
                x2, y2 = x - 1, y
            self.remove_wall(x, y, x2, y2, direction)
            self.generation_steps.append((x, y, x2, y2, direction))

    def _validate_entry_exit(self) -> None:
        entry_x, entry_y = self.entry
        exit_x, exit_y = self.exit

        if self.grid[entry_y][entry_x].pattern:
            raise ValueError("Entry point is inside the '42' pattern!")
        if self.grid[exit_y][exit_x].pattern:
            raise ValueError("Exit point is inside the '42' pattern!")

    def _ensure_no_dead_ends(self) -> None:
        while True:
            dead_ends = self._find_all_dead_ends()
            if not dead_ends:
                return
            for x, y in dead_ends:
                self._break_one_wall(x, y)

            if self._find_all_dead_ends() == dead_ends:
                break

    def _safe_remove_wall(self, x: int, y: int, direction: str) -> None:
        offsets = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
        if direction not in offsets:
            return

        dx, dy = offsets[direction]
        nx, ny = x + dx, y + dy

        if not (0 <= nx < self.width and 0 <= ny < self.height):
            return
        if self.grid[y][x].pattern or self.grid[ny][nx].pattern:
            return

        self.remove_wall(x, y, nx, ny, direction)
        self.generation_steps.append((x, y, nx, ny, direction))

    def _open_corners_and_center(self) -> None:
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

    def generate(self, animation: bool = False, algo: str = "dfs") -> None:
        self.grid = ([[Cell() for _ in range(self.width)]
                      for _ in range(self.height)])
        self._apply_pattern_42()
        self._validate_entry_exit()

        if algo == "dfs":
            self._generate_dfs()

        if self.perfect is False:
            self._open_corners_and_center()
            self._ensure_no_dead_ends()

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
        self.show_path = not self.show_path
        self.print_maze()

    def rotate_wall_colours(self) -> None:
        self.colour_index = (self.colour_index + 1) % len(self.wall_colours)
        self.print_maze()

    def print_maze(self) -> None:
        center_y, center_x = self.height // 2, self.width // 2
        pattern_coords = [
            (-1, 0), (-1, 1), (-1, 2), (-2, 0), (-3, 0), (-3, -1), (-3, -2),
            (1, 0), (3, -1), (1, -2), (2, -2), (3, -2), (2, 0), (3, 0),
            (1, 1), (3, 2), (2, 2), (1, 2)
        ]

        reset = "\033[0m"
        wall_colour = self.wall_colours[self.colour_index]
        pattern_colour = "\033[32m"
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
                # side = wall_block if self.grid[y][x].east else " "
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
                # below = wall_block if self.grid[y][x].south else " "
                row_bottom += below + wall_block
            print(row_bottom)
