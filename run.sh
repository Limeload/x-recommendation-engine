#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to show usage
usage() {
    cat << EOF
Usage: $0 [COMMAND]

Commands:
    start           Start both backend and frontend (default)
    backend         Start only backend
    frontend        Start only frontend
    install         Install dependencies only
    clean           Stop running servers and cleanup
    help            Show this help message

Examples:
    $0 start                # Start both servers
    $0 backend              # Start only backend
    $0 install              # Install dependencies
    $0 clean                # Stop servers

EOF
}

# Function to check dependencies
check_dependencies() {
    local missing=0

    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        missing=1
    fi

    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        missing=1
    fi

    if [ $missing -eq 1 ]; then
        echo ""
        print_warning "Please install missing dependencies:"
        echo "  - Python 3.8+: https://www.python.org/downloads/"
        echo "  - Node.js 16+: https://nodejs.org/"
        exit 1
    fi

    print_success "All dependencies found"
}

# Function to install dependencies
install_deps() {
    echo ""
    print_info "Installing backend dependencies..."
    cd "$SCRIPT_DIR/backend"

    # On macOS, force ARM64 architecture for consistency
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # Always recreate venv on macOS to ensure proper architecture
        if [ -d "venv" ]; then
            rm -rf venv
        fi
        # Use Python 3.12 for better ARM64 support
        /usr/local/bin/python3.12 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        deactivate
    else
        if [ -d "venv" ]; then
            rm -rf venv
        fi
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        deactivate
    fi
    print_success "Virtual environment created"
    print_success "Backend dependencies installed"

    echo ""
    print_info "Installing frontend dependencies..."
    cd "$SCRIPT_DIR/frontend"

    if [ ! -d "node_modules" ]; then
        npm install
    fi

    print_success "Frontend dependencies installed"

    cd "$SCRIPT_DIR"
}

# Function to start backend
start_backend() {
    echo ""
    print_info "Starting backend server..."

    cd "$SCRIPT_DIR/backend"

    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found. Run: $0 install"
        return 1
    fi

    source venv/bin/activate

    export PYTHONUNBUFFERED=1
    # Run python directly - the venv is already compiled for the correct architecture
    python main.py &
    BACKEND_PID=$!

    sleep 2

    if kill -0 $BACKEND_PID 2>/dev/null; then
        print_success "Backend started (PID: $BACKEND_PID)"
        echo "   URL: http://localhost:8000"
        echo "   API Docs: http://localhost:8000/docs"
        return 0
    else
        print_error "Backend failed to start"
        return 1
    fi
}

# Function to start frontend
start_frontend() {
    echo ""
    print_info "Starting frontend server..."

    cd "$SCRIPT_DIR/frontend"

    if [ ! -d "node_modules" ]; then
        print_error "Dependencies not found. Run: $0 install"
        return 1
    fi

    npm run dev &
    FRONTEND_PID=$!

    sleep 3

    if kill -0 $FRONTEND_PID 2>/dev/null; then
        print_success "Frontend started (PID: $FRONTEND_PID)"
        echo "   URL: http://localhost:3000"
        return 0
    else
        print_error "Frontend failed to start"
        return 1
    fi
}

# Function to start both servers
start_all() {
    echo ""
    print_info "Starting Recommendation Engine..."
    echo ""

    # Check if ports are available
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port 8000 is already in use"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return 1
        fi
    fi

    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port 3000 is already in use"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return 1
        fi
    fi

    # Start servers
    start_backend || return 1
    start_frontend || return 1

    echo ""
    print_success "All servers running!"
    echo ""
    echo "========================================="
    echo "Backend:  http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo ""
    echo "API Docs: http://localhost:8000/docs"
    echo "========================================="
    echo ""
    print_info "Press Ctrl+C to stop servers"

    # Wait for interrupt
    wait
}

# Function to cleanup and stop servers
cleanup() {
    echo ""
    print_info "Stopping servers..."

    # Kill all child processes
    pkill -P $$ 2>/dev/null || true

    # Kill background processes
    jobs -p | xargs kill 2>/dev/null || true

    print_success "Servers stopped"
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Main script logic
case "${1:-start}" in
    start)
        check_dependencies
        install_deps
        start_all
        ;;
    backend)
        check_dependencies
        install_deps
        start_backend
        wait
        ;;
    frontend)
        check_dependencies
        install_deps
        start_frontend
        wait
        ;;
    install)
        check_dependencies
        install_deps
        print_success "Installation complete!"
        ;;
    clean)
        cleanup
        ;;
    help)
        usage
        ;;
    *)
        print_error "Unknown command: $1"
        usage
        exit 1
        ;;
esac
