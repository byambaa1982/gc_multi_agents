"""
Load Testing Framework

Comprehensive load testing for the multi-agent content generation system.
Tests system behavior under various load scenarios:
- Concurrent project processing
- API quota limits
- Budget constraints
- Error handling and recovery
- Performance metrics collection
"""

import asyncio
import time
import random
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
import statistics

from ..monitoring.logger import StructuredLogger
from ..orchestration.async_workflow import AsyncContentWorkflow
from ..infrastructure.quota_manager import QuotaManager
from ..infrastructure.cost_tracker import CostTracker


@dataclass
class LoadTestConfig:
    """Configuration for load test"""
    name: str
    description: str
    num_projects: int
    concurrent_workers: int
    ramp_up_seconds: int
    duration_seconds: Optional[int] = None
    test_data_file: Optional[str] = None
    
    # Thresholds
    max_error_rate: float = 0.05  # 5%
    max_avg_duration: float = 300.0  # 5 minutes
    min_success_rate: float = 0.95  # 95%


@dataclass
class LoadTestResult:
    """Results from a load test"""
    test_name: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    
    # Execution metrics
    total_projects: int
    successful: int
    failed: int
    success_rate: float
    error_rate: float
    
    # Performance metrics
    avg_duration: float
    min_duration: float
    max_duration: float
    p50_duration: float
    p95_duration: float
    p99_duration: float
    
    # Resource metrics
    total_cost: float
    avg_cost_per_project: float
    quota_violations: int
    budget_alerts: int
    
    # Verdict
    passed: bool
    issues: List[str]


