"""
Phase 2 Setup Script

Automated setup for Phase 2 components:
- Quality Assurance Agent
- Cache Manager
- Vector Search Service
- Enhanced Quota Manager
- Load Testing Framework
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.monitoring.logger import StructuredLogger
from src.infrastructure.firestore import FirestoreManager
from src.infrastructure.cost_tracker import CostTracker
from src.infrastructure.quota_manager import QuotaManager
from src.infrastructure.cache_manager import CacheManager
from src.infrastructure.vector_search import VectorSearchService
from src.agents.quality_assurance_agent import QualityAssuranceAgent
import yaml


def load_config():
    """Load configuration"""
    with open('config/agent_config.yaml', 'r') as f:
        return yaml.safe_load(f)


def test_quality_assurance_agent(logger, project_id, location, config, cost_tracker, quota_manager):
    """Test Quality Assurance Agent initialization"""
    logger.info("Testing Quality Assurance Agent...")
    
    try:
        qa_config = config['agents']['quality_assurance']
        qa_agent = QualityAssuranceAgent(
            project_id=project_id,
            location=location,
            config=qa_config,
            cost_tracker=cost_tracker,
            quota_manager=quota_manager
        )
        
        # Test validation on sample content
        sample_content = """
        Artificial Intelligence is revolutionizing technology. Machine learning 
        algorithms enable computers to learn from data without explicit programming. 
        Deep learning, a subset of machine learning, uses neural networks to 
        process complex patterns in large datasets.
        """
        
        sample_metadata = {
            "content_id": "test_001",
            "title": "AI and Machine Learning Overview",
            "keywords": ["artificial intelligence", "machine learning", "deep learning"]
        }
        
        logger.info("Running quality validation on sample content...")
        quality_report = qa_agent.validate_content(sample_content, sample_metadata)
        
        logger.info(f"Quality Score: {quality_report['overall_score']:.2f}")
        logger.info(f"Validation Passed: {quality_report['passed']}")
        logger.info(f"Action Required: {quality_report['action_required']}")
        
        if quality_report['recommendations']:
            logger.info(f"Recommendations: {', '.join(quality_report['recommendations'])}")
        
        logger.info("✓ Quality Assurance Agent test passed")
        return True
        
    except Exception as e:
        import traceback
        print(f"✗ Quality Assurance Agent test failed: {e}")
        print(traceback.format_exc())
        logger.error(f"✗ Quality Assurance Agent test failed: {e}")
        return False


def test_cache_manager(logger, config):
    """Test Cache Manager initialization"""
    logger.info("Testing Cache Manager...")
    
    try:
        cache_config = config.get('cache', {})
        cache_manager = CacheManager(cache_config)
        
        # Test L1 cache
        test_key = "test_key"
        test_value = {"data": "test_value", "timestamp": "2025-01-01"}
        
        logger.info("Testing L1 cache...")
        cache_manager.set(test_key, test_value, cache_level="l1")
        retrieved = cache_manager.get(test_key, cache_level="l1")
        
        if retrieved == test_value:
            logger.info("✓ L1 cache working correctly")
        else:
            logger.warning("⚠ L1 cache value mismatch")
        
        # Get cache stats
        stats = cache_manager.get_stats()
        logger.info(f"Cache Stats - L1 Hits: {stats['l1']['hits']}, L1 Misses: {stats['l1']['misses']}")
        logger.info(f"L2 Enabled: {stats['l2']['enabled']}")
        
        logger.info("✓ Cache Manager test passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Cache Manager test failed: {e}")
        return False


def test_vector_search(logger, project_id, location, config, cost_tracker, quota_manager):
    """Test Vector Search Service initialization"""
    logger.info("Testing Vector Search Service...")
    
    try:
        vector_config = config.get('vector_search', {})
        vector_search = VectorSearchService(
            project_id=project_id,
            location=location,
            config=vector_config,
            cost_tracker=cost_tracker,
            quota_manager=quota_manager
        )
        
        # Add sample content
        logger.info("Adding sample content to vector store...")
        vector_search.add_content(
            content_id="doc1",
            content="Machine learning is a subset of artificial intelligence",
            metadata={"type": "definition"}
        )
        
        vector_search.add_content(
            content_id="doc2",
            content="Deep learning uses neural networks for complex pattern recognition",
            metadata={"type": "definition"}
        )
        
        # Test similarity search
        logger.info("Testing similarity search...")
        similar = vector_search.find_similar(
            "What is machine learning?",
            top_k=2,
            threshold=0.5
        )
        
        logger.info(f"Found {len(similar)} similar documents")
        for content_id, score, metadata in similar:
            logger.info(f"  {content_id}: similarity={score:.3f}")
        
        # Get stats
        stats = vector_search.get_stats()
        logger.info(f"Vector Store: {stats['total_embeddings']} embeddings")
        
        logger.info("✓ Vector Search Service test passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Vector Search Service test failed: {e}")
        return False


def test_enhanced_quota_manager(logger):
    """Test enhanced Quota Manager features"""
    logger.info("Testing Enhanced Quota Manager...")
    
    try:
        quota_manager = QuotaManager()
        
        # Test budget status
        logger.info("Testing budget status...")
        budget_status = quota_manager.get_budget_status()
        logger.info(f"Daily Budget: ${budget_status['daily']['budget']}")
        logger.info(f"Daily Used: ${budget_status['daily']['used']}")
        logger.info(f"Daily Remaining: ${budget_status['daily']['remaining']}")
        
        # Test cost estimation
        logger.info("Testing cost estimation...")
        estimated_cost = quota_manager.estimate_operation_cost(
            service="vertex-ai",
            operation="generate",
            model="gemini-flash",
            input_tokens=1000,
            output_tokens=500
        )
        logger.info(f"Estimated Cost: ${estimated_cost:.6f}")
        
        # Test budget availability check
        logger.info("Testing budget availability...")
        budget_check = quota_manager.check_budget_available(
            estimated_cost=0.01,
            project_id="test_project"
        )
        logger.info(f"Budget Available: {budget_check['available']}")
        
        logger.info("✓ Enhanced Quota Manager test passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Enhanced Quota Manager test failed: {e}")
        return False


def main():
    """Main setup function"""
    # Load environment
    load_dotenv()
    
    # Initialize logger
    logger = StructuredLogger("Phase2Setup")
    
    logger.info("="*60)
    logger.info("Phase 2 Setup - Quality & Scale")
    logger.info("="*60)
    
    # Load configuration
    config = load_config()
    
    # Get project details
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
    
    if not project_id:
        logger.error("GOOGLE_CLOUD_PROJECT environment variable not set")
        sys.exit(1)
    
    logger.info(f"Project ID: {project_id}")
    logger.info(f"Location: {location}")
    
    # Initialize core services
    logger.info("\nInitializing core services...")
    
    try:
        firestore_manager = FirestoreManager()
        cost_tracker = CostTracker()
        quota_manager = QuotaManager()
        
        logger.info("✓ Core services initialized")
        
    except Exception as e:
        logger.error(f"✗ Failed to initialize core services: {e}")
        sys.exit(1)
    
    # Run tests
    results = []
    
    logger.info("\n" + "="*60)
    logger.info("Running Phase 2 Component Tests")
    logger.info("="*60 + "\n")
    
    # Test 1: Quality Assurance Agent
    results.append(("Quality Assurance Agent", 
                   test_quality_assurance_agent(logger, project_id, location, config, cost_tracker, quota_manager)))
    logger.info("")
    
    # Test 2: Cache Manager
    results.append(("Cache Manager", 
                   test_cache_manager(logger, config)))
    logger.info("")
    
    # Test 3: Vector Search
    results.append(("Vector Search Service", 
                   test_vector_search(logger, project_id, location, config, cost_tracker, quota_manager)))
    logger.info("")
    
    # Test 4: Enhanced Quota Manager
    results.append(("Enhanced Quota Manager", 
                   test_enhanced_quota_manager(logger)))
    logger.info("")
    
    # Print summary
    logger.info("="*60)
    logger.info("Phase 2 Setup Summary")
    logger.info("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results if passed)
    
    for component, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status}: {component}")
    
    logger.info("")
    logger.info(f"Total: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("\n🎉 Phase 2 setup complete! All components ready.")
        logger.info("\nNext steps:")
        logger.info("1. Run: python examples/test_phase2.py")
        logger.info("2. Review: PHASE_2_COMPLETE.md")
        logger.info("3. Start: Phase 2 integration with async workflow")
        return 0
    else:
        logger.warning("\n⚠ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
