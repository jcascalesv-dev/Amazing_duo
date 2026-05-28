import random
import sys
import os
from collections import deque

# Constantes para los bits de las paredes (N, E, S, W)
N: int = 1  # 2^0
E: int = 2  # 2^1
S: int = 4  # 2^2
W: int = 8  # 2^3

# Mapeo de direcciones: (delta_x, delta_y, muro_a_romper, muro_opuesto)
DIRECTIONS: list[tuple[int, int, int, int]] = [
    (0, -1, N, S),  # Ir al Norte
    (1, 0, E, W),   # Ir al Este
    (0, 1, S, N),   # Ir al Sur
    (-1, 0, W, E)   # Ir al Oeste
]

# Representación del 42 ('X' serán muros cerrados, '.' será espacio libre
# para pasillos) Tamaño: 7 de ancho x 5 de alto
PATTERN_42: list[str] = [
    "X.X.XXX",
    "X.X...X",
    "XXX.XXX",
    "..X.X..",
    "..X.XXX"
]


class InvalidMazeConfig(Exception):
    """Excepción personalizada para errores de configuración del laberinto."""
    pass


class MazeGenerator:
    """Clase generadora de laberintos utilizando DFS (Recursive Backtracker).
    """

    def __init__(self, width: int, height: int, perfect: bool,
                 seed: int | None = None) -> None:
        """
        Inicializa el generador de laberintos.

        Args:
            width (int): Ancho del laberinto.
            height (int): Alto del laberinto.
            perfect (bool): Si es True, genera un laberinto sin bucles.
            seed (int | None): Semilla para generación aleatoria reproducible.
        """
        self.width: int = width
        self.height: int = height
        self.perfect: bool = perfect

        if seed is not None:
            random.seed(seed)

        # Inicializamos la cuadrícula: 15 (binario 1111) significa todos
        # los muros cerrados.
        self.grid: list[list[int]] = [
            [15 for _ in range(width)] for _ in range(height)]

        # Matriz booleana para saber si una celda ha sido visitada por el DFS
        self.visited: list[list[bool]] = [
            [False for _ in range(width)] for _ in range(height)]
        self.solution_coords: list[tuple[int, int]] = []

    def _stamp_42(self) -> None:
        """
        Estampa el patrón '42' en el centro del laberinto.
        Marca las celdas del patrón como visitadas para que el DFS las ignore
        y queden como celdas completamente cerradas (valor 15).
        """
        pattern_h: int = len(PATTERN_42)
        pattern_w: int = len(PATTERN_42[0])

        # Comprobamos si el laberinto es lo suficientemente grande.
        # Le damos un margen de +2 para que haya al menos un pasillo alrededor
        # y no corte caminos.
        if self.width < pattern_w + 2 or self.height < pattern_h + 2:
            print(
                "Error: The maze size is too small"
                " to draw the '42' pattern.", file=sys.stderr)
            return

        # Calculamos el desplazamiento para centrar el patrón
        offset_x: int = (self.width - pattern_w) // 2
        offset_y: int = (self.height - pattern_h) // 2

        # Iteramos sobre el diseño del patrón
        for py, row in enumerate(PATTERN_42):
            for px, char in enumerate(row):
                if char == 'X':
                    # Marcamos la celda como visitada.
                    # El DFS no entrará aquí, y por lo tanto sus muros nunca
                    # se romperán (se quedan en 15)
                    self.visited[offset_y + py][offset_x + px] = True

    def _get_unvisited_neighbors(self, cx: int, cy: int
                                 ) -> list[tuple[int, int, int, int]]:
        """Devuelve los vecinos válidos y no visitados de una celda."""
        neighbors: list[tuple[int, int, int, int]] = []

        for dx, dy, wall, opp_wall in DIRECTIONS:
            nx, ny = cx + dx, cy + dy

            # Verificar límites del mapa
            if 0 <= nx < self.width and 0 <= ny < self.height:
                # Verificar si no ha sido visitado
                if not self.visited[ny][nx]:
                    neighbors.append((nx, ny, wall, opp_wall))

        return neighbors

    def _is_in_42_pattern(self, x: int, y: int) -> bool:
        """Comprueba si una coordenada pertenece a un muro del patrón 42."""
        pattern_h: int = len(PATTERN_42)
        pattern_w: int = len(PATTERN_42[0])
        offset_x: int = (self.width - pattern_w) // 2
        offset_y: int = (self.height - pattern_h) // 2

        if (offset_x <= x < offset_x + pattern_w and
                offset_y <= y < offset_y + pattern_h):
            char_x = x - offset_x
            char_y = y - offset_y
            if PATTERN_42[char_y][char_x] == 'X':
                return True
        return False

    def _make_imperfect(self) -> None:
        """Rompe muros aleatoriamente para crear bucles y atajos."""
        # Calculamos cuántos muros romper (ej. 2 del tamaño total)
        num_walls: int = (self.width * self.height) // 20
        if num_walls == 0:
            num_walls = 1

        broken_count: int = 0
        attempts: int = 0
        max_attempts: int = num_walls * 10

        while broken_count < num_walls and attempts < max_attempts:
            attempts += 1
            # Evitamos los bordes (1 a width-2)
            cx: int = random.randint(1, self.width - 2)
            cy: int = random.randint(1, self.height - 2)

            if self._is_in_42_pattern(cx, cy):
                continue

            dx, dy, wall, opp_wall = random.choice(DIRECTIONS)
            nx, ny = cx + dx, cy + dy

            # Verificamos que el vecino tampoco es el borde ni el patrón 42
            if (nx <= 0 or nx >= self.width - 1 or
                    ny <= 0 or ny >= self.height - 1):
                continue
            if self._is_in_42_pattern(nx, ny):
                continue

            # Si hay un muro entre las celdas, lo rompemos
            if self.grid[cy][cx] & wall:
                self.grid[cy][cx] &= ~wall
                self.grid[ny][nx] &= ~opp_wall
                broken_count += 1

    def _solve_bfs(self, start_x: int, start_y: int,
                   end_x: int, end_y: int) -> None:
        """Encuentra el camino más corto tras generar el laberinto."""
        queue: deque[tuple[int, int]] = deque([(start_x, start_y)])
        visited_bfs: set[tuple[int, int]] = {(start_x, start_y)}

        # Diccionario para rastrear de dónde venimos
        came_from: dict[tuple[int, int], tuple[int, int] | None] = {
            (start_x, start_y): None
        }

        while queue:
            cx, cy = queue.popleft()

            if cx == end_x and cy == end_y:
                # Reconstruimos la ruta caminando hacia atrás
                path: list[tuple[int, int]] = []
                current: tuple[int, int] | None = (cx, cy)
                while current is not None:
                    path.append(current)
                    current = came_from[current]

                # Invertimos la lista para que vaya desde START hasta END
                self.solution_coords = path[::-1]
                return

            for dx, dy, wall, _ in DIRECTIONS:
                if not (self.grid[cy][cx] & wall):
                    nx, ny = cx + dx, cy + dy
                    if (nx, ny) not in visited_bfs:
                        visited_bfs.add((nx, ny))
                        came_from[(nx, ny)] = (cx, cy)
                        queue.append((nx, ny))

        # Si sale del while, es que no hay solución posible
        self.solution_coords = []

    def generate(
            self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        """
        Genera el laberinto utilizando un DFS iterativo (con pila).
        Usamos iterativo en lugar de recursivo para evitar el límite
        de recursividad de Python en laberintos grandes.
        """
        if not (0 <= start_x < self.width and 0 <= start_y < self.height):
            print(
                f"Error: ENTRY ({start_x},{start_y}) out of range.",
                file=sys.stderr
            )
            sys.exit()
        if not (0 <= end_x < self.width and 0 <= end_y < self.height):
            print(
                f"Error: EXIT ({end_x},{end_y}) out of range.",
                file=sys.stderr
            )
            sys.exit()

        # 1. Intentar estampar el patrón 42
        self._stamp_42()

        # 2. VALIDACIÓN: ¿La entrada o salida caen en un muro del 42?
        if self.visited[start_y][start_x]:
            raise InvalidMazeConfig(
                f"Error: ENTRY ({start_x},{start_y}) falls inside a '42' wall."
                " Please change ENTRY in config.txt."
            )

        if self.visited[end_y][end_x]:
            raise InvalidMazeConfig(
                f"Error: EXIT ({end_x},{end_y}) falls inside a '42' wall. "
                "Please change EXIT in config.txt."
            )

        # 3. Inicializar el DFS
        stack: list[tuple[int, int]] = [(start_x, start_y)]
        self.visited[start_y][start_x] = True

        while stack:
            cx, cy = stack[-1]  # Mirar la celda actual sin sacarla de la pila
            neighbors = self._get_unvisited_neighbors(cx, cy)

            if neighbors:
                # Elegir un vecino aleatorio
                nx, ny, wall_to_break, opposite_wall = random.choice(neighbors)

                # Romper los muros correspondientes usando bitwise AND y NOT
                self.grid[cy][cx] &= ~wall_to_break
                self.grid[ny][nx] &= ~opposite_wall

                # Marcar como visitado meter en la pila
                self.visited[ny][nx] = True

                # Meter en la pila
                stack.append((nx, ny))
            else:
                # Si no hay vecinos, retrocedemos (backtrack)
                stack.pop()

        # 1. Si no es perfecto, rompemos muros extra para crear atajos
        if not self.perfect:
            self._make_imperfect()

        # 2. Finalmente, calculamos el camino más corto real con BFS
        self._solve_bfs(start_x, start_y, end_x, end_y)

    def get_solution_path_string(self) -> str:
        """Convierte la lista de coordenadas de la solución en un string."""
        path_str: str = ""

        # Si no se encontró solución
        # (no debería pasar en un laberinto perfecto)
        if not hasattr(self, 'solution_coords') or not self.solution_coords:
            return path_str

        # Comparamos cada celda con la siguiente para saber la dirección
        for i in range(len(self.solution_coords) - 1):
            cx, cy = self.solution_coords[i]
            nx, ny = self.solution_coords[i + 1]

            if nx == cx + 1:
                path_str += "E"
            elif nx == cx - 1:
                path_str += "W"
            elif ny == cy + 1:
                path_str += "S"
            elif ny == cy - 1:
                path_str += "N"

        return path_str

    def save_to_file(self, filename: str, start: tuple[int, int],
                     end: tuple[int, int]) -> None:
        """Guarda el laberinto siguiendo estrictamente
          el formato del subject."""
        with open(filename, 'w', encoding="utf-8") as f:
            # 1. Escribir el mapa en hexadecimal
            for row in self.grid:
                # Convertimos cada celda a hex (mayúsculas) y las unimos
                line = "".join(f"{cell:X}" for cell in row)
                f.write(f"{line}\n")

            # 2. Línea vacía de separación
            f.write("\n")

            # 3. Metadatos del laberinto
            f.write(f"{start[0]},{start[1]}\n")  # Entrada x,y
            f.write(f"{end[0]},{end[1]}\n")      # Salida x,y
            path_str: str = self.get_solution_path_string()
            if not path_str:
                raise InvalidMazeConfig(
                    "Error: No valid path found from ENTRY to EXIT.")
            f.write(f"{path_str}\n")                 # Solución N,E,S,W
            # --- PARCHE DE SINCRONIZACIÓN DE DISCO ---
            f.flush()            # Vacía el buffer interno de Python
            os.fsync(f.fileno())  # Obliga al SO a escribir en el disco
