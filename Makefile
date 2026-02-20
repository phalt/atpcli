help:
	@echo Developer commands for apcli
	@echo
	@grep -E '^[ .a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo

install:  ## Install requirements ready for development
	uv sync

format: ## Format the code correctly
	uv run ruff format .
	uv run ruff check --fix .

clean:  ## Clear any cache files and test files
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf dist/
	rm -rf **/__pycache__
	rm -rf **/*.pyc
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf site/

test:  ## Run tests
	uv run pytest -vvv -x --cov=apcli --cov-report=term-missing --cov-report=html --cov-config=pyproject.toml

docs-serve:  ## Run a local documentation server
	uv run mkdocs serve

docs-build:  ## Build the documentation
	uv run mkdocs build

shell:  ## Run a Python shell
	uv run python

release:  ## Build a new version and release it
	uv build && uv publish
