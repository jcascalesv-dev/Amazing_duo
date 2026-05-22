*This project has been created as part of the 42 curriculum by jcascale, mjabalqu.*

# A-Maze-ing

## DESCRIPCIÓN
**A-Maze-ing** es un generador y visualizador de laberintos desarrollado como proyecto colaborativo para **42 Málaga**. El sistema permite la creación de laberintos perfectos (un solo camino) e imperfectos (con bucles), garantizando siempre el cálculo de la ruta más corta. Incluye un motor lógico en Python y una interfaz gráfica para la visualización del resultado.

### Requisitos técnicos
Para asegurar la calidad y robustez del código, el proyecto cumple con los siguientes estándares:
- **Lenguaje:** Python 3.10 o superior.
- **Linter:** Estricto cumplimiento de `flake8`.
- **Tipado:** Tipado estático exhaustivo validado con `mypy`.
- **Gráficos:** Visualización integrada (MiniLibX / Terminal).

### Configuración (`config.txt`)
El generador lee los parámetros desde un archivo de texto con el siguiente formato:
- `WIDTH` / `HEIGHT`: Dimensiones de la cuadrícula.
- `ENTRY` / `EXIT`: Coordenadas `x,y` de los puntos de inicio y fin.
- `OUTPUT_FILE`: Ruta del archivo `.txt` de salida donde se guardará la matriz.
- `PERFECT`: `true` para laberintos sin bucles, `false` para incluir atajos.
- `SEED`: (Opcional) Semilla para generación reproducible.

### Características del Motor (Parte Técnica)
- **Generación:** Algoritmo *Backtracker* (DFS) adaptado para asegurar pasillos de entre 1 y 2 celdas de ancho.
- **Patrón "42":** Inserción obligatoria del patrón "42" como zona de muros cerrados e infranqueables en el centro del laberinto.
- **Resolución:** Implementación de *Breadth-First Search* (BFS) para garantizar que la ruta exportada sea siempre la **más corta**, superando las limitaciones de búsqueda en laberintos con bucles.
- **Formato de Salida:** Exportación en matriz hexadecimal (0-F) donde cada bit representa una pared (N=1, E=2, S=4, W=8).

### Representación Visual (Parte Gráfica)
La interfaz permite:
- Visualizar el laberinto generado a partir del archivo hexadecimal.
- Mostrar/Ocultar la ruta óptima calculada por el motor.
- Regenerar el laberinto de forma dinámica.
- Personalización de la interfaz y visualización interactiva.

### División del Trabajo
- **Lógica y Motor (Backend):** Desarrollo del algoritmo de generación, resolución matemática (BFS), sistema de empaquetado y validación de normas estrictas (Mypy/Flake8).
- **Interfaz y Gráficos (Frontend):** Implementación de la visualización, manejo de eventos de usuario e integración de la salida hexadecimal para el renderizado.

## INSTRUCCIONES

### Instalación como módulo
Este proyecto está diseñado para ser reutilizable. Puedes instalar el motor de generación localmente en tu entorno:
```bash
make install
```

### Generación de laberintos
Para generar un laberinto basado en un archivo de configuración:
```bash
python3 a_maze_ing.py config.txt
```

### Ejecución de Tests y Linter
```bash
make lint    # Ejecuta la comprobación estricta de Flake8 y Mypy
make build   # Genera los archivos de distribución (.tar.gz y .whl)
```

## RECURSOS
- El enunciado oficial del proyecto (en.subject.pdf).
- Información buscada a través del navegador.
- Pear to Pear.

### Uso de IA (transparencia)
Durante el desarrollo y depuración de este proyecto se utilizó asistencia basada en IA para:
- Generar documentación (README.md).
- Aclarar conceptos.