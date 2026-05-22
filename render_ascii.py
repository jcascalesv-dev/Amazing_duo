from typing import Any


def render_maze(
    dims: dict[str, int], maze_coords: list[str], way: dict[str, Any]
) -> None:
    print("\n--- RENDERIZADO ASCII DEL LABERINTO ---")
    for row in maze_coords:
        top_line = ""
        mid_line = ""
        for digit in row:
            decimal: int = int(digit, 16)
            # Muro Norte (Bit 0)
            if decimal & 1:
                top_line += "+---"
            else:
                top_line += "+   "
            # Muro Oeste (Bit 3)
            if decimal == 15:
                mid_line += "| x "
            elif decimal & 8:
                mid_line += "|   "
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

