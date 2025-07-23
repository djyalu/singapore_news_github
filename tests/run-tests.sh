#!/bin/bash

# Singapore News Scraper Test Runner
# Comprehensive test execution script

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_ROOT="$(dirname "$TEST_DIR")"
REPORTS_DIR="$TEST_DIR/reports"
COVERAGE_DIR="$TEST_DIR/coverage"

# Create directories
mkdir -p "$REPORTS_DIR"
mkdir -p "$COVERAGE_DIR"

# Function to print colored output
print_status() {
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python test dependencies..."
    
    if ! command_exists pip; then
        print_error "pip not found. Please install Python and pip first."
        exit 1
    fi
    
    cd "$TEST_DIR"
    pip install -r requirements.txt
    cd "$PROJECT_ROOT"
    pip install -r requirements.txt 2>/dev/null || print_warning "Main requirements.txt not found"
}

# Function to install Node.js dependencies
install_node_deps() {
    print_status "Installing Node.js test dependencies..."
    
    if ! command_exists npm; then
        print_error "npm not found. Please install Node.js and npm first."
        exit 1
    fi
    
    cd "$TEST_DIR"
    npm install
}

# Function to run Python tests
run_python_tests() {
    print_status "Running Python unit tests..."
    
    cd "$PROJECT_ROOT"
    
    # Set PYTHONPATH to include project root and scripts
    export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/scripts:$PYTHONPATH"
    
    # Run pytest with coverage
    python -m pytest tests/ \
        --verbose \
        --cov=scripts \
        --cov-report=html:tests/coverage/python \
        --cov-report=xml:tests/coverage/python/coverage.xml \
        --cov-report=term-missing \
        --junit-xml=tests/reports/python-results.xml \
        --tb=short
    
    print_success "Python tests completed"
}

# Function to run JavaScript tests
run_javascript_tests() {
    print_status "Running JavaScript unit tests..."
    
    cd "$TEST_DIR"
    
    # Run Jest tests
    npm test -- --coverage --coverageDirectory=coverage/javascript --ci --watchAll=false
    
    print_success "JavaScript tests completed"
}

# Function to run API integration tests
run_api_tests() {
    print_status "Running API integration tests..."
    
    cd "$PROJECT_ROOT"
    export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/scripts:$PYTHONPATH"
    
    # Run API-specific tests
    python -m pytest tests/test_api_integration.py \
        --verbose \
        --junit-xml=tests/reports/api-results.xml \
        --tb=short
    
    print_success "API integration tests completed"
}

# Function to run E2E tests
run_e2e_tests() {
    print_status "Running E2E tests with Playwright..."
    
    cd "$TEST_DIR"
    
    # Install Playwright browsers if needed
    if ! npx playwright --version >/dev/null 2>&1; then
        print_status "Installing Playwright browsers..."
        npx playwright install
    fi
    
    # Run Playwright tests
    npx playwright test --reporter=html --reporter=junit
    
    print_success "E2E tests completed"
}

# Function to run security tests
run_security_tests() {
    print_status "Running security tests..."
    
    cd "$PROJECT_ROOT"
    
    # Check for common security issues
    echo "Checking for hardcoded secrets..."
    
    # Look for potential secrets in code
    SECRET_PATTERNS=(
        "password.*=.*['\"].*['\"]"
        "api.*key.*=.*['\"].*['\"]"
        "token.*=.*['\"].*['\"]"
        "secret.*=.*['\"].*['\"]"
    )
    
    SECURITY_ISSUES=0
    for pattern in "${SECRET_PATTERNS[@]}"; do
        if grep -r -i -E "$pattern" --include="*.py" --include="*.js" --include="*.json" . 2>/dev/null; then
            print_warning "Potential hardcoded secret found (pattern: $pattern)"
            SECURITY_ISSUES=$((SECURITY_ISSUES + 1))
        fi
    done
    
    if [ $SECURITY_ISSUES -eq 0 ]; then
        print_success "No obvious security issues found"
    else
        print_warning "Found $SECURITY_ISSUES potential security issues"
    fi
}

# Function to run performance tests
run_performance_tests() {
    print_status "Running basic performance checks..."
    
    cd "$PROJECT_ROOT"
    
    # Check file sizes
    echo "Checking file sizes..."
    find . -name "*.js" -o -name "*.py" | while read -r file; do
        size=$(wc -l < "$file" 2>/dev/null || echo "0")
        if [ "$size" -gt 1000 ]; then
            print_warning "Large file detected: $file ($size lines)"
        fi
    done
    
    # Check for potential performance issues
    echo "Checking for performance anti-patterns..."
    
    # Check for blocking operations
    if grep -r "sleep\|time.sleep\|setTimeout.*[0-9]\{4,\}" --include="*.py" --include="*.js" . 2>/dev/null; then
        print_warning "Long blocking operations found"
    fi
    
    print_success "Performance checks completed"
}

