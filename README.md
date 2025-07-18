# LaTeX File Tracker

A comprehensive web application for organizing and managing LaTeX files from Overleaf projects. Track your academic documents with hierarchical organization (Year → Semester → Subject → Files), version history, compilation status, and powerful search capabilities.

## 🚀 Features

### Core Functionality
- **Hierarchical Organization**: Organize files by Year → Semester → Subject → Files
- **Multiple File Upload**: Upload single files or multiple files at once
- **File Management**: Upload, create, edit, and preview LaTeX files
- **Version History**: Track changes with automatic versioning
- **LaTeX Compilation**: Automatic PDF compilation with status tracking
- **Search & Filter**: Advanced search across content, tags, and metadata
- **Export Options**: Download individual files or bulk export
- **Dashboard Analytics**: View statistics and recent activity

### File Input Methods
- **Manual Upload**: Upload single or multiple .tex files
- **Copy & Paste**: Directly paste LaTeX content
- **Multi-File Selection**: Select and upload multiple files simultaneously
- **Git Integration**: (Coming Soon) Sync with Overleaf via Git

### Academic Organization
- **Year Management**: Create and manage academic years (2024, 2025, etc.)
- **Semester System**: Fall, Spring, Summer, Winter semesters per year
- **Subject Organization**: Color-coded subjects within each semester
- **File Tracking**: Word count, file size, compilation status, tags, and notes

### Installation Options
- **One-Click Installation**: Automated setup scripts for Linux/Mac/Windows
- **Docker Support**: Container-based deployment
- **Manual Setup**: Traditional installation method
- **Linux Optimized**: Multi-distribution support with systemd integration

## 🐧 Linux Optimization

LaTeX Tracker is fully optimized for Linux environments with comprehensive distribution support:

### Supported Linux Distributions
- **Ubuntu/Debian** - Full automatic installation
- **Fedora/CentOS/RHEL** - DNF package manager support
- **Arch/Manjaro** - Pacman package manager support
- **openSUSE/SLES** - Zypper package manager support
- **Generic Linux** - Manual dependency instructions

### Linux-Specific Features
- **Multi-Distribution Setup**: Automatic detection and package installation
- **Systemd Integration**: Production-ready service files
- **Resource Monitoring**: Memory, CPU, and disk usage tracking
- **Enhanced File Watching**: Optimized for Linux file systems
- **MongoDB Optimization**: Custom configuration for development
- **Process Management**: PID-based service tracking
- **Comprehensive Logging**: Structured logs in `logs/` directory

### Linux Installation
```bash
# Clone and install (Ubuntu/Debian/Fedora/Arch/openSUSE)
git clone https://github.com/Er4564/Latex_Tracker.git
cd Latex_Tracker
chmod +x install.sh
./install.sh

# For production deployment with systemd services
./install.sh --production
```

### Linux System Requirements
- **Memory**: 1GB RAM minimum, 2GB recommended
- **Storage**: 2GB free space minimum
- **Dependencies**: Auto-installed (Node.js 16+, Python 3.8+, MongoDB, XeTeX)
- **Permissions**: sudo access for package installation

## 🏗️ Project Structure

