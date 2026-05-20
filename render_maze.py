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


def main() -> None:
    try:
        maze_file: str = (get_file_name())
        maze_coords: list[str] = get_maze_coords(maze_file)
        print(maze_coords[0][0])  # compruebo que puedo acceder a cada dígito.
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
