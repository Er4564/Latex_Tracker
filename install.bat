#!/bin/bash

# LaTeX Tracker - Linux One-Click Installation Script

echo "🚀 Starting LaTeX Tracker Installation for Linux..."

# Check if we're in the right directory
if [[ ! -f "backend/server.py" ]]; then
    echo "❌ ERROR: Please run this script from the LaTeX_Tracker root directory"
    read -p "Press Enter to exit..."
    exit 1
fi

if [[ ! -f "frontend/package.json" ]]; then
    echo "❌ ERROR: Please run this script from the LaTeX_Tracker root directory"
    read -p "Press Enter to exit..."
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+ from https://python.org"
    read -p "Press Enter to exit..."
    exit 1
else
    echo "✅ Python found"
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+ from https://nodejs.org"
    read -p "Press Enter to exit..."
    exit 1
else
    echo "✅ Node.js found"
fi

# Check for MongoDB (optional - will use cloud MongoDB if not found)
if ! command -v mongod &> /dev/null; then
    echo "⚠️  MongoDB not found locally. You can:"
    echo "    1. Install MongoDB Community Server from https://mongodb.com"
    echo "    2. Use MongoDB Atlas (cloud) - update MONGO_URL in backend/.env"
fi

echo
echo "📦 Setting up backend..."
cd backend || exit

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
python3 -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [[ ! -f ".env" ]]; then
    echo "📝 Creating backend .env file..."
    echo "MONGO_URL=mongodb://localhost:27017" > .env
    echo "DB_NAME=latex_tracker" >> .env
    echo "✅ Backend .env file created"
fi

cd ..

echo
echo "🎨 Setting up frontend..."
cd frontend || exit

# Install dependencies
npm install

# Create .env file if it doesn't exist
if [[ ! -f ".env" ]]; then
    echo "📝 Creating frontend .env file..."
    echo "REACT_APP_BACKEND_URL=http://localhost:8000" > .env
    echo "✅ Frontend .env file created"
fi

cd ..

echo
echo "🔧 Creating startup scripts..."

# Create Linux start script
cat <<EOL > start.sh
#!/bin/bash
echo "🚀 Starting LaTeX Tracker..."

echo
echo "Starting backend server..."
cd backend
source venv/bin/activate
nohup uvicorn server:app --reload --host 0.0.0.0 --port 8000 &> backend.log &
cd ..

echo
echo "Starting frontend..."
cd frontend
nohup npm start &> frontend.log &
cd ..

echo
echo "✅ LaTeX Tracker is starting up!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
EOL
chmod +x start.sh

# Create Linux stop script
cat <<EOL > stop.sh
#!/bin/bash
echo "🛑 Stopping LaTeX Tracker..."
pkill -f "uvicorn server:app"
pkill -f "npm start"
echo "✅ All services stopped"
EOL
chmod +x stop.sh

echo
echo "🎉 Installation complete!"
echo
echo "To start the application:"
echo "  Run: ./start.sh"
echo
echo "To stop the application:"
echo "  Run: ./stop.sh"
echo
echo "The application will be available at:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Documentation: http://localhost:8000/docs"
echo
read -p "Press Enter to exit..."
