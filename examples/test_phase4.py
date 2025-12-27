"""
Phase 4 Example: Publishing and Analytics

Demonstrates:
- Publishing content to multiple platforms
- Retrieving analytics
- Performance monitoring
- User management
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.publisher_agent import PublisherAgent
from src.infrastructure.analytics_dashboard import AnalyticsDashboard
from src.infrastructure.platform_integrations import PlatformIntegrationManager
from src.infrastructure.user_management import UserManager, Role, Permission
from src.monitoring.performance_monitor import performance_monitor
from src.orchestration.workflow import ContentGenerationWorkflow


def example_1_publish_content():
    """Example 1: Publish content to multiple platforms"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Publishing Content to Multiple Platforms")
    print("="*80)
    
    publisher = PublisherAgent()
    
    # Sample content to publish
    content = {
        'title': 'The Future of AI in 2026: Top 10 Trends',
        'body': '''Artificial Intelligence continues to revolutionize every industry...
        
        In this comprehensive guide, we explore the top 10 AI trends that will shape 2026:
        
        1. Generative AI Becomes Mainstream
        2. AI-Powered Automation
        3. Ethical AI Development
        4. Edge AI Computing
        5. Multimodal AI Systems
        
        ... (full article content here)
        ''',
        'excerpt': 'Discover the top AI trends that will dominate 2026 and how they will impact your business.',
        'tags': ['AI', 'Technology', 'Innovation', 'Future', 'Trends'],
        'images': [
            'https://example.com/ai-trends-2026.jpg',
            'https://example.com/ai-infographic.jpg'
        ],
        'author': 'Tech Insights Team',
        'seo': {
            'meta_description': 'Explore the top 10 AI trends for 2026 including generative AI, automation, and ethical development.',
            'keywords': ['AI trends', '2026', 'artificial intelligence', 'machine learning']
        }
    }
    
    # Platforms to publish to
    platforms = ['twitter', 'linkedin', 'medium', 'wordpress']
    
    print(f"\n📤 Publishing to platforms: {', '.join(platforms)}")
    
    # Publish content
    result = publisher.execute(
        project_id='demo_project_001',
        platforms=platforms,
        content=content
    )
    
    print(f"\n✅ Publishing Status: {result['status']}")
    print(f"📊 Total Cost: ${result['cost']:.4f}")
    
    print("\n📋 Platform Results:")
    for platform, platform_result in result['results'].items():
        status_icon = "✅" if platform_result['success'] else "❌"
        print(f"  {status_icon} {platform.capitalize()}:")
        print(f"     - URL: {platform_result.get('url', 'N/A')}")
        print(f"     - Status: {platform_result.get('status', 'N/A')}")


