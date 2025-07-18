#!/bin/bash

# LaTeX Tracker - One-Click Installation Script
echo "🚀 Starting LaTeX Tracker Installation..."

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

# Check if running on supported OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Cygwin;;
    MINGW*)     MACHINE=MinGw;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

print_status "Detected OS: $MACHINE"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install system dependencies based on OS
install_system_deps() {
    print_status "Installing system dependencies..."
    
    if [[ "$MACHINE" == "Linux" ]]; then
        # Check for package manager
        if command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv nodejs npm mongodb texlive-xetex texlive-latex-extra
        elif command_exists yum; then
            sudo yum install -y python3 python3-pip nodejs npm mongodb-server texlive-xetex
        elif command_exists pacman; then
            sudo pacman -S python python-pip nodejs npm mongodb texlive-core texlive-latexextra
        else
            print_error "No supported package manager found. Please install manually:"
            print_error "- Python 3.8+"
            print_error "- Node.js 16+"
            print_error "- MongoDB"
            print_error "- LaTeX (texlive-xetex)"
            exit 1
        fi
    elif [[ "$MACHINE" == "Mac" ]]; then
        if command_exists brew; then
            brew install python3 node mongodb/brew/mongodb-community mactex
        else
            print_error "Homebrew not found. Please install it first: https://brew.sh/"
            exit 1
        fi
    else
        print_warning "Unsupported OS. Please install dependencies manually."
    fi
}

# Check and install Python
check_python() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        print_success "Python found: $(python3 --version)"
    else
        print_error "Python 3 not found. Installing..."
        install_system_deps
    fi
}

# Check and install Node.js
check_node() {
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_success "Node.js found: $NODE_VERSION"
    else
        print_error "Node.js not found. Installing..."
        install_system_deps
    fi
}

# Check and install MongoDB
check_mongodb() {
    if command_exists mongod || command_exists mongo; then
        print_success "MongoDB found"
    else
        print_warning "MongoDB not found. Installing..."
        install_system_deps
    fi
}

# Start MongoDB
start_mongodb() {
    print_status "Starting MongoDB..."
    
    if [[ "$MACHINE" == "Linux" ]]; then
        if command_exists systemctl; then
            sudo systemctl start mongod
            sudo systemctl enable mongod
        else
            sudo service mongod start
        fi
    elif [[ "$MACHINE" == "Mac" ]]; then
        brew services start mongodb/brew/mongodb-community
    fi
    
    # Wait for MongoDB to start
    sleep 3
    print_success "MongoDB started"
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_status "Creating backend .env file..."
        cat > .env << EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=latex_tracker
EOF
        print_success "Backend .env file created"
    fi
    
    cd ..
    print_success "Backend setup complete"
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    npm install
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_status "Creating frontend .env file..."
        cat > .env << EOF
REACT_APP_BACKEND_URL=http://localhost:8000
EOF
        print_success "Frontend .env file created"
    fi
    
    cd ..
    print_success "Frontend setup complete"
}

# Create startup scripts
create_startup_scripts() {
    print_status "Creating startup scripts..."
    
    # Create start script
    cat > start.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting LaTeX Tracker..."

# Start MongoDB if not running
if ! pgrep -x "mongod" > /dev/null; then
    echo "Starting MongoDB..."
    if [[ "$(uname -s)" == "Linux" ]]; then
        sudo systemctl start mongod
    elif [[ "$(uname -s)" == "Darwin" ]]; then
        brew services start mongodb/brew/mongodb-community
    fi
    sleep 3
fi

# Start backend in background
echo "Starting backend server..."
cd backend
source venv/bin/activate
uvicorn server:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend
echo "Starting frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ LaTeX Tracker is starting up!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
trap 'echo "Stopping services..."; kill $BACKEND_PID $FRONTEND_PID; exit' INT
wait
EOF

    chmod +x start.sh
    
    # Create stop script
    cat > stop.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping LaTeX Tracker..."

# Kill backend processes
pkill -f "uvicorn server:app"

# Kill frontend processes
pkill -f "npm start"

echo "✅ All services stopped"
EOF

    chmod +x stop.sh
    
    print_success "Startup scripts created"
}

# Main installation process
main() {
    print_status "LaTeX Tracker One-Click Installer"
    print_status "================================="
    
    # Check if we're in the right directory
    if [ ! -f "backend/server.py" ] || [ ! -f "frontend/package.json" ]; then
        print_error "Please run this script from the LaTeX_Tracker root directory"
        exit 1
    fi
    
    # Check dependencies
    check_python
    check_node
    check_mongodb
    
    # Start MongoDB
    start_mongodb
    
    # Setup backend and frontend
    setup_backend
    setup_frontend
    
    # Create startup scripts
    create_startup_scripts
    
    print_success "🎉 Installation complete!"
    print_status ""
    print_status "To start the application:"
    print_status "  ./start.sh"
    print_status ""
    print_status "To stop the application:"
    print_status "  ./stop.sh"
    print_status ""
    print_status "The application will be available at:"
    print_status "  Frontend: http://localhost:3000"
    print_status "  Backend API: http://localhost:8000"
    print_status "  API Documentation: http://localhost:8000/docs"
}

# Run main function
main "$@"
