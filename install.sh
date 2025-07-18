#!/bin/bash

# LaTeX Tracker - Ubuntu Optimized Installation Script
echo "🚀 Starting LaTeX Tracker Installation for Ubuntu..."

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

# Check if running on Ubuntu
if ! command_exists lsb_release || [[ "$(lsb_release -si)" != "Ubuntu" ]]; then
    print_warning "This script is optimized for Ubuntu. It may work on other Debian-based systems."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install system dependencies for Ubuntu
install_ubuntu_deps() {
    print_status "Installing system dependencies for Ubuntu..."
    
    # Update package list
    sudo apt-get update -y
    
    # Install essential packages
    sudo apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        nodejs \
        npm \
        mongodb \
        texlive-xetex \
        texlive-latex-extra \
        texlive-fonts-recommended \
        curl \
        wget \
        git
    
    # Install latest Node.js (version 18+) if needed
    NODE_VERSION=$(node --version 2>/dev/null | sed 's/v//' | cut -d. -f1)
    if [[ -z "$NODE_VERSION" ]] || [[ "$NODE_VERSION" -lt 16 ]]; then
        print_status "Installing Node.js 18..."
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi
    
    # Start and enable MongoDB
    sudo systemctl start mongod
    sudo systemctl enable mongod
    
    print_success "Ubuntu dependencies installed successfully"
}

# Check and install dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    local missing_deps=()
    
    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        print_success "Python found: $(python3 --version)"
    else
        missing_deps+=("python3")
    fi
    
    # Check Node.js
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_success "Node.js found: $NODE_VERSION"
    else
        missing_deps+=("nodejs")
    fi
    
    # Check MongoDB
    if command_exists mongod; then
        print_success "MongoDB found"
    else
        missing_deps+=("mongodb")
    fi
    
    # Install missing dependencies
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        print_status "Installing missing dependencies: ${missing_deps[*]}"
        install_ubuntu_deps
    fi
}

# Start MongoDB
start_mongodb() {
    print_status "Starting MongoDB..."
    
    if ! pgrep -x "mongod" > /dev/null; then
        sudo systemctl start mongod
        sleep 3
        
        if pgrep -x "mongod" > /dev/null; then
            print_success "MongoDB started successfully"
        else
            print_error "Failed to start MongoDB"
            print_status "You can use MongoDB Atlas (cloud) instead"
            print_status "Update MONGO_URL in backend/.env to use cloud MongoDB"
        fi
    else
        print_success "MongoDB already running"
    fi
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
    
    # Clear npm cache
    npm cache clean --force
    
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

# Create startup scripts optimized for Ubuntu
create_startup_scripts() {
    print_status "Creating Ubuntu-optimized startup scripts..."
    
    # Create start script
    cat > start.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting LaTeX Tracker..."

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo "Starting MongoDB..."
    sudo systemctl start mongod
    sleep 3
fi

# Start backend in background
echo "Starting backend server..."
cd backend
source venv/bin/activate
nohup uvicorn server:app --reload --host 127.0.0.1 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid
cd ..

# Wait for backend to start
sleep 5

# Check if backend started successfully
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ Backend started successfully (PID: $BACKEND_PID)"
else
    echo "❌ Backend failed to start. Check backend.log for details."
    exit 1
fi

# Start frontend
echo "Starting frontend..."
cd frontend
nohup npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
cd ..

# Wait for frontend to start
sleep 10

echo "✅ LaTeX Tracker is running!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "📋 Logs: backend.log and frontend.log"
echo ""
echo "To stop the application, run: ./stop.sh"
EOF

    chmod +x start.sh
    
    # Create stop script
    cat > stop.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping LaTeX Tracker..."

# Stop backend
if [ -f backend.pid ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        kill $BACKEND_PID
        echo "Backend stopped (PID: $BACKEND_PID)"
    fi
    rm -f backend.pid
fi

# Stop frontend
if [ -f frontend.pid ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        kill $FRONTEND_PID
        echo "Frontend stopped (PID: $FRONTEND_PID)"
    fi
    rm -f frontend.pid
fi

# Fallback: kill any remaining processes
pkill -f "uvicorn server:app" 2>/dev/null
pkill -f "npm start" 2>/dev/null

echo "✅ All services stopped"
EOF

    chmod +x stop.sh
    
    # Create status script
    cat > status.sh << 'EOF'
#!/bin/bash

echo "� LaTeX Tracker Status"
echo "======================="

# Check MongoDB
if pgrep -x "mongod" > /dev/null; then
    echo "✅ MongoDB: Running"
else
    echo "❌ MongoDB: Stopped"
fi

# Check backend
if [ -f backend.pid ] && ps -p $(cat backend.pid) > /dev/null; then
    echo "✅ Backend: Running (PID: $(cat backend.pid))"
    echo "   URL: http://localhost:8000"
else
    echo "❌ Backend: Stopped"
fi

# Check frontend
if [ -f frontend.pid ] && ps -p $(cat frontend.pid) > /dev/null; then
    echo "✅ Frontend: Running (PID: $(cat frontend.pid))"
    echo "   URL: http://localhost:3000"
else
    echo "❌ Frontend: Stopped"
fi

echo ""
echo "Recent logs:"
echo "Backend: tail backend.log"
echo "Frontend: tail frontend.log"
EOF

    chmod +x status.sh
    
    print_success "Ubuntu-optimized scripts created"
}

# Main installation process
main() {
    print_status "LaTeX Tracker Ubuntu Installation"
    print_status "================================="
    
    # Check if we're in the right directory
    if [ ! -f "backend/server.py" ] || [ ! -f "frontend/package.json" ]; then
        print_error "Please run this script from the LaTeX_Tracker root directory"
        exit 1
    fi
    
    # Check and install dependencies
    check_dependencies
    
    # Start MongoDB
    start_mongodb
    
    # Setup backend and frontend
    setup_backend
    setup_frontend
    
    # Create startup scripts
    create_startup_scripts
    
    print_success "🎉 Installation complete!"
    print_status ""
    print_status "Quick commands:"
    print_status "  Start:  ./start.sh"
    print_status "  Stop:   ./stop.sh"
    print_status "  Status: ./status.sh"
    print_status ""
    print_status "The application will be available at:"
    print_status "  Frontend: http://localhost:3000"
    print_status "  Backend API: http://localhost:8000"
    print_status "  API Documentation: http://localhost:8000/docs"
    print_status ""
    print_status "Logs are saved to backend.log and frontend.log"
}

# Run main function
main "$@"
