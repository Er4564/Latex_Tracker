#!/usr/bin/env python3
"""
Final comprehensive test to verify all core functionality
"""

import requests
import json

BACKEND_URL = "https://6d9b4f3d-a7f0-42bc-be0d-06f77e3ab827.preview.emergentagent.com/api"

def run_final_test():
    """Run a final comprehensive test of all core functionality"""
    session = requests.Session()
    results = []
    
    # Test 1: API Root
    try:
        response = session.get(f"{BACKEND_URL}/")
        results.append(("API Root", response.status_code == 200))
    except:
        results.append(("API Root", False))
    
    # Test 2: Terms CRUD
    try:
        # Create
        term_data = {"name": "Final Test Term", "description": "Test term"}
        response = session.post(f"{BACKEND_URL}/terms", json=term_data)
        term_created = response.status_code == 200
        if term_created:
            term = response.json()
            term_id = term['id']
            
            # Read
            response = session.get(f"{BACKEND_URL}/terms/{term_id}")
            term_read = response.status_code == 200
            
            # Update
            update_data = {"name": "Updated Final Test Term"}
            response = session.put(f"{BACKEND_URL}/terms/{term_id}", json=update_data)
            term_updated = response.status_code == 200
            
            results.append(("Terms CRUD", term_created and term_read and term_updated))
        else:
            results.append(("Terms CRUD", False))
    except:
        results.append(("Terms CRUD", False))
    
    # Test 3: Subjects CRUD
    try:
        if 'term_id' in locals():
            # Create
            subject_data = {"name": "Final Test Subject", "term_id": term_id}
            response = session.post(f"{BACKEND_URL}/subjects", json=subject_data)
            subject_created = response.status_code == 200
            if subject_created:
                subject = response.json()
                subject_id = subject['id']
                
                # Read
                response = session.get(f"{BACKEND_URL}/subjects/{subject_id}")
                subject_read = response.status_code == 200
                
                # Update
                update_data = {"name": "Updated Final Test Subject"}
                response = session.put(f"{BACKEND_URL}/subjects/{subject_id}", json=update_data)
                subject_updated = response.status_code == 200
                
                results.append(("Subjects CRUD", subject_created and subject_read and subject_updated))
            else:
                results.append(("Subjects CRUD", False))
        else:
            results.append(("Subjects CRUD", False))
    except:
        results.append(("Subjects CRUD", False))
    
    # Test 4: Files CRUD
    try:
        if 'subject_id' in locals() and 'term_id' in locals():
            # Create
            file_data = {
                "name": "final_test.tex",
                "subject_id": subject_id,
                "term_id": term_id,
                "content": "\\documentclass{article}\\begin{document}Final test\\end{document}",
                "tags": ["test"]
            }
            response = session.post(f"{BACKEND_URL}/files", json=file_data)
            file_created = response.status_code == 200
            if file_created:
                file_obj = response.json()
                file_id = file_obj['id']
                
                # Read
                response = session.get(f"{BACKEND_URL}/files/{file_id}")
                file_read = response.status_code == 200
                
                # Update
                update_data = {"content": "\\documentclass{article}\\begin{document}Updated final test\\end{document}"}
                response = session.put(f"{BACKEND_URL}/files/{file_id}", json=update_data)
                file_updated = response.status_code == 200
                
                results.append(("Files CRUD", file_created and file_read and file_updated))
            else:
                results.append(("Files CRUD", False))
        else:
            results.append(("Files CRUD", False))
    except:
        results.append(("Files CRUD", False))
    
    # Test 5: Search
    try:
        search_data = {"query": "final"}
        response = session.post(f"{BACKEND_URL}/search", json=search_data)
        results.append(("Search", response.status_code == 200))
    except:
        results.append(("Search", False))
    
    # Test 6: Export
    try:
        if 'file_id' in locals():
            # Single export
            response = session.get(f"{BACKEND_URL}/export/{file_id}")
            single_export = response.status_code == 200
            
            # Bulk export
            response = session.post(f"{BACKEND_URL}/export/bulk", json=[file_id])
            bulk_export = response.status_code == 200
            
            results.append(("Export", single_export and bulk_export))
        else:
            results.append(("Export", False))
    except:
        results.append(("Export", False))
    
    # Test 7: Stats
    try:
        response = session.get(f"{BACKEND_URL}/stats")
        results.append(("Stats", response.status_code == 200))
    except:
        results.append(("Stats", False))
    
    # Print results
    print("=== FINAL TEST RESULTS ===")
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\nFinal Score: {passed}/{total} tests passed")
    return passed == total

if __name__ == "__main__":
    success = run_final_test()
    if success:
        print("\n🎉 All core functionality is working correctly!")
    else:
        print("\n⚠️  Some core functionality issues remain.")