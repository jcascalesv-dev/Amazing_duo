from typing import Any
import sys


def get_maze_coords(maze_file: str) -> list[str]:
    maze_coords: list[str] = []
    try:
        with open(maze_file, "r", encoding="utf-8") as file:
            row: str = file.readline()
            while row and row != "\n":
                maze_coords.append(row.strip())
                row = file.readline()
    except FileNotFoundError:
        print("Critical error: "
              f"The file could not be found {maze_file}.", file=sys.stderr)
        sys.exit()
    except Exception as e:
        raise Exception(f"Unexpected error reading the file: {str(e)}")
    return maze_coords


def get_way(maze_file: str) -> dict[str, Any]:
    way: dict[str, Any] = {}
    try:
        with open(maze_file, "r", encoding="utf-8") as file:
            row: str = file.readline()
            while row and row != "\n":
                row = file.readline()
                continue
            row = file.readline()
            if row:
                way["entrance"] = tuple(int(r) for r in row.strip().split(","))
            row = file.readline()
            if row:
                way["exit"] = tuple(int(r) for r in row.strip().split(","))
            row = file.readline()
            if row:
                way["directions"] = row.strip()
    except FileNotFoundError as e:
        raise Exception(f"Error: file {maze_file} doesn't exist: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error reading the file: {str(e)}")
    return way