def example_2_analytics_dashboard():
    """Example 2: View analytics dashboard"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Analytics Dashboard")
    print("="*80)
    
    dashboard = AnalyticsDashboard()
    
    print("\n📊 Getting Dashboard Summary...")
    summary = dashboard.get_dashboard_summary()
    
    print("\n" + "-"*80)
    print("OVERVIEW")
    print("-"*80)
    overview = summary['overview']
    print(f"Total Projects: {overview['total_projects']}")
    print(f"Active Projects: {overview['active_projects']}")
    print(f"Completed Projects: {overview['completed_projects']}")
    print(f"Total Content Generated: {overview['total_content_generated']}")
    
    print("\n" + "-"*80)
    print("COSTS")
    print("-"*80)
    costs = summary['costs']
    print(f"Total Spent: ${costs['total_spent']:.2f}")
    print(f"This Month: ${costs['this_month']:.2f}")
    print(f"Average per Project: ${costs['average_per_project']:.2f}")
    print(f"Budget Utilization: {costs['budget_utilization']:.1f}%")
    
    print("\n" + "-"*80)
    print("QUALITY METRICS")
    print("-"*80)
    quality = summary['quality']
    print(f"Average Quality Score: {quality['average_quality_score']:.1%}")
    print(f"Content Passing QA: {quality['content_passing_qa']:.1%}")
    
    print("\n" + "-"*80)
    print("ENGAGEMENT")
    print("-"*80)
    engagement = summary['engagement']
    print(f"Total Views: {engagement['total_views']:,}")
    print(f"Total Engagement: {engagement['total_engagement']:,}")
    print(f"Avg Engagement Rate: {engagement['average_engagement_rate']:.1%}")
    
    print("\n" + "-"*80)
    print("TOP PERFORMERS")
    print("-"*80)
    top = summary['top_performers']
    print(f"Best Platform: {top['best_platform'].upper()}")
    print(f"Best Agent: {top['best_agent'].upper()}")
    
    print("\n📈 Top Content:")
    for i, content_item in enumerate(top['best_content'], 1):
        print(f"  {i}. {content_item['title']}")
        print(f"     Views: {content_item['views']:,} | Engagement: {content_item['engagement_rate']:.1%}")


def example_3_platform_comparison():
    """Example 3: Compare platform performance"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Platform Performance Comparison")
    print("="*80)
    
    dashboard = AnalyticsDashboard()
    
    platforms = ['twitter', 'linkedin', 'instagram', 'medium']
    
    print(f"\n📊 Comparing platforms: {', '.join(platforms)}")
    
    comparison = dashboard.get_platform_comparison(platforms=platforms, time_range_days=30)
    
    print("\n" + "-"*80)
    print(f"{'Platform':<12} {'Publications':<15} {'Avg Views':<12} {'Engagement Rate':<18}")
    print("-"*80)
    
    for platform, metrics in comparison['platforms'].items():
        print(f"{platform.capitalize():<12} {metrics['total_publications']:<15} "
              f"{metrics['average_views']:<12.0f} {metrics['engagement_rate']:<18.1%}")
    
    print("\n🏆 Best Platform: " + comparison['best_platform'].upper())
    
    print("\n💡 Recommendations:")
    for i, rec in enumerate(comparison['recommendations'], 1):
        print(f"  {i}. {rec}")


def example_4_agent_performance():
    """Example 4: Monitor agent performance"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Agent Performance Monitoring")
    print("="*80)
    
    dashboard = AnalyticsDashboard()
    
    print("\n📊 Getting Agent Performance Metrics...")
    
    agent_perf = dashboard.get_agent_performance(time_range_days=30)
    
    print("\n" + "-"*80)
    print(f"{'Agent':<20} {'Tasks':<10} {'Avg Time':<12} {'Success':<10} {'Cost':<10}")
    print("-"*80)
    
    for agent_name, metrics in agent_perf['agents'].items():
        print(f"{agent_name.capitalize():<20} {metrics['tasks_completed']:<10} "
              f"{metrics['average_execution_time']:<12.1f}s {metrics['success_rate']:<10.1%} "
              f"${metrics['total_cost']:<9.2f}")
    
    print("\n" + "-"*80)
    print("SUMMARY")
    print("-"*80)
    summary = agent_perf['summary']
    print(f"Total Tasks: {summary['total_tasks']}")
    print(f"Total Cost: ${summary['total_cost']:.2f}")
    print(f"Avg Success Rate: {summary['average_success_rate']:.1%}")
    print(f"Most Used Agent: {summary['most_used_agent'].upper()}")
    print(f"Most Expensive Agent: {summary['most_expensive_agent'].upper()}")


def example_5_user_management():
    """Example 5: User management and permissions"""
    print("\n" + "="*80)
    print("EXAMPLE 5: User Management")
    print("="*80)
    
    user_manager = UserManager()
    
    print("\n👤 Creating new users...")
    
    # Create users with different roles
    users = [
        {
            'email': 'editor@example.com',
            'password': 'editor123',
            'name': 'Jane Editor',
            'role': Role.EDITOR
        },
        {
            'email': 'creator@example.com',
            'password': 'creator123',
            'name': 'John Creator',
            'role': Role.CONTENT_CREATOR
        },
        {
            'email': 'viewer@example.com',
            'password': 'viewer123',
            'name': 'Bob Viewer',
            'role': Role.VIEWER
        }
    ]
    
    created_users = []
    for user_data in users:
        try:
            user = user_manager.create_user(**user_data)
            created_users.append(user)
            print(f"✅ Created user: {user['name']} ({user['role']})")
        except ValueError as e:
            print(f"⚠️  {e}")
    
    print("\n🔐 Testing Authentication...")
    auth_result = user_manager.authenticate('editor@example.com', 'editor123')
    if auth_result:
        print(f"✅ Authentication successful for {auth_result['name']}")
        print(f"   Session Token: {auth_result['session_token'][:20]}...")
    
    print("\n🔑 Testing Permissions...")
    if created_users:
        user = created_users[0]
        user_id = user['user_id']
        
        permissions_to_check = [
            Permission.CREATE_PROJECT,
            Permission.PUBLISH_CONTENT,
            Permission.MANAGE_USERS
        ]
        
        print(f"\nPermissions for {user['name']} ({user['role']}):")
        for perm in permissions_to_check:
            has_perm = user_manager.has_permission(user_id, perm)
            status = "✅" if has_perm else "❌"
            print(f"  {status} {perm.value}")


def example_6_performance_monitoring():
    """Example 6: Real-time performance monitoring"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Performance Monitoring")
    print("="*80)
    
    print("\n⏱️  Tracking Operations...")
    
    # Simulate some operations
    import time
    
    for i in range(5):
        with performance_monitor.track_operation('agent.content'):
            time.sleep(0.1)  # Simulate work
    
    for i in range(3):
        with performance_monitor.track_operation('agent.research'):
            time.sleep(0.05)  # Simulate work
    
    print("\n📊 Performance Metrics:")
    
    metrics = performance_monitor.get_metrics()
    
    print("\n" + "-"*80)
    print(f"{'Operation':<30} {'Count':<10} {'Avg Time':<12} {'Success Rate':<15}")
    print("-"*80)
    
    for op_name, op_metrics in metrics.items():
        print(f"{op_name:<30} {op_metrics['count']:<10} "
              f"{op_metrics['average_time']:<12.4f}s {op_metrics['success_rate']:<15.1%}")
    
    # Check for alerts
    alerts = performance_monitor.get_alerts()
    
    if alerts:
        print("\n⚠️  Active Alerts:")
        for alert in alerts:
            print(f"  [{alert['severity'].upper()}] {alert['message']}")
    else:
        print("\n✅ No performance alerts")


