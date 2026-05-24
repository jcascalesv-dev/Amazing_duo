from typing import Any
import sys

"""
Función para leer el fichero config y obtener el nombre del fichero
donde se va a guardar el laberinto.
"""


def get_file_name() -> str:
    with open("config.txt", "r") as file:
        text: list[str] = file.readlines()
        for line in text:
            if line.startswith("OUTPUT_FILE="):
                return line.strip().removeprefix("OUTPUT_FILE=")
        raise Exception("Fatal error: No 'OUTPUT_FILE' line in the file")


"""
Función para leer el fichero del laberinto y obtener
las coordenadas para renderizar los muros.
"""


def get_maze_coords(maze_file: str) -> list[str]:
    maze_coords: list[str] = []
    try:
        with open(maze_file, "r") as file:
            row: str = file.readline()
            while row and row != "\n":
                maze_coords.append(row.strip())
                row = file.readline()
    except FileNotFoundError:
        print("Error crítico: "
              f"No se encuentra el archivo {maze_file}.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        raise Exception(f"Unexpected error reading the file: {str(e)}")
    return maze_coords


"""
Función para leer el fichero config y obtener las dimensiones
del laberinto.
"""


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


"""
Función para leer el fichero del laberinto y obtener los puntos de
inicio y fin y las direcciones para recrear el camino.
"""


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
