#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_step() {
    echo -e "${GREEN}==>${NC} $1"
}

print_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

# Function to check if Python virtual environment is activated
check_venv() {
    if [ -z "$VIRTUAL_ENV" ]; then
        print_error "Python virtual environment is not activated"
        print_step "Please activate the virtual environment first:"
        echo "source venv/bin/activate  # Linux/Mac"
        echo "venv\\Scripts\\activate   # Windows"
        exit 1
    fi
}

# Function to check if required packages are installed
check_dependencies() {
    print_step "Checking test dependencies..."
    
    # Check pytest
    if ! python -c "import pytest" &> /dev/null; then
        print_error "pytest is not installed"
        print_step "Installing pytest..."
        pip install pytest
    fi
    
    # Check pytest-cov
    if ! python -c "import pytest_cov" &> /dev/null; then
        print_error "pytest-cov is not installed"
        print_step "Installing pytest-cov..."
        pip install pytest-cov
    fi
    
    # Check pytest-asyncio
    if ! python -c "import pytest_asyncio" &> /dev/null; then
        print_error "pytest-asyncio is not installed"
        print_step "Installing pytest-asyncio..."
        pip install pytest-asyncio
    fi
    
    # Check pytest-mock
    if ! python -c "import pytest_mock" &> /dev/null; then
        print_error "pytest-mock is not installed"
        print_step "Installing pytest-mock..."
        pip install pytest-mock
    fi
}

# Function to run tests
run_tests() {
    local test_type=$1
    local coverage=$2
    
    print_step "Running $test_type tests..."
    
    if [ "$coverage" = true ]; then
        pytest "tests/$test_type" \
            --cov=src \
            --cov-report=term-missing \
            --cov-report=html \
            -v
    else
        pytest "tests/$test_type" -v
    fi
}

# Function to clean up test artifacts
cleanup() {
    print_step "Cleaning up test artifacts..."
    
    # Remove coverage data
    rm -rf .coverage
    rm -rf htmlcov
    
    # Remove test cache
    rm -rf .pytest_cache
    
    # Remove test data
    rm -rf tests/data/*
}

# Main function
main() {
    # Check virtual environment
    check_venv
    
    # Check dependencies
    check_dependencies
    
    # Parse command line arguments
    local run_unit=true
    local run_integration=true
    local run_e2e=true
    local with_coverage=true
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --unit-only)
                run_integration=false
                run_e2e=false
                ;;
            --integration-only)
                run_unit=false
                run_e2e=false
                ;;
            --e2e-only)
                run_unit=false
                run_integration=false
                ;;
            --no-coverage)
                with_coverage=false
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
        shift
    done
    
    # Create test data directory
    mkdir -p tests/data
    
    # Run tests
    if [ "$run_unit" = true ]; then
        run_tests "unit" $with_coverage
    fi
    
    if [ "$run_integration" = true ]; then
        run_tests "integration" $with_coverage
    fi
    
    if [ "$run_e2e" = true ]; then
        run_tests "e2e" $with_coverage
    fi
    
    # Cleanup
    cleanup
    
    print_step "All tests completed successfully!"
}

# Run main function
main "$@" 