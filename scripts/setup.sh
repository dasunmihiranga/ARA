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

# Check if Python 3.8+ is installed
check_python() {
    print_step "Checking Python version..."
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if (( $(echo "$PYTHON_VERSION >= 3.8" | bc -l) )); then
            echo "Python $PYTHON_VERSION found"
        else
            print_error "Python 3.8 or higher is required"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_step "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Virtual environment created and activated"
}

# Install dependencies
install_dependencies() {
    print_step "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "Dependencies installed successfully"
}

# Create necessary directories
create_directories() {
    print_step "Creating project directories..."
    mkdir -p data/{models,cache,vector_store,knowledge_graphs}
    mkdir -p logs
    echo "Directories created successfully"
}

# Copy configuration files
setup_config() {
    print_step "Setting up configuration files..."
    if [ ! -f .env ]; then
        cp .env.example .env
        print_warning "Please update .env with your configuration"
    fi
    echo "Configuration files set up"
}

# Check system requirements
check_system() {
    print_step "Checking system requirements..."
    
    # Check available memory
    MEMORY=$(free -m | awk '/^Mem:/{print $2}')
    if [ "$MEMORY" -lt 4096 ]; then
        print_warning "Less than 4GB of RAM available. Some features may not work optimally."
    fi
    
    # Check disk space
    DISK_SPACE=$(df -m . | awk 'NR==2 {print $4}')
    if [ "$DISK_SPACE" -lt 10240 ]; then
        print_warning "Less than 10GB of free disk space. Consider freeing up space."
    fi
    
    echo "System requirements checked"
}

# Main setup process
main() {
    echo "Starting setup process..."
    
    check_python
    create_venv
    install_dependencies
    create_directories
    setup_config
    check_system
    
    echo -e "${GREEN}Setup completed successfully!${NC}"
    echo "To activate the virtual environment, run: source venv/bin/activate"
    echo "To start the server, run: ./scripts/start_server.sh"
}

# Run main function
main 