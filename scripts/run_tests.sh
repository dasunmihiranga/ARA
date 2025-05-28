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

# Check test dependencies
check_dependencies() {
    print_step "Checking test dependencies..."
    
    # Check if pytest is installed
    if ! python -c "import pytest" &>/dev/null; then
        print_error "pytest not found"
        echo "Installing pytest..."
        pip install pytest pytest-cov pytest-asyncio pytest-mock
    fi
    
    # Check if test requirements are installed
    if [ -f "tests/requirements.txt" ]; then
        print_step "Installing test requirements..."
        pip install -r tests/requirements.txt
    fi
    
    echo "Dependencies checked"
}

# Run unit tests
run_unit_tests() {
    print_step "Running unit tests..."
    
    pytest tests/unit \
        --cov=src/research_assistant \
        --cov-report=term-missing \
        --cov-report=html \
        -v
}

# Run integration tests
run_integration_tests() {
    print_step "Running integration tests..."
    
    pytest tests/integration \
        --cov=src/research_assistant \
        --cov-append \
        --cov-report=term-missing \
        --cov-report=html \
        -v
}

# Run API tests
run_api_tests() {
    print_step "Running API tests..."
    
    pytest tests/api \
        --cov=src/research_assistant \
        --cov-append \
        --cov-report=term-missing \
        --cov-report=html \
        -v
}

# Generate coverage report
generate_coverage_report() {
    print_step "Generating coverage report..."
    
    # Combine coverage reports
    coverage combine
    
    # Generate HTML report
    coverage html -d coverage_report
    
    echo "Coverage report generated in coverage_report/"
}

# Clean up test artifacts
cleanup() {
    print_step "Cleaning up test artifacts..."
    
    # Remove coverage data
    rm -f .coverage*
    
    # Remove pytest cache
    rm -rf .pytest_cache
    
    echo "Cleanup completed"
}

# Main test process
main() {
    echo "Starting test process..."
    
    check_venv
    check_dependencies
    
    # Run all test suites
    run_unit_tests
    run_integration_tests
    run_api_tests
    
    generate_coverage_report
    cleanup
    
    echo -e "${GREEN}All tests completed successfully!${NC}"
}

# Run main function
main 