# Function to generate comprehensive report
generate_report() {
    print_status "Generating test report..."
    
    REPORT_FILE="$REPORTS_DIR/test-summary-$(date +%Y%m%d-%H%M%S).html"
    
    cat > "$REPORT_FILE" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Singapore News Scraper Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border-left: 4px solid #007cba; }
        .success { border-left-color: #28a745; }
        .warning { border-left-color: #ffc107; }
        .error { border-left-color: #dc3545; }
        pre { background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }
        .timestamp { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Singapore News Scraper Test Report</h1>
        <p class="timestamp">Generated: $(date)</p>
    </div>
    
    <div class="section">
        <h2>Test Summary</h2>
        <ul>
            <li>Python Unit Tests: $([ -f "$REPORTS_DIR/python-results.xml" ] && echo "✅ Completed" || echo "❌ Not Run")</li>
            <li>JavaScript Unit Tests: $([ -d "$COVERAGE_DIR/javascript" ] && echo "✅ Completed" || echo "❌ Not Run")</li>
            <li>API Integration Tests: $([ -f "$REPORTS_DIR/api-results.xml" ] && echo "✅ Completed" || echo "❌ Not Run")</li>
            <li>E2E Tests: $([ -f "$TEST_DIR/test-results" ] && echo "✅ Completed" || echo "❌ Not Run")</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>Coverage Reports</h2>
        <ul>
            <li><a href="../coverage/python/index.html">Python Coverage</a></li>
            <li><a href="../coverage/javascript/lcov-report/index.html">JavaScript Coverage</a></li>
        </ul>
    </div>
    
    <div class="section">
        <h2>Test Files</h2>
        <ul>
            <li>Python Tests: $(find "$TEST_DIR" -name "test_*.py" | wc -l) files</li>
            <li>JavaScript Tests: $(find "$TEST_DIR" -name "*.test.js" | wc -l) files</li>
            <li>E2E Tests: $(find "$TEST_DIR/e2e" -name "*.spec.js" 2>/dev/null | wc -l) files</li>
        </ul>
    </div>
</body>
</html>
EOF
    
    print_success "Test report generated: $REPORT_FILE"
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up temporary files..."
    
    # Remove temporary test files
    find "$TEST_DIR" -name "*.pyc" -delete 2>/dev/null || true
    find "$TEST_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Main execution
main() {
    print_status "Starting Singapore News Scraper Test Suite"
    print_status "Test directory: $TEST_DIR"
    print_status "Project root: $PROJECT_ROOT"
    
    # Parse command line arguments
    SKIP_INSTALL=false
    RUN_ALL=true
    RUN_PYTHON=false
    RUN_JS=false
    RUN_API=false
    RUN_E2E=false
    RUN_SECURITY=false
    RUN_PERFORMANCE=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-install)
                SKIP_INSTALL=true
                shift
                ;;
            --python-only)
                RUN_ALL=false
                RUN_PYTHON=true
                shift
                ;;
            --js-only)
                RUN_ALL=false
                RUN_JS=true
                shift
                ;;
            --api-only)
                RUN_ALL=false
                RUN_API=true
                shift
                ;;
            --e2e-only)
                RUN_ALL=false
                RUN_E2E=true
                shift
                ;;
            --security-only)
                RUN_ALL=false
                RUN_SECURITY=true
                shift
                ;;
            --performance-only)
                RUN_ALL=false
                RUN_PERFORMANCE=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --skip-install      Skip dependency installation"
                echo "  --python-only       Run only Python tests"
                echo "  --js-only          Run only JavaScript tests"
                echo "  --api-only         Run only API tests"
                echo "  --e2e-only         Run only E2E tests"
                echo "  --security-only    Run only security tests"
                echo "  --performance-only Run only performance tests"
                echo "  --help             Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Install dependencies unless skipped
    if [ "$SKIP_INSTALL" = false ]; then
        install_python_deps
        install_node_deps
    fi
    
    # Run tests based on options
    EXIT_CODE=0
    
    if [ "$RUN_ALL" = true ] || [ "$RUN_PYTHON" = true ]; then
        run_python_tests || EXIT_CODE=1
    fi
    
    if [ "$RUN_ALL" = true ] || [ "$RUN_JS" = true ]; then
        run_javascript_tests || EXIT_CODE=1
    fi
    
    if [ "$RUN_ALL" = true ] || [ "$RUN_API" = true ]; then
        run_api_tests || EXIT_CODE=1
    fi
    
    if [ "$RUN_ALL" = true ] || [ "$RUN_E2E" = true ]; then
        run_e2e_tests || EXIT_CODE=1
    fi
    
    if [ "$RUN_ALL" = true ] || [ "$RUN_SECURITY" = true ]; then
        run_security_tests || EXIT_CODE=1
    fi
    
    if [ "$RUN_ALL" = true ] || [ "$RUN_PERFORMANCE" = true ]; then
        run_performance_tests || EXIT_CODE=1
    fi
    
    # Generate report
    generate_report
    
    # Cleanup
    cleanup
    
    # Final status
    if [ $EXIT_CODE -eq 0 ]; then
        print_success "All tests completed successfully!"
    else
        print_error "Some tests failed. Check the reports for details."
    fi
    
    exit $EXIT_CODE
}

# Run main function
main "$@"