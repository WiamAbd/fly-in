
run:
	python main.py $(MAP)

install:
	pip install flake8 mypy pygame

debug:
	python -m pdb main.py $(MAP)

clean:
	rm -rf __pycache__
	rm -rf .mypy_cache

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
