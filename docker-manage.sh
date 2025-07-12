#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

show_help() {
    echo "Dataset Catalog API Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start the application in development mode"
    echo "  stop        Stop the application"
    echo "  restart     Restart the application"
    echo "  logs        Show application logs"
    echo "  status      Show container status"
    echo "  clean       Stop and remove all containers, networks, and volumes"
    echo "  build       Build the Docker image"
    echo "  test        Run tests in Docker container"
    echo "  help        Show this help message"
    echo ""
}
    echo "  build       Build the Docker image"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start                # Start in development mode"
    echo "  $0 logs                # Show all logs"
    echo "  $0 clean               # Clean up everything"
}

start_dev() {
    print_info "Starting Dataset Catalog API in development mode..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_info "Creating .env file from template..."
        cp .env.example .env
        print_warning "Please review and update the .env file with your settings"
    fi
    
    docker-compose up -d
    
    print_success "Application started successfully!"
    print_info "Services available at:"
    print_info "  - API: http://localhost:5000"
    print_info "  - API Documentation: http://localhost:5000/apidocs"
    print_info "  - MongoDB Admin: http://localhost:8081 (admin/admin123)"
    print_info ""
    print_info "Use '$0 logs' to view logs"
    print_info "Use '$0 stop' to stop the application"
}

# Function to stop the application
stop_app() {
    print_info "Stopping Dataset Catalog API..."
    docker-compose down 2>/dev/null || true
    print_success "Application stopped successfully!"
}

# Function to restart the application
restart_app() {
    stop_app
    sleep 2
    start_dev
}

# Function to show logs
show_logs() {
    print_info "Showing application logs (Press Ctrl+C to exit)..."
    docker-compose logs -f 2>/dev/null ||print_error "No running containers found"
}

# Function to show container status
show_status() {
    print_info "Container status:"
    docker-compose ps 2>/dev/null || print_error "No containers found"
}

# Function to clean up everything
clean_up() {
    print_warning "This will stop and remove all containers, networks, and volumes!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning up..."
        docker-compose down -v 2>/dev/null || true
        print_success "Cleanup completed!"
    else
        print_info "Cleanup cancelled."
    fi
}

build_image() {
    print_info "Building Docker image..."
    docker-compose build --no-cache
    print_success "Docker image built successfully!"
}

run_tests() {
    print_info "Running tests in Docker container..."
    docker-compose run --rm api python -m pytest -v
    print_success "Tests completed successfully!"
}

main() {
    check_docker
    
    case "${1:-}" in
        "start")
            start_dev
            ;;
        "stop")
            stop_app
            ;;
        "restart")
            restart_app
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "clean")
            clean_up
            ;;
        "build")
            build_image
            ;;
        "test")
            run_tests
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        "")
            print_error "No command specified."
            show_help
            exit 1
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
