MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
--disallow-untyped-defs --check-untyped-defs
MAIN = parsing.py
CONFIG = config.txt

.PHONY: run, install, clean, build, lint

install:
	@python3 -m poetry install

run:
	@python3 $(MAIN) $(CONFIG)

clean:
	@find . -name "__pycache__" -o -name ".mypy_cache" -o -name "dist" | xargs rm -rf
	@rm -f *.whl *.tar.gz
	@echo "All code clean"


debug:
	@python3 -m poetry run python3 -m pdb $(MAIN) $(CONFIG)

lint:
	@python3 -m poetry run python3 -m mypy . $(MYPY_FLAGS)
	@python3 -m poetry run python3 -m flake8 .
