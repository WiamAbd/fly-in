
run:
	python main.py $(MAP)

clean:
	rm -rf __pycache__
	rm -rf .mypy_cache

install:
	pip install flake8 mypy pygame

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

debug:
	python -m pdb main.py $(MAP)
