.PHONY: help install backend frontend start clean lint test

help:
	@echo "Recommendation Engine - Project Commands"
	@echo ""
	@echo "Usage: make [COMMAND]"
	@echo ""
	@echo "Commands:"
	@echo "  install     Install dependencies for both backend and frontend"
	@echo "  backend     Install backend and start backend server only"
	@echo "  frontend    Install frontend and start frontend server only"
	@echo "  start       Install dependencies and start both servers"
	@echo "  clean       Stop running servers and remove temporary files"
	@echo "  lint        Run linting checks"
	@echo "  test        Run test suite"
	@echo "  help        Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make start              # Start both servers"
	@echo "  make backend            # Start only backend"
	@echo "  make test               # Run tests"

install:
	@echo "Installing dependencies..."
	@cd backend && python3 -m venv venv && . venv/bin/activate && pip install -q -r requirements.txt && deactivate
	@cd frontend && npm install --silent
	@echo "✓ Dependencies installed"

backend: install
	@echo "Starting backend server..."
	@cd backend && . venv/bin/activate && python main.py

frontend: install
	@echo "Starting frontend server..."
	@cd frontend && npm run dev

start: install
	@echo "Starting both servers..."
	@echo ""
	@echo "Backend:  http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo ""
	@echo "Run in separate terminals or use: ./run.sh"
	@echo ""
	@echo "Backend:"
	@cd backend && . venv/bin/activate && python main.py &
	@echo ""
	@echo "Frontend:"
	@cd frontend && npm run dev

clean:
	@echo "Cleaning up..."
	@pkill -f "python main.py" || true
	@pkill -f "next dev" || true
	@pkill -f "npm run dev" || true
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name node_modules -prune -o -type f -name "*.pyc" -delete
	@echo "✓ Cleanup complete"

lint:
	@echo "Running linters..."
	@cd backend && . venv/bin/activate && python -m pylint backend/ || true
	@cd frontend && npm run lint || true

test:
	@echo "Running tests..."
	@cd .. && pytest test_exploration_layer.py -v
	@cd frontend && npm run test || true

.DEFAULT_GOAL := help
