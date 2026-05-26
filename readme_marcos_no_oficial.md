# A_Maze_Ing - Guía de Arquitectura y Referencia
Este documento es un mapa mental del proyecto. Explica cómo fluye la información desde que se ejecuta el programa en la terminal hasta que el servidor X11 de Linux dibuja los píxeles en la pantalla.

## Esquema de Ejecución (El Flujo de Vida)
El programa sigue una arquitectura secuencial muy estricta que se divide en dos grandes fases: La Generación (cálculo pesado e I/O de disco) y El Renderizado (bucle infinito controlado por eventos).

### a_maze_ing.py (El Director de Orquesta)

Se ejecuta el script. Lo primero que hace es leer el archivo config.txt a la memoria RAM.

Extrae las reglas del juego (dimensiones, semillas, nombre del archivo de salida).

### mazegen/generator.py (El Motor Matemático - Código de Javi)

Recibe las dimensiones.

Usa un algoritmo DFS (Búsqueda en Profundidad) iterativo para romper muros en la memoria y crear el laberinto.

Usa BFS (Búsqueda en Anchura) para encontrar el camino más corto de entrada a salida.

I/O: Vuelca todo este cálculo matemático escribiendo un archivo físico en el disco (ej. maze.txt).

### get_maze_data.py (El Traductor)

Abre ese archivo .txt recién creado.

Convierte las cadenas de texto y los valores hexadecimales en estructuras de datos de Python listas para usarse (listas y diccionarios).

### render.py (El Motor Gráfico)

Recibe las estructuras de datos limpias.

Inicializa la conexión con el servidor gráfico de Linux usando mlx.py.

Pinta el mapa inicial.

Cede el control del programa al bucle infinito de la MiniLibX (mlx_loop). A partir de aquí, el programa solo reacciona a eventos (teclado o reloj del sistema).

## 📂 Anatomía de los Archivos
### 1. a_maze_ing.py
Es el punto de entrada o Main. Su único trabajo es delegar responsabilidades. No calcula laberintos ni dibuja pantallas, solo coordina qué módulo debe actuar en cada momento y le pasa los datos necesarios para que no haya que leer el disco duro varias veces (cumpliendo el principio Single Source of Truth).

### 2. mazegen/generator.py
Aquí vive la lógica pura. Es importante destacar que usa una pila (deque) en lugar de recursividad pura para el DFS. Esto es vital porque si el laberinto es inmenso, la recursividad haría saltar el límite de memoria de Python (RecursionError). Escribe el mapa usando números hexadecimales, donde cada bit (1, 2, 4, 8) representa un muro (Norte, Este, Sur, Oeste).

### 3. get_maze_data.py
Módulo de saneamiento.

get_maze_coords: Extrae la matriz principal.

get_way: Parsea la entrada, la salida y las direcciones ("N, S, E, W").

### 4. mlx.py (El Puente de C a Python)
Este archivo es un Wrapper. La MiniLibX es una librería compilada en C (libmlx.so). Python no sabe hablar C nativamente. Este archivo usa la librería ctypes de Python para definir las firmas de memoria y decirle a Python cómo debe empaquetar los datos antes de enviárselos a las funciones de C.

Nota: No hace falta que modifiques este archivo, trátalo como un "driver" del sistema.

### 5. render.py (El Corazón Gráfico)
Este es el archivo más complejo porque abandona la programación lineal y pasa a la Programación Orientada a Eventos. Está diseñado como un demonio/servicio de sistema: se queda en segundo plano esperando interrupciones.

Entendiendo el Patrón "Game Loop"
Para no saturar el servidor X11 (lo que causaba parpadeos o cierres al grabar la pantalla), el motor gráfico divide el trabajo en tres actores:

El Teclado (key_hook) - El Jefe:

Es una interrupción de hardware. Cuando pulsas una tecla, el programa se congela una fracción de milisegundo para atenderte.

Por eso, aquí nunca se dibuja nada. Solo se cambian variables de estado (ej. color_index = 1) y se levanta una bandera: needs_redraw = True.

El Bucle de Fondo (background_loop) - El Vigilante:

Enganchado a mlx_loop_hook. Se ejecuta miles de veces por segundo en el tiempo libre del procesador.

Su único trabajo es mirar si la bandera needs_redraw está levantada. Si lo está, da la orden de pintar y baja la bandera. Esto asegura que el sistema operativo solo dibuje cuando tiene la red y los recursos libres.

El Pintor (draw_frame):

Es la función esclava. Cuando se le llama, borra toda la ventana de un plumazo y vuelve a dibujar el estado actual de los datos leyendo la matriz y comprobando interruptores (show_path, color_index). Aplica la técnica del "Lienzo Plano": sobreescribe los píxeles antiguos con los nuevos.

Estructuras de Datos Clave en render.py
Listas de Texturas (walls_h, logos_42): Las texturas (imágenes XPM) se cargan una sola vez al inicio y se guardan en listas en la RAM. Al pulsar el botón de cambiar color, simplemente sumamos +1 a un índice (usando un operador ternario para que vuelva a 0 al llegar al final). Al repintar, el programa busca en la lista usando ese índice.

El set de Direcciones: La función transform_directions convierte el camino de "N, S, E, W" en coordenadas exactas (X, Y). Se guarda en un objeto tipo set en lugar de una lista. Al pintar miles de celdas por segundo, preguntar si una celda existe en un set es infinitamente más rápido a nivel de CPU que iterar sobre una lista convencional.

## 🚀 Resumen para la Evaluación
Si te preguntan por qué el código está estructurado así, tus tres argumentos principales son:

Separación de responsabilidades: Cada módulo hace una sola cosa.

Optimización de I/O: El archivo de configuración se lee una única vez y fluye por memoria, protegiendo las lecturas a disco.

Seguridad del Hilo Gráfico: El dibujado está desacoplado del input del usuario mediante un Loop Hook, previniendo saturaciones del buffer gráfico en Linux y bloqueos por interrupción de hardware.