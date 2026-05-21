from typing import Any
from mlx import Mlx
CELL_SIZE = 32  # constante para el tamano de las texturas en pixels


def render_maze(
    dims: dict[str, int], maze_coords: list[str], way: dict[str, Any]
) -> None:
    # calculamos el tamano de la ventana en pixels
    screen_width: int = (dims["WIDTH"] * CELL_SIZE) + CELL_SIZE
    screen_height: int = (dims["HEIGHT"] * CELL_SIZE) + CELL_SIZE
    # Fabricamos nuestro objeto gráfico a partir del plano
    mlx_visual = Mlx()
    # Guardamos el identificador del motor gráfico
    mlx_ptr = mlx_visual.mlx_init()
    # Estamos usando un traductor ya que la librería está hecha en c
    # pero no tiene tipado así que lo silenciamos.
    window_ptr: int = mlx_visual.mlx_new_window(  # type: ignore
        mlx_ptr, screen_width, screen_height, "A-maze-ing!"
    )
    # Cargamos la textura para el muro. Descomponemos en 3 variables
    # pero solo necesitamos la imagen puesto que las medidas ya las tenemos.
    img_wall_north, _, _ = mlx_visual.mlx_xpm_file_to_image(  # type: ignore
        mlx_ptr, "textures/wall_north.xpm"
        )
    img_wall_east, _, _ = mlx_visual.mlx_xpm_file_to_image(  # type: ignore
        mlx_ptr, "textures/wall_east.xpm"
        )
    img_wall_south, _, _ = mlx_visual.mlx_xpm_file_to_image(  # type: ignore
        mlx_ptr, "textures/wall_south.xpm"
        )
    img_wall_west, _, _ = mlx_visual.mlx_xpm_file_to_image(  # type: ignore
        mlx_ptr, "textures/wall_west.xpm"
        )
    for y, row in enumerate(maze_coords):
        for x, digit in enumerate(row):
            decimal: int = int(digit, 16)
            pixel_x = x * CELL_SIZE
            pixel_y = y * CELL_SIZE
            if decimal & 1:
                mlx_visual.mlx_put_image_to_window(  # type: ignore
                    mlx_ptr, window_ptr, img_wall_north, pixel_x, pixel_y
                )
            if decimal & 2:
                mlx_visual.mlx_put_image_to_window(  # type: ignore
                    mlx_ptr, window_ptr, img_wall_east, pixel_x, pixel_y
                )
            if decimal & 4:
                mlx_visual.mlx_put_image_to_window(  # type: ignore
                    mlx_ptr, window_ptr, img_wall_south, pixel_x, pixel_y
                )
            if decimal & 8:
                mlx_visual.mlx_put_image_to_window(  # type: ignore
                    mlx_ptr, window_ptr, img_wall_west, pixel_x, pixel_y
                )
    # Llamamos al método de la librería que es un bucle infinito
    # para evitar que la ventana se cierre tras renderizar el
    # laberinto y quede a la espera.
    mlx_visual.mlx_loop(mlx_ptr)  # type: ignore
