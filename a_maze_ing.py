import sys
import time
from mazegen.generator import MazeGenerator, InvalidMazeConfig
from typing import Any
from get_maze_data import get_maze_coords, get_way
from render import render_maze


def parse_config(filepath: str) -> dict[str, str]:
    """Lee el archivo de configuración y extrae las variables clave-valor."""
    config: dict[str, str] = {}

    try:
        with open(filepath, 'r', encoding="utf-8") as f:
            for line in f:
                # Quitamos espacios en blanco a los lados
                line = line.strip()

                # Ignoramos líneas vacías o comentarios
                if not line or line.startswith('#'):
                    continue

                # Separamos por el primer '=' que encontremos
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()

    except FileNotFoundError:
        print(f"Error: Config file '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)

    return config


def parse_coords(coord_str: str) -> tuple[int, int]:
    """Convierte un string 'x,y' en una tupla de enteros (x, y)."""
    try:
        x, y = map(int, coord_str.split(','))
        return x, y
    except ValueError:
        print(f"Error: Invalid coordinate format '{coord_str}'."
              " Expected: 'x,y'.", file=sys.stderr)
        sys.exit(1)


def parse_bool(bool_str: str) -> bool:
    """Convierte un string ('true', 'false', '1', '0') a su valor booleano."""
    return bool_str.strip().lower() in ('true', '1')


def main() -> None:
    # 1. Validamos que se pase el archivo por argumento
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <config.txt>", file=sys.stderr)
        sys.exit(1)

    config_file = sys.argv[1]

    # 2. Parseamos la configuración
    config = parse_config(config_file)

    # 3. Extraemos las variables (con validación básica)
    try:
        width = int(config['WIDTH'])
        height = int(config['HEIGHT'])
        entry_pos = parse_coords(config['ENTRY'])
        exit_pos = parse_coords(config['EXIT'])
        output_file = config['OUTPUT_FILE']

        # Opcionales
        seed = int(config['SEED']) if 'SEED' in config else None
        perfect = parse_bool(config['PERFECT']
                             ) if 'PERFECT' in config else True

    except KeyError as e:
        print(f"Error: Missing required configuration key: {e}",
              file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Invalid number format in configuration. {e}",
              file=sys.stderr)
        sys.exit(1)

    # 4. Instanciamos y ejecutamos el generador
    try:
        generator = MazeGenerator(
            width=width, height=height, perfect=perfect, seed=seed)
        generator.generate(start_x=entry_pos[0], start_y=entry_pos[1],
                           end_x=exit_pos[0], end_y=exit_pos[1])
        generator.save_to_file(
            filename=output_file, start=entry_pos, end=exit_pos)
        print(f"Maze successfully generated and saved to {output_file}")

    except InvalidMazeConfig as e:  # Aquí capturamos tu InvalidMazeConfig
        print(e, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Captura de emergencia por si algo explota
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
    # 5. Arrancamos la maquinaria del renderizado.
    try:
        maze_coords: list[str] = get_maze_coords(output_file)
        time.sleep(0.5)
        dims: dict[str, int] = {"WIDTH": width, "HEIGHT": height}
        time.sleep(0.5)
        way: dict[str, Any] = get_way(output_file)
        time.sleep(0.5)
        render_maze(dims, maze_coords, way, perfect, output_file)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
