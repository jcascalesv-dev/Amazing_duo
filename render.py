import sys
import time
import os
from typing import Any
from mlx import Mlx

CELL_SIZE = 32
WALL_THICKNESS = 4
MAX_SCREEN_WIDTH = 1920
MAX_SCREEN_HEIGHT = 1080
MENU_HEIGHT = 40
# Códigos de teclado para Linux (X11)
KEY_1 = 49
KEY_2 = 50
KEY_3 = 51
KEY_4 = 52
KEY_ESC = 65307


def transform_directions(
    entrance: tuple[int, int], directions: str
) -> set[tuple[int, int]]:
    """Transforma la cadena de direcciones en
    un SET de coordenadas ultrarrápido."""
    x, y = entrance
    start: list[tuple[int, int]] = [(x, y)]
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
    # 1. Pre-procesar el camino usando tu técnica optimizada
    directions_set = transform_directions(way["entrance"], way["directions"])
    # 2. Calculamos el tamaño final de la ventana
    screen_width: int = dims["WIDTH"] * CELL_SIZE
    screen_height: int = (dims["HEIGHT"] * CELL_SIZE) + MENU_HEIGHT
    # 3. EL ESCUDO ANTI-CRASHES
    if screen_width > MAX_SCREEN_WIDTH or screen_height > MAX_SCREEN_HEIGHT:
        print("Error Crítico: El laberinto es "
              "demasiado grande para la interfaz gráfica "
              f"({screen_width}x{screen_height} px). El límite seguro es "
              f"{MAX_SCREEN_WIDTH}x{MAX_SCREEN_HEIGHT} px. "
              "Por favor, use el modo de renderizado ASCII.", file=sys.stderr)
        sys.exit(1)
    # 4. Inicializamos la librería gráfica
    mlx_visual = Mlx()
    mlx_ptr = mlx_visual.mlx_init()
    window_ptr: int = mlx_visual.mlx_new_window(  # type: ignore
        mlx_ptr, screen_width, screen_height, "A-maze-ing MLX!"
    )
    # 5. CARGAMOS TODAS LAS TEXTURAS (Muros + Interior)
    img_wall_h, _, _ = mlx_visual.mlx_xpm_file_to_image(  # type: ignore
        mlx_ptr, "textures/wall_h.xpm"
    )
    img_wall_v, _, _ = mlx_visual.mlx_xpm_file_to_image(  # type: ignore
        mlx_ptr, "textures/wall_v.xpm"
    )
    img_logo_42, _, _ = mlx_visual.mlx_xpm_file_to_image(  # type: ignore
        mlx_ptr, "textures/logo_42.xpm"
    )
    img_start, _, _ = mlx_visual.mlx_xpm_file_to_image(  # type: ignore
        mlx_ptr, "textures/start.xpm"
    )
    img_exit, _, _ = mlx_visual.mlx_xpm_file_to_image(  # type: ignore
        mlx_ptr, "textures/exit.xpm"
    )
    img_path, _, _ = mlx_visual.mlx_xpm_file_to_image(  # type: ignore
        mlx_ptr, "textures/path.xpm"
    )
    # Le damos a la ventana un instante para mapearse
    # y evitar el corte superior
    time.sleep(0.3)
    show_path = True

    # 6. EL BUCLE MAESTRO DE RENDERIZADO
    def draw_frame() -> None:
        for y, row in enumerate(maze_coords):
            for x, digit in enumerate(row):
                decimal: int = int(digit, 16)
                pixel_x = x * CELL_SIZE
                pixel_y = y * CELL_SIZE
                coord = (x, y)
                # --- A. EL INTERIOR DE LA CELDA (Z-Index) ---
                # Dibujamos esto PRIMERO para que los muros
                # siempre queden por encima si hay roce
                if coord == way["entrance"]:
                    # Centramos la imagen de 24x24 en
                    # la celda de 32x32 (+4 píxeles)
                    mlx_visual.mlx_put_image_to_window(  # type: ignore
                        mlx_ptr, window_ptr, img_start,
                        pixel_x + 4, pixel_y + 4
                    )
                elif coord == way["exit"]:
                    mlx_visual.mlx_put_image_to_window(  # type: ignore
                        mlx_ptr, window_ptr, img_exit, pixel_x + 4, pixel_y + 4
                    )
                elif decimal == 15:
                    # El bloque masivo del 42 rellena
                    # todo el hueco exacto de 32x32
                    mlx_visual.mlx_put_image_to_window(  # type: ignore
                        mlx_ptr, window_ptr, img_logo_42, pixel_x, pixel_y
                    )
                #elif coord in directions_set:
                #    # Centramos el rastro del camino de 8x8
                #    # en la celda de 32x32 (+12 píxeles)
                #    mlx_visual.mlx_put_image_to_window(  # type: ignore
                #        mlx_ptr, window_ptr, img_path,
                #        pixel_x + 12, pixel_y + 12
                #    )
                # --- B. LÓGICA DE MUROS INTERNOS (Norte y Oeste) ---
                if decimal & 1:
                    mlx_visual.mlx_put_image_to_window(  # type: ignore
                        mlx_ptr, window_ptr, img_wall_h, pixel_x, pixel_y
                    )
                if decimal & 8:
                    mlx_visual.mlx_put_image_to_window(  # type: ignore
                        mlx_ptr, window_ptr, img_wall_v, pixel_x, pixel_y
                    )
                # --- C. CIERRE PERIMETRAL EXTERIOR ---
                if x == len(row) - 1 and (decimal & 2):
                    mlx_visual.mlx_put_image_to_window(  # type: ignore
                        mlx_ptr, window_ptr, img_wall_v,
                        pixel_x + CELL_SIZE - WALL_THICKNESS, pixel_y
                    )
                if y == len(maze_coords) - 1 and (decimal & 4):
                    mlx_visual.mlx_put_image_to_window(  # type: ignore
                        mlx_ptr, window_ptr, img_wall_h,
                        pixel_x, pixel_y + CELL_SIZE - WALL_THICKNESS
                    )
        # 7. PINTAR EL TEXTO DEL MENÚ EN LA FRANJA NEGRA
        # Lo centramos verticalmente en los 40px extra,
        # y le damos un margen izquierdo
        menu_text = "1: regen | 2: path | 3: color | 4: quit"
        mlx_visual.mlx_string_put(  # type: ignore
            mlx_ptr, window_ptr, 20, screen_height - 25, 0xFFFFFF, menu_text
        )

    #  8. LOS HOOKS (El Cerebro)
    def key_hook(keycode: int, param: Any) -> int:
        """Captura las pulsaciones del teclado."""
        if keycode == KEY_ESC or keycode == KEY_4:
            print("Cerrando la interfaz gráfica de forma limpia...")
            mlx_visual.mlx_destroy_window(mlx_ptr, window_ptr)  # type: ignore
            os._exit(0)
        elif keycode == KEY_1:
            print("[HOOK] Has pulsado 1: Regenerar mapa (Lógica pendiente)")
        elif keycode == KEY_2:
            nonlocal show_path
            show_path = False
            draw_frame()
        elif keycode == KEY_3:
            print("[HOOK] Has pulsado 3: Cambiar Color (Lógica pendiente)")
        return 0

    def close_hook(param: Any) -> int:
        """Captura el clic en la 'X' de la ventana del sistema operativo."""
        print("Cierre forzado desde la X de la ventana.")
        mlx_visual.mlx_destroy_window(mlx_ptr, window_ptr)  # type: ignore
        sys.exit(0)
    # Conectamos las funciones a la ventana
    mlx_visual.mlx_key_hook(window_ptr, key_hook, None)  # type: ignore
    # El evento 17 en X11 es 'DestroyNotify' (Clic en la X)
    mlx_visual.mlx_hook(window_ptr, 17, 0, close_hook, None)  # type: ignore
    # 9. Primer renderizado inical
    draw_frame()
    # 10. Mantener la ventana abierta
    mlx_visual.mlx_loop(mlx_ptr)  # type: ignore
