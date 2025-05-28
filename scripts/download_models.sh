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

# Check if Ollama is installed
check_ollama() {
    print_step "Checking Ollama installation..."
    if ! command -v ollama &>/dev/null; then
        print_error "Ollama is not installed"
        echo "Please install Ollama from https://ollama.ai"
        exit 1
    fi
    echo "Ollama found"
}

# Download models from config
download_models() {
    print_step "Reading model configurations..."
    if [ ! -f "config/models.yaml" ]; then
        print_error "models.yaml not found"
        exit 1
    fi
    
    # Parse models from YAML (using Python)
    MODELS=$(python3 -c "
import yaml
with open('config/models.yaml', 'r') as f:
    config = yaml.safe_load(f)
    print('\n'.join(config.get('models', {}).keys()))
")
    
    for model in $MODELS; do
        print_step "Downloading model: $model"
        ollama pull $model
        
        if [ $? -eq 0 ]; then
            echo "Successfully downloaded $model"
        else
            print_error "Failed to download $model"
            exit 1
        fi
    done
}

# Verify model downloads
verify_models() {
    print_step "Verifying model downloads..."
    for model in $MODELS; do
        if ollama list | grep -q "$model"; then
            echo "Verified $model"
        else
            print_error "Failed to verify $model"
            exit 1
        fi
    done
}

# Check disk space
check_disk_space() {
    print_step "Checking available disk space..."
    DISK_SPACE=$(df -m . | awk 'NR==2 {print $4}')
    if [ "$DISK_SPACE" -lt 20480 ]; then
        print_warning "Less than 20GB of free disk space. Some models may not fit."
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Main download process
main() {
    echo "Starting model download process..."
    
    check_venv
    check_ollama
    check_disk_space
    download_models
    verify_models
    
    echo -e "${GREEN}Model download completed successfully!${NC}"
    echo "Available models:"
    ollama list
}

# Run main function
main 