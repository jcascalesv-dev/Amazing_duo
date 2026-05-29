import sys
import os
import time
import random
from typing import Any
from mlx import Mlx
from mazegen.generator import MazeGenerator, InvalidMazeConfig
from get_maze_data import get_maze_coords, get_way

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CELL_SIZE = 48
WALL_THICKNESS = 4
MAX_SCREEN_WIDTH = 2560
MAX_SCREEN_HEIGHT = 1440
MIN_SCREEN_WIDTH = 640
MIN_SCREEN_HEIGHT = 480
MENU_HEIGHT = 60
# Keyboard codes for Linux (X11)
KEY_1 = 49
KEY_2 = 50
KEY_3 = 51
KEY_4 = 52
KEY_5 = 53
KEY_ESC = 65307


def transform_directions(
    entrance: tuple[int, int], directions: str
) -> set[tuple[int, int]]:
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
    dims: dict[str, int], maze_coords: list[str],
    way: dict[str, Any], perfect: bool, output_file: str
) -> None:
    # Pre-process the path
    directions_set = transform_directions(way["entrance"], way["directions"])
    # We calculate the final size of the window
    screen_width: int = dims["WIDTH"] * CELL_SIZE
    screen_height: int = (dims["HEIGHT"] * CELL_SIZE) + MENU_HEIGHT
    # We checked that we did not exceed the screen resolution limits.
    if screen_width > MAX_SCREEN_WIDTH or screen_height > MAX_SCREEN_HEIGHT:
        print("Critical Error: The labyrinth is "
              "too large for the graphical interface "
              f"({screen_width}x{screen_height} px). The safe limit is "
              f"{MAX_SCREEN_WIDTH}x{MAX_SCREEN_HEIGHT} px.", file=sys.stderr)
        sys.exit()
    screen_width = max(screen_width, MIN_SCREEN_WIDTH)
    screen_height = max(screen_height, MIN_SCREEN_HEIGHT)
    # We initialize the graphics library
    mlx_visual = Mlx()
    # mlx_ptr gives us access to interact with the screen
    mlx_ptr = mlx_visual.mlx_init()
    # we create the window
    window_ptr: int = mlx_visual.mlx_new_window(
        mlx_ptr, screen_width, screen_height, "A-maze-ing MLX!"
    )
    # WE LOADED ALL TEXTURES into memory (Walls + Interior)
    walls_h = [
        mlx_visual.mlx_xpm_file_to_image(
            mlx_ptr, os.path.join(BASE_DIR, "textures", "wall_h.xpm"))[0],
        mlx_visual.mlx_xpm_file_to_image(
            mlx_ptr,
            os.path.join(BASE_DIR, "textures", "wall_h_green.xpm"))[0],
        mlx_visual.mlx_xpm_file_to_image(
            mlx_ptr, os.path.join(BASE_DIR, "textures", "wall_h_blue.xpm"))[0]
    ]
    walls_v = [
        mlx_visual.mlx_xpm_file_to_image(
            mlx_ptr, os.path.join(BASE_DIR, "textures", "wall_v.xpm"))[0],
        mlx_visual.mlx_xpm_file_to_image(
            mlx_ptr,
            os.path.join(BASE_DIR, "textures", "wall_v_green.xpm"))[0],
        mlx_visual.mlx_xpm_file_to_image(
            mlx_ptr, os.path.join(BASE_DIR, "textures", "wall_v_blue.xpm"))[0]
    ]
    logos = [
        mlx_visual.mlx_xpm_file_to_image(
            mlx_ptr, os.path.join(BASE_DIR, "textures", "logo_42.xpm"))[0],
        mlx_visual.mlx_xpm_file_to_image(
            mlx_ptr, os.path.join(BASE_DIR, "textures", "logo_42_red.xpm"))[0],
        mlx_visual.mlx_xpm_file_to_image(
            mlx_ptr,
            os.path.join(BASE_DIR, "textures", "logo_42_yellow.xpm"))[0]
    ]
    # We discard arguments 2 and 3 from the function's return value
    # because they are the image dimensions and we don't need them
    img_start, _, _ = mlx_visual.mlx_xpm_file_to_image(
        mlx_ptr, os.path.join(BASE_DIR, "textures", "start.xpm")
    )
    img_exit, _, _ = mlx_visual.mlx_xpm_file_to_image(
        mlx_ptr, os.path.join(BASE_DIR, "textures", "exit.xpm")
    )
    img_path, _, _ = mlx_visual.mlx_xpm_file_to_image(
        mlx_ptr, os.path.join(BASE_DIR, "textures", "path.xpm")
    )
    menu_text, _, _ = mlx_visual.mlx_xpm_file_to_image(
        mlx_ptr, os.path.join(BASE_DIR, "textures", "menu_text.xpm")
    )
    # We give the window a moment to map itself and avoid the top cut
    show_path = False
    color_index = 0  # (0=Red, 1=Green, 2=Blue)
    logo_color_in = 0
    needs_redraw = True

    # RENDERING LOOP
    def draw_frame() -> None:
        # Clean the screen before painting
        mlx_visual.mlx_clear_window(mlx_ptr, window_ptr)
        for y, row in enumerate(maze_coords):
            for x, digit in enumerate(row):
                decimal: int = int(digit, 16)
                pixel_x = x * CELL_SIZE
                pixel_y = y * CELL_SIZE
                coord = (x, y)
                # THE INTERIOR OF THE CELL (Z-Index)
                # We draw this FIRST so that the walls will always
                # be on top if there is friction
                if coord == way["entrance"]:
                    # We centered the 24x24 image in the
                    # 32x32 cell (+4 pixels)
                    mlx_visual.mlx_put_image_to_window(
                        mlx_ptr, window_ptr, img_start,
                        pixel_x + 1, pixel_y + 1
                    )
                elif coord == way["exit"]:
                    mlx_visual.mlx_put_image_to_window(
                        mlx_ptr, window_ptr, img_exit, pixel_x + 1, pixel_y + 4
                    )
                elif decimal == 15:
                    # The massive 42 block fills the entire 32x32 space
                    mlx_visual.mlx_put_image_to_window(
                        mlx_ptr, window_ptr, logos[logo_color_in],
                        pixel_x, pixel_y
                    )
                elif coord in directions_set and show_path:
                    # We center the 8x8 path trace on
                    # the 48x48 cell (+20 pixels)
                    mlx_visual.mlx_put_image_to_window(
                        mlx_ptr, window_ptr, img_path,
                        pixel_x + 20, pixel_y + 20
                    )
                # INTERNAL WALL LOGIC (North and West)
                if decimal & 1:
                    mlx_visual.mlx_put_image_to_window(
                        mlx_ptr, window_ptr, walls_h[color_index],
                        pixel_x, pixel_y
                    )
                if decimal & 8:
                    mlx_visual.mlx_put_image_to_window(
                        mlx_ptr, window_ptr, walls_v[color_index],
                        pixel_x, pixel_y
                    )
                # EXTERIOR PERIMETER ENCLOSURE
                if x == len(row) - 1 and (decimal & 2):
                    mlx_visual.mlx_put_image_to_window(
                        mlx_ptr, window_ptr, walls_v[color_index],
                        pixel_x + CELL_SIZE - WALL_THICKNESS, pixel_y
                    )
                if y == len(maze_coords) - 1 and (decimal & 4):
                    mlx_visual.mlx_put_image_to_window(
                        mlx_ptr, window_ptr, walls_h[color_index],
                        pixel_x, pixel_y + CELL_SIZE - WALL_THICKNESS
                    )
                time.sleep(0.0015)
        # PAINT THE MENU TEXT
        # Center it vertically within the extra 60px, and give it a left margin
        mlx_visual.mlx_put_image_to_window(
            mlx_ptr, window_ptr, menu_text, 10, screen_height - 60
        )

    #  HOOKS. Callback functions
    def key_hook(keycode: int, param: Any) -> int:
        nonlocal show_path, color_index, needs_redraw, logo_color_in
        if keycode == KEY_ESC or keycode == KEY_5:
            print("Closing maze window...")
            mlx_visual.mlx_destroy_window(mlx_ptr, window_ptr)
            os._exit(0)
        elif keycode == KEY_1:
            nonlocal maze_coords, way, directions_set
            width = dims["WIDTH"]
            height = dims["HEIGHT"]
            entry_pos = way["entrance"]
            exit_pos = way["exit"]
            try:
                new_seed = random.randint(1, 999999)
                generator = MazeGenerator(width=width, height=height,
                                          perfect=perfect, seed=new_seed)
                generator.generate(start_x=entry_pos[0], start_y=entry_pos[1],
                                   end_x=exit_pos[0], end_y=exit_pos[1])
                generator.save_to_file(filename=output_file, start=entry_pos,
                                       end=exit_pos)
                maze_coords = get_maze_coords(output_file)
                way = get_way(output_file)
                directions_set = transform_directions(
                    way["entrance"], way["directions"]
                )
                needs_redraw = True
            except InvalidMazeConfig as e:
                print("[GENERATION ERROR] Invalid configuration:"
                      f"{e}", file=sys.stderr)
            except Exception as e:
                print("[SYSTEM ERROR] Unexpected failure during regeneration:"
                      f"{e}", file=sys.stderr)
        elif keycode == KEY_2:
            show_path = not show_path
            needs_redraw = True
        elif keycode == KEY_3:
            color_index = color_index + 1 if color_index < 2 else 0
            needs_redraw = True
        elif keycode == KEY_4:
            logo_color_in = logo_color_in + 1 if logo_color_in < 2 else 0
            needs_redraw = True
        # The library function expects us to return an int
        return 0

    def close_hook(param: Any) -> int:
        print("Forced closure from the X of the window.")
        mlx_visual.mlx_destroy_window(mlx_ptr, window_ptr)
        os._exit(0)

    def background_loop(param: Any) -> int:
        nonlocal needs_redraw
        if needs_redraw:
            draw_frame()
            needs_redraw = False
        return 0
    # We connect the functions to the window. We pass the callback functions
    # so they execute when the user presses a key
    mlx_visual.mlx_key_hook(window_ptr, key_hook, None)
    # Event 17 in X11 is 'DestroyNotify' (Click on the X)
    mlx_visual.mlx_hook(window_ptr, 33, 0, close_hook, None)
    mlx_visual.mlx_loop_hook(mlx_ptr, background_loop, None)
    # Keep the window open (infinite loop)
    mlx_visual.mlx_loop(mlx_ptr)
