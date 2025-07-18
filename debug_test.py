#!/usr/bin/env python3
"""
Debug specific issues found in the API testing
"""

import requests
import json

BACKEND_URL = "https://6d9b4f3d-a7f0-42bc-be0d-06f77e3ab827.preview.emergentagent.com/api"

def debug_subject_update():
    """Debug the subject update 422 error"""
    session = requests.Session()
    
    # First create a term
    term_data = {
        "name": "Debug Term",
        "description": "Term for debugging"
    }
    
    term_response = session.post(f"{BACKEND_URL}/terms", json=term_data)
    if term_response.status_code != 200:
        print(f"Failed to create term: {term_response.status_code}")
        return
    
    term = term_response.json()
    print(f"Created term: {term['id']}")
    
    # Create a subject
    subject_data = {
        "name": "Debug Subject",
        "description": "Subject for debugging",
        "term_id": term['id'],
        "color": "#FF0000"
    }
    
    subject_response = session.post(f"{BACKEND_URL}/subjects", json=subject_data)
    if subject_response.status_code != 200:
        print(f"Failed to create subject: {subject_response.status_code}")
        return
    
    subject = subject_response.json()
    print(f"Created subject: {subject['id']}")
    
    # Try to update the subject - this is where the 422 error occurs
    update_data = {
        "name": "Debug Subject - Updated",
        "description": "Updated description",
        "term_id": term['id'],  # Include term_id in update
        "color": "#00FF00"
    }
    
    update_response = session.put(f"{BACKEND_URL}/subjects/{subject['id']}", json=update_data)
    print(f"Update response status: {update_response.status_code}")
    print(f"Update response text: {update_response.text}")
    
    if update_response.status_code != 200:
        # Try with minimal update data
        minimal_update = {
            "name": "Debug Subject - Minimal Update"
        }
        minimal_response = session.put(f"{BACKEND_URL}/subjects/{subject['id']}", json=minimal_update)
        print(f"Minimal update status: {minimal_response.status_code}")
        print(f"Minimal update text: {minimal_response.text}")

def debug_bulk_export():
    """Debug the bulk export 500 error"""
    session = requests.Session()
    
    # Get existing files
    files_response = session.get(f"{BACKEND_URL}/files")
    if files_response.status_code != 200:
        print(f"Failed to get files: {files_response.status_code}")
        return
    
    files = files_response.json()
    if not files:
        print("No files available for bulk export test")
        return
    
    # Try bulk export with first file
    file_ids = [files[0]['id']]
    print(f"Attempting bulk export with file IDs: {file_ids}")
    
    export_response = session.post(f"{BACKEND_URL}/export/bulk", json=file_ids)
    print(f"Bulk export status: {export_response.status_code}")
    print(f"Bulk export text: {export_response.text}")

if __name__ == "__main__":
    print("=== Debugging Subject Update Issue ===")
    debug_subject_update()
    
    print("\n=== Debugging Bulk Export Issue ===")
    debug_bulk_export()