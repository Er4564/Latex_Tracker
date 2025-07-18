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
    term_id: str
    color: Optional[str] = "#3B82F6"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SubjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    term_id: str
    color: Optional[str] = "#3B82F6"

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
    term_id: str
    content: str
    word_count: int
    file_size: int
    compilation_status: str = "unknown"
    compilation_output: Optional[str] = None
    tags: List[str] = []
    notes: Optional[str] = None
    source_type: str = "manual"  # "manual", "git", "paste"
    git_url: Optional[str] = None
    git_branch: Optional[str] = None
    git_path: Optional[str] = None
    versions: List[FileVersion] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TexFileCreate(BaseModel):
    name: str
    subject_id: str
    term_id: str
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

class SearchRequest(BaseModel):
    query: str
    term_id: Optional[str] = None
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

# Routes
@api_router.get("/")
async def root():
    return {"message": "LaTeX File Tracker API"}

# Term endpoints
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
    # Verify term exists
    term = await db.terms.find_one({"id": subject.term_id})
    if not term:
        raise HTTPException(status_code=404, detail="Term not found")
    
    subject_obj = Subject(**subject.dict())
    await db.subjects.insert_one(subject_obj.dict())
    return subject_obj

@api_router.get("/subjects", response_model=List[Subject])
async def get_subjects(term_id: Optional[str] = None):
    query = {"term_id": term_id} if term_id else {}
    subjects = await db.subjects.find(query).to_list(1000)
    return [Subject(**subject) for subject in subjects]

@api_router.get("/subjects/{subject_id}", response_model=Subject)
async def get_subject(subject_id: str):
    subject = await db.subjects.find_one({"id": subject_id})
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return Subject(**subject)

@api_router.put("/subjects/{subject_id}", response_model=Subject)
async def update_subject(subject_id: str, subject_update: SubjectCreate):
    subject = await db.subjects.find_one({"id": subject_id})
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
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
    # Verify subject and term exist
    subject = await db.subjects.find_one({"id": file_data.subject_id})
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    term = await db.terms.find_one({"id": file_data.term_id})
    if not term:
        raise HTTPException(status_code=404, detail="Term not found")
    
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
    
    await db.tex_files.insert_one(file_obj.dict())
    return file_obj

@api_router.get("/files", response_model=List[TexFile])
async def get_files(
    term_id: Optional[str] = None,
    subject_id: Optional[str] = None,
    tags: Optional[str] = None
):
    query = {}
    if term_id:
        query["term_id"] = term_id
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
    if search_request.term_id:
        query["term_id"] = search_request.term_id
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
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Get all files
        files = await db.tex_files.find({"id": {"$in": file_ids}}).to_list(1000)
        
        if not files:
            raise HTTPException(status_code=404, detail="No files found")
        
        # Create files in temp directory
        for file in files:
            file_path = os.path.join(temp_dir, file["name"])
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file["content"])
        
        # Create zip file
        zip_path = os.path.join(temp_dir, "latex_files.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                file_path = os.path.join(temp_dir, file["name"])
                zipf.write(file_path, file["name"])
        
        return FileResponse(
            path=zip_path,
            filename="latex_files.zip",
            media_type='application/zip'
        )
    
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir)

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