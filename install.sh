#!/bin/bash

# LaTeX Tracker - Linux Multi-Distribution Optimized Installation Script
set -e

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting LaTeX Tracker Installation for Linux...${NC}"

# Detect Linux distribution
detect_linux_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        DISTRO_VERSION=$VERSION_ID
        echo -e "${CYAN}📋 Detected: $PRETTY_NAME${NC}"
    else
        DISTRO="unknown"
        echo -e "${YELLOW}⚠️  Unknown distribution, assuming Ubuntu/Debian${NC}"
    fi
}

# System resource check
check_system_resources() {
    echo -e "${BLUE}🔍 Checking system resources...${NC}"
    
    # Check available memory
    TOTAL_MEM=$(free -m | awk 'NR==2{print $2}')
    FREE_MEM=$(free -m | awk 'NR==2{print $7}')
    FREE_MEM_PERCENT=$(echo "scale=1; $FREE_MEM * 100 / $TOTAL_MEM" | bc -l 2>/dev/null || echo "0")
    
    echo -e "${CYAN}💾 Memory: ${FREE_MEM}MB free of ${TOTAL_MEM}MB (${FREE_MEM_PERCENT}%)${NC}"
    
    if (( $(echo "$FREE_MEM < 500" | bc -l 2>/dev/null || echo "1") )); then
        echo -e "${YELLOW}⚠️  Warning: Low memory available. Consider closing other applications.${NC}"
    fi
    
    # Check disk space
    DISK_USAGE=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
    DISK_AVAIL=$(df -h . | tail -1 | awk '{print $4}')
    
    echo -e "${CYAN}💿 Disk: ${DISK_AVAIL} available (${DISK_USAGE}% used)${NC}"
    
    if [ "$DISK_USAGE" -gt 90 ]; then
        echo -e "${RED}❌ Error: Not enough disk space (${DISK_USAGE}% used)${NC}"
        exit 1
    fi
    
    # Check CPU cores
    CPU_CORES=$(nproc)
    echo -e "${CYAN}🔧 CPU: ${CPU_CORES} cores available${NC}"
}

# Enhanced dependency installation
install_dependencies_by_distro() {
    echo -e "${BLUE}📦 Installing dependencies for $DISTRO...${NC}"
    
    case $DISTRO in
        ubuntu|debian|pop|mint)
            echo -e "${CYAN}🔄 Updating package list...${NC}"
            sudo apt-get update -qq
            
            echo -e "${CYAN}📋 Installing system packages...${NC}"
            sudo apt-get install -y \
                curl \
                wget \
                git \
                build-essential \
                software-properties-common \
                apt-transport-https \
                ca-certificates \
                gnupg \
                lsb-release \
                bc
            
            # Install Node.js
            if ! command -v node &> /dev/null; then
                echo -e "${CYAN}📦 Installing Node.js...${NC}"
                curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
                sudo apt-get install -y nodejs
            fi
            
            # Install Python
            if ! command -v python3 &> /dev/null; then
                echo -e "${CYAN}🐍 Installing Python...${NC}"
                sudo apt-get install -y python3 python3-pip python3-venv python3-dev
            fi
            
            # Install MongoDB
            if ! command -v mongod &> /dev/null; then
                echo -e "${CYAN}🍃 Installing MongoDB...${NC}"
                wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
                echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
                sudo apt-get update -qq
                sudo apt-get install -y mongodb-org
            fi
            
            # Install LaTeX
            echo -e "${CYAN}📄 Installing LaTeX (XeTeX)...${NC}"
            sudo apt-get install -y texlive-xetex texlive-fonts-recommended texlive-fonts-extra
            ;;
            
        fedora|centos|rhel|rocky|almalinux)
            echo -e "${CYAN}🔄 Updating package list...${NC}"
            sudo dnf update -y -q
            
            echo -e "${CYAN}📋 Installing system packages...${NC}"
            sudo dnf install -y \
                curl \
                wget \
                git \
                gcc \
                gcc-c++ \
                make \
                bc
            
            # Install Node.js
            if ! command -v node &> /dev/null; then
                echo -e "${CYAN}📦 Installing Node.js...${NC}"
                sudo dnf install -y nodejs npm
            fi
            
            # Install Python
            if ! command -v python3 &> /dev/null; then
                echo -e "${CYAN}🐍 Installing Python...${NC}"
                sudo dnf install -y python3 python3-pip python3-devel
            fi
            
            # Install MongoDB
            if ! command -v mongod &> /dev/null; then
                echo -e "${CYAN}🍃 Installing MongoDB...${NC}"
                sudo tee /etc/yum.repos.d/mongodb-org-6.0.repo > /dev/null <<EOF
