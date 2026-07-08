import random
from collections import deque


class Cell:
    def __init__(self) -> None:
        self.north = True
        self.east = True
        self.south = True
        self.west = True
        self.visited = False


class MazeGenerator:
    def __init__(self, width: int,
                 height: int, entry: tuple[int, int],
                 exit: tuple[int, int],
                 output_file: str,
                 seed: int | None = None) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.output_file = output_file

        if seed is not None:
            random.seed(seed)

        self.grid = [[Cell() for _ in range(width)] for _ in range(height)]

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

    def generate(self) -> None:
        try:
            stack = []

            start_x = random.randint(0, self.width - 1)
            start_y = random.randint(0, self.height - 1)

            current = self.grid[start_y][start_x]
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
                else:
                    stack.pop()
        except IndexError as er:
            print(f"Generation failed: Grid access error at ({x}, {y}) - {er}")
            raise
        except Exception as er:
            print(f"An unexpected error occurred "
                  f"during maze generation: {er}")
            raise

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

    def export_to_hex(self) -> None:
        with open(self.output_file, 'w') as file:
            for y in range(0, self.height):
                row_string = ""
                for x in range(0, self.width):
                    cell = self.grid[y][x]
                    val = ((1 if cell.north else 0) + (2 if cell.east else 0) +
                           (4 if cell.south else 0) + (8 if cell.west else 0))
                    row_string += hex(val)[2:]
                file.write(f"{row_string}\n")

    # test
    def print_maze(self) -> None:
        center_y, center_x = self.height // 2, self.width // 2
        pattern_coords = [
            (-1, 0), (-1, 1), (-1, 2), (-2, 0), (-3, 0), (-3, -1), (-3, -2),
            (1, 0), (3, -1), (1, -2), (2, -2), (3, -2), (2, 0), (3, 0),
            (1, 1), (3, 2), (2, 2), (1, 2)
        ]

        print("\u2588" * (self.width * 2 + 1))
        for y in range(self.height):
            row = "\u2588"
            for x in range(self.width):
                is_42 = (x - center_x, y - center_y) in pattern_coords
                char = " " if is_42 else (" " if not self.grid[y][x].east else "\u2588")
                row += (" " if is_42 else " ") + ("\u2588" if self.grid[y][x].east else " ")
            print(row)

            row_bottom = "\u2588"
            for x in range(self.width):
                row_bottom += ("\u2588" if self.grid[y][x].south else " ") + "\u2588"
            print(row_bottom)
