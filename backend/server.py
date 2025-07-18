from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import json
import re
import base64
import io
import zipfile
import tempfile
import shutil
import subprocess
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class Year(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    year: int  # e.g., 2024
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class YearCreate(BaseModel):
    year: int
    description: Optional[str] = None

class YearUpdate(BaseModel):
    year: Optional[int] = None
    description: Optional[str] = None

class Semester(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    year_id: str
    name: str  # "Fall", "Spring", "Summer", "Winter"
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SemesterCreate(BaseModel):
    year_id: str
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class SemesterUpdate(BaseModel):
    year_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

# Legacy Term model for backward compatibility (will be deprecated)
class Term(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TermCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class Subject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    semester_id: str
    color: Optional[str] = "#3B82F6"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SubjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    semester_id: str
    color: Optional[str] = "#3B82F6"

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    semester_id: Optional[str] = None
    color: Optional[str] = None

class FileVersion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    word_count: int
    file_size: int
    compilation_status: str = "unknown"  # "success", "error", "unknown"
    compilation_output: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TexFile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    subject_id: str
    semester_id: str
    content: str
    word_count: int
    file_size: int
    compilation_status: str = "unknown"
    compilation_output: Optional[str] = None
    tags: List[str] = []
    notes: Optional[str] = None
    source_type: str = "manual"  # "manual", "git", "paste", "multi_upload"
    git_url: Optional[str] = None
    git_branch: Optional[str] = None
    git_path: Optional[str] = None
    versions: List[FileVersion] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TexFileCreate(BaseModel):
    name: str
    subject_id: str
    semester_id: str
    content: str
    tags: List[str] = []
    notes: Optional[str] = None
    source_type: str = "manual"
    git_url: Optional[str] = None
    git_branch: Optional[str] = None
    git_path: Optional[str] = None

class TexFileUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    compilation_status: Optional[str] = None
    compilation_output: Optional[str] = None

class MultiFileUpload(BaseModel):
    files: List[dict]  # List of {name, content} objects
    subject_id: str
    semester_id: str
    tags: List[str] = []
    notes: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    semester_id: Optional[str] = None
    subject_id: Optional[str] = None
    tags: Optional[List[str]] = None

# Helper Functions
def count_words(text: str) -> int:
    """Count words in LaTeX text, ignoring commands"""
    # Remove LaTeX commands
    text = re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})*', '', text)
    # Remove comments
    text = re.sub(r'%.*', '', text)
    # Count words
    words = text.split()
    return len(words)

def get_file_size(content: str) -> int:
    """Get file size in bytes"""
    return len(content.encode('utf-8'))

def create_file_version(content: str) -> FileVersion:
    """Create a new file version"""
    word_count = count_words(content)
    file_size = get_file_size(content)
    return FileVersion(
        content=content,
        word_count=word_count,
        file_size=file_size
    )

async def compile_latex_to_pdf(content: str, filename: str = "document.tex") -> tuple[str, str, str]:
    """
    Compile LaTeX content to PDF using xelatex
    Returns: (status, output, pdf_path_or_error)
    """
    # Create temporary directory for compilation
    with tempfile.TemporaryDirectory() as temp_dir:
        tex_path = os.path.join(temp_dir, filename)
        pdf_path = os.path.join(temp_dir, filename.replace('.tex', '.pdf'))
        
        try:
            # Write LaTeX content to file
            with open(tex_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Run xelatex compilation
            process = await asyncio.create_subprocess_exec(
                'xelatex',
                '-interaction=nonstopmode',
                '-output-directory', temp_dir,
                tex_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=temp_dir
            )
            
            stdout, stderr = await process.communicate()
            output = stdout.decode('utf-8') + stderr.decode('utf-8')
            
            # Check if PDF was created successfully
            if process.returncode == 0 and os.path.exists(pdf_path):
                # Copy PDF to a permanent location
                permanent_pdf_path = tempfile.mktemp(suffix='.pdf')
                shutil.copy2(pdf_path, permanent_pdf_path)
                return "success", output, permanent_pdf_path
            else:
                return "error", output, f"Compilation failed with return code {process.returncode}"
                
        except Exception as e:
            return "error", str(e), f"Exception during compilation: {str(e)}"

# Routes
@api_router.get("/")
async def root():
    return {"message": "LaTeX File Tracker API"}

# Year endpoints
@api_router.post("/years", response_model=Year)
async def create_year(year: YearCreate):
    # Check if year already exists
    existing = await db.years.find_one({"year": year.year})
    if existing:
        raise HTTPException(status_code=400, detail="Year already exists")
    
    year_obj = Year(**year.dict())
    await db.years.insert_one(year_obj.dict())
    return year_obj

@api_router.get("/years", response_model=List[Year])
async def get_years():
    years = await db.years.find().sort("year", -1).to_list(100)
    return [Year(**year) for year in years]

@api_router.get("/years/{year_id}", response_model=Year)
async def get_year(year_id: str):
    year = await db.years.find_one({"id": year_id})
    if not year:
        raise HTTPException(status_code=404, detail="Year not found")
    return Year(**year)

@api_router.put("/years/{year_id}", response_model=Year)
async def update_year(year_id: str, year_update: YearUpdate):
    year = await db.years.find_one({"id": year_id})
    if not year:
        raise HTTPException(status_code=404, detail="Year not found")
    
    update_data = {k: v for k, v in year_update.dict().items() if v is not None}
    if update_data:
        await db.years.update_one({"id": year_id}, {"$set": update_data})
    
    updated_year = await db.years.find_one({"id": year_id})
    return Year(**updated_year)

@api_router.delete("/years/{year_id}")
async def delete_year(year_id: str):
    # Check if year has semesters
    semesters = await db.semesters.find_one({"year_id": year_id})
    if semesters:
        raise HTTPException(status_code=400, detail="Cannot delete year with existing semesters")
    
    result = await db.years.delete_one({"id": year_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Year not found")
    return {"message": "Year deleted successfully"}

# Semester endpoints
@api_router.post("/semesters", response_model=Semester)
async def create_semester(semester: SemesterCreate):
    # Verify year exists
    year = await db.years.find_one({"id": semester.year_id})
    if not year:
        raise HTTPException(status_code=404, detail="Year not found")
    
    semester_obj = Semester(**semester.dict())
    await db.semesters.insert_one(semester_obj.dict())
    return semester_obj

@api_router.get("/semesters", response_model=List[Semester])
async def get_semesters(year_id: Optional[str] = None):
    query = {"year_id": year_id} if year_id else {}
    semesters = await db.semesters.find(query).sort("created_at", -1).to_list(100)
    return [Semester(**semester) for semester in semesters]

@api_router.get("/semesters/{semester_id}", response_model=Semester)
async def get_semester(semester_id: str):
    semester = await db.semesters.find_one({"id": semester_id})
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    return Semester(**semester)

@api_router.put("/semesters/{semester_id}", response_model=Semester)
async def update_semester(semester_id: str, semester_update: SemesterUpdate):
    semester = await db.semesters.find_one({"id": semester_id})
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    
    update_data = {k: v for k, v in semester_update.dict().items() if v is not None}
    if update_data:
        await db.semesters.update_one({"id": semester_id}, {"$set": update_data})
    
    updated_semester = await db.semesters.find_one({"id": semester_id})
    return Semester(**updated_semester)

@api_router.delete("/semesters/{semester_id}")
async def delete_semester(semester_id: str):
    # Check if semester has subjects
    subjects = await db.subjects.find_one({"semester_id": semester_id})
    if subjects:
        raise HTTPException(status_code=400, detail="Cannot delete semester with existing subjects")
    
    result = await db.semesters.delete_one({"id": semester_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Semester not found")
    return {"message": "Semester deleted successfully"}

# Term endpoints (legacy - for backward compatibility)
@api_router.post("/terms", response_model=Term)
async def create_term(term: TermCreate):
    term_obj = Term(**term.dict())
    await db.terms.insert_one(term_obj.dict())
    return term_obj

@api_router.get("/terms", response_model=List[Term])
async def get_terms():
    terms = await db.terms.find().to_list(1000)
    return [Term(**term) for term in terms]

@api_router.get("/terms/{term_id}", response_model=Term)
async def get_term(term_id: str):
    term = await db.terms.find_one({"id": term_id})
    if not term:
        raise HTTPException(status_code=404, detail="Term not found")
    return Term(**term)

@api_router.put("/terms/{term_id}", response_model=Term)
async def update_term(term_id: str, term_update: TermCreate):
    term = await db.terms.find_one({"id": term_id})
    if not term:
        raise HTTPException(status_code=404, detail="Term not found")
    
    updated_term = Term(**term)
    for key, value in term_update.dict(exclude_unset=True).items():
        setattr(updated_term, key, value)
    
    await db.terms.replace_one({"id": term_id}, updated_term.dict())
    return updated_term

@api_router.delete("/terms/{term_id}")
async def delete_term(term_id: str):
    result = await db.terms.delete_one({"id": term_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Term not found")
    # Also delete associated subjects and files
    await db.subjects.delete_many({"term_id": term_id})
    await db.tex_files.delete_many({"term_id": term_id})
    return {"message": "Term deleted successfully"}

# Subject endpoints
@api_router.post("/subjects", response_model=Subject)
async def create_subject(subject: SubjectCreate):
    # Verify semester exists
    semester = await db.semesters.find_one({"id": subject.semester_id})
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    
    subject_obj = Subject(**subject.dict())
    await db.subjects.insert_one(subject_obj.dict())
    return subject_obj

@api_router.get("/subjects", response_model=List[Subject])
async def get_subjects(semester_id: Optional[str] = None):
    query = {"semester_id": semester_id} if semester_id else {}
    subjects = await db.subjects.find(query).to_list(1000)
    return [Subject(**subject) for subject in subjects]

@api_router.get("/subjects/{subject_id}", response_model=Subject)
async def get_subject(subject_id: str):
    subject = await db.subjects.find_one({"id": subject_id})
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return Subject(**subject)

@api_router.put("/subjects/{subject_id}", response_model=Subject)
async def update_subject(subject_id: str, subject_update: SubjectUpdate):
    subject = await db.subjects.find_one({"id": subject_id})
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # Verify semester exists if semester_id is being updated
    if subject_update.semester_id and subject_update.semester_id != subject.get('semester_id'):
        semester = await db.semesters.find_one({"id": subject_update.semester_id})
        if not semester:
            raise HTTPException(status_code=404, detail="Semester not found")
    
    updated_subject = Subject(**subject)
    for key, value in subject_update.dict(exclude_unset=True).items():
        setattr(updated_subject, key, value)
    
    await db.subjects.replace_one({"id": subject_id}, updated_subject.dict())
    return updated_subject

@api_router.delete("/subjects/{subject_id}")
async def delete_subject(subject_id: str):
    result = await db.subjects.delete_one({"id": subject_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Subject not found")
    # Also delete associated files
    await db.tex_files.delete_many({"subject_id": subject_id})
    return {"message": "Subject deleted successfully"}

# File endpoints
@api_router.post("/files", response_model=TexFile)
async def create_file(file_data: TexFileCreate):
    # Verify subject and semester exist
    subject = await db.subjects.find_one({"id": file_data.subject_id})
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    semester = await db.semesters.find_one({"id": file_data.semester_id})
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    
    # Create file with version
    word_count = count_words(file_data.content)
    file_size = get_file_size(file_data.content)
    initial_version = create_file_version(file_data.content)
    
    file_obj = TexFile(
        **file_data.dict(),
        word_count=word_count,
        file_size=file_size,
        versions=[initial_version]
    )
    
    # Try to compile the LaTeX file automatically
    try:
        status, output, result = await compile_latex_to_pdf(file_data.content, file_data.name)
        file_obj.compilation_status = status
        file_obj.compilation_output = output
    except Exception as e:
        # If compilation fails, still create the file but mark compilation as error
        file_obj.compilation_status = "error"
        file_obj.compilation_output = f"Auto-compilation failed: {str(e)}"
    
    await db.tex_files.insert_one(file_obj.dict())
    return file_obj

@api_router.post("/files/multi-upload", response_model=List[TexFile])
async def create_multiple_files(multi_upload: MultiFileUpload):
    # Verify subject and semester exist
    subject = await db.subjects.find_one({"id": multi_upload.subject_id})
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    semester = await db.semesters.find_one({"id": multi_upload.semester_id})
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    
    created_files = []
    
    for file_data in multi_upload.files:
        # Validate file data
        if not file_data.get('name') or not file_data.get('content'):
            continue
            
        # Create file with version
        word_count = count_words(file_data['content'])
        file_size = get_file_size(file_data['content'])
        initial_version = create_file_version(file_data['content'])
        
        file_obj = TexFile(
            name=file_data['name'],
            subject_id=multi_upload.subject_id,
            semester_id=multi_upload.semester_id,
            content=file_data['content'],
            word_count=word_count,
            file_size=file_size,
            tags=multi_upload.tags,
            notes=multi_upload.notes,
            source_type="multi_upload",
            versions=[initial_version]
        )
        
        # Try to compile the LaTeX file automatically
        try:
            status, output, result = await compile_latex_to_pdf(file_data['content'], file_data['name'])
            file_obj.compilation_status = status
            file_obj.compilation_output = output
        except Exception as e:
            # If compilation fails, still create the file but mark compilation as error
            file_obj.compilation_status = "error"
            file_obj.compilation_output = f"Auto-compilation failed: {str(e)}"
        
        await db.tex_files.insert_one(file_obj.dict())
        created_files.append(file_obj)
    
    return created_files

@api_router.get("/files", response_model=List[TexFile])
async def get_files(
    semester_id: Optional[str] = None,
    subject_id: Optional[str] = None,
    tags: Optional[str] = None
):
    query = {}
    if semester_id:
        query["semester_id"] = semester_id
    if subject_id:
        query["subject_id"] = subject_id
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        query["tags"] = {"$in": tag_list}
    
    files = await db.tex_files.find(query).to_list(1000)
    return [TexFile(**file) for file in files]

@api_router.get("/files/{file_id}", response_model=TexFile)
async def get_file(file_id: str):
    file = await db.tex_files.find_one({"id": file_id})
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return TexFile(**file)

@api_router.put("/files/{file_id}", response_model=TexFile)
async def update_file(file_id: str, file_update: TexFileUpdate):
    file = await db.tex_files.find_one({"id": file_id})
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_obj = TexFile(**file)
    
    # If content is being updated, create a new version
    if file_update.content and file_update.content != file_obj.content:
        new_version = create_file_version(file_update.content)
        file_obj.versions.append(new_version)
        file_obj.content = file_update.content
        file_obj.word_count = new_version.word_count
        file_obj.file_size = new_version.file_size
    
    # Update other fields
    for key, value in file_update.dict(exclude_unset=True).items():
        if key != "content":
            setattr(file_obj, key, value)
    
    file_obj.updated_at = datetime.utcnow()
    
    await db.tex_files.replace_one({"id": file_id}, file_obj.dict())
    return file_obj

@api_router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    result = await db.tex_files.delete_one({"id": file_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": "File deleted successfully"}

# File upload endpoint
@api_router.post("/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    subject_id: str = Form(...),
    term_id: str = Form(...),
    tags: str = Form(""),
    notes: str = Form("")
):
    # Verify it's a .tex file
    if not file.filename.endswith('.tex'):
        raise HTTPException(status_code=400, detail="Only .tex files are allowed")
    
    # Read file content
    content = await file.read()
    try:
        content_str = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")
    
    # Create file
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    file_data = TexFileCreate(
        name=file.filename,
        subject_id=subject_id,
        term_id=term_id,
        content=content_str,
        tags=tag_list,
        notes=notes if notes else None,
        source_type="manual"
    )
    
    return await create_file(file_data)

# Search endpoint
@api_router.post("/search")
async def search_files(search_request: SearchRequest):
    query = {}
    
    # Add filters
    if search_request.semester_id:
        query["semester_id"] = search_request.semester_id
    if search_request.subject_id:
        query["subject_id"] = search_request.subject_id
    if search_request.tags:
        query["tags"] = {"$in": search_request.tags}
    
    # Add text search
    if search_request.query:
        query["$or"] = [
            {"name": {"$regex": search_request.query, "$options": "i"}},
            {"content": {"$regex": search_request.query, "$options": "i"}},
            {"notes": {"$regex": search_request.query, "$options": "i"}},
            {"tags": {"$regex": search_request.query, "$options": "i"}}
        ]
    
    files = await db.tex_files.find(query).to_list(1000)
    return [TexFile(**file) for file in files]

# Export endpoint
@api_router.get("/export/{file_id}")
async def export_file(file_id: str):
    file = await db.tex_files.find_one({"id": file_id})
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as tmp_file:
        tmp_file.write(file["content"])
        tmp_file_path = tmp_file.name
    
    return FileResponse(
        path=tmp_file_path,
        filename=file["name"],
        media_type='application/x-tex'
    )

# Bulk export endpoint
@api_router.post("/export/bulk")
async def export_bulk(file_ids: List[str]):
    if not file_ids:
        raise HTTPException(status_code=400, detail="No files selected")
    
    # Get all files
    files = await db.tex_files.find({"id": {"$in": file_ids}}).to_list(1000)
    
    if not files:
        raise HTTPException(status_code=404, detail="No files found")
    
    # Create temporary zip file
    with tempfile.NamedTemporaryFile(mode='w+b', suffix='.zip', delete=False) as tmp_zip:
        zip_path = tmp_zip.name
    
    # Create zip file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            # Add file content directly to zip without creating temp files
            zipf.writestr(file["name"], file["content"])
    
    return FileResponse(
        path=zip_path,
        filename="latex_files.zip",
        media_type='application/zip'
    )

# Dashboard stats endpoint
@api_router.get("/stats")
async def get_stats():
    total_terms = await db.terms.count_documents({})
    total_subjects = await db.subjects.count_documents({})
    total_files = await db.tex_files.count_documents({})
    
    # Get files by compilation status
    compilation_stats = await db.tex_files.aggregate([
        {"$group": {"_id": "$compilation_status", "count": {"$sum": 1}}}
    ]).to_list(1000)
    
    # Get recent files
    recent_files = await db.tex_files.find().sort("updated_at", -1).limit(5).to_list(5)
    
    return {
        "total_terms": total_terms,
        "total_subjects": total_subjects,
        "total_files": total_files,
        "compilation_stats": {stat["_id"]: stat["count"] for stat in compilation_stats},
        "recent_files": [TexFile(**file) for file in recent_files]
    }

# Compilation endpoint
@api_router.post("/files/{file_id}/compile")
async def compile_file(file_id: str):
    """Compile a LaTeX file to PDF"""
    file = await db.tex_files.find_one({"id": file_id})
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Compile the LaTeX content
    status, output, result = await compile_latex_to_pdf(file["content"], file["name"])
    
    # Update file with compilation results
    file_obj = TexFile(**file)
    file_obj.compilation_status = status
    file_obj.compilation_output = output
    file_obj.updated_at = datetime.utcnow()
    
    await db.tex_files.replace_one({"id": file_id}, file_obj.dict())
    
    if status == "success":
        return {
            "status": status,
            "message": "Compilation successful",
            "pdf_available": True,
            "output": output
        }
    else:
        return {
            "status": status,
            "message": "Compilation failed",
            "pdf_available": False,
            "output": output,
            "error": result
        }

# PDF download endpoint
@api_router.get("/files/{file_id}/pdf")
async def get_pdf(file_id: str):
    """Get compiled PDF for a file"""
    file = await db.tex_files.find_one({"id": file_id})
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if file.get("compilation_status") != "success":
        # Try to compile first
        status, output, result = await compile_latex_to_pdf(file["content"], file["name"])
        
        # Update file with compilation results
        file_obj = TexFile(**file)
        file_obj.compilation_status = status
        file_obj.compilation_output = output
        file_obj.updated_at = datetime.utcnow()
        
        await db.tex_files.replace_one({"id": file_id}, file_obj.dict())
        
        if status != "success":
            raise HTTPException(status_code=400, detail=f"Compilation failed: {result}")
        
        pdf_path = result
    else:
        # Re-compile to get fresh PDF
        status, output, pdf_path = await compile_latex_to_pdf(file["content"], file["name"])
        if status != "success":
            raise HTTPException(status_code=400, detail=f"Compilation failed: {pdf_path}")
    
    return FileResponse(
        path=pdf_path,
        filename=file["name"].replace('.tex', '.pdf'),
        media_type='application/pdf'
    )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()