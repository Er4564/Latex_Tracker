#!/usr/bin/env python3
"""
Comprehensive Backend API Test for LaTeX File Tracking System
Tests all endpoints systematically following the workflow:
Create terms → Create subjects → Add files → Search → Export functionality
"""

import requests
import json
import os
import tempfile
from datetime import datetime
from typing import Dict, List, Any

# Get backend URL from environment
BACKEND_URL = "https://6d9b4f3d-a7f0-42bc-be0d-06f77e3ab827.preview.emergentagent.com/api"

class LaTeXTrackerAPITest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_data = {
            'terms': [],
            'subjects': [],
            'files': []
        }
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        if data:
            result['data'] = data
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Root", True, f"API is accessible: {data.get('message', '')}")
                return True
            else:
                self.log_test("API Root", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Root", False, f"Connection error: {str(e)}")
            return False
    
    def test_terms_crud(self):
        """Test Terms CRUD operations"""
        print("\n=== Testing Terms Management ===")
        
        # Test CREATE term
        term_data = {
            "name": "Fall 2024 Semester",
            "description": "Fall semester for academic year 2024",
            "start_date": "2024-09-01T00:00:00Z",
            "end_date": "2024-12-15T00:00:00Z"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/terms", json=term_data)
            if response.status_code == 200:
                term = response.json()
                self.test_data['terms'].append(term)
                self.log_test("Create Term", True, f"Created term: {term['name']}")
            else:
                self.log_test("Create Term", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Term", False, f"Error: {str(e)}")
            return False
        
        # Test GET all terms
        try:
            response = self.session.get(f"{self.base_url}/terms")
            if response.status_code == 200:
                terms = response.json()
                self.log_test("Get All Terms", True, f"Retrieved {len(terms)} terms")
            else:
                self.log_test("Get All Terms", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get All Terms", False, f"Error: {str(e)}")
            return False
        
        # Test GET specific term
        if self.test_data['terms']:
            term_id = self.test_data['terms'][0]['id']
            try:
                response = self.session.get(f"{self.base_url}/terms/{term_id}")
                if response.status_code == 200:
                    term = response.json()
                    self.log_test("Get Specific Term", True, f"Retrieved term: {term['name']}")
                else:
                    self.log_test("Get Specific Term", False, f"Status: {response.status_code}")
                    return False
            except Exception as e:
                self.log_test("Get Specific Term", False, f"Error: {str(e)}")
                return False
        
        # Test UPDATE term
        if self.test_data['terms']:
            term_id = self.test_data['terms'][0]['id']
            update_data = {
                "name": "Fall 2024 Semester - Updated",
                "description": "Updated fall semester description"
            }
            try:
                response = self.session.put(f"{self.base_url}/terms/{term_id}", json=update_data)
                if response.status_code == 200:
                    updated_term = response.json()
                    self.test_data['terms'][0] = updated_term
                    self.log_test("Update Term", True, f"Updated term: {updated_term['name']}")
                else:
                    self.log_test("Update Term", False, f"Status: {response.status_code}")
                    return False
            except Exception as e:
                self.log_test("Update Term", False, f"Error: {str(e)}")
                return False
        
        return True
    
    def test_subjects_crud(self):
        """Test Subjects CRUD operations"""
        print("\n=== Testing Subjects Management ===")
        
        if not self.test_data['terms']:
            self.log_test("Subjects Test Setup", False, "No terms available for testing subjects")
            return False
        
        term_id = self.test_data['terms'][0]['id']
        
        # Test CREATE subject
        subject_data = {
            "name": "Advanced Calculus",
            "description": "Calculus III - Multivariable Calculus",
            "term_id": term_id,
            "color": "#FF6B6B"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/subjects", json=subject_data)
            if response.status_code == 200:
                subject = response.json()
                self.test_data['subjects'].append(subject)
                self.log_test("Create Subject", True, f"Created subject: {subject['name']}")
            else:
                self.log_test("Create Subject", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Subject", False, f"Error: {str(e)}")
            return False
        
        # Create another subject for testing
        subject_data2 = {
            "name": "Linear Algebra",
            "description": "Matrix theory and vector spaces",
            "term_id": term_id,
            "color": "#4ECDC4"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/subjects", json=subject_data2)
            if response.status_code == 200:
                subject = response.json()
                self.test_data['subjects'].append(subject)
                self.log_test("Create Second Subject", True, f"Created subject: {subject['name']}")
            else:
                self.log_test("Create Second Subject", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Create Second Subject", False, f"Error: {str(e)}")
        
        # Test GET all subjects
        try:
            response = self.session.get(f"{self.base_url}/subjects")
            if response.status_code == 200:
                subjects = response.json()
                self.log_test("Get All Subjects", True, f"Retrieved {len(subjects)} subjects")
            else:
                self.log_test("Get All Subjects", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get All Subjects", False, f"Error: {str(e)}")
            return False
        
        # Test GET subjects by term
        try:
            response = self.session.get(f"{self.base_url}/subjects?term_id={term_id}")
            if response.status_code == 200:
                subjects = response.json()
                self.log_test("Get Subjects by Term", True, f"Retrieved {len(subjects)} subjects for term")
            else:
                self.log_test("Get Subjects by Term", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Subjects by Term", False, f"Error: {str(e)}")
            return False
        
        # Test GET specific subject
        if self.test_data['subjects']:
            subject_id = self.test_data['subjects'][0]['id']
            try:
                response = self.session.get(f"{self.base_url}/subjects/{subject_id}")
                if response.status_code == 200:
                    subject = response.json()
                    self.log_test("Get Specific Subject", True, f"Retrieved subject: {subject['name']}")
                else:
                    self.log_test("Get Specific Subject", False, f"Status: {response.status_code}")
                    return False
            except Exception as e:
                self.log_test("Get Specific Subject", False, f"Error: {str(e)}")
                return False
        
        # Test UPDATE subject
        if self.test_data['subjects']:
            subject_id = self.test_data['subjects'][0]['id']
            update_data = {
                "name": "Advanced Calculus - Updated",
                "description": "Updated calculus course description",
                "color": "#FF8E53"
            }
            try:
                response = self.session.put(f"{self.base_url}/subjects/{subject_id}", json=update_data)
                if response.status_code == 200:
                    updated_subject = response.json()
                    self.test_data['subjects'][0] = updated_subject
                    self.log_test("Update Subject", True, f"Updated subject: {updated_subject['name']}")
                else:
                    self.log_test("Update Subject", False, f"Status: {response.status_code}")
                    return False
            except Exception as e:
                self.log_test("Update Subject", False, f"Error: {str(e)}")
                return False
        
        return True
    
    def test_files_crud(self):
        """Test Files CRUD operations"""
        print("\n=== Testing Files Management ===")
        
        if not self.test_data['subjects'] or not self.test_data['terms']:
            self.log_test("Files Test Setup", False, "No subjects/terms available for testing files")
            return False
        
        term_id = self.test_data['terms'][0]['id']
        subject_id = self.test_data['subjects'][0]['id']
        
        # Test CREATE file
        file_data = {
            "name": "calculus_homework_1.tex",
            "subject_id": subject_id,
            "term_id": term_id,
            "content": """\\documentclass{article}
\\usepackage{amsmath}
\\usepackage{amsfonts}

\\title{Calculus Homework 1}
\\author{Student Name}
\\date{\\today}

\\begin{document}
\\maketitle

\\section{Problem 1}
Find the derivative of $f(x) = x^3 + 2x^2 - 5x + 1$.

\\section{Solution}
Using the power rule:
\\begin{align}
f'(x) &= 3x^2 + 4x - 5
\\end{align}

\\section{Problem 2}
Evaluate the integral $\\int_0^1 x^2 dx$.

\\section{Solution}
\\begin{align}
\\int_0^1 x^2 dx &= \\left[\\frac{x^3}{3}\\right]_0^1 \\\\
&= \\frac{1}{3} - 0 = \\frac{1}{3}
\\end{align}

\\end{document}""",
            "tags": ["homework", "calculus", "derivatives", "integrals"],
            "notes": "First homework assignment covering basic derivatives and integrals",
            "source_type": "manual"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/files", json=file_data)
            if response.status_code == 200:
                file_obj = response.json()
                self.test_data['files'].append(file_obj)
                self.log_test("Create File", True, f"Created file: {file_obj['name']} (Word count: {file_obj['word_count']})")
            else:
                self.log_test("Create File", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create File", False, f"Error: {str(e)}")
            return False
        
        # Create another file for testing
        file_data2 = {
            "name": "linear_algebra_notes.tex",
            "subject_id": self.test_data['subjects'][1]['id'] if len(self.test_data['subjects']) > 1 else subject_id,
            "term_id": term_id,
            "content": """\\documentclass{article}
\\usepackage{amsmath}
\\usepackage{amsfonts}

\\title{Linear Algebra Notes}
\\author{Student Name}

\\begin{document}
\\maketitle

\\section{Matrices}
A matrix is a rectangular array of numbers arranged in rows and columns.

\\section{Matrix Operations}
\\subsection{Addition}
Matrices can be added element-wise if they have the same dimensions.

\\subsection{Multiplication}
Matrix multiplication follows the rule: $(AB)_{ij} = \\sum_{k} A_{ik}B_{kj}$

\\section{Determinants}
The determinant of a 2x2 matrix is:
$$\\det\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix} = ad - bc$$

\\end{document}""",
            "tags": ["notes", "linear-algebra", "matrices"],
            "notes": "Class notes on matrix operations and determinants",
            "source_type": "manual"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/files", json=file_data2)
            if response.status_code == 200:
                file_obj = response.json()
                self.test_data['files'].append(file_obj)
                self.log_test("Create Second File", True, f"Created file: {file_obj['name']}")
            else:
                self.log_test("Create Second File", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Create Second File", False, f"Error: {str(e)}")
        
        # Test GET all files
        try:
            response = self.session.get(f"{self.base_url}/files")
            if response.status_code == 200:
                files = response.json()
                self.log_test("Get All Files", True, f"Retrieved {len(files)} files")
            else:
                self.log_test("Get All Files", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get All Files", False, f"Error: {str(e)}")
            return False
        
        # Test GET files by term
        try:
            response = self.session.get(f"{self.base_url}/files?term_id={term_id}")
            if response.status_code == 200:
                files = response.json()
                self.log_test("Get Files by Term", True, f"Retrieved {len(files)} files for term")
            else:
                self.log_test("Get Files by Term", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Files by Term", False, f"Error: {str(e)}")
            return False
        
        # Test GET files by subject
        try:
            response = self.session.get(f"{self.base_url}/files?subject_id={subject_id}")
            if response.status_code == 200:
                files = response.json()
                self.log_test("Get Files by Subject", True, f"Retrieved {len(files)} files for subject")
            else:
                self.log_test("Get Files by Subject", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Files by Subject", False, f"Error: {str(e)}")
            return False
        
        # Test GET files by tags
        try:
            response = self.session.get(f"{self.base_url}/files?tags=homework,calculus")
            if response.status_code == 200:
                files = response.json()
                self.log_test("Get Files by Tags", True, f"Retrieved {len(files)} files with specified tags")
            else:
                self.log_test("Get Files by Tags", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Files by Tags", False, f"Error: {str(e)}")
            return False
        
        # Test GET specific file
        if self.test_data['files']:
            file_id = self.test_data['files'][0]['id']
            try:
                response = self.session.get(f"{self.base_url}/files/{file_id}")
                if response.status_code == 200:
                    file_obj = response.json()
                    self.log_test("Get Specific File", True, f"Retrieved file: {file_obj['name']}")
                else:
                    self.log_test("Get Specific File", False, f"Status: {response.status_code}")
                    return False
            except Exception as e:
                self.log_test("Get Specific File", False, f"Error: {str(e)}")
                return False
        
        # Test UPDATE file (content change to test version history)
        if self.test_data['files']:
            file_id = self.test_data['files'][0]['id']
            update_data = {
                "content": """\\documentclass{article}
\\usepackage{amsmath}
\\usepackage{amsfonts}

\\title{Calculus Homework 1 - Revised}
\\author{Student Name}
\\date{\\today}

\\begin{document}
\\maketitle

\\section{Problem 1}
Find the derivative of $f(x) = x^3 + 2x^2 - 5x + 1$.

\\section{Solution}
Using the power rule:
\\begin{align}
f'(x) &= 3x^2 + 4x - 5
\\end{align}

\\section{Problem 2}
Evaluate the integral $\\int_0^1 x^2 dx$.

\\section{Solution}
\\begin{align}
\\int_0^1 x^2 dx &= \\left[\\frac{x^3}{3}\\right]_0^1 \\\\
&= \\frac{1}{3} - 0 = \\frac{1}{3}
\\end{align}

\\section{Problem 3 - NEW}
Find the limit $\\lim_{x \\to 0} \\frac{\\sin x}{x}$.

\\section{Solution}
This is a standard limit that equals 1.

\\end{document}""",
                "notes": "Updated homework with additional problem",
                "compilation_status": "success"
            }
            try:
                response = self.session.put(f"{self.base_url}/files/{file_id}", json=update_data)
                if response.status_code == 200:
                    updated_file = response.json()
                    self.test_data['files'][0] = updated_file
                    version_count = len(updated_file.get('versions', []))
                    self.log_test("Update File", True, f"Updated file with {version_count} versions in history")
                else:
                    self.log_test("Update File", False, f"Status: {response.status_code}")
                    return False
            except Exception as e:
                self.log_test("Update File", False, f"Error: {str(e)}")
                return False
        
        return True
    
    def test_file_upload(self):
        """Test file upload endpoint"""
        print("\n=== Testing File Upload ===")
        
        if not self.test_data['subjects'] or not self.test_data['terms']:
            self.log_test("File Upload Test Setup", False, "No subjects/terms available for testing upload")
            return False
        
        term_id = self.test_data['terms'][0]['id']
        subject_id = self.test_data['subjects'][0]['id']
        
        # Create a temporary .tex file
        tex_content = """\\documentclass{article}
\\usepackage{amsmath}

\\title{Uploaded LaTeX File}
\\author{Test User}

\\begin{document}
\\maketitle

\\section{Introduction}
This is a test file uploaded via the API.

\\section{Mathematics}
Here's an equation:
$$E = mc^2$$

\\end{document}"""
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as tmp_file:
                tmp_file.write(tex_content)
                tmp_file_path = tmp_file.name
            
            # Upload the file
            with open(tmp_file_path, 'rb') as f:
                files = {'file': ('uploaded_test.tex', f, 'text/plain')}
                data = {
                    'subject_id': subject_id,
                    'term_id': term_id,
                    'tags': 'uploaded,test,api',
                    'notes': 'File uploaded via API test'
                }
                
                response = self.session.post(f"{self.base_url}/files/upload", files=files, data=data)
                
                if response.status_code == 200:
                    uploaded_file = response.json()
                    self.test_data['files'].append(uploaded_file)
                    self.log_test("File Upload", True, f"Uploaded file: {uploaded_file['name']}")
                else:
                    self.log_test("File Upload", False, f"Status: {response.status_code}, Response: {response.text}")
                    return False
            
            # Clean up temp file
            os.unlink(tmp_file_path)
            
        except Exception as e:
            self.log_test("File Upload", False, f"Error: {str(e)}")
            return False
        
        return True
    
    def test_search(self):
        """Test search functionality"""
        print("\n=== Testing Search Functionality ===")
        
        if not self.test_data['files']:
            self.log_test("Search Test Setup", False, "No files available for testing search")
            return False
        
        # Test search by content
        search_data = {
            "query": "derivative"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/search", json=search_data)
            if response.status_code == 200:
                results = response.json()
                self.log_test("Search by Content", True, f"Found {len(results)} files containing 'derivative'")
            else:
                self.log_test("Search by Content", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Search by Content", False, f"Error: {str(e)}")
            return False
        
        # Test search by name
        search_data = {
            "query": "calculus"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/search", json=search_data)
            if response.status_code == 200:
                results = response.json()
                self.log_test("Search by Name", True, f"Found {len(results)} files with 'calculus' in name/content")
            else:
                self.log_test("Search by Name", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Search by Name", False, f"Error: {str(e)}")
            return False
        
        # Test search with filters
        if self.test_data['terms'] and self.test_data['subjects']:
            search_data = {
                "query": "homework",
                "term_id": self.test_data['terms'][0]['id'],
                "subject_id": self.test_data['subjects'][0]['id']
            }
            
            try:
                response = self.session.post(f"{self.base_url}/search", json=search_data)
                if response.status_code == 200:
                    results = response.json()
                    self.log_test("Search with Filters", True, f"Found {len(results)} files with filters applied")
                else:
                    self.log_test("Search with Filters", False, f"Status: {response.status_code}")
                    return False
            except Exception as e:
                self.log_test("Search with Filters", False, f"Error: {str(e)}")
                return False
        
        # Test search by tags
        search_data = {
            "query": "",
            "tags": ["homework", "calculus"]
        }
        
        try:
            response = self.session.post(f"{self.base_url}/search", json=search_data)
            if response.status_code == 200:
                results = response.json()
                self.log_test("Search by Tags", True, f"Found {len(results)} files with specified tags")
            else:
                self.log_test("Search by Tags", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Search by Tags", False, f"Error: {str(e)}")
            return False
        
        return True
    
    def test_export(self):
        """Test export functionality"""
        print("\n=== Testing Export Functionality ===")
        
        if not self.test_data['files']:
            self.log_test("Export Test Setup", False, "No files available for testing export")
            return False
        
        # Test single file export
        file_id = self.test_data['files'][0]['id']
        
        try:
            response = self.session.get(f"{self.base_url}/export/{file_id}")
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                self.log_test("Single File Export", True, f"Exported file successfully (Content-Type: {content_type})")
            else:
                self.log_test("Single File Export", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Single File Export", False, f"Error: {str(e)}")
            return False
        
        # Test bulk export
        file_ids = [file['id'] for file in self.test_data['files'][:2]]  # Export first 2 files
        
        try:
            response = self.session.post(f"{self.base_url}/export/bulk", json=file_ids)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_length = response.headers.get('content-length', 'unknown')
                self.log_test("Bulk Export", True, f"Exported {len(file_ids)} files as ZIP (Size: {content_length} bytes)")
            else:
                self.log_test("Bulk Export", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Bulk Export", False, f"Error: {str(e)}")
            return False
        
        return True
    
    def test_stats(self):
        """Test dashboard statistics"""
        print("\n=== Testing Dashboard Statistics ===")
        
        try:
            response = self.session.get(f"{self.base_url}/stats")
            if response.status_code == 200:
                stats = response.json()
                expected_keys = ['total_terms', 'total_subjects', 'total_files', 'compilation_stats', 'recent_files']
                
                missing_keys = [key for key in expected_keys if key not in stats]
                if missing_keys:
                    self.log_test("Dashboard Stats", False, f"Missing keys: {missing_keys}")
                    return False
                
                self.log_test("Dashboard Stats", True, 
                    f"Terms: {stats['total_terms']}, Subjects: {stats['total_subjects']}, Files: {stats['total_files']}")
                return True
            else:
                self.log_test("Dashboard Stats", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Dashboard Stats", False, f"Error: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        print("\n=== Testing Error Handling ===")
        
        # Test 404 for non-existent term
        try:
            response = self.session.get(f"{self.base_url}/terms/non-existent-id")
            if response.status_code == 404:
                self.log_test("404 Error Handling", True, "Correctly returned 404 for non-existent term")
            else:
                self.log_test("404 Error Handling", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("404 Error Handling", False, f"Error: {str(e)}")
        
        # Test invalid file upload (non-.tex file)
        try:
            files = {'file': ('test.txt', b'This is not a tex file', 'text/plain')}
            data = {
                'subject_id': 'invalid-id',
                'term_id': 'invalid-id'
            }
            response = self.session.post(f"{self.base_url}/files/upload", files=files, data=data)
            if response.status_code == 400:
                self.log_test("Invalid File Upload", True, "Correctly rejected non-.tex file")
            else:
                self.log_test("Invalid File Upload", False, f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_test("Invalid File Upload", False, f"Error: {str(e)}")
    
    def cleanup_test_data(self):
        """Clean up test data (optional - for clean testing environment)"""
        print("\n=== Cleaning Up Test Data ===")
        
        # Delete test files
        for file_obj in self.test_data['files']:
            try:
                response = self.session.delete(f"{self.base_url}/files/{file_obj['id']}")
                if response.status_code == 200:
                    self.log_test("Delete Test File", True, f"Deleted file: {file_obj['name']}")
                else:
                    self.log_test("Delete Test File", False, f"Failed to delete file: {file_obj['name']}")
            except Exception as e:
                self.log_test("Delete Test File", False, f"Error deleting {file_obj['name']}: {str(e)}")
        
        # Delete test subjects
        for subject in self.test_data['subjects']:
            try:
                response = self.session.delete(f"{self.base_url}/subjects/{subject['id']}")
                if response.status_code == 200:
                    self.log_test("Delete Test Subject", True, f"Deleted subject: {subject['name']}")
                else:
                    self.log_test("Delete Test Subject", False, f"Failed to delete subject: {subject['name']}")
            except Exception as e:
                self.log_test("Delete Test Subject", False, f"Error deleting {subject['name']}: {str(e)}")
        
        # Delete test terms
        for term in self.test_data['terms']:
            try:
                response = self.session.delete(f"{self.base_url}/terms/{term['id']}")
                if response.status_code == 200:
                    self.log_test("Delete Test Term", True, f"Deleted term: {term['name']}")
                else:
                    self.log_test("Delete Test Term", False, f"Failed to delete term: {term['name']}")
            except Exception as e:
                self.log_test("Delete Test Term", False, f"Error deleting {term['name']}: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive LaTeX File Tracker API Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Test sequence following the workflow
        tests = [
            ("API Connectivity", self.test_api_root),
            ("Terms CRUD", self.test_terms_crud),
            ("Subjects CRUD", self.test_subjects_crud),
            ("Files CRUD", self.test_files_crud),
            ("File Upload", self.test_file_upload),
            ("Search Functionality", self.test_search),
            ("Export Functionality", self.test_export),
            ("Dashboard Statistics", self.test_stats),
            ("Error Handling", self.test_error_handling),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test function error: {str(e)}")
        
        # Optional cleanup (comment out if you want to keep test data)
        # self.cleanup_test_data()
        
        print("\n" + "=" * 60)
        print(f"🏁 Test Summary: {passed_tests}/{total_tests} tests passed")
        
        # Print detailed results
        print("\n📊 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = LaTeXTrackerAPITest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! The LaTeX File Tracker API is working correctly.")
        exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the detailed results above.")
        exit(1)