[mongodb-org-6.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/8/mongodb-org/6.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-6.0.asc
EOF
                sudo dnf install -y mongodb-org
            fi
            
            # Install LaTeX
            echo -e "${CYAN}📄 Installing LaTeX (XeTeX)...${NC}"
            sudo dnf install -y texlive-xetex texlive-collection-fontsrecommended
            ;;
            
        arch|manjaro)
            echo -e "${CYAN}🔄 Updating package list...${NC}"
            sudo pacman -Sy --noconfirm
            
            echo -e "${CYAN}📋 Installing system packages...${NC}"
            sudo pacman -S --noconfirm \
                curl \
                wget \
                git \
                base-devel \
                bc
            
            # Install Node.js
            if ! command -v node &> /dev/null; then
                echo -e "${CYAN}📦 Installing Node.js...${NC}"
                sudo pacman -S --noconfirm nodejs npm
            fi
            
            # Install Python
            if ! command -v python3 &> /dev/null; then
                echo -e "${CYAN}🐍 Installing Python...${NC}"
                sudo pacman -S --noconfirm python python-pip
            fi
            
            # Install MongoDB
            if ! command -v mongod &> /dev/null; then
                echo -e "${CYAN}🍃 Installing MongoDB...${NC}"
                sudo pacman -S --noconfirm mongodb-bin
            fi
            
            # Install LaTeX
            echo -e "${CYAN}📄 Installing LaTeX (XeTeX)...${NC}"
            sudo pacman -S --noconfirm texlive-bin texlive-fontsrecommended
            ;;
            
        opensuse*|sles)
            echo -e "${CYAN}🔄 Updating package list...${NC}"
            sudo zypper refresh
            
            echo -e "${CYAN}📋 Installing system packages...${NC}"
            sudo zypper install -y \
                curl \
                wget \
                git \
                gcc \
                gcc-c++ \
                make \
                bc
            
            # Install Node.js
            if ! command -v node &> /dev/null; then
                echo -e "${CYAN}📦 Installing Node.js...${NC}"
                sudo zypper install -y nodejs18 npm18
            fi
            
            # Install Python
            if ! command -v python3 &> /dev/null; then
                echo -e "${CYAN}🐍 Installing Python...${NC}"
                sudo zypper install -y python3 python3-pip python3-devel
            fi
            
            # Install LaTeX
            echo -e "${CYAN}📄 Installing LaTeX (XeTeX)...${NC}"
            sudo zypper install -y texlive-xetex
            ;;
            
        *)
            echo -e "${YELLOW}⚠️  Unsupported distribution: $DISTRO${NC}"
            echo -e "${YELLOW}Please install the following manually:${NC}"
            echo "  - Node.js 16+"
            echo "  - Python 3.8+"
            echo "  - MongoDB"
            echo "  - XeTeX (texlive-xetex)"
            read -p "Press Enter to continue assuming dependencies are installed..."
            ;;
    esac
}

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

# MongoDB optimization for Linux
optimize_mongodb_linux() {
    print_status "Optimizing MongoDB configuration for development..."
    
    # Create optimized MongoDB config
    sudo mkdir -p /etc/mongodb
    sudo tee /etc/mongodb/mongod-latex-tracker.conf > /dev/null <<EOF
# MongoDB Configuration for LaTeX Tracker
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true
  wiredTiger:
    engineConfig:
      cacheSizeGB: 1
      
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log
  logRotate: reopen

net:
  port: 27017
  bindIp: 127.0.0.1

processManagement:
  fork: true
  pidFilePath: /var/run/mongodb/mongod.pid
  timeZoneInfo: /usr/share/zoneinfo

# Performance optimizations for development
operationProfiling:
  mode: off
  
setParameter:
  enableLocalhostAuthBypass: true
EOF

    print_success "MongoDB configuration optimized for local development"
}

