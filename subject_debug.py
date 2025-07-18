#!/usr/bin/env python3
"""
Specific debug for subject update 422 error
"""

import requests
import json

BACKEND_URL = "https://6d9b4f3d-a7f0-42bc-be0d-06f77e3ab827.preview.emergentagent.com/api"

def test_subject_update_validation():
    """Test different subject update scenarios"""
    session = requests.Session()
    
    # Get existing subjects
    subjects_response = session.get(f"{BACKEND_URL}/subjects")
    if subjects_response.status_code != 200:
        print(f"Failed to get subjects: {subjects_response.status_code}")
        return
    
    subjects = subjects_response.json()
    if not subjects:
        print("No subjects available for testing")
        return
    
    subject = subjects[0]
    subject_id = subject['id']
    print(f"Testing with subject: {subject['name']} (ID: {subject_id})")
    
    # Test 1: Update with all fields
    update_data_full = {
        "name": "Updated Subject Name",
        "description": "Updated description",
        "term_id": subject['term_id'],
        "color": "#FF0000"
    }
    
    response = session.put(f"{BACKEND_URL}/subjects/{subject_id}", json=update_data_full)
    print(f"Full update - Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Full update error: {response.text}")
    
    # Test 2: Update with minimal fields
    update_data_minimal = {
        "name": "Minimal Update Name"
    }
    
    response = session.put(f"{BACKEND_URL}/subjects/{subject_id}", json=update_data_minimal)
    print(f"Minimal update - Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Minimal update error: {response.text}")
    
    # Test 3: Update with invalid term_id
    update_data_invalid = {
        "name": "Invalid Term Update",
        "term_id": "non-existent-term-id"
    }
    
    response = session.put(f"{BACKEND_URL}/subjects/{subject_id}", json=update_data_invalid)
    print(f"Invalid term update - Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Invalid term update error: {response.text}")

if __name__ == "__main__":
    test_subject_update_validation()