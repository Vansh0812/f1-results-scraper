# F1 Results Scraper - Development Makefile
# =========================================

.PHONY: help install install-dev test lint format type-check clean build docker run scrape

# Default target
help:
	@echo "F1 Results Scraper - Development Commands"
	@echo "========================================"
	@echo ""
	@echo "Installation:"
	@echo "  install      Install package dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  test         Run test suite with coverage"
	@echo "  lint         Run code linting"
	@echo "  format       Format code with black"
	@echo "  type-check   Run type checking with mypy"
	@echo "  clean        Clean build artifacts"
	@echo ""
	@echo "Building:"
	@echo "  build        Build Python package"
	@echo "  docker       Build Docker image"
	@echo ""
	@echo "Running:"
	@echo "  run          Run scraper with default settings"
	@echo "  scrape-2024  Scrape 2024 season data"
	@echo "  scrape-2025  Scrape 2025 season data"
	@echo ""

# Installation targets
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8 mypy pre-commit
	pre-commit install

# Development targets
test:
	@echo "Running test suite..."
	pytest tests/ -v --cov=f1_scraper_pro --cov-report=html --cov-report=term-missing

lint:
	@echo "Running code linting..."
	flake8 f1_scraper_pro.py --max-line-length=127 --extend-ignore=E203,W503
	@echo "Linting completed successfully!"

format:
	@echo "Formatting code..."
	black f1_scraper_pro.py tests/
	@echo "Code formatting completed!"

type-check:
	@echo "Running type checking..."
	mypy f1_scraper_pro.py --ignore-missing-imports
	@echo "Type checking completed!"

# Quality assurance
check: lint type-check test
	@echo "All quality checks passed!"

# Cleaning targets
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf output/
	rm -rf *.log
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "Cleanup completed!"

# Building targets
build: clean
	@echo "Building Python package..."
	python setup.py sdist bdist_wheel
	@echo "Package built successfully!"

docker:
	@echo "Building Docker image..."
	docker build -t f1-results-scraper:latest .
	@echo "Docker image built successfully!"

docker-compose:
	@echo "Starting services with docker-compose..."
	docker-compose up -d
	@echo "Services started!"

# Running targets
run:
	@echo "Running F1 scraper with default settings..."
	python f1_scraper_pro.py --summary

scrape-2024:
	@echo "Scraping 2024 F1 season..."
	python f1_scraper_pro.py --year 2024 --output-dir ./data/2024 --summary

scrape-2025:
	@echo "Scraping 2025 F1 season..."
	python f1_scraper_pro.py --year 2025 --output-dir ./data/2025 --summary

scrape-debug:
	@echo "Running scraper in debug mode..."
	python f1_scraper_pro.py --log-level DEBUG --summary

# Development workflow
dev-setup: install-dev
	@echo "Development environment setup complete!"
	@echo "Run 'make check' to verify everything is working."

# Production deployment
deploy-prod:
	@echo "Deploying to production..."
	docker-compose -f docker-compose.prod.yml up -d
	@echo "Production deployment complete!"

# Backup and restore
backup-data:
	@echo "Backing up scraped data..."
	tar -czf backup_$(shell date +%Y%m%d_%H%M%S).tar.gz output/
	@echo "Data backup completed!"

# Performance testing
benchmark:
	@echo "Running performance benchmarks..."
	python -m timeit -s "from f1_scraper_pro import F1ResultsScraperPro" \
		"scraper = F1ResultsScraperPro(year=2024); scraper.scrape()"

# Documentation
docs:
	@echo "Generating documentation..."
	python -m pydoc -w f1_scraper_pro
	@echo "Documentation generated!"

# Security checks
security-check:
	@echo "Running security checks..."
	pip-audit
	safety check
	@echo "Security checks completed!"

# Release preparation
pre-release: clean check security-check build
	@echo "Pre-release checks completed successfully!"
	@echo "Ready for release!"

# Environment info
env-info:
	@echo "Environment Information"
	@echo "======================"
	@echo "Python version: $(shell python --version)"
	@echo "Pip version: $(shell pip --version)"
	@echo "Virtual env: $(VIRTUAL_ENV)"
	@echo "Working directory: $(shell pwd)"
	@echo ""
	@echo "Installed packages:"
	@pip list --format=columns

# Quick commands for common workflows
quick-test: format lint test
	@echo "Quick development cycle completed!"

full-check: clean install-dev check security-check
	@echo "Full quality assurance completed!"