"""
Quick test to verify local app can import dependencies
"""
try:
    print("Testing imports...")
    from fastapi import FastAPI
    print("✓ FastAPI imported successfully")
    
    from src.orchestration import ContentGenerationWorkflow
    print("✓ ContentGenerationWorkflow imported successfully")
    
    from src.monitoring import StructuredLogger
    print("✓ StructuredLogger imported successfully")
    
    print("\n✅ All imports successful! App should work.")
    print("\nTo run the app:")
    print("  venv\\Scripts\\python.exe app.py")
    print("\nOr use the batch file:")
    print("  start_local.bat")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    print("\nPlease ensure all dependencies are installed:")
    print("  venv\\Scripts\\pip.exe install -r requirements.txt")
