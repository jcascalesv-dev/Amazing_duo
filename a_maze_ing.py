import sys
import time
from mazegen.generator import MazeGenerator, InvalidMazeConfig
from typing import Any
from get_maze_data import get_maze_coords, get_way
from render import render_maze


def parse_config(filepath: str) -> dict[str, str]:
    config: dict[str, str] = {}

    try:
        with open(filepath, 'r', encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # We ignore blank lines or comments
                if not line or line.startswith('#'):
                    continue
                # We separate by the first '=' we find
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()

    except FileNotFoundError:
        print(f"Error: Config file '{filepath}' not found.", file=sys.stderr)
        sys.exit()

    return config


def parse_coords(coord_str: str) -> tuple[int, int]:
    try:
        x, y = map(int, coord_str.split(','))
        return x, y
    except ValueError:
        print(f"Error: Invalid coordinate format '{coord_str}'."
              " Expected: 'x,y'.", file=sys.stderr)
        sys.exit()


def parse_bool(bool_str: str) -> bool:
    return bool_str.strip().lower() in ('true', '1')


def main() -> None:
    # We validate that the file is passed as an argument
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <config.txt>", file=sys.stderr)
        sys.exit()

    config_file = sys.argv[1]

    # We parse the configuration
    config = parse_config(config_file)
    time.sleep(1.5)

    # We extract the variables (with basic validation)
    try:
        width = int(config['WIDTH'])
        if width < 3:
            print(f"Error: {width} must be greater than two.",
                  file=sys.stderr)
            sys.exit()
        height = int(config['HEIGHT'])
        if height < 3:
            print(f"Error: {height} must be greater than two.",
                  file=sys.stderr)
            sys.exit()
        entry_pos = parse_coords(config['ENTRY'])
        exit_pos = parse_coords(config['EXIT'])
        output_file = config['OUTPUT_FILE']

        # Optional
        seed = int(config['SEED']) if 'SEED' in config else None

        perfect = parse_bool(config['PERFECT']
                             ) if 'PERFECT' in config else True

    except KeyError as e:
        print(f"Error: Missing required configuration key: {e}",
              file=sys.stderr)
        sys.exit()
    except ValueError as e:
        print(f"Error: Invalid number format in configuration. {e}",
              file=sys.stderr)
        sys.exit()

    # We instantiate and run the generator
    try:
        generator = MazeGenerator(
            width=width, height=height, perfect=perfect, seed=seed)
        generator.generate(start_x=entry_pos[0], start_y=entry_pos[1],
                           end_x=exit_pos[0], end_y=exit_pos[1])
        generator.save_to_file(
            filename=output_file, start=entry_pos, end=exit_pos)
        print(f"Maze successfully generated and saved to {output_file}")

    except InvalidMazeConfig as e:
        print(e, file=sys.stderr)
        sys.exit()
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit()
    # We start the rendering process.
    try:
        maze_coords: list[str] = get_maze_coords(output_file)
        time.sleep(0.2)
        dims: dict[str, int] = {"WIDTH": width, "HEIGHT": height}
        way: dict[str, Any] = get_way(output_file)
        time.sleep(0.2)
        render_maze(dims, maze_coords, way, perfect, output_file)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
