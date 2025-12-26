"""
Validation script for Phase 0 implementation

This script checks that all components are properly configured
and ready for testing.
"""

import os
import sys
from pathlib import Path


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def check_environment():
    """Check environment variables"""
    print_section("1. Environment Configuration")
    
    required_vars = [
        'GOOGLE_CLOUD_PROJECT',
        'FIRESTORE_COLLECTION',
        'VERTEX_AI_LOCATION'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} = {value}")
        else:
            print(f"❌ {var} not set")
            missing.append(var)
    
    return len(missing) == 0


def check_files():
    """Check that all required files exist"""
    print_section("2. Project Structure")
    
    required_files = [
        'main.py',
        'requirements.txt',
        '.env',
        'config/agent_config.yaml',
        'config/prompts.yaml',
        'src/agents/base_agent.py',
        'src/agents/research_agent.py',
        'src/agents/content_agent.py',
        'src/infrastructure/firestore.py',
        'src/infrastructure/cost_tracker.py',
        'src/orchestration/workflow.py',
        'src/monitoring/logger.py',
        'examples/generate_blog_post.py',
        'tests/test_agents.py'
    ]
    
    missing = []
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            missing.append(file)
    
    return len(missing) == 0


def check_imports():
    """Check that Python packages can be imported"""
    print_section("3. Python Dependencies")
    
    packages = [
        ('google.cloud.aiplatform', 'google-cloud-aiplatform'),
        ('google.cloud.firestore', 'google-cloud-firestore'),
        ('google.cloud.logging', 'google-cloud-logging'),
        ('vertexai', 'google-cloud-aiplatform'),
        ('dotenv', 'python-dotenv'),
        ('yaml', 'pyyaml'),
        ('tenacity', 'tenacity')
    ]
    
    missing = []
    for module, package in packages:
        try:
            __import__(module)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} not installed")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Install missing packages:")
        print(f"   pip install {' '.join(missing)}")
    
    return len(missing) == 0


def check_gcp_auth():
    """Check GCP authentication"""
    print_section("4. GCP Authentication")
    
    try:
        from google.auth import default
        credentials, project = default()
        print(f"✅ GCP credentials found")
        print(f"✅ Default project: {project}")
        return True
    except Exception as e:
        print(f"❌ GCP authentication failed: {e}")
        print("\n⚠️  Run: gcloud auth application-default login")
        return False


def check_src_imports():
    """Check that source modules can be imported"""
    print_section("5. Source Code Validation")
    
    try:
        # Add parent directory to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from src.agents import ResearchAgent, ContentGeneratorAgent
        print("✅ Agents module")
        
        from src.infrastructure import FirestoreManager, CostTracker
        print("✅ Infrastructure module")
        
        from src.orchestration import ContentGenerationWorkflow
        print("✅ Orchestration module")
        
        from src.monitoring import StructuredLogger
        print("✅ Monitoring module")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def print_summary(results):
    """Print validation summary"""
    print_section("Validation Summary")
    
    all_passed = all(results.values())
    
    for check, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {check}")
    
    print("\n" + "=" * 80)
    
    if all_passed:
        print("🎉 All validation checks passed!")
        print("\nYou're ready to generate content:")
        print("  python main.py --topic 'Your Topic Here'")
        print("\nOr run the example:")
        print("  python examples/generate_blog_post.py")
    else:
        print("⚠️  Some validation checks failed.")
        print("\nPlease fix the issues above before proceeding.")
        print("See SETUP.md for detailed setup instructions.")
    
    print("=" * 80)


def main():
    """Run all validation checks"""
    print("=" * 80)
    print("  PHASE 0 VALIDATION")
    print("  Multi-Agent Content Generation System")
    print("=" * 80)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run checks
    results = {
        'Environment Configuration': check_environment(),
        'Project Structure': check_files(),
        'Python Dependencies': check_imports(),
        'GCP Authentication': check_gcp_auth(),
        'Source Code Validation': check_src_imports()
    }
    
    # Print summary
    print_summary(results)
    
    # Exit with error code if any check failed
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