```
Latex_Tracker/
├── install.sh              # Linux/Mac one-click installer
├── install.bat             # Windows one-click installer
├── start.sh                # Quick start script (auto-generated)
├── stop.sh                 # Stop services script (auto-generated)
├── docker-compose.yml      # Docker container setup
├── backend/                # FastAPI backend server
│   ├── server.py          # Main API server with all endpoints
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile         # Docker configuration
├── frontend/              # React frontend application
│   ├── src/
│   │   ├── App.js        # Main React component with new structure
│   │   ├── App.css       # Styling with Tailwind CSS
│   │   ├── index.js      # React entry point
│   │   └── index.css     # Global styles
│   ├── public/
│   │   └── index.html    # HTML template
│   ├── package.json      # Node.js dependencies
│   ├── tailwind.config.js # Tailwind CSS configuration
│   ├── craco.config.js   # Create React App configuration
│   └── Dockerfile        # Docker configuration
├── tests/                 # Test files and utilities
└── README.md             # This file
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **MongoDB**: Document database with Motor async driver
- **Pydantic**: Data validation and serialization
- **LaTeX Compilation**: XeLaTeX for PDF generation
- **Python Libraries**: 
  - `pymongo` for database operations
  - `python-dotenv` for environment management
  - `boto3` for potential cloud storage

### Frontend
- **React 19**: Modern React with hooks
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API communication
- **React Router**: Client-side routing

### Development Tools
- **CRACO**: Customize Create React App
- **PostCSS**: CSS processing
- **ESLint & Prettier**: Code formatting and linting

## 📦 Installation & Setup

### 🚀 One-Click Installation (Recommended)

#### Linux/Mac
```bash
# Make the script executable and run
chmod +x install.sh
./install.sh
```

#### Windows
```batch
# Double-click install.bat or run in Command Prompt
install.bat
```

#### Docker (Cross-platform)
```bash
# Clone the repository and run with Docker
git clone <repository-url>
cd Latex_Tracker
docker-compose up -d
```

### Manual Installation

#### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB database
- LaTeX distribution (for compilation features)

#### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment file:
```bash
cp .env.example .env
# Edit .env with your MongoDB connection string and database name
```

5. Start the backend server:
```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
# Create .env file in frontend directory
echo "REACT_APP_BACKEND_URL=http://localhost:8000" > .env
```

4. Start the development server:
```bash
npm start
```

### 🎯 Quick Start (After Installation)

#### Using Generated Scripts
```bash
# Start all services
./start.sh

# Stop all services  
./stop.sh
```

#### Direct Commands
```bash
# Start backend (in backend/ directory)
source venv/bin/activate && uvicorn server:app --reload

# Start frontend (in frontend/ directory)
npm start
```

The application will be available at `http://localhost:3000`

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=latex_tracker
```

#### Frontend (.env)
```env
REACT_APP_BACKEND_URL=http://localhost:8000
```

## 📊 API Endpoints

### Academic Year Management
- `GET /api/years` - List all academic years
- `POST /api/years` - Create new academic year
- `PUT /api/years/{id}` - Update academic year
- `DELETE /api/years/{id}` - Delete academic year

### Semester Management
- `GET /api/semesters` - List all semesters (with optional year filter)
- `POST /api/semesters` - Create new semester
- `PUT /api/semesters/{id}` - Update semester
- `DELETE /api/semesters/{id}` - Delete semester

### Subject Management
- `GET /api/subjects` - List all subjects (with optional semester filter)
- `POST /api/subjects` - Create new subject
- `PUT /api/subjects/{id}` - Update subject
- `DELETE /api/subjects/{id}` - Delete subject

### File Management
- `GET /api/files` - List all files (with optional filters)
- `POST /api/files` - Create new file
- `POST /api/files/multi-upload` - Upload multiple files at once
- `PUT /api/files/{id}` - Update file
- `DELETE /api/files/{id}` - Delete file
- `POST /api/files/upload` - Upload .tex file
- `POST /api/files/{id}/compile` - Compile LaTeX to PDF
- `GET /api/files/{id}/pdf` - Download compiled PDF

### Search & Export
- `POST /api/search` - Search files with filters
- `GET /api/files/{id}/export` - Export single file
- `POST /api/export/bulk` - Bulk export files

### Dashboard & Legacy
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/terms` - Legacy terms endpoint (backward compatibility)

## 💾 Database Schema

### Collections

