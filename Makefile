.PHONY: setup update clean env run test lint pipeline remove register ollama


# Default path if PYTHON_ENV_PATH is not set
PYTHON_ENV_PATH ?= .venv
PYTHON_EXECUTABLE ?= python3
KERNEL_NAME ?= factue
KERNEL_DISPLAY_NAME ?= Python (MS FactUE)

# Setup venv + pip-tools + editable install
# pip-compile requirements.in --output-file=requirements.txt && 
# Load variables from .env file if it exists
ifneq (,$(wildcard .env))
	include .env
	export
endif

register:
	python -m ipykernel install --user --name $(KERNEL_NAME) --display-name "$(KERNEL_DISPLAY_NAME)"

setup:
	$(PYTHON_EXECUTABLE) -m venv $(PYTHON_ENV_PATH)
	. $(PYTHON_ENV_PATH)/bin/activate && \
	pip install --upgrade pip pip-tools && \
	pip-compile requirements.in && \
	pip-sync requirements.txt && \
	echo "Setup complete in $(PYTHON_ENV_PATH)!"

remove:
	@if [ -d "$(shell echo $(PYTHON_ENV_PATH))" ]; then \
		echo "Removing environment at $(shell echo $(PYTHON_ENV_PATH))"; \
		rm -rf $(shell echo $(PYTHON_ENV_PATH)); \
	else \
		echo "No environment found at $(shell echo $(PYTHON_ENV_PATH))"; \
	fi

# Compile dependencies (if you're using pip-tools)
update:
	. $(PYTHON_ENV_PATH)/bin/activate && pip-compile requirements.in --output-file=requirements.txt && \
	pip-sync requirements.txt && \
	echo "pip-tools completed!"


# Remove the venv & build artifacts
clean:
	rm -rf $(PYTHON_ENV_PATH) __pycache__ *.pyc build dist
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
	clear
	black factue/ 
	isort factue/ 
	flake8 factue/
	mypy factue/
	pyright factue/ 

ollama:
	@echo "Starting Ollama server ..."
	@echo "Ollama models: $(OLLAMA_MODELS)"
	@echo "Ollama executable: $(OLLAMA_EXECUTABLE)"
	@echo "Ollama host: $(OLLAMA_HOST)"
	OLLAMA_MODELS=$(OLLAMA_MODELS) $(OLLAMA_EXECUTABLE) serve 