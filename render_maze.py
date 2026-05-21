from typing import Any


def get_file_name() -> str:
    with open("config.txt", "r") as file:
        text: list[str] = file.readlines()
        for line in text:
            if line.startswith("OUTPUT_FILE="):
                return line.strip().removeprefix("OUTPUT_FILE=")
        raise Exception("Fatal error: No 'OUTPUT_FILE' line in the file")


def get_maze_coords(maze_file: str) -> list[str]:
    maze_coords: list[str] = []
    try:
        with open(maze_file, "r") as file:
            row: str = file.readline()
            while row and row != "\n":
                maze_coords.append(row.strip())
                row = file.readline()
    except FileNotFoundError as e:
        raise Exception(f"Error: file {maze_file} doesn't exist: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error reading the file: {str(e)}")
    return maze_coords


def get_dimensions() -> dict[str, int]:
    with open("config.txt", "r") as file:
        dims: dict[str, int] = {}
        text: list[str] = file.readlines()
        for line in text:
            line_clean = line.strip()
            if not line_clean or line_clean.startswith("#"):
                continue
            if line_clean.startswith("WIDTH="):
                dims["WIDTH"] = (int(line_clean.removeprefix("WIDTH=")))
            elif line_clean.startswith("HEIGHT="):
                dims["HEIGHT"] = (int(line_clean.removeprefix("HEIGHT=")))
        if len(dims) < 2:
            raise Exception("Fatal error: No 'WIDTH' "
                            "or 'HEIGHT' line in the file config.txt")
        return dims


def get_way(maze_file: str) -> dict[str, Any]:
    way: dict[str, Any] = {}
    try:
        with open(maze_file, "r") as file:
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


def main() -> None:
    try:
        maze_file: str = (get_file_name())
        maze_coords: list[str] = get_maze_coords(maze_file)
        dims = get_dimensions()
        way: dict[str, Any] = get_way(maze_file)
        print(maze_coords[0][0])  # compruebo que puedo acceder a cada dígito.
        print(dims)
        print(way)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