#### Years
```javascript
{
  "id": "uuid",
  "year": 2024,
  "description": "Academic year 2024-2025",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Semesters
```javascript
{
  "id": "uuid",
  "year_id": "year_uuid",
  "name": "Fall",
  "description": "Fall semester",
  "start_date": "2024-09-01",
  "end_date": "2024-12-15",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Subjects
```javascript
{
  "id": "uuid",
  "name": "Advanced Calculus",
  "description": "Calculus III - Multivariable Calculus",
  "semester_id": "semester_uuid",
  "color": "#FF6B6B",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Files
```javascript
{
  "id": "uuid",
  "name": "homework_1.tex",
  "subject_id": "subject_uuid",
  "semester_id": "semester_uuid",
  "content": "\\documentclass{article}...",
  "word_count": 150,
  "file_size": 1024,
  "compilation_status": "success",
  "compilation_output": "...",
  "tags": ["homework", "calculus"],
  "notes": "First assignment",
  "source_type": "manual", // "manual", "git", "paste", "multi_upload"
  "versions": [...],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## 🖥️ User Interface

### Dashboard
- Overview statistics (years, semesters, subjects, files, compilation status)
- Recent files list
- Quick access to main functions

### Files View
- Grid layout with file cards showing compilation status
- Multi-level filtering (Year → Semester → Subject)
- Multiple file selection and upload
- File preview and editing with LaTeX syntax highlighting
- Bulk operations and export

### Management View
- **Years**: Create and manage academic years (2024, 2025, etc.)
- **Semesters**: Organize by Fall, Spring, Summer, Winter within each year
- **Subjects**: Color-coded subject organization within semesters
- Hierarchical view with drill-down navigation

### New Features
- **One-Click Setup**: Automated installation for all platforms
- **Multi-File Upload**: Select and upload multiple .tex files simultaneously
- **Academic Structure**: Clear Year → Semester → Subject → Files hierarchy
- **Enhanced Organization**: Better default organization matching academic calendar

## 🧪 Testing

The project includes comprehensive testing utilities:

- `backend_test.py` - Backend API testing
- `latex_test.py` - LaTeX compilation testing
- `final_test.py` - End-to-end testing
- `debug_test.py` - Debug utilities

Run tests:
```bash
# Backend tests
python backend_test.py

# LaTeX compilation tests
python latex_test.py
```

## 🚀 Deployment

### Production Build

#### Frontend
```bash
cd frontend
npm run build
```

#### Backend
```bash
cd backend
pip install gunicorn
gunicorn server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Docker Deployment (Optional)
Create Dockerfiles for both frontend and backend for containerized deployment.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if necessary
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Ensure MongoDB is running
   - Check connection string in .env file

2. **LaTeX Compilation Fails**
   - Install XeLaTeX: `sudo apt-get install texlive-xetex`
   - Check LaTeX syntax in uploaded files

3. **Frontend Can't Connect to Backend**
   - Verify backend is running on correct port
   - Check REACT_APP_BACKEND_URL in frontend .env

4. **CORS Issues**
   - Backend includes CORS middleware
   - Ensure frontend URL is properly configured

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the test files for examples
3. Create an issue in the repository

## 🎯 Future Enhancements

- [ ] Git integration for Overleaf sync
- [ ] Collaborative editing features
- [ ] Advanced LaTeX syntax highlighting
- [ ] Real-time compilation preview
- [ ] Mobile-responsive design improvements
- [ ] Advanced analytics and reporting
- [ ] User authentication and permissions
- [ ] Cloud storage integration
- [ ] Drag-and-drop file organization
- [ ] Calendar integration for semester dates
- [ ] Export to different formats (Word, PDF collections)
- [ ] Template management system

## 🆘 Quick Troubleshooting

### Installation Issues
1. **Script permissions (Linux/Mac)**: `chmod +x install.sh`
2. **Missing dependencies**: The installer will attempt to install them automatically
3. **MongoDB connection**: Use MongoDB Atlas if local installation fails

### Common Runtime Issues
1. **Backend won't start**: Check Python version (3.8+) and dependencies
2. **Frontend can't connect**: Verify REACT_APP_BACKEND_URL in frontend/.env
3. **LaTeX compilation fails**: Install texlive-xetex package
4. **File upload errors**: Check file permissions and disk space

### Quick Fixes
```bash
# Reset and restart
./stop.sh
./start.sh

# Check logs
# Backend: Check terminal output where uvicorn is running
# Frontend: Check browser console (F12)

# Reset database (if needed)
# Connect to MongoDB and drop the latex_tracker database
```
