NAME = a_maze_ing
PYTHON = python3
PIP = pip3

all: run

install:
	$(PIP) install .
	$(PIP) install mlx-2.2-py3-none-any.whl

build:
	$(PIP) install --upgrade build
	$(PYTHON) -m build
	mv dist/mazegen-*.whl .
	mv dist/mazegen-*.tar.gz .
	rm -rf dist

run:
	$(PYTHON) a_maze_ing.py config.txt

debug:
	$(PYTHON) -m pdb a_maze_ing.py config.txt

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

clean:
	rm -rf build dist *.egg-info .mypy_cache .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -f maze.txt
	rm -f mazegen-1.0.0.tar.gz
	rm -f mazegen-1.0.0-py3-none-any.whl

fclean: clean
	$(PIP) uninstall -y mlx-2.2-py3-none-any.whl
	$(PIP) uninstall -y mazegen

.PHONY: all install build run lint lint-strict clean fclean debug