VENV := .venv
PY   := $(VENV)/bin

install: $(VENV)
	$(PY)/pip install --upgrade pip
	$(PY)/pip install -r requirements.txt
	$(PY)/pip install -e .

$(VENV):
	python3 -m venv $(VENV)

run:
	$(PY)/python3 a_maze_ing.py config.txt

debug:
	$(PY)/python3 -m pdb a_maze_ing.py config.txt

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
	rm -rf $(VENV)

re: fclean install

.PHONY: install run debug lint lint-strict clean fclean re build