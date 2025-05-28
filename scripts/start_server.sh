#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print with color
print_step() {
    echo -e "${GREEN}==>${NC} $1"
}

print_error() {
    echo -e "${RED}Error:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}Warning:${NC} $1"
}

# Check if virtual environment is activated
check_venv() {
    if [ -z "$VIRTUAL_ENV" ]; then
        print_error "Virtual environment is not activated"
        echo "Please run: source venv/bin/activate"
        exit 1
    fi
}

# Check if required services are running
check_services() {
    print_step "Checking required services..."
    
    # Check if Ollama is running
    if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
        print_error "Ollama service is not running"
        echo "Please start Ollama service"
        exit 1
    fi
    
    # Check if ChromaDB is running (if using)
    if [ -f ".env" ] && grep -q "CHROMA_HOST" .env; then
        CHROMA_HOST=$(grep CHROMA_HOST .env | cut -d '=' -f2)
        if ! curl -s "$CHROMA_HOST/health" &>/dev/null; then
            print_warning "ChromaDB service is not running"
            echo "Some features may not work properly"
        fi
    fi
    
    echo "Required services checked"
}

# Check configuration
check_config() {
    print_step "Checking configuration..."
    
    # Check if .env exists
    if [ ! -f ".env" ]; then
        print_error ".env file not found"
        echo "Please run setup.sh first"
        exit 1
    fi
    
    # Check if config files exist
    for config in "config/models.yaml" "config/search_sources.yaml" "config/extraction_rules.yaml" "config/analysis_templates.yaml" "config/logging.yaml"; do
        if [ ! -f "$config" ]; then
            print_error "$config not found"
            exit 1
        fi
    done
    
    echo "Configuration checked"
}

# Start the server
start_server() {
    print_step "Starting server..."
    
    # Get server configuration from .env
    HOST=$(grep HOST .env | cut -d '=' -f2)
    PORT=$(grep PORT .env | cut -d '=' -f2)
    WORKERS=$(grep WORKERS .env | cut -d '=' -f2)
    
    # Start uvicorn server
    uvicorn src.research_assistant.server:app \
        --host "$HOST" \
        --port "$PORT" \
        --workers "$WORKERS" \
        --reload \
        --log-level info
}

# Handle signals
trap 'echo -e "\n${YELLOW}Shutting down server...${NC}"; exit 0' INT TERM

# Main startup process
main() {
    echo "Starting server process..."
    
    check_venv
    check_services
    check_config
    start_server
}

# Run main function
main 