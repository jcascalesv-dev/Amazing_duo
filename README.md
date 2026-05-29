*This project has been created as part of the 42 curriculum by jcascale, mjabalqu.*

# A-MAZE-ING 

## 1. DESCRIPCIÓN
**A-Maze-Ing** es un proyecto integral de generación algorítmica y renderizado gráfico de laberintos. El objetivo es calcular matemáticamente un laberinto perfecto (o imperfecto), volcar su estructura en un formato de almacenamiento específico y levantar un motor gráfico personalizado para visualizarlo e interactuar con él.

El proyecto destaca por una arquitectura muy estricta que separa la carga computacional (Matemáticas e I/O de disco) de la carga visual (Renderizado orientado a eventos), superando cuellos de botella del sistema operativo (X11) y cachés de red (NFS).

## 2. INSTRUCCIONES

### Instalación
El proyecto incluye un `Makefile` para automatizar las tareas principales.
Para instalar las dependencias necesarias:
`make install`

### Ejecución
El programa principal coordina los distintos módulos y requiere un archivo de configuración como argumento. Para ejecutarlo:
`make run` 
O manualmente mediante el intérprete de Python:
`python3 a_maze_ing.py config.txt`

### Pruebas y Linter
Para asegurar la calidad del código según el estándar de 42:
`make lint` o `make lint-strict`


## 3. ARCHIVO DE CONFIGURACIÓN
El programa lee un archivo de texto plano (`config.txt`) con la estructura `KEY=VALUE` por línea. Las líneas que comienzan por `#` son ignoradas.

**Claves obligatorias:**
* `WIDTH`: Anchura del laberinto en celdas (Ej: `WIDTH=20`).
* `HEIGHT`: Altura del laberinto en celdas (Ej: `HEIGHT=15`).
* `ENTRY`: Coordenadas de inicio en formato X,Y (Ej: `ENTRY=0,0`).
* `EXIT`: Coordenadas de salida en formato X,Y (Ej: `EXIT=19,14`).
* `OUTPUT_FILE`: Nombre del archivo donde se guardará la estructura (Ej: `OUTPUT_FILE=maze.txt`).
* `PERFECT`: Define si existe una ruta única (`True`) o si hay bucles (`False`).

**Clave opcional implementada:**
* `SEED`: Número entero para garantizar la reproducibilidad matemática de un laberinto en concreto.

## 4. ALGORITMO DE GENERACIÓN DEL LABERINTO
Hemos utilizado dos algoritmos clásicos de grafos para el motor lógico (`generator.py`):
1.  **DFS (Depth-First Search) Iterativo:** Usado para la "excavación" del laberinto.
2.  **BFS (Breadth-First Search):** Usado para calcular el camino más corto ("N, S, E, W") una vez terminada la excavación.

**¿Por qué estas elecciones?**
Se optó por implementar el DFS usando una pila (`deque`) en lugar de recursividad pura. En laberintos de grandes dimensiones (ej. 100x100), un enfoque recursivo haría saltar el límite de memoria del intérprete (`RecursionError`). La pila permite generar mapas masivos de forma segura. El cálculo se vuelca a disco usando una codificación hexadecimal (1=Norte, 2=Este, 4=Sur, 8=Oeste).

## 5. REUSABILIDAD (The `mazegen` Module)
La lógica de generación está aislada en un módulo independiente llamado `mazegen`, diseñado para poder ser exportado e importado en futuros proyectos.

**¿Cómo construir el paquete?**
Desde la raíz del repositorio, con la herramienta estándar de Python (`build`), puedes generar los archivos `.whl` y `.tar.gz`:
`python3 -m build`
Esto generará un paquete (ej. `mazegen-1.0.0-py3-none-any.whl`) en el directorio `raiz` listo para ser instalado mediante `pip install`.

**Uso rápido del módulo:**
```python
from mazegen.generator import MazeGenerator
```
### 1. Instanciar el generador
generator = MazeGenerator(width=20, height=15, perfect=True, seed=42)

### 2. Calcular el laberinto
generator.generate(start_x=0, start_y=0, end_x=19, end_y=14)

