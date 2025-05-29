.PHONY: help install test lint format check-format check-types check-security clean run build-docker run-docker stop-docker

# Define variables
PYTHON = python
PIP = pip
PYTEST = pytest
BLACK = black
ISORT = isort
FLAKE8 = flake8
MYPY = mypy
BANDIT = bandit
SAFETY = safety
DOCKER = docker
DOCKER_COMPOSE = docker-compose

# Help command to show all available commands
help:
	@echo "Available commands:"
	@echo "  make install          - Install dependencies"
	@echo "  make test             - Run tests"
	@echo "  make lint             - Run all linters"
	@echo "  make format           - Format code with black and isort"
	@echo "  make check-format     - Check code formatting"
	@echo "  make check-types      - Run type checking with mypy"
	@echo "  make check-security   - Run security checks"
	@echo "  make clean            - Clean up temporary files"
	@echo "  make run              - Run the application"
	@echo "  make build-docker     - Build Docker image"
	@echo "  make run-docker       - Run the application in Docker"
	@echo "  make stop-docker      - Stop all Docker containers"

# Install dependencies
install:
	@echo "Installing dependencies..."
	${PIP} install -e .[dev]
	@echo "\nInstallation complete!"

# Run tests
test:
	@echo "Running tests..."
	${PYTEST} tests/ -v --cov=neoserve_ai --cov-report=term-missing --cov-report=html

# Run all linters
lint: check-format check-types check-security

# Format code with black and isort
format:
	@echo "Formatting code..."
	${BLACK} .
	${ISORT} .


# Check code formatting
check-format:
	@echo "Checking code formatting..."
	${BLACK} --check .
	${ISORT} --check-only .

# Run type checking
check-types:
	@echo "Running type checking..."
	${MYPY} neoserve_ai tests

# Run security checks
check-security:
	@echo "Running security checks..."
	${BANDIT} -r neoserve_ai
	${SAFETY} check

# Clean up temporary files
clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/

# Run the application
run:
	@echo "Starting NeoServe AI..."
	uvicorn neoserve_ai.main:app --reload

# Build Docker image
build-docker:
	@echo "Building Docker image..."
	${DOCKER} build -t neoserve-ai .

# Run the application in Docker
run-docker: build-docker
	@echo "Starting NeoServe AI in Docker..."
	${DOCKER_COMPOSE} up -d

# Stop all Docker containers
stop-docker:
	@echo "Stopping Docker containers..."
	${DOCKER_COMPOSE} down

# Default target
default: help