# Create systemd services for production deployment
create_systemd_services() {
    print_status "Creating systemd services..."
    
    CURRENT_USER=$(whoami)
    CURRENT_DIR=$(pwd)
    
    # Backend service
    sudo tee /etc/systemd/system/latex-tracker-backend.service > /dev/null <<EOF
[Unit]
Description=LaTeX Tracker Backend API
Documentation=https://github.com/Er4564/Latex_Tracker
After=network.target mongodb.service
Wants=mongodb.service

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR/backend
Environment=PATH=$CURRENT_DIR/backend/venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=$CURRENT_DIR/backend
Environment=PYTHONUNBUFFERED=1
ExecStart=$CURRENT_DIR/backend/venv/bin/uvicorn server:app --host 127.0.0.1 --port 8000 --workers 1
ExecReload=/bin/kill -HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

    # Frontend service (for production builds)
    sudo tee /etc/systemd/system/latex-tracker-frontend.service > /dev/null <<EOF
[Unit]
Description=LaTeX Tracker Frontend
Documentation=https://github.com/Er4564/Latex_Tracker
After=network.target latex-tracker-backend.service
Wants=latex-tracker-backend.service

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR/frontend
Environment=NODE_ENV=production
Environment=PATH=/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/bin/npx serve -s build -l 3000
ExecReload=/bin/kill -HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable services
    sudo systemctl daemon-reload
    
    print_success "Systemd services created"
    print_status "Services can be managed with:"
    echo "  sudo systemctl start latex-tracker-backend"
    echo "  sudo systemctl start latex-tracker-frontend"
    echo "  sudo systemctl enable latex-tracker-backend latex-tracker-frontend"
}

# Create Linux-optimized environment files
create_linux_env() {
    print_status "Creating Linux-optimized environment files..."
    
    # Create necessary directories
    sudo mkdir -p /tmp/latex_tracker/{uploads,compile}
    sudo chmod 755 /tmp/latex_tracker
    sudo chmod 777 /tmp/latex_tracker/{uploads,compile}
    
    # Backend .env with Linux paths
    cat > backend/.env << EOF
# LaTeX Tracker Backend Configuration
MONGO_URL=mongodb://localhost:27017
DB_NAME=latex_tracker
LOG_LEVEL=INFO
UPLOAD_DIR=/tmp/latex_tracker/uploads
COMPILE_DIR=/tmp/latex_tracker/compile
MAX_FILE_SIZE=10485760
LATEX_TIMEOUT=30
ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
DEBUG=true
EOF

    # Frontend .env
    cat > frontend/.env << EOF
# LaTeX Tracker Frontend Configuration
REACT_APP_BACKEND_URL=http://localhost:8000
REACT_APP_MAX_FILE_SIZE=10485760
DISABLE_HOT_RELOAD=false
GENERATE_SOURCEMAP=true
FAST_REFRESH=true
EOF

    print_success "Environment files created with Linux optimizations"
}

# Initialize
detect_linux_distro
check_system_resources
install_dependencies_by_distro

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
    print_status "Creating Linux-optimized startup scripts with enhanced monitoring..."
    
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
    print_status "LaTeX Tracker Linux Multi-Distribution Installation"
    print_status "================================================="
    
    # Check if we're in the right directory
    if [ ! -f "backend/server.py" ] || [ ! -f "frontend/package.json" ]; then
        print_error "Please run this script from the LaTeX_Tracker root directory"
        exit 1
    fi
    
    # Check and install dependencies (already done during init)
    print_success "Dependencies checked and installed"
    
    # Optimize MongoDB for Linux
    optimize_mongodb_linux
    
    # Create Linux-optimized environment files
    create_linux_env
    
    # Start MongoDB
    start_mongodb
    
    # Setup backend and frontend
    setup_backend
    setup_frontend
    
    # Create systemd services for production use
    if [ "$1" = "--production" ]; then
        create_systemd_services
        print_status "Production services created. Use 'sudo systemctl start latex-tracker-backend latex-tracker-frontend' to start in production mode."
    fi
    
    # Create startup scripts for development
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
