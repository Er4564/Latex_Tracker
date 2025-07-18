@echo off
REM LaTeX Tracker - Windows One-Click Installation Script

echo 🚀 Starting LaTeX Tracker Installation for Windows...

REM Check if we're in the right directory
if not exist "backend\server.py" (
    echo ❌ ERROR: Please run this script from the LaTeX_Tracker root directory
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo ❌ ERROR: Please run this script from the LaTeX_Tracker root directory
    pause
    exit /b 1
)

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
) else (
    echo ✅ Python found
)

REM Check for Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found. Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
) else (
    echo ✅ Node.js found
)

REM Check for MongoDB (optional - will use cloud MongoDB if not found)
mongod --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  MongoDB not found locally. You can:
    echo    1. Install MongoDB Community Server from https://mongodb.com
    echo    2. Use MongoDB Atlas (cloud) - update MONGO_URL in backend\.env
)

echo.
echo 📦 Setting up backend...
cd backend

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating backend .env file...
    echo MONGO_URL=mongodb://localhost:27017> .env
    echo DB_NAME=latex_tracker>> .env
    echo ✅ Backend .env file created
)

cd ..

echo.
echo 🎨 Setting up frontend...
cd frontend

REM Install dependencies
npm install

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating frontend .env file...
    echo REACT_APP_BACKEND_URL=http://localhost:8000> .env
    echo ✅ Frontend .env file created
)

cd ..

echo.
echo 🔧 Creating startup scripts...

REM Create Windows start script
echo @echo off> start.bat
echo echo 🚀 Starting LaTeX Tracker...>> start.bat
echo.>> start.bat
echo echo Starting backend server...>> start.bat
echo cd backend>> start.bat
echo call venv\Scripts\activate.bat>> start.bat
echo start /B uvicorn server:app --reload --host 0.0.0.0 --port 8000>> start.bat
echo cd ..>> start.bat
echo.>> start.bat
echo timeout /t 5 /nobreak ^> nul>> start.bat
echo.>> start.bat
echo echo Starting frontend...>> start.bat
echo cd frontend>> start.bat
echo start npm start>> start.bat
echo cd ..>> start.bat
echo.>> start.bat
echo echo ✅ LaTeX Tracker is starting up!>> start.bat
echo echo 📱 Frontend: http://localhost:3000>> start.bat
echo echo 🔧 Backend API: http://localhost:8000>> start.bat
echo echo 📚 API Docs: http://localhost:8000/docs>> start.bat
echo echo.>> start.bat
echo echo Press any key to close this window...>> start.bat
echo pause>> start.bat

REM Create Windows stop script
echo @echo off> stop.bat
echo echo 🛑 Stopping LaTeX Tracker...>> stop.bat
echo taskkill /F /IM "uvicorn.exe" 2^>nul>> stop.bat
echo taskkill /F /IM "node.exe" 2^>nul>> stop.bat
echo echo ✅ All services stopped>> stop.bat
echo pause>> stop.bat

echo.
echo 🎉 Installation complete!
echo.
echo To start the application:
echo   Double-click start.bat or run: start.bat
echo.
echo To stop the application:
echo   Double-click stop.bat or run: stop.bat
echo.
echo The application will be available at:
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8000
echo   API Documentation: http://localhost:8000/docs
echo.
pause
