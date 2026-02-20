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

test:  ## Run tests
	uv run pytest -vvv -x --cov=apcli --cov-report=term-missing --cov-report=html --cov-config=pyproject.toml

shell:  ## Run a Python shell
	uv run python
