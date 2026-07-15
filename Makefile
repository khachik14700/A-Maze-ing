NAME = a_maze_ing

PYTHON = python3
PIP = pip3
FLAKE8 = flake8
MYPY = mypy

.PHONY: install run debug clean lint lint-strict

install:
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) $(NAME).py config.txt

debug:
	$(PYTHON) -m pdb $(NAME).py config.txt

lint:
	$(FLAKE8) .
	$(MYPY) . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(FLAKE8) .
	$(MYPY) . --strict

clean:
	rm -rf __pycache__ .mypy_cache
	rm -rf *.egg-info
	rm -rf build dist
	find . -type d -name "__pycache__" -exec rm -rf {} +