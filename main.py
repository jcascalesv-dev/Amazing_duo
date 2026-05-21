from typing import Any
from get_maze_data import (
    get_file_name,
    get_maze_coords,
    get_dimensions,
    get_way
)
from render import render_maze


def main() -> None:
    try:
        maze_file: str = (get_file_name())
        maze_coords: list[str] = get_maze_coords(maze_file)
        dims: dict[str, int] = get_dimensions()
        way: dict[str, Any] = get_way(maze_file)
        render_maze(dims, maze_coords, way)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
