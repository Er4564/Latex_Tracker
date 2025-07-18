# LaTeX File Tracker

A comprehensive web application for organizing and managing LaTeX files from Overleaf projects. Track your academic documents with multi-level organization, version history, compilation status, and powerful search capabilities.

## 🚀 Features

### Core Functionality
- **Multi-level Organization**: Organize files by Term/Semester → Subject → Files
- **File Management**: Upload, create, edit, and preview LaTeX files
- **Version History**: Track changes with automatic versioning
- **LaTeX Compilation**: Automatic PDF compilation with status tracking
- **Search & Filter**: Advanced search across content, tags, and metadata
- **Export Options**: Download individual files or bulk export
- **Dashboard Analytics**: View statistics and recent activity

### File Input Methods
- **Manual Upload**: Upload existing .tex files
- **Copy & Paste**: Directly paste LaTeX content
- **Git Integration**: (Coming Soon) Sync with Overleaf via Git

### File Tracking
- Word count and file size tracking
- Last modified dates
- Compilation status (Success/Error/Unknown)
- Custom tags and notes
- Source type tracking

## 🏗️ Project Structure

```
Latex_Tracker/
├── backend/                 # FastAPI backend server
│   ├── server.py           # Main API server with all endpoints
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   ├── App.css        # Styling with Tailwind CSS
│   │   ├── index.js       # React entry point
│   │   └── index.css      # Global styles
│   ├── public/
│   │   └── index.html     # HTML template
│   ├── package.json       # Node.js dependencies
│   ├── tailwind.config.js # Tailwind CSS configuration
│   └── craco.config.js    # Create React App configuration
├── tests/                  # Test files and utilities
└── README.md              # This file
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

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB database
- LaTeX distribution (for compilation features)

### Backend Setup

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

### Frontend Setup

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

### Terms Management
- `GET /api/terms` - List all terms
- `POST /api/terms` - Create new term
- `PUT /api/terms/{id}` - Update term
- `DELETE /api/terms/{id}` - Delete term

### Subjects Management
- `GET /api/subjects` - List all subjects
- `POST /api/subjects` - Create new subject
- `PUT /api/subjects/{id}` - Update subject
- `DELETE /api/subjects/{id}` - Delete subject

### Files Management
- `GET /api/files` - List all files
- `POST /api/files` - Create new file
- `PUT /api/files/{id}` - Update file
- `DELETE /api/files/{id}` - Delete file
- `POST /api/files/upload` - Upload .tex file
- `POST /api/files/{id}/compile` - Compile LaTeX to PDF
- `GET /api/files/{id}/pdf` - Download compiled PDF

### Search & Export
- `POST /api/search` - Search files with filters
- `GET /api/files/{id}/export` - Export single file
- `POST /api/export/bulk` - Bulk export files

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics

## 💾 Database Schema

### Collections

#### Terms
```javascript
{
  "id": "uuid",
  "name": "Fall 2024",
  "description": "Fall semester 2024",
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
  "term_id": "term_uuid",
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
  "term_id": "term_uuid",
  "content": "\\documentclass{article}...",
  "word_count": 150,
  "file_size": 1024,
  "compilation_status": "success",
  "compilation_output": "...",
  "tags": ["homework", "calculus"],
  "notes": "First assignment",
  "source_type": "manual",
  "versions": [...],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## 🖥️ User Interface

### Dashboard
- Overview statistics (terms, subjects, files, compilation status)
- Recent files list
- Quick access to main functions

### Files View
- Grid layout with file cards
- Search and filter capabilities
- File preview and editing
- Bulk operations

### Management View
- Terms and subjects organization
- Create, edit, and delete operations
- Color-coded subject organization

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
