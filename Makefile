NAME = a_maze_ing
PYTHON = python3
PIP = pip3

# Regla por defecto
all: run

# Instala el paquete localmente en tu entorno virtual
install:
	$(PIP) install .

# Construye los archivos .tar.gz y .whl (el subject suele pedir esto)
build:
	$(PIP) install --upgrade build
	$(PYTHON) -m build
	mv dist/mazegen-*.whl .
	mv dist/mazegen-*.tar.gz .
	rm -rf dist

# Ejecuta tu script de prueba
run:
	$(PYTHON) a_maze_ing.py config.txt

# Pasa la lupa estricta de 42 (Mypy y Flake8)
lint:
	@echo "--- Running Flake8 ---"
	flake8 mazegen a_maze_ing.py render.py get_maze_data.py
	@echo "--- Running Mypy ---"
	mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs mazegen a_maze_ing.py render.py get_maze_data.py

lint-strict:
	@echo "--- Running Flake8 ---"
	flake8 mazegen a_maze_ing.py render.py get_maze_data.py
	@echo "--- Running Mypy ---"
	mypy --strict --ignore-missing-imports mazegen a_maze_ing.py render.py get_maze_data.py

# Limpia basura generada por Python y compilaciones
clean:
	rm -rf build dist *.egg-info .mypy_cache .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -f maze.txt

# Desinstala el paquete y ejecuta clean
fclean: clean
	$(PIP) uninstall -y $(NAME)

# Reinicia todo
re: fclean all

.PHONY: all install build run lint lint-strict clean fclean re