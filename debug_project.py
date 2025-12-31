"""
Debug script to show full project data
"""
import os
import json
from dotenv import load_dotenv
from src.infrastructure.firestore import FirestoreManager

load_dotenv()

def show_full_project(project_id):
    """Show complete project data"""
    
    firestore_manager = FirestoreManager()
    project = firestore_manager.get_project(project_id)
    
    if project:
        print(f"\n{'='*70}")
        print(f"FULL PROJECT DATA: {project_id}")
        print(f"{'='*70}\n")
        print(json.dumps(project, indent=2, default=str))
        print(f"\n{'='*70}")
    else:
        print(f"❌ Project not found: {project_id}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        show_full_project(sys.argv[1])
    else:
        print("Usage: python debug_project.py <project_id>")
