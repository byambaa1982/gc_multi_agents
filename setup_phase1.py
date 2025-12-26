"""
Phase 1 Setup Script
Sets up GCP infrastructure for Phase 1 deployment
"""

import os
import sys
from google.cloud import pubsub_v1
from src.infrastructure.pubsub_manager import PubSubManager
from src.monitoring.logger import StructuredLogger


def main():
    """Run Phase 1 infrastructure setup"""
    logger = StructuredLogger(name='setup')
    
    logger.info("=" * 60)
    logger.info("Phase 1 Infrastructure Setup")
    logger.info("=" * 60)
    
    # Check environment variables
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    
    if not project_id:
        logger.error("GOOGLE_CLOUD_PROJECT environment variable not set")
        logger.info("\nPlease set your GCP project ID:")
        logger.info("export GOOGLE_CLOUD_PROJECT='your-project-id'")
        sys.exit(1)
    
    logger.info(f"\nProject ID: {project_id}")
    
    try:
        # Step 1: Setup Pub/Sub infrastructure
        logger.info("\n" + "=" * 60)
        logger.info("Step 1: Setting up Pub/Sub Topics and Subscriptions")
        logger.info("=" * 60)
        
        pubsub_manager = PubSubManager()
        pubsub_manager.setup_infrastructure()
        
        logger.info("✓ Pub/Sub infrastructure created successfully")
        
        # Step 2: Verify Firestore
        logger.info("\n" + "=" * 60)
        logger.info("Step 2: Verifying Firestore Database")
        logger.info("=" * 60)
        
        from src.infrastructure import FirestoreManager
        
        db = FirestoreManager()
        logger.info(f"✓ Firestore connection verified")
        
        # Step 3: Setup Quota Manager
        logger.info("\n" + "=" * 60)
        logger.info("Step 3: Initializing Quota Manager")
        logger.info("=" * 60)
        
        from src.infrastructure import QuotaManager
        
        quota_manager = QuotaManager()
        logger.info("✓ Quota Manager initialized")
        
        # Step 4: Verify Agents
        logger.info("\n" + "=" * 60)
        logger.info("Step 4: Verifying Agents")
        logger.info("=" * 60)
        
        from src.agents import (
            ResearchAgent,
            ContentGeneratorAgent,
            EditorAgent,
            SEOOptimizerAgent
        )
        
        agents = [
            ('Research Agent', ResearchAgent),
            ('Content Generator', ContentGeneratorAgent),
            ('Editor Agent', EditorAgent),
            ('SEO Optimizer', SEOOptimizerAgent)
        ]
        
        for agent_name, agent_class in agents:
            try:
                agent = agent_class()
                logger.info(f"✓ {agent_name} initialized successfully")
            except Exception as e:
                logger.error(f"✗ Failed to initialize {agent_name}: {e}")
                raise
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("Setup Complete!")
        logger.info("=" * 60)
        logger.info("\nPhase 1 infrastructure is ready:")
        logger.info("✓ Pub/Sub topics and subscriptions")
        logger.info("✓ Firestore database connection")
        logger.info("✓ Quota manager")
        logger.info("✓ All agents (Research, Content, Editor, SEO)")
        logger.info("\nNext steps:")
        logger.info("1. Run: python examples/test_phase1.py")
        logger.info("2. Monitor logs in Cloud Logging")
        logger.info("3. Check Firestore for project data")
        
    except Exception as e:
        logger.error(f"\n✗ Setup failed: {e}")
        logger.info("\nPlease ensure:")
        logger.info("1. You have the necessary GCP permissions")
        logger.info("2. Required APIs are enabled:")
        logger.info("   - Pub/Sub API")
        logger.info("   - Firestore API")
        logger.info("   - Vertex AI API")
        logger.info("   - Cloud Logging API")
        logger.info("3. You're authenticated: gcloud auth application-default login")
        sys.exit(1)


if __name__ == '__main__':
    main()
