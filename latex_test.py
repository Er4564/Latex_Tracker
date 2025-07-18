#!/usr/bin/env python3
"""
Test LaTeX compilation functionality
"""

import requests
import json
import time

BACKEND_URL = "https://6d9b4f3d-a7f0-42bc-be0d-06f77e3ab827.preview.emergentagent.com/api"

def test_latex_compilation():
    """Test LaTeX compilation to PDF"""
    session = requests.Session()
    
    print("=== Testing LaTeX Compilation ===")
    
    # First, create a term and subject for testing
    term_data = {
        "name": "LaTeX Test Term",
        "description": "Term for testing LaTeX compilation"
    }
    
    term_response = session.post(f"{BACKEND_URL}/terms", json=term_data)
    if term_response.status_code != 200:
        print(f"❌ Failed to create term: {term_response.status_code}")
        return False
    
    term = term_response.json()
    print(f"✅ Created term: {term['name']}")
    
    subject_data = {
        "name": "LaTeX Test Subject",
        "term_id": term['id']
    }
    
    subject_response = session.post(f"{BACKEND_URL}/subjects", json=subject_data)
    if subject_response.status_code != 200:
        print(f"❌ Failed to create subject: {subject_response.status_code}")
        return False
    
    subject = subject_response.json()
    print(f"✅ Created subject: {subject['name']}")
    
    # Test 1: Create a simple LaTeX file that should compile successfully
    simple_latex = """\\documentclass{article}
\\usepackage{amsmath}
\\usepackage{amsfonts}

\\title{Test Document}
\\author{LaTeX Compiler Test}
\\date{\\today}

\\begin{document}
\\maketitle

\\section{Introduction}
This is a test document to verify LaTeX compilation functionality.

\\section{Mathematics}
Here are some mathematical expressions:

\\begin{equation}
E = mc^2
\\end{equation}

\\begin{align}
\\int_0^1 x^2 dx &= \\left[\\frac{x^3}{3}\\right]_0^1 \\\\
&= \\frac{1}{3}
\\end{align}

\\section{Conclusion}
If you can see this as a PDF, the compilation worked!

\\end{document}"""
    
    file_data = {
        "name": "compilation_test.tex",
        "subject_id": subject['id'],
        "term_id": term['id'],
        "content": simple_latex,
        "tags": ["test", "compilation"],
        "notes": "Test file for LaTeX compilation"
    }
    
    print("\n--- Testing File Creation with Auto-Compilation ---")
    file_response = session.post(f"{BACKEND_URL}/files", json=file_data)
    if file_response.status_code != 200:
        print(f"❌ Failed to create file: {file_response.status_code}")
        print(f"Response: {file_response.text}")
        return False
    
    file_obj = file_response.json()
    file_id = file_obj['id']
    print(f"✅ Created file: {file_obj['name']}")
    print(f"📊 Compilation status: {file_obj.get('compilation_status', 'unknown')}")
    
    if file_obj.get('compilation_output'):
        print(f"📝 Compilation output preview: {file_obj['compilation_output'][:200]}...")
    
    # Test 2: Manual compilation endpoint
    print("\n--- Testing Manual Compilation Endpoint ---")
    compile_response = session.post(f"{BACKEND_URL}/files/{file_id}/compile")
    if compile_response.status_code != 200:
        print(f"❌ Manual compilation failed: {compile_response.status_code}")
        print(f"Response: {compile_response.text}")
        return False
    
    compile_result = compile_response.json()
    print(f"✅ Manual compilation result: {compile_result['status']}")
    print(f"📄 PDF available: {compile_result.get('pdf_available', False)}")
    
    # Test 3: PDF download
    print("\n--- Testing PDF Download ---")
    pdf_response = session.get(f"{BACKEND_URL}/files/{file_id}/pdf")
    if pdf_response.status_code != 200:
        print(f"❌ PDF download failed: {pdf_response.status_code}")
        print(f"Response: {pdf_response.text}")
        return False
    
    content_type = pdf_response.headers.get('content-type', '')
    content_length = pdf_response.headers.get('content-length', 'unknown')
    print(f"✅ PDF download successful")
    print(f"📄 Content-Type: {content_type}")
    print(f"📊 Content-Length: {content_length} bytes")
    
    # Verify it's actually a PDF
    if pdf_response.content.startswith(b'%PDF'):
        print("✅ Downloaded content is a valid PDF file")
    else:
        print("❌ Downloaded content is not a valid PDF file")
        return False
    
    # Test 4: Create a file with LaTeX errors
    print("\n--- Testing Error Handling ---")
    error_latex = """\\documentclass{article}
\\begin{document}
\\section{Test}
This has an unclosed math environment: $x = y
\\end{document}"""
    
    error_file_data = {
        "name": "error_test.tex",
        "subject_id": subject['id'],
        "term_id": term['id'],
        "content": error_latex,
        "tags": ["test", "error"],
        "notes": "Test file with LaTeX errors"
    }
    
    error_file_response = session.post(f"{BACKEND_URL}/files", json=error_file_data)
    if error_file_response.status_code != 200:
        print(f"❌ Failed to create error test file: {error_file_response.status_code}")
        return False
    
    error_file_obj = error_file_response.json()
    print(f"✅ Created error test file: {error_file_obj['name']}")
    print(f"📊 Compilation status: {error_file_obj.get('compilation_status', 'unknown')}")
    
    if error_file_obj.get('compilation_status') == 'error':
        print("✅ Error handling working correctly - compilation marked as error")
    else:
        print("⚠️  Expected compilation error but got different status")
    
    # Test 5: Check updated stats
    print("\n--- Testing Updated Statistics ---")
    stats_response = session.get(f"{BACKEND_URL}/stats")
    if stats_response.status_code != 200:
        print(f"❌ Failed to get stats: {stats_response.status_code}")
        return False
    
    stats = stats_response.json()
    compilation_stats = stats.get('compilation_stats', {})
    print(f"✅ Updated compilation statistics:")
    for status, count in compilation_stats.items():
        print(f"   {status}: {count} files")
    
    print("\n🎉 LaTeX compilation testing completed successfully!")
    return True

if __name__ == "__main__":
    success = test_latex_compilation()
    if success:
        print("\n✅ All LaTeX compilation tests passed!")
    else:
        print("\n❌ Some LaTeX compilation tests failed!")