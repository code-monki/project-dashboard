# =============================================================================
# Makefile for the Project Dashboard
#
# This Makefile provides a set of targets to automate common development
# tasks such as setting up the environment, running tests, and cleaning up.
# =============================================================================

# Default shell for executing commands
SHELL := /bin/bash

# Use a python interpreter from a virtual environment if it exists
VENV := .venv
PYTHON := $(VENV)/bin/python

.PHONY: help install test clean

# Default target: show help
default: help

# Self-documenting help target.
# From: https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help:
    @echo "Usage: make [target]"
    @echo ""
    @echo "Targets:"
    @grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
        awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: $(VENV)/bin/activate ## Install dependencies and set up the virtual environment.
$(VENV)/bin/activate: requirements.txt
    @if [ ! -d "$(VENV)" ]; then \
        echo ">>> Creating virtual environment..."; \
        python3 -m venv $(VENV); \
    fi
    @echo ">>> Installing dependencies from requirements.txt..."
    $(PYTHON) -m pip install -r requirements.txt
    @touch $(VENV)/bin/activate

test: ## Run the pytest test suite.
    @echo ">>> Running tests..."
    $(PYTHON) -m pytest

clean: ## Remove build artifacts and cache directories.
    @echo ">>> Cleaning up..."
    @rm -rf .pytest_cache
    @rm -rf .mypy_cache
    @find . -type d -name "__pycache__" -exec rm -rf {} +
    @echo "Cleanup complete."