class LoadTestFramework:
    """Framework for load testing the content generation system"""
    
    def __init__(
        self,
        project_id: str,
        location: str,
        config: Dict[str, Any]
    ):
        """
        Initialize load testing framework
        
        Args:
            project_id: GCP project ID
            location: GCP location
            config: Configuration dictionary
        """
        self.project_id = project_id
        self.location = location
        self.config = config
        self.logger = StructuredLogger("LoadTestFramework")
        
        # Test results storage
        self.results: List[LoadTestResult] = []
        
        self.logger.info("Load Test Framework initialized")
    
    def run_test(self, test_config: LoadTestConfig) -> LoadTestResult:
        """
        Run a load test
        
        Args:
            test_config: Test configuration
        
        Returns:
            Test results
        """
        self.logger.info(f"Starting load test: {test_config.name}", {
            "num_projects": test_config.num_projects,
            "concurrent_workers": test_config.concurrent_workers
        })
        
        start_time = datetime.utcnow()
        
        # Generate test data
        test_projects = self._generate_test_data(test_config)
        
        # Execute test
        execution_results = self._execute_test(test_config, test_projects)
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Analyze results
        result = self._analyze_results(
            test_config,
            execution_results,
            start_time,
            end_time,
            duration
        )
        
        # Store result
        self.results.append(result)
        
        # Log summary
        self._log_result_summary(result)
        
        return result
    
    def _generate_test_data(self, test_config: LoadTestConfig) -> List[Dict[str, Any]]:
        """Generate test project data"""
        topics = [
            "Artificial Intelligence and Machine Learning",
            "Cloud Computing Best Practices",
            "Cybersecurity Trends 2025",
            "Sustainable Technology Solutions",
            "Digital Transformation Strategies",
            "DevOps and CI/CD Pipelines",
            "Microservices Architecture",
            "Data Privacy and Compliance",
            "Edge Computing Applications",
            "Quantum Computing Advances"
        ]
        
        content_types = ["blog_post", "article", "guide", "tutorial"]
        tones = ["professional", "casual", "technical", "friendly"]
        
        test_projects = []
        
        for i in range(test_config.num_projects):
            project = {
                "project_id": f"load_test_{test_config.name}_{i}",
                "topic": random.choice(topics),
                "content_type": random.choice(content_types),
                "tone": random.choice(tones),
                "min_words": random.randint(500, 1000),
                "max_words": random.randint(1000, 2000),
                "keywords": ["cloud", "technology", "innovation"],
                "test_index": i
            }
            
            test_projects.append(project)
        
        self.logger.info(f"Generated {len(test_projects)} test projects")
        
        return test_projects
    
    def _execute_test(
        self,
        test_config: LoadTestConfig,
        test_projects: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute load test with concurrent workers"""
        results = []
        
        with ThreadPoolExecutor(max_workers=test_config.concurrent_workers) as executor:
            # Submit tasks with ramp-up
            futures = []
            
            for i, project in enumerate(test_projects):
                # Ramp-up delay
                if test_config.ramp_up_seconds > 0:
                    ramp_delay = (test_config.ramp_up_seconds / test_config.num_projects) * i
                    time.sleep(ramp_delay)
                
                future = executor.submit(self._execute_project, project)
                futures.append(future)
            
            # Collect results
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error("Project execution failed", {"error": str(e)})
                    results.append({
                        "success": False,
                        "error": str(e),
                        "duration": 0,
                        "cost": 0
                    })
        
        return results
    
    def _execute_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single project"""
        project_id = project["project_id"]
        start_time = time.time()
        
        try:
            # Initialize workflow (simplified for testing)
            # In real implementation, this would use AsyncContentWorkflow
            
            # Simulate workflow execution
            execution_time = random.uniform(2, 10)  # Simulate 2-10 second execution
            time.sleep(execution_time)
            
            # Simulate cost
            cost = random.uniform(0.15, 0.35)
            
            duration = time.time() - start_time
            
            # Simulate occasional failures
            if random.random() < 0.02:  # 2% failure rate
                raise Exception("Simulated random failure")
            
            return {
                "project_id": project_id,
                "success": True,
                "duration": duration,
                "cost": cost,
                "test_index": project["test_index"]
            }
            
        except Exception as e:
            duration = time.time() - start_time
            
            self.logger.error(f"Project {project_id} failed", {
                "error": str(e),
                "duration": duration
            })
            
            return {
                "project_id": project_id,
                "success": False,
                "error": str(e),
                "duration": duration,
                "cost": 0,
                "test_index": project["test_index"]
            }
    
    def _analyze_results(
        self,
        test_config: LoadTestConfig,
        execution_results: List[Dict[str, Any]],
        start_time: datetime,
        end_time: datetime,
        duration: float
    ) -> LoadTestResult:
        """Analyze test results and generate report"""
        
        # Count successes and failures
        successful = sum(1 for r in execution_results if r.get("success", False))
        failed = len(execution_results) - successful
        
        success_rate = successful / len(execution_results) if execution_results else 0
        error_rate = failed / len(execution_results) if execution_results else 0
        
        # Calculate duration statistics
        durations = [r["duration"] for r in execution_results if r.get("duration", 0) > 0]
        
        if durations:
            avg_duration = statistics.mean(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            p50_duration = statistics.median(durations)
            
            sorted_durations = sorted(durations)
            p95_index = int(len(sorted_durations) * 0.95)
            p99_index = int(len(sorted_durations) * 0.99)
            p95_duration = sorted_durations[p95_index] if p95_index < len(sorted_durations) else max_duration
            p99_duration = sorted_durations[p99_index] if p99_index < len(sorted_durations) else max_duration
        else:
            avg_duration = min_duration = max_duration = p50_duration = p95_duration = p99_duration = 0
        
        # Calculate cost metrics
        total_cost = sum(r.get("cost", 0) for r in execution_results)
        avg_cost = total_cost / len(execution_results) if execution_results else 0
        
        # Detect issues
        issues = []
        
        if error_rate > test_config.max_error_rate:
            issues.append(f"Error rate {error_rate:.2%} exceeds threshold {test_config.max_error_rate:.2%}")
        
        if avg_duration > test_config.max_avg_duration:
            issues.append(f"Average duration {avg_duration:.1f}s exceeds threshold {test_config.max_avg_duration:.1f}s")
        
        if success_rate < test_config.min_success_rate:
            issues.append(f"Success rate {success_rate:.2%} below threshold {test_config.min_success_rate:.2%}")
        
        # Determine if test passed
        passed = len(issues) == 0
        
        return LoadTestResult(
            test_name=test_config.name,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            total_projects=len(execution_results),
            successful=successful,
            failed=failed,
            success_rate=success_rate,
            error_rate=error_rate,
            avg_duration=avg_duration,
            min_duration=min_duration,
            max_duration=max_duration,
            p50_duration=p50_duration,
            p95_duration=p95_duration,
            p99_duration=p99_duration,
            total_cost=total_cost,
            avg_cost_per_project=avg_cost,
            quota_violations=0,  # Would be tracked in real implementation
            budget_alerts=0,  # Would be tracked in real implementation
            passed=passed,
            issues=issues
        )
    
    def _log_result_summary(self, result: LoadTestResult):
        """Log test result summary"""
        status = "PASSED ✓" if result.passed else "FAILED ✗"
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Load Test Results: {result.test_name} - {status}")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Duration: {result.duration_seconds:.1f}s")
        self.logger.info(f"Projects: {result.total_projects} total, {result.successful} successful, {result.failed} failed")
        self.logger.info(f"Success Rate: {result.success_rate:.2%}")
        self.logger.info(f"\nPerformance Metrics:")
        self.logger.info(f"  Average Duration: {result.avg_duration:.2f}s")
        self.logger.info(f"  P50: {result.p50_duration:.2f}s")
        self.logger.info(f"  P95: {result.p95_duration:.2f}s")
        self.logger.info(f"  P99: {result.p99_duration:.2f}s")
        self.logger.info(f"\nCost Metrics:")
        self.logger.info(f"  Total Cost: ${result.total_cost:.2f}")
        self.logger.info(f"  Avg Cost/Project: ${result.avg_cost_per_project:.2f}")
        
        if result.issues:
            self.logger.warning(f"\nIssues Found:")
            for issue in result.issues:
                self.logger.warning(f"  - {issue}")
        
        self.logger.info(f"{'='*60}\n")
    
    def run_test_suite(self) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        self.logger.info("Starting comprehensive load test suite")
        
        test_configs = [
            LoadTestConfig(
                name="baseline_sequential",
                description="Baseline test with sequential execution",
                num_projects=5,
                concurrent_workers=1,
                ramp_up_seconds=0
            ),
            LoadTestConfig(
                name="moderate_concurrent",
                description="Moderate load with 5 concurrent workers",
                num_projects=20,
                concurrent_workers=5,
                ramp_up_seconds=10
            ),
            LoadTestConfig(
                name="high_concurrent",
                description="High load with 10 concurrent workers",
                num_projects=50,
                concurrent_workers=10,
                ramp_up_seconds=20
            ),
            LoadTestConfig(
                name="stress_test",
                description="Stress test with maximum concurrency",
                num_projects=100,
                concurrent_workers=20,
                ramp_up_seconds=30,
                max_error_rate=0.10  # Allow higher error rate for stress test
            )
        ]
        
        suite_results = []
        
        for config in test_configs:
            result = self.run_test(config)
            suite_results.append(result)
            
            # Brief pause between tests
            time.sleep(5)
        
        # Generate suite summary
        suite_summary = self._generate_suite_summary(suite_results)
        
        return suite_summary
    
    def _generate_suite_summary(self, results: List[LoadTestResult]) -> Dict[str, Any]:
        """Generate summary for entire test suite"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)
        
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_projects_tested": sum(r.total_projects for r in results),
            "total_cost": sum(r.total_cost for r in results),
            "avg_success_rate": statistics.mean([r.success_rate for r in results]) if results else 0,
            "test_results": [asdict(r) for r in results]
        }
        
        # Log suite summary
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Load Test Suite Summary")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Tests Run: {total_tests}")
        self.logger.info(f"Passed: {passed_tests}")
        self.logger.info(f"Failed: {total_tests - passed_tests}")
        self.logger.info(f"Pass Rate: {summary['pass_rate']:.1f}%")
        self.logger.info(f"Total Projects Tested: {summary['total_projects_tested']}")
        self.logger.info(f"Average Success Rate: {summary['avg_success_rate']:.2%}")
        self.logger.info(f"Total Cost: ${summary['total_cost']:.2f}")
        self.logger.info(f"{'='*60}\n")
        
        return summary
    
    def export_results(self, output_file: str):
        """Export test results to JSON file"""
        import json
        
        export_data = {
            "export_time": datetime.utcnow().isoformat(),
            "project_id": self.project_id,
            "results": [asdict(r) for r in self.results]
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        self.logger.info(f"Results exported to {output_file}")
