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
    except Exception as e:
        raise Exception(f"Error: {str(e)}")
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
                            "or 'HEIGHT' line in the file")
        return dims


def main() -> None:
    try:
        maze_file: str = (get_file_name())
        maze_coords: list[str] = get_maze_coords(maze_file)
        dims = get_dimensions()
        print(maze_coords[0][0])  # compruebo que puedo acceder a cada dígito.
        print(dims)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