### 3. Guardar el archivo en el formato del subject
generator.save_to_file("maze.txt", start=(0,0), exit=(19,19))

### 4. Acceder al camino resuelto
camino = generator.get_solution_path_string() # Retorna "E,S,S,E..."

## 6. ROLES DEL EQUIPO
jcascale: Arquitectura del motor lógico, parseo de datos de entrada, algoritmos matemáticos (DFS, BFS), gestión de bitwise para muros y estructura del paquete reutilizable. Makefile y Poetry.

mjabalqu: Arquitectura de sistemas, puente ctypes con MiniLibX (C to Python), Event Loop de X11, gestión de I/O, texturización escalada y archivo README.md.

# Planificación y Evolución:
El proyecto comenzó con un diseño lineal, que probó ser insuficiente debido a las condiciones de carrera del servidor gráfico (X11) y a la caché de lectura del disco de red (NFS) de la escuela. La evolución más crítica del proyecto fue refactorizar render.py hacia una arquitectura orientada a eventos (mlx_loop_hook).

# Qué funcionó bien y qué se puede mejorar:

Éxitos en el Motor Lógico: La decisión de diseñar el algoritmo de generación DFS (Depth-First Search) con un enfoque iterativo, utilizando una estructura de pila (deque) en lugar de depender de la recursividad clásica. Esto ha resultado ser un acierto absoluto, ya que permite calcular laberintos de proporciones masivas de forma instantánea sin arriesgarse a sufrir el temido RecursionError (límite de profundidad de llamadas) nativo de Python.

Éxitos en el Renderizado y Sistemas: La estabilización del motor gráfico frente a las desincronizaciones de X11 en los ordenadores de la escuela. La implementación de una estrategia de Rate Limiting (aplicando micropausas de 0.0015s en el bucle de dibujado) logró regular el flujo de peticiones, evitando el desbordamiento del socket de la MiniLibX y garantizando que ningún muro se perdiese por pérdida de paquetes durante la carga gráfica.

Áreas de mejora futura: Dada la limitación técnica actual del wrapper de la MiniLibX, que no permite de forma sencilla aplicar un "doble búfer" puro (construir la imagen completa en la memoria RAM antes de mandarla a la pantalla de un solo golpe), el renderizado sigue atado a estampar los gráficos celda por celda. En proyectos futuros, acceder directamente a la matriz de bytes de la imagen en memoria para manipular píxeles individuales permitiría exprimir la velocidad de carga al máximo.

# Herramientas específicas utilizadas:

GIMP: Creación, limpieza del canal alfa y texturización (XPM) para evitar crasheos de semitransparencias nativas.

Flake8 & Mypy: Para forzar el estándar PEP-8 y tipado estricto.

## 7. FUNCIONES AVANZADAS / OPCIONES TÉCNICAS
Gestión segura de la MiniLibX: El archivo mlx.py nativo de la librería actúa como un "Wrapper" usando la librería ctypes. Convierte estructuras nativas de Python a los punteros de C que exige libmlx.so.

Event-Driven Daemon: El renderizado no es lineal. Existe un "Jefe" (key_hook) que atiende interrupciones de hardware para cambiar estados (ej. needs_redraw = True), y un "Vigilante" (background_loop) que solo ejecuta llamadas gráficas pesadas cuando el servidor X11 está libre y ocioso, previniendo segfaults.

Sets vs Listas: El renderizado en tiempo real usa objetos set para calcular colisiones del camino. Comprobar coordenadas en un set O(1) es infinitamente más rápido a nivel CPU que iterar listas convencionales.

## 8. RECURSOS
Documentación oficial de la MiniLibX (Eventos y Hooks en C).

Documentación de Python sobre ctypes y Foreign Function Interfaces (FFI).

Búsquedas generales en google sobre algoritmos DFS y BFS.

Uso de IA (Gemini): Se utilizó como asistente avanzado de "System Administration". Ayudó a diagnosticar condiciones de carrera en el servidor gráfico X11, entender el caché de atributos (acregmin) del sistema de archivos NFS de Ubuntu que corrompía las lecturas, y a perfilar la técnica de estrangulamiento de tráfico (Rate Limiting) en el socket de red para evitar el descarte de frames en la MiniLibX.