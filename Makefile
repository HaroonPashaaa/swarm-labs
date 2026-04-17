# Makefile for Swarm Labs

.PHONY: help install test lint format docker run clean

help:
	@echo "Wojak Capital Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  install    - Install dependencies"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linters"
	@echo "  format     - Format code"
	@echo "  docker     - Build Docker image"
	@echo "  run        - Run the swarm"
	@echo "  clean      - Clean build files"

install:
	pip install -r requirements.txt

test:
	pytest --cov=. --cov-report=html

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	mypy . || true

format:
	black .
	isort .

docker:
	docker build -t swarm-labs .

run:
	python -m openclaw.core

clean:
	rm -rf __pycache__ .pytest_cache htmlcov .mypy_cache
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

dev:
	docker-compose up -d

dev-down:
	docker-compose down

logs:
	docker-compose logs -f swarm
