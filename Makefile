VENV := .venv
PY   := $(VENV)/bin

install: $(VENV) build-mlx
	$(PY)/pip install --upgrade pip
	$(PY)/pip install -r requirements.txt
	$(PY)/pip install -e .

$(VENV):
	python3 -m venv $(VENV)

build-mlx: mlx_CLXV
	cd mlx_CLXV && make
	$(PY)/pip install ./mlx_CLXV/mlx*.whl

mlx_CLXV:
	git clone git@github.com:42school/mlx_CLXV.git

run:
	CONFIG=config.txt $(PY)/python3 a_maze_ing.py

debug:
	CONFIG=config.txt $(PY)/python3 -m pdb a_maze_ing.py

build:
	$(PY)/python3 -m build

lint:
	$(PY)/flake8 .
	$(PY)/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(PY)/flake8 .
	$(PY)/mypy --strict .

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache

fclean: clean
	rm -rf $(VENV) mlx_CLXV

re: fclean install

.PHONY: install run debug lint lint-strict clean fclean re build build-mlx