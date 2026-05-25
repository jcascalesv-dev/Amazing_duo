from typing import Any


def transform_directions(
    entrance: tuple[int, int], directions: str
) -> set[Any]:
    x: int
    y: int
    x, y = entrance
    start: list[tuple[int, int]] = []
    start.append(entrance)
    for direction in directions:
        if direction == "N":
            y -= 1
        elif direction == "E":
            x += 1
        elif direction == "S":
            y += 1
        elif direction == "W":
            x -= 1
        start.append((x, y))
    return set(start)


def render_maze(
    dims: dict[str, int], maze_coords: list[str], way: dict[str, Any]
) -> None:
    directions = transform_directions(way["entrance"], way["directions"])
    print("\n--- RENDERIZADO ASCII DEL LABERINTO ---")
    for y, row in enumerate(maze_coords):
        top_line = ""
        mid_line = ""
        for x, digit in enumerate(row):
            decimal: int = int(digit, 16)
            # Muro Norte (Bit 0)
            if decimal & 1:
                top_line += "+---"
            else:
                top_line += "+   "
            # Muro Oeste (Bit 3)
            if decimal & 8:
                if (x, y) == way["entrance"]:
                    mid_line += "| 🏁"
                elif (x, y) == way["exit"]:
                    mid_line += "| ✅"
                elif (x, y) in directions:
                    mid_line += "| ○ "
                elif decimal == 15:
                    mid_line += "| ⦿ "
                else:
                    mid_line += "|   "
            else:
                if (x, y) == way["entrance"]:
                    mid_line += "  🏁"
                elif (x, y) == way["exit"]:
                    mid_line += "  ✅"
                elif (x, y) in directions:
                    mid_line += "  ○ "
                elif decimal == 15:
                    mid_line += "  ⦿ "
                else:
                    mid_line += "    "
        # Cerramos el borde derecho de cada fila (Muro Este de la última celda)
        last_decimal = int(row[-1], 16)
        top_line += "+"
        mid_line += "|" if (last_decimal & 2) else " "
        print(top_line)
        print(mid_line)
    # Dibujamos el muro Sur de la última fila (Bit 2)
    bottom_line = ""
    for digit in maze_coords[-1]:
        if int(digit, 16) & 4:
            bottom_line += "+---"
        else:
            bottom_line += "+   "
    bottom_line += "+"
    print(bottom_line)
