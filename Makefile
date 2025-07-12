.PHONY: help start start-prod stop restart logs status clean build test test-service test-watch

help:
	@echo "Dataset Catalog API - Available Commands:"
	@echo ""
	@echo "  start       Start the application in development mode"
	@echo "  start-prod  Start the application in production mode"
	@echo "  stop        Stop the application"
	@echo "  restart     Restart the application"
	@echo "  logs        Show application logs"
	@echo "  status      Show container status"
	@echo "  clean       Stop and remove all containers, networks, and volumes"
	@echo "  build       Build the Docker image"
	@echo "  test        Run tests in Docker container"
	@echo "  test-service Run tests using dedicated test service"
	@echo "  test-watch  Run tests in watch mode"
	@echo "  help        Show this help message"

start:
	@echo "Starting Dataset Catalog API in development mode..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file from template"; fi
	docker-compose up -d
	@echo "✅ Application started successfully!"
	@echo "📍 API: http://localhost:5000"
	@echo "📍 API Documentation: http://localhost:5000/apidocs"
	@echo "📍 MongoDB Admin: http://localhost:8081 (admin/admin123)"

stop:
	@echo "Stopping Dataset Catalog API..."
	docker-compose down 2>/dev/null || true
	docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
	@echo "✅ Application stopped successfully!"

restart: stop
	@sleep 2
	@$(MAKE) start

logs:
	@echo "Showing application logs (Press Ctrl+C to exit)..."
	docker-compose logs -f 2>/dev/null || docker-compose -f docker-compose.prod.yml logs -f 2>/dev/null

status:
	@echo "Container status:"
	@docker-compose ps 2>/dev/null || docker-compose -f docker-compose.prod.yml ps 2>/dev/null || echo "No containers found"

clean:
	@echo "⚠️  This will stop and remove all containers, networks, and volumes!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "Cleaning up..."
	docker-compose down -v 2>/dev/null || true
	docker-compose -f docker-compose.prod.yml down -v 2>/dev/null || true
	@echo "✅ Cleanup completed!"

build:
	@echo "Building Docker image..."
	docker-compose build --no-cache
	@echo "✅ Docker image built successfully!"

test:
	@echo "Running tests in Docker container..."
	docker-compose run --rm api python -m pytest -v
	@echo "✅ Tests completed!"

# Local development without Docker
install:
	@echo "Installing dependencies for local development..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

run-local:
	@echo "Running application locally..."
	python app.py

test-local:
	@echo "Running tests locally..."
	pytest -v
