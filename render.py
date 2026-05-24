import sys
from typing import Any
from mlx import Mlx

CELL_SIZE = 32
WALL_THICKNESS = 4  # El grosor en píxeles de nuestros nuevos archivos .xpm
MAX_SCREEN_WIDTH = 1920
MAX_SCREEN_HEIGHT = 1080


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
    # 1. Calculamos el tamaño final de la ventana
    screen_width: int = dims["WIDTH"] * CELL_SIZE
    screen_height: int = dims["HEIGHT"] * CELL_SIZE
    # 2. EL ESCUDO ANTI-CRASHES
    if screen_width > MAX_SCREEN_WIDTH or screen_height > MAX_SCREEN_HEIGHT:
        print("Error Crítico: El laberinto es demasiado "
              "grande para la interfaz gráfica "
              f"({screen_width}x{screen_height} px). El límite seguro es "
              f"{MAX_SCREEN_WIDTH}x{MAX_SCREEN_HEIGHT} px. "
              "Por favor, use el modo de renderizado ASCII.", file=sys.stderr)
        sys.exit(1)
    # 3. Inicializamos la librería gráfica
    mlx_visual = Mlx()
    mlx_ptr = mlx_visual.mlx_init()
    window_ptr: int = mlx_visual.mlx_new_window(  # type: ignore
        mlx_ptr, screen_width, screen_height, "A-maze-ing MLX!"
    )
    # 4. CARGAMOS LAS DOS TEXTURAS MAESTRAS
    img_wall_h, _, _ = mlx_visual.mlx_xpm_file_to_image(  # type: ignore
        mlx_ptr, "textures/wall_h.xpm"
    )
    img_wall_v, _, _ = mlx_visual.mlx_xpm_file_to_image(  # type: ignore
        mlx_ptr, "textures/wall_v.xpm"
    )
    # 5. EL BUCLE DE RENDERIZADO DE MUROS
    for y, row in enumerate(maze_coords):
        for x, digit in enumerate(row):
            decimal: int = int(digit, 16)
            pixel_x = x * CELL_SIZE
            pixel_y = y * CELL_SIZE
            # --- A. LÓGICA DE MUROS INTERNOS (Norte y Oeste) ---
            if decimal & 1:  # NORTE(bloque horizontal en el techo de la celda)
                mlx_visual.mlx_put_image_to_window(  # type: ignore
                    mlx_ptr, window_ptr, img_wall_h, pixel_x, pixel_y
                )
            if decimal & 8:  # OESTE (bloque vertical en la pared izquierda)
                mlx_visual.mlx_put_image_to_window(  # type: ignore
                    mlx_ptr, window_ptr, img_wall_v, pixel_x, pixel_y
                )
            # --- B. CIERRE PERIMETRAL EXTERIOR ---
            # Borde Este (última colum):Empujamos el muro vertical a la derecha
            if x == len(row) - 1 and (decimal & 2):
                mlx_visual.mlx_put_image_to_window(  # type: ignore
                    mlx_ptr, window_ptr, img_wall_v, 
                    pixel_x + CELL_SIZE - WALL_THICKNESS, pixel_y
                )
            # Borde Sur (última fila): Empujamos el muro horizontal hacia abajo
            if y == len(maze_coords) - 1 and (decimal & 4):
                mlx_visual.mlx_put_image_to_window(  # type: ignore
                    mlx_ptr, window_ptr, img_wall_h, 
                    pixel_x, pixel_y + CELL_SIZE - WALL_THICKNESS
                )
    # 6. Mantener la ventana abierta
    mlx_visual.mlx_loop(mlx_ptr)  # type: ignore