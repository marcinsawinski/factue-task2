.PHONY: setup update clean env run test lint pipeline

# Setup venv + pip-tools + editable install
# pip-compile requirements.in --output-file=requirements.txt && 

setup:

	python3 -m venv .venv
	. .venv/bin/activate && \
	pip install --upgrade pip pip-tools && \
	pip-sync requirements.txt && \
	echo "Setup complete!"

# Compile dependencies (if you're using pip-tools)
update:
	. .venv/bin/activate && pip-compile requirements.in --output-file=requirements.txt && \
	pip-sync requirements.txt && \
	echo "pip-tools completed!"


# Remove the venv & build artifacts
clean:
	rm -rf .venv __pycache__ *.pyc build dist
# Load environment (manual sourcing still needed in interactive shells)
env:
	. ./env.sh

# Run Luigi pipeline with environment loaded
run:
	. ./env.sh && python -m factue.main

pipeline:
	. ./env.sh && luigi --module my_pipeline.luigi_tasks.tasks ProcessedDataTask --date $(shell date +%F) --local-scheduler

# Run tests with environment loaded
test:
	. ./env.sh && pytest -v factue/tests/

# Lint & format code
lint:
	black factue/ 
	isort factue/ 
	flake8 factue/
	mypy factue/
	pyright factue/ 