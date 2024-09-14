.PHONY: all
all: clean setup test lint mypy

.PHONY: setup
setup: pyproject.toml
	poetry check
	poetry install

.PHONY: test
test:
	poetry run pytest --cov=obsidian_tools/ --cov-report=xml

.PHONY: shell
shell:
	poetry run bpython

.PHONY: coverage.xml
coverage.xml: test

.PHONY: coverage
coverage: coverage.xml
	poetry run coverage html
	open htmlcov/index.html

.PHONY: lint
lint:
	poetry run isort --check .
	poetry run black --check .
	poetry run ruff check .

.PHONY: lintfix
lintfix:
	poetry run isort .
	poetry run black .
	poetry run ruff check . --fix

.PHONY: prettier
prettier:
	npx \
		--package prettier \
		--call 'prettier --write obsidian_tools/templates tests/responses'

.PHONY: mypy
mypy:
	poetry run mypy obsidian_tools/

.PHONY: clean
clean:
	rm -fr ./.mypy_cache
	rm -fr ./.pytest_cache
	rm -fr ./.ruff_cache
	rm -fr ./dist
	rm -f .coverage
	rm -f coverage.xml
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
	poetry env remove --all

.PHONY: ci
ci: setup test lint mypy
