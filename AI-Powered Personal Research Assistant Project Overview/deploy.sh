#!/bin/bash

# AI Research Assistant Deployment Script
# This script prepares and deploys the research assistant application

set -e  # Exit on any error

echo "🚀 AI Research Assistant Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed"
        exit 1
    fi
    
    # Check pnpm
    if ! command -v pnpm &> /dev/null; then
        print_warning "pnpm not found, installing..."
        npm install -g pnpm
    fi
    
    print_success "Prerequisites check completed"
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd research-assistant-backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing backend dependencies..."
    pip install -r requirements.txt
    
    # Check OpenAI API key
    if [ -z "$OPENAI_API_KEY" ]; then
        print_warning "OPENAI_API_KEY environment variable not set"
        print_warning "Please set it before running the application"
    fi
    
    cd ..
    print_success "Backend setup completed"
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd research-assistant-frontend
    
    # Install dependencies
    print_status "Installing frontend dependencies..."
    pnpm install
    
    cd ..
    print_success "Frontend setup completed"
}

# Build frontend for production
build_frontend() {
    print_status "Building frontend for production..."
    
    cd research-assistant-frontend
    pnpm run build
    
    # Copy build files to backend static directory
    if [ -d "dist" ]; then
        print_status "Copying build files to backend..."
        cp -r dist/* ../research-assistant-backend/src/static/
        print_success "Frontend build copied to backend"
    else
        print_error "Frontend build failed - dist directory not found"
        exit 1
    fi
    
    cd ..
}

# Run tests
run_tests() {
    print_status "Running integration tests..."
    
    cd research-assistant-backend
    source venv/bin/activate
    
    # Run mock integration test
    if python ../test_integration_mock.py; then
        print_success "Integration tests passed"
    else
        print_error "Integration tests failed"
        exit 1
    fi
    
    cd ..
}

# Start services
start_services() {
    print_status "Starting services..."
    
    # Start backend
    cd research-assistant-backend
    source venv/bin/activate
    
    print_status "Starting Flask backend on port 5000..."
    python src/main.py &
    BACKEND_PID=$!
    
    cd ..
    
    # Wait for backend to start
    sleep 5
    
    # Test backend health
    if curl -f http://localhost:5000/api/documents > /dev/null 2>&1; then
        print_success "Backend is running successfully"
    else
        print_warning "Backend health check failed, but continuing..."
    fi
    
    print_success "Services started successfully"
    print_status "Backend PID: $BACKEND_PID"
    print_status "Access the application at: http://localhost:5000"
}

# Main deployment function
deploy() {
    local mode=${1:-"development"}
    
    print_status "Deploying in $mode mode..."
    
    check_prerequisites
    setup_backend
    setup_frontend
    
    if [ "$mode" = "production" ]; then
        build_frontend
    fi
    
    run_tests
    
    if [ "$mode" = "development" ]; then
        print_status "Development mode - starting both frontend and backend..."
        
        # Start backend
        cd research-assistant-backend
        source venv/bin/activate
        python src/main.py &
        BACKEND_PID=$!
        cd ..
        
        # Start frontend
        cd research-assistant-frontend
        pnpm run dev --host &
        FRONTEND_PID=$!
        cd ..
        
        print_success "Development servers started"
        print_status "Frontend: http://localhost:5173"
        print_status "Backend: http://localhost:5000"
        print_status "Backend PID: $BACKEND_PID"
        print_status "Frontend PID: $FRONTEND_PID"
        
    else
        start_services
    fi
}

# Help function
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  development    Deploy in development mode (default)"
    echo "  production     Deploy in production mode"
    echo "  help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Deploy in development mode"
    echo "  $0 development        # Deploy in development mode"
    echo "  $0 production         # Deploy in production mode"
    echo ""
    echo "Environment Variables:"
    echo "  OPENAI_API_KEY       Required for OpenAI API access"
    echo ""
}

# Main script logic
case "${1:-development}" in
    "development")
        deploy "development"
        ;;
    "production")
        deploy "production"
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac

