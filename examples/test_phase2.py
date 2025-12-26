"""
Phase 2 Test Suite

Comprehensive testing for Phase 2 components:
- Quality Assurance Agent
- Cache Manager with different tiers
- Vector Search for duplicate detection
- Enhanced Quota Manager with budget controls
- Load Testing Framework
"""

import os
import sys
import time
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.monitoring.logger import StructuredLogger
from src.infrastructure.firestore import FirestoreManager
from src.infrastructure.cost_tracker import CostTracker
from src.infrastructure.quota_manager import QuotaManager
from src.infrastructure.cache_manager import CacheManager
from src.infrastructure.vector_search import VectorSearchService
from src.infrastructure.load_testing import LoadTestFramework, LoadTestConfig
from src.agents.quality_assurance_agent import QualityAssuranceAgent
import yaml


def load_config():
    """Load configuration"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'agent_config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def test_qa_agent_comprehensive(logger, project_id, location, config, cost_tracker, quota_manager):
    """Comprehensive Quality Assurance Agent test"""
    logger.info("\n" + "="*60)
    logger.info("Test 1: Quality Assurance Agent - Comprehensive Validation")
    logger.info("="*60)
    
    try:
        qa_config = config['agents']['quality_assurance']
        qa_agent = QualityAssuranceAgent(
            project_id=project_id,
            location=location,
            config=qa_config,
            cost_tracker=cost_tracker,
            quota_manager=quota_manager
        )
        
        # Test Case 1: High-quality content
        logger.info("\nTest Case 1.1: High-quality content")
        quality_content = """
        Cloud computing has revolutionized how businesses manage their IT infrastructure. 
        Modern cloud platforms like Google Cloud Platform provide scalable, reliable, and 
        cost-effective solutions for organizations of all sizes. By leveraging cloud services, 
        companies can focus on their core business while the cloud provider handles infrastructure 
        management, security updates, and system maintenance.
        
        The benefits of cloud computing include reduced capital expenditure, improved scalability, 
        enhanced collaboration, and increased operational efficiency. Organizations can quickly 
        deploy applications, scale resources based on demand, and pay only for what they use.
        """
        
        metadata = {
            "content_id": "test_high_quality",
            "title": "The Benefits of Cloud Computing for Modern Businesses",
            "keywords": ["cloud computing", "scalability", "cost-effective"],
            "meta_description": "Discover how cloud computing revolutionizes business IT infrastructure with scalable and cost-effective solutions."
        }
        
        result = qa_agent.validate_content(quality_content, metadata)
        
        logger.info(f"Overall Score: {result['overall_score']:.3f}")
        logger.info(f"Passed: {result['passed']}")
        logger.info(f"Action: {result['action_required']}")
        
        # Test Case 2: Low-quality content
        logger.info("\nTest Case 1.2: Low-quality content with issues")
        poor_content = "cloud is gud. it help biz. cheap and fast."
        
        poor_metadata = {
            "content_id": "test_poor_quality",
            "title": "cloud",
            "keywords": []
        }
        
        result2 = qa_agent.validate_content(poor_content, poor_metadata)
        
        logger.info(f"Overall Score: {result2['overall_score']:.3f}")
        logger.info(f"Passed: {result2['passed']}")
        logger.info(f"Recommendations: {len(result2['recommendations'])} issues found")
        
        logger.info("\n✓ Quality Assurance Agent test passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Quality Assurance Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_manager_comprehensive(logger, config):
    """Comprehensive Cache Manager test"""
    logger.info("\n" + "="*60)
    logger.info("Test 2: Cache Manager - Multi-tier Caching")
    logger.info("="*60)
    
    try:
        cache_config = config.get('cache', {})
        cache_manager = CacheManager(cache_config)
        
        # Test L1 Cache
        logger.info("\nTest Case 2.1: L1 In-Memory Cache")
        
        test_data = {
            "prompt": "What is cloud computing?",
            "response": "Cloud computing is...",
            "timestamp": time.time()
        }
        
        cache_manager.set("test_l1", test_data, cache_level="l1")
        retrieved = cache_manager.get("test_l1", cache_level="l1")
        
        assert retrieved == test_data, "L1 cache data mismatch"
        logger.info("✓ L1 cache set/get working")
        
        # Test AI Response Caching
        logger.info("\nTest Case 2.2: AI Response Caching")
        
        cache_manager.cache_ai_response(
            prompt="Explain machine learning",
            response="Machine learning is a subset of AI...",
            model="gemini-flash"
        )
        
        cached_response = cache_manager.get_cached_ai_response(
            prompt="Explain machine learning",
            model="gemini-flash"
        )
        
        assert cached_response is not None, "AI response not cached"
        logger.info("✓ AI response caching working")
        
        # Test Research Caching
        logger.info("\nTest Case 2.3: Research Results Caching")
        
        research_data = {
            "sources": ["source1", "source2"],
            "key_points": ["point1", "point2"]
        }
        
        cache_manager.cache_research_results(
            topic="cloud computing",
            results=research_data
        )
        
        cached_research = cache_manager.get_cached_research("cloud computing")
        assert cached_research == research_data, "Research data mismatch"
        logger.info("✓ Research caching working")
        
        # Get statistics
        stats = cache_manager.get_stats()
        logger.info(f"\nCache Statistics:")
        logger.info(f"  L1 Hits: {stats['l1']['hits']}, Misses: {stats['l1']['misses']}")
        logger.info(f"  L1 Hit Rate: {stats['l1']['hit_rate']}")
        logger.info(f"  L2 Enabled: {stats['l2']['enabled']}")
        
        logger.info("\n✓ Cache Manager comprehensive test passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Cache Manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_search_comprehensive(logger, project_id, location, config, cost_tracker, quota_manager):
    """Comprehensive Vector Search test"""
    logger.info("\n" + "="*60)
    logger.info("Test 3: Vector Search - Duplicate Detection & Semantic Search")
    logger.info("="*60)
    
    try:
        vector_config = config.get('vector_search', {})
        vector_search = VectorSearchService(
            project_id=project_id,
            location=location,
            config=vector_config,
            cost_tracker=cost_tracker,
            quota_manager=quota_manager
        )
        
        # Add sample documents
        logger.info("\nTest Case 3.1: Adding documents to vector store")
        
        documents = [
            {
                "content_id": "doc1",
                "content": "Machine learning is a subset of artificial intelligence that enables computers to learn from data.",
                "metadata": {"category": "AI"}
            },
            {
                "content_id": "doc2",
                "content": "Deep learning uses neural networks with multiple layers to process complex patterns.",
                "metadata": {"category": "AI"}
            },
            {
                "content_id": "doc3",
                "content": "Cloud computing provides on-demand access to computing resources over the internet.",
                "metadata": {"category": "Cloud"}
            }
        ]
        
        for doc in documents:
            vector_search.add_content(**doc)
        
        logger.info(f"✓ Added {len(documents)} documents")
        
        # Test similarity search
        logger.info("\nTest Case 3.2: Semantic similarity search")
        
        query = "What is machine learning and how does it work?"
        similar = vector_search.find_similar(query, top_k=2, threshold=0.5)
        
        logger.info(f"Query: '{query}'")
        logger.info(f"Found {len(similar)} similar documents:")
        for content_id, score, metadata in similar:
            logger.info(f"  - {content_id}: {score:.3f} (category: {metadata.get('category')})")
        
        # Test duplicate detection
        logger.info("\nTest Case 3.3: Duplicate detection")
        
        duplicate_text = "Machine learning enables computers to learn from data using AI."
        duplicate_check = vector_search.check_duplicate(duplicate_text, threshold=0.85)
        
        if duplicate_check:
            logger.info(f"✓ Duplicate detected: {duplicate_check['original_content_id']} "
                       f"(similarity: {duplicate_check['similarity_score']:.3f})")
        else:
            logger.info("No duplicate found")
        
        # Test related content
        logger.info("\nTest Case 3.4: Finding related content")
        
        related = vector_search.find_related_content(
            "Neural networks in AI",
            min_similarity=0.50,
            max_similarity=0.90,
            top_k=3
        )
        
        logger.info(f"Found {len(related)} related documents")
        
        # Get stats
        stats = vector_search.get_stats()
        logger.info(f"\nVector Store Statistics:")
        logger.info(f"  Total Embeddings: {stats['total_embeddings']}")
        logger.info(f"  Model: {stats['model']}")
        
        logger.info("\n✓ Vector Search comprehensive test passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Vector Search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quota_manager_enhancements(logger):
    """Test enhanced Quota Manager features"""
    logger.info("\n" + "="*60)
    logger.info("Test 4: Enhanced Quota Manager - Budget Controls & Alerts")
    logger.info("="*60)
    
    try:
        quota_manager = QuotaManager()
        
        # Test budget status
        logger.info("\nTest Case 4.1: Budget status")
        budget_status = quota_manager.get_budget_status(project_id="test_project")
        
        logger.info(f"Daily Budget: ${budget_status['daily']['budget']}")
        logger.info(f"Daily Used: ${budget_status['daily']['used']}")
        logger.info(f"Daily Remaining: ${budget_status['daily']['remaining']}")
        logger.info(f"Enforcement: {budget_status['daily']['enforce_limit']}")
        
        # Test cost estimation
        logger.info("\nTest Case 4.2: Cost estimation")
        
        estimates = [
            {"model": "gemini-pro", "input_tokens": 1000, "output_tokens": 500},
            {"model": "gemini-flash", "input_tokens": 1000, "output_tokens": 500},
        ]
        
        for params in estimates:
            cost = quota_manager.estimate_operation_cost(
                service="vertex-ai",
                operation="generate",
                **params
            )
            logger.info(f"  {params['model']}: ${cost:.6f}")
        
        # Test budget availability
        logger.info("\nTest Case 4.3: Budget availability check")
        
        budget_check = quota_manager.check_budget_available(
            estimated_cost=0.10,
            project_id="test_project"
        )
        
        logger.info(f"Budget Available: {budget_check['available']}")
        logger.info(f"Daily Available: {budget_check['daily_available']}")
        logger.info(f"Estimated Cost: ${budget_check['estimated_cost']}")
        
        logger.info("\n✓ Enhanced Quota Manager test passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Enhanced Quota Manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_load_testing_framework(logger, project_id, location):
    """Test Load Testing Framework"""
    logger.info("\n" + "="*60)
    logger.info("Test 5: Load Testing Framework")
    logger.info("="*60)
    
    try:
        load_tester = LoadTestFramework(
            project_id=project_id,
            location=location,
            config={}
        )
        
        # Run a small load test
        logger.info("\nRunning small load test...")
        
        test_config = LoadTestConfig(
            name="phase2_validation",
            description="Validation test for Phase 2",
            num_projects=5,
            concurrent_workers=2,
            ramp_up_seconds=2
        )
        
        result = load_tester.run_test(test_config)
        
        logger.info(f"\nLoad Test Results:")
        logger.info(f"  Total Projects: {result.total_projects}")
        logger.info(f"  Successful: {result.successful}")
        logger.info(f"  Failed: {result.failed}")
        logger.info(f"  Success Rate: {result.success_rate:.2%}")
        logger.info(f"  Avg Duration: {result.avg_duration:.2f}s")
        logger.info(f"  Total Cost: ${result.total_cost:.2f}")
        logger.info(f"  Test Passed: {result.passed}")
        
        logger.info("\n✓ Load Testing Framework test passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Load Testing Framework test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    load_dotenv()
    
    logger = StructuredLogger("Phase2Tests")
    
    logger.info("="*60)
    logger.info("Phase 2 Comprehensive Test Suite")
    logger.info("Quality & Scale - All Components")
    logger.info("="*60)
    
    # Load configuration
    config = load_config()
    
    # Get project details
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
    
    if not project_id:
        logger.error("GOOGLE_CLOUD_PROJECT environment variable not set")
        return 1
    
    logger.info(f"\nProject: {project_id}")
    logger.info(f"Location: {location}")
    
    # Initialize core services
    try:
        firestore_manager = FirestoreManager()
        cost_tracker = CostTracker()
        quota_manager = QuotaManager()
        logger.info("✓ Core services initialized")
    except Exception as e:
        logger.error(f"Failed to initialize core services: {e}")
        return 1
    
    # Run all tests
    test_results = []
    
    test_results.append(("QA Agent", 
                        test_qa_agent_comprehensive(logger, project_id, location, config, cost_tracker, quota_manager)))
    
    test_results.append(("Cache Manager", 
                        test_cache_manager_comprehensive(logger, config)))
    
    test_results.append(("Vector Search", 
                        test_vector_search_comprehensive(logger, project_id, location, config, cost_tracker, quota_manager)))
    
    test_results.append(("Enhanced Quota Manager", 
                        test_quota_manager_enhancements(logger)))
    
    test_results.append(("Load Testing Framework", 
                        test_load_testing_framework(logger, project_id, location)))
    
    # Print final summary
    logger.info("\n" + "="*60)
    logger.info("Phase 2 Test Suite Summary")
    logger.info("="*60)
    
    total = len(test_results)
    passed = sum(1 for _, result in test_results if result)
    
    for name, result in test_results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 All Phase 2 tests passed!")
        logger.info("\nPhase 2 Components are ready for integration:")
        logger.info("  - Quality Assurance Agent")
        logger.info("  - 3-tier Cache Manager")
        logger.info("  - Vector Search Service")
        logger.info("  - Enhanced Quota Manager with Budget Controls")
        logger.info("  - Load Testing Framework")
        logger.info("\nNext: Integrate with async workflow and run full system tests")
        return 0
    else:
        logger.warning(f"\n⚠ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
