import random
import sys
import os
from collections import deque

# Constants for the wall bits (N, E, S, W)
N: int = 1  # 2^0
E: int = 2  # 2^1
S: int = 4  # 2^2
W: int = 8  # 2^3

# Address mapping: (delta_x, delta_y, wall_to_break, opposite_wall)
DIRECTIONS: list[tuple[int, int, int, int]] = [
    (0, -1, N, S),  # Go North
    (1, 0, E, W),   # Go East
    (0, 1, S, N),   # Go South
    (-1, 0, W, E)   # Go West
]

# Representation of 42 ('X' will be closed walls, '.' will be open space
# for corridors) Size: 7 wide x 5 high
PATTERN_42: list[str] = [
    "X.X.XXX",
    "X.X...X",
    "XXX.XXX",
    "..X.X..",
    "..X.XXX"
]


class InvalidMazeConfig(Exception):
    pass


class MazeGenerator:
    def __init__(self, width: int, height: int, perfect: bool,
                 seed: int | None = None) -> None:
        # Initialize the maze generator.
        self.width: int = width
        self.height: int = height
        self.perfect: bool = perfect

        if seed is not None:
            random.seed(seed)

        # Initialize the grid: 15 (binary 1111) means all walls closed.
        self.grid: list[list[int]] = [
            [15 for _ in range(width)] for _ in range(height)]

        # Boolean array to determine if a cell has been visited by the DFS
        self.visited: list[list[bool]] = [
            [False for _ in range(width)] for _ in range(height)]
        self.solution_coords: list[tuple[int, int]] = []

    def _stamp_42(self) -> None:
        pattern_h: int = len(PATTERN_42)
        pattern_w: int = len(PATTERN_42[0])

        # We check if the maze is large enough. We add a margin of +2
        if self.width < pattern_w + 2 or self.height < pattern_h + 2:
            print(
                "Error: The maze size is too small"
                " to draw the '42' pattern.", file=sys.stderr)
            return

        # We calculate the offset to center the pattern
        offset_x: int = (self.width - pattern_w) // 2
        offset_y: int = (self.height - pattern_h) // 2

        # We iterated on the pattern design
        for py, row in enumerate(PATTERN_42):
            for px, char in enumerate(row):
                if char == 'X':
                    self.visited[offset_y + py][offset_x + px] = True

    def _get_unvisited_neighbors(self, cx: int, cy: int
                                 ) -> list[tuple[int, int, int, int]]:
        neighbors: list[tuple[int, int, int, int]] = []

        for dx, dy, wall, opp_wall in DIRECTIONS:
            nx, ny = cx + dx, cy + dy

            # Check map boundaries
            if 0 <= nx < self.width and 0 <= ny < self.height:
                # Check if it has not been visited
                if not self.visited[ny][nx]:
                    neighbors.append((nx, ny, wall, opp_wall))
        return neighbors

    def _is_in_42_pattern(self, x: int, y: int) -> bool:
        pattern_h: int = len(PATTERN_42)
        pattern_w: int = len(PATTERN_42[0])
        offset_x: int = (self.width - pattern_w) // 2
        offset_y: int = (self.height - pattern_h) // 2

        if (offset_x <= x < offset_x + pattern_w and
                offset_y <= y < offset_y + pattern_h):
            char_x = x - offset_x
            char_y = y - offset_y
            if PATTERN_42[char_y][char_x] == 'X':
                return True
        return False

    def _make_imperfect(self) -> None:
        # We calculate how many walls to break down
        # (e.g., 5% of the total size)
        num_walls: int = (self.width * self.height) // 20
        if num_walls == 0:
            num_walls = 1

        broken_count: int = 0
        attempts: int = 0
        max_attempts: int = num_walls * 10

        while broken_count < num_walls and attempts < max_attempts:
            attempts += 1
            # We avoid the edges
            cx: int = random.randint(1, self.width - 2)
            cy: int = random.randint(1, self.height - 2)

            if self._is_in_42_pattern(cx, cy):
                continue

            dx, dy, wall, opp_wall = random.choice(DIRECTIONS)
            nx, ny = cx + dx, cy + dy

            # We verified that the neighbor is neither
            # the border nor the pattern 42
            if (nx <= 0 or nx >= self.width - 1 or
                    ny <= 0 or ny >= self.height - 1):
                continue
            if self._is_in_42_pattern(nx, ny):
                continue

            # If there's a wall between the cells, we'll break it down.
            if self.grid[cy][cx] & wall:
                self.grid[cy][cx] &= ~wall
                self.grid[ny][nx] &= ~opp_wall
                broken_count += 1

    def _solve_bfs(self, start_x: int, start_y: int,
                   end_x: int, end_y: int) -> None:
        queue: deque[tuple[int, int]] = deque([(start_x, start_y)])
        visited_bfs: set[tuple[int, int]] = {(start_x, start_y)}

        # Dictionary to trace where we come from
        came_from: dict[tuple[int, int], tuple[int, int] | None] = {
            (start_x, start_y): None
        }

        while queue:
            cx, cy = queue.popleft()

            if cx == end_x and cy == end_y:
                # We retraced the route by walking backwards.
                path: list[tuple[int, int]] = []
                current: tuple[int, int] | None = (cx, cy)
                while current is not None:
                    path.append(current)
                    current = came_from[current]

                # We reversed the list so that it goes from START to END
                self.solution_coords = path[::-1]
                return

            for dx, dy, wall, _ in DIRECTIONS:
                if not (self.grid[cy][cx] & wall):
                    nx, ny = cx + dx, cy + dy
                    if (nx, ny) not in visited_bfs:
                        visited_bfs.add((nx, ny))
                        came_from[(nx, ny)] = (cx, cy)
                        queue.append((nx, ny))

        # If it exits the while loop, there is no possible solution.
        self.solution_coords = []

    def generate(
            self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:

        # Validate start and exit parameters
        if not (0 <= start_x < self.width and 0 <= start_y < self.height):
            print(
                f"Error: ENTRY ({start_x},{start_y}) out of range.",
                file=sys.stderr
            )
            sys.exit()
        if not (0 <= end_x < self.width and 0 <= end_y < self.height):
            print(
                f"Error: EXIT ({end_x},{end_y}) out of range.",
                file=sys.stderr
            )
            sys.exit()

        # Try to print pattern 42
        self._stamp_42()

        # Validate start and exit parameters in 42
        if self.visited[start_y][start_x]:
            raise InvalidMazeConfig(
                f"Error: ENTRY ({start_x},{start_y}) falls inside a '42' wall."
                " Please change ENTRY in config.txt."
            )

        if self.visited[end_y][end_x]:
            raise InvalidMazeConfig(
                f"Error: EXIT ({end_x},{end_y}) falls inside a '42' wall. "
                "Please change EXIT in config.txt."
            )

        # 3. Initialize the DFS
        stack: list[tuple[int, int]] = [(start_x, start_y)]
        self.visited[start_y][start_x] = True

        while stack:
            cx, cy = stack[-1]  # Look at the current cell without removing
            neighbors = self._get_unvisited_neighbors(cx, cy)

            if neighbors:
                # Choose a random neighbor
                nx, ny, wall_to_break, opposite_wall = random.choice(neighbors)

                # Break down the corresponding walls using bitwise AND and NOT.
                self.grid[cy][cx] &= ~wall_to_break
                self.grid[ny][nx] &= ~opposite_wall

                # Mark as visited, add to stack
                self.visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                # If there are no neighbors, we go backtrack.
                stack.pop()

        if not self.perfect:
            self._make_imperfect()

        # Finally, we calculated the actual shortest path using BFS
        self._solve_bfs(start_x, start_y, end_x, end_y)

    def get_solution_path_string(self) -> str:
        path_str: str = ""

        if not hasattr(self, 'solution_coords') or not self.solution_coords:
            return path_str

        # We compare each cell with the next to find the direction
        for i in range(len(self.solution_coords) - 1):
            cx, cy = self.solution_coords[i]
            nx, ny = self.solution_coords[i + 1]
            if nx == cx + 1:
                path_str += "E"
            elif nx == cx - 1:
                path_str += "W"
            elif ny == cy + 1:
                path_str += "S"
            elif ny == cy - 1:
                path_str += "N"

        return path_str

    def save_to_file(self, filename: str, start: tuple[int, int],
                     end: tuple[int, int]) -> None:
        with open(filename, 'w', encoding="utf-8") as f:
            # Write the map in hexadecimal
            for row in self.grid:
                line = "".join(f"{cell:X}" for cell in row)
                f.write(f"{line}\n")
            f.write("\n")
            f.write(f"{start[0]},{start[1]}\n")  # Start x,y
            f.write(f"{end[0]},{end[1]}\n")      # Exit x,y
            path_str: str = self.get_solution_path_string()
            if not path_str:
                raise InvalidMazeConfig(
                    "Error: No valid path found from ENTRY to EXIT.")
            f.write(f"{path_str}\n")                 # Solution NESW...

            f.flush()            # Empty Python's internal buffer
            os.fsync(f.fileno())  # It forces the OS to write to the disk.
