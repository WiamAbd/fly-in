
run:
	python main.py $(MAP)

clean:
	rm -rf __pycache__

install:
	pip install flake8 mypy

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

debug:
	python -m pdb main.py $(MAP)