def example_7_complete_workflow():
    """Example 7: Complete workflow with publishing"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Complete Content Generation and Publishing Workflow")
    print("="*80)
    
    workflow = ContentGenerationWorkflow()
    
    print("\n🚀 Starting complete workflow...")
    print("   Topic: AI-Powered Content Creation")
    print("   Platforms: LinkedIn, Medium")
    
    result = workflow.generate_and_publish(
        topic='AI-Powered Content Creation: The Future is Now',
        platforms=['linkedin', 'medium'],
        tone='professional and informative',
        target_word_count=1500
    )
    
    if result['success']:
        print("\n✅ Workflow completed successfully!")
        print(f"\n📝 Project ID: {result['project_id']}")
        
        # Generation results
        gen = result['generation']
        print(f"\n📊 Generation:")
        print(f"   - Word Count: {gen['content'].get('word_count', 'N/A')}")
        print(f"   - Cost: ${gen['project']['costs'].get('total', 0):.4f}")
        
        # Publishing results
        pub = result['publishing']
        print(f"\n📤 Publishing:")
        for platform, platform_result in pub['publishing_results']['results'].items():
            status_icon = "✅" if platform_result['success'] else "❌"
            print(f"   {status_icon} {platform.capitalize()}: {platform_result.get('url', 'N/A')}")
    else:
        print(f"\n❌ Workflow failed: {result.get('error')}")


def main():
    """Run all Phase 4 examples"""
    print("\n" + "="*80)
    print(" "*20 + "PHASE 4 EXAMPLES: Publishing & Analytics")
    print("="*80)
    
    examples = [
        ("Publishing Content", example_1_publish_content),
        ("Analytics Dashboard", example_2_analytics_dashboard),
        ("Platform Comparison", example_3_platform_comparison),
        ("Agent Performance", example_4_agent_performance),
        ("User Management", example_5_user_management),
        ("Performance Monitoring", example_6_performance_monitoring),
        # Skip workflow example for now (requires Phase 2 QA agent update)
        # ("Complete Workflow", example_7_complete_workflow)
    ]
    
    for i, (name, func) in enumerate(examples, 1):
        print(f"\n\n{'='*80}")
        print(f"Running Example {i}/{len(examples)}: {name}")
        print(f"{'='*80}")
        
        try:
            func()
        except Exception as e:
            print(f"\n❌ Error running example: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n\n" + "="*80)
    print(" "*25 + "ALL EXAMPLES COMPLETED")
    print("="*80)


if __name__ == '__main__':
    main()
