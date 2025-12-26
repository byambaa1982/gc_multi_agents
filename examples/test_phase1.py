"""
Phase 1 Test Script
Tests the complete Phase 1 workflow with all agents
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.orchestration.async_workflow import AsyncContentWorkflow
from src.monitoring.logger import StructuredLogger


def test_async_workflow():
    """Test the async workflow end-to-end"""
    import threading
    logger = StructuredLogger(name='test_phase1')
    
    logger.info("=" * 60)
    logger.info("Phase 1 Async Workflow Test")
    logger.info("=" * 60)
    
    try:
        # Initialize workflow
        logger.info("\nInitializing async workflow...")
        workflow = AsyncContentWorkflow()
        
        # Set up event handlers
        logger.info("Setting up event handlers...")
        workflow.setup_event_handlers()
        
        # Start event loop in background thread
        logger.info("Starting event loop in background...")
        event_thread = threading.Thread(target=workflow.run_event_loop, daemon=True)
        event_thread.start()
        time.sleep(2)  # Give it time to start
        
        # Start a test workflow
        test_topic = "The Future of Artificial Intelligence in Healthcare"
        logger.info(f"\nStarting workflow for topic: {test_topic}")
        
        project_id = workflow.start_workflow(
            topic=test_topic,
            tone='professional and informative',
            target_word_count=1200,
            primary_keyword='AI in healthcare'
        )
        
        logger.info(f"✓ Workflow started with project ID: {project_id}")
        
        # Monitor workflow progress
        logger.info("\nMonitoring workflow progress...")
        logger.info("(Press Ctrl+C to stop monitoring)")
        
        max_wait = 300  # 5 minutes max
        start_time = time.time()
        last_status = None
        
        while time.time() - start_time < max_wait:
            status = workflow.get_workflow_status(project_id)
            current_status = status['status']
            
            if current_status != last_status:
                logger.info(f"\nStatus: {current_status}")
                logger.info(f"Completed stages: {', '.join(status['completed_stages'])}")
                logger.info(f"Total cost so far: ${status['costs'].get('total', 0):.4f}")
                last_status = current_status
            
            if current_status == 'completed':
                logger.info("\n" + "=" * 60)
                logger.info("✓ Workflow Completed Successfully!")
                logger.info("=" * 60)
                
                # Display results
                logger.info(f"\nProject ID: {project_id}")
                logger.info(f"Total Cost: ${status['costs'].get('total', 0):.4f}")
                logger.info(f"Duration: {time.time() - start_time:.1f} seconds")
                logger.info(f"\nCompleted Stages:")
                for stage in status['completed_stages']:
                    logger.info(f"  ✓ {stage}")
                
                logger.info(f"\nView full results in Firestore:")
                logger.info(f"Collection: content_projects")
                logger.info(f"Document ID: {project_id}")
                
                return True
            
            elif current_status == 'failed':
                logger.error("\n✗ Workflow Failed")
                logger.error(f"Errors: {status.get('errors', [])}")
                return False
            
            time.sleep(5)  # Check every 5 seconds
        
        logger.warning("\n⚠ Workflow monitoring timeout")
        logger.info("The workflow may still be running in the background")
        logger.info(f"Check project status with ID: {project_id}")
        
    except KeyboardInterrupt:
        logger.info("\n\nMonitoring stopped by user")
        logger.info(f"Project ID: {project_id}")
        logger.info("The workflow continues running in the background")
    
    except Exception as e:
        logger.error(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quota_manager():
    """Test quota manager functionality"""
    logger = StructuredLogger(name='test_quota')
    
    logger.info("\n" + "=" * 60)
    logger.info("Testing Quota Manager")
    logger.info("=" * 60)
    
    try:
        from src.infrastructure import QuotaManager
        
        quota_manager = QuotaManager()
        
        # Test quota check
        logger.info("\nChecking quota for Vertex AI...")
        result = quota_manager.check_quota('vertex_ai_gemini_pro', 'request', 1)
        
        if result['allowed']:
            logger.info(f"✓ Quota available")
            logger.info(f"  Tokens remaining: {result['tokens_remaining']}")
        else:
            logger.warning(f"⚠ Quota limit reached")
            logger.warning(f"  Wait time: {result['wait_time_seconds']} seconds")
        
        # Test usage report
        logger.info("\nGenerating usage report...")
        report = quota_manager.get_usage_report(hours=24)
        
        logger.info(f"✓ Usage Report (last 24 hours):")
        logger.info(f"  Total requests: {report.get('total_requests', 0)}")
        logger.info(f"  Total cost: ${report.get('total_cost', 0):.4f}")
        logger.info(f"  Daily budget: ${report['budget_status']['daily_budget']:.2f}")
        logger.info(f"  Daily used: ${report['budget_status']['daily_used']:.4f}")
        logger.info(f"  Daily remaining: ${report['budget_status']['daily_remaining']:.4f}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Quota manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Phase 1 tests"""
    logger = StructuredLogger(name='test_main')
    
    logger.info("=" * 60)
    logger.info("Phase 1 Test Suite")
    logger.info("=" * 60)
    
    results = []
    
    # Test 1: Quota Manager
    logger.info("\n[Test 1/2] Quota Manager")
    results.append(('Quota Manager', test_quota_manager()))
    
    # Test 2: Async Workflow
    logger.info("\n[Test 2/2] Async Workflow")
    results.append(('Async Workflow', test_async_workflow()))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        logger.info("\n✓ All tests passed!")
        logger.info("Phase 1 is working correctly")
        sys.exit(0)
    else:
        logger.error("\n✗ Some tests failed")
        logger.error("Please review the errors above")
        sys.exit(1)


if __name__ == '__main__':
    main()
