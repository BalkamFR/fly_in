MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
--disallow-untyped-defs --check-untyped-defs --explicit-package-bases
MAIN = main.py

.PHONY: run, install, clean, build, lint

install:
	@uv sync

run:
	@uv run python3 $(MAIN)

clean:
	@find . -name "__pycache__" -o -name ".mypy_cache" -o -name "dist" | xargs rm -rf
	@rm -f *.whl *.tar.gz
	@echo "All code clean"

debug:
	@uv run python3 -m pdb $(MAIN)

FLAKE8_FLAGS = --exclude=.venv,__pycache__,.git --max-line-length=79

lint:
	@uv run mypy . $(MYPY_FLAGS)
	@uv run flake8 . $(FLAKE8_FLAGS)
