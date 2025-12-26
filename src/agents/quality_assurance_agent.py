"""
Quality Assurance Agent

Validates content quality across multiple dimensions:
- Plagiarism detection
- Grammar and readability validation
- Brand voice consistency
- SEO compliance
- Content safety checks
- Fact-checking validation
"""

import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

import vertexai
from vertexai.generative_models import GenerativeModel

from ..monitoring.logger import StructuredLogger
from ..infrastructure.cost_tracker import CostTracker
from ..infrastructure.quota_manager import QuotaManager


class QualityAssuranceAgent:
    """Quality Assurance Agent for comprehensive content validation"""
    
    def __init__(
        self,
        project_id: str,
        location: str,
        config: Dict[str, Any],
        cost_tracker: CostTracker,
        quota_manager: QuotaManager
    ):
        """
        Initialize Quality Assurance Agent
        
        Args:
            project_id: GCP project ID
            location: GCP location
            config: Agent configuration
            cost_tracker: Cost tracking service
            quota_manager: Quota management service
        """
        self.project_id = project_id
        self.location = location
        self.config = config
        self.cost_tracker = cost_tracker
        self.quota_manager = quota_manager
        self.logger = StructuredLogger("QualityAssuranceAgent")
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Initialize Gemini model
        model_name = config.get("model", "gemini-1.5-flash")
        self.model = GenerativeModel(model_name)
        
        # Quality thresholds
        self.thresholds = config.get("quality_thresholds", {
            "overall_score": 0.85,
            "plagiarism_score": 0.95,
            "grammar_score": 0.90,
            "readability_score": 0.80,
            "seo_score": 0.85,
            "brand_voice_score": 0.80,
            "content_safety_score": 0.95
        })
        
        self.logger.info("Quality Assurance Agent initialized",
            model=model_name,
            thresholds=self.thresholds
        )
    
    def validate_content(
        self,
        content: str,
        metadata: Dict[str, Any],
        brand_guidelines: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive quality validation
        
        Args:
            content: Content to validate
            metadata: Content metadata (title, keywords, etc.)
            brand_guidelines: Optional brand voice guidelines
        
        Returns:
            Quality report with scores and recommendations
        """
        self.logger.info("Starting quality validation",
            content_length=len(content),
            has_brand_guidelines=brand_guidelines is not None
        )
        
        try:
            # Check quota before processing
            quota_check = self.quota_manager.check_quota("vertex-ai", tokens=1)
            if not quota_check.get('allowed', False):
                raise Exception("Quota exceeded for Vertex AI")
            
            # Perform all quality checks
            quality_checks = {
                "plagiarism": self._check_plagiarism(content),
                "grammar": self._check_grammar(content),
                "readability": self._check_readability(content),
                "seo": self._check_seo(content, metadata),
                "brand_voice": self._check_brand_voice(content, brand_guidelines),
                "content_safety": self._check_content_safety(content)
            }
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(quality_checks)
            
            # Determine action required
            action_required = self._determine_action(overall_score, quality_checks)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(quality_checks)
            
            # Create quality report
            quality_report = {
                "timestamp": datetime.utcnow().isoformat(),
                "content_id": metadata.get("content_id", "unknown"),
                "overall_score": overall_score,
                "passed": overall_score >= self.thresholds["overall_score"],
                "checks": quality_checks,
                "action_required": action_required,
                "recommendations": recommendations,
                "thresholds": self.thresholds
            }
            
            self.logger.info("Quality validation complete",
                overall_score=overall_score,
                passed=quality_report["passed"],
                action_required=action_required
            )
            
            return quality_report
            
        except Exception as e:
            self.logger.error("Quality validation failed",
                error=str(e),
                content_id=metadata.get("content_id")
            )
            raise
    
    def _check_plagiarism(self, content: str) -> Dict[str, Any]:
        """Check for plagiarism using AI-powered analysis"""
        try:
            prompt = f"""
Analyze the following content for originality and potential plagiarism indicators.
Look for:
1. Generic or copied phrases
2. Overly common expressions
3. Lack of unique voice
4. Unusual pattern consistency

Content:
{content[:3000]}

Provide a plagiarism score (0-1, where 1 is completely original) and identify any concerns.

Respond in JSON format:
{{
    "score": 0.95,
    "concerns": ["list of concerns"],
    "confidence": 0.9,
    "passed": true
}}
"""
            
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            result["passed"] = result.get("score", 0) >= self.thresholds["plagiarism_score"]
            
            return result
            
        except Exception as e:
            self.logger.error("Plagiarism check failed", error=str(e))
            return {
                "score": 0.0,
                "concerns": [f"Check failed: {str(e)}"],
                "confidence": 0.0,
                "passed": False
            }
    
    def _check_grammar(self, content: str) -> Dict[str, Any]:
        """Check grammar and language quality"""
        try:
            prompt = f"""
Analyze the following content for grammar, spelling, and language quality.
Check for:
1. Grammatical errors
2. Spelling mistakes
3. Punctuation issues
4. Sentence structure problems
5. Word choice appropriateness

Content:
{content[:3000]}

Provide a grammar score (0-1, where 1 is perfect) and list any issues found.

Respond in JSON format:
{{
    "score": 0.92,
    "issues": ["list of issues"],
    "error_count": 2,
    "passed": true
}}
"""
            
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            result["passed"] = result.get("score", 0) >= self.thresholds["grammar_score"]
            
            return result
            
        except Exception as e:
            self.logger.error("Grammar check failed", error=str(e))
            return {
                "score": 0.0,
                "issues": [f"Check failed: {str(e)}"],
                "error_count": 999,
                "passed": False
            }
    
    def _check_readability(self, content: str) -> Dict[str, Any]:
        """Check content readability"""
        try:
            # Calculate basic readability metrics
            words = content.split()
            sentences = re.split(r'[.!?]+', content)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            word_count = len(words)
            sentence_count = len(sentences) if sentences else 1
            avg_words_per_sentence = word_count / sentence_count
            
            # Estimate syllables (simplified)
            syllable_count = sum(self._count_syllables(word) for word in words)
            
            # Calculate Flesch Reading Ease (simplified)
            # Score = 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
            flesch_score = 206.835 - 1.015 * avg_words_per_sentence - 84.6 * (syllable_count / word_count)
            flesch_score = max(0, min(100, flesch_score))  # Clamp to 0-100
            
            # Normalize to 0-1 scale (60-80 is ideal, so center around that)
            normalized_score = min(1.0, flesch_score / 100)
            
            readability_result = {
                "score": normalized_score,
                "flesch_score": flesch_score,
                "word_count": word_count,
                "sentence_count": sentence_count,
                "avg_words_per_sentence": avg_words_per_sentence,
                "reading_level": self._get_reading_level(flesch_score),
                "passed": normalized_score >= self.thresholds["readability_score"]
            }
            
            return readability_result
            
        except Exception as e:
            self.logger.error("Readability check failed", error=str(e))
            return {
                "score": 0.0,
                "error": str(e),
                "passed": False
            }
    
    def _count_syllables(self, word: str) -> int:
        """Simplified syllable counting"""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent 'e'
        if word.endswith('e'):
            syllable_count -= 1
        
        # Every word has at least one syllable
        return max(1, syllable_count)
    
    def _get_reading_level(self, flesch_score: float) -> str:
        """Convert Flesch score to reading level"""
        if flesch_score >= 90:
            return "5th grade (very easy)"
        elif flesch_score >= 80:
            return "6th grade (easy)"
        elif flesch_score >= 70:
            return "7th grade (fairly easy)"
        elif flesch_score >= 60:
            return "8th-9th grade (standard)"
        elif flesch_score >= 50:
            return "10th-12th grade (fairly difficult)"
        elif flesch_score >= 30:
            return "College (difficult)"
        else:
            return "College graduate (very difficult)"
    
    def _check_seo(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Check SEO optimization"""
        try:
            title = metadata.get("title", "")
            keywords = metadata.get("keywords", [])
            meta_description = metadata.get("meta_description", "")
            
            seo_checks = {
                "title_length": 10 <= len(title) <= 60,
                "has_keywords": len(keywords) > 0,
                "keyword_in_title": any(kw.lower() in title.lower() for kw in keywords) if keywords else False,
                "meta_description_length": 120 <= len(meta_description) <= 160 if meta_description else False,
                "content_length": len(content.split()) >= 300,
                "keyword_density": self._calculate_keyword_density(content, keywords)
            }
            
            # Calculate SEO score
            passed_checks = sum(1 for check in seo_checks.values() if check is True or (isinstance(check, float) and check > 0))
            total_checks = len([v for v in seo_checks.values() if isinstance(v, bool)])
            seo_score = passed_checks / total_checks if total_checks > 0 else 0.5
            
            return {
                "score": seo_score,
                "checks": seo_checks,
                "passed": seo_score >= self.thresholds["seo_score"]
            }
            
        except Exception as e:
            self.logger.error("SEO check failed", error=str(e))
            return {
                "score": 0.0,
                "error": str(e),
                "passed": False
            }
    
    def _calculate_keyword_density(self, content: str, keywords: List[str]) -> float:
        """Calculate keyword density"""
        if not keywords:
            return 0.0
        
        content_lower = content.lower()
        total_words = len(content.split())
        
        keyword_count = sum(content_lower.count(kw.lower()) for kw in keywords)
        density = keyword_count / total_words if total_words > 0 else 0.0
        
        # Optimal density is 1-2%
        if 0.01 <= density <= 0.02:
            return 1.0
        elif density < 0.01:
            return density / 0.01  # Scale up to 1.0
        else:
            return max(0, 1.0 - (density - 0.02) * 10)  # Penalize over-optimization
    
    def _check_brand_voice(self, content: str, brand_guidelines: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Check brand voice consistency"""
        try:
            if not brand_guidelines:
                return {
                    "score": 1.0,
                    "note": "No brand guidelines provided",
                    "passed": True
                }
            
            tone = brand_guidelines.get("tone", "professional")
            voice_attributes = brand_guidelines.get("attributes", [])
            
            prompt = f"""
Analyze if the following content matches the brand voice guidelines.

Brand Guidelines:
- Tone: {tone}
- Voice Attributes: {', '.join(voice_attributes)}

Content:
{content[:2000]}

Evaluate how well the content matches these guidelines on a scale of 0-1.

Respond in JSON format:
{{
    "score": 0.85,
    "matches": ["list of what matches well"],
    "mismatches": ["list of what doesn't match"],
    "passed": true
}}
"""
            
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            result["passed"] = result.get("score", 0) >= self.thresholds["brand_voice_score"]
            
            return result
            
        except Exception as e:
            self.logger.error("Brand voice check failed", error=str(e))
            return {
                "score": 0.5,
                "error": str(e),
                "passed": True  # Don't fail on brand voice check errors
            }
    
    def _check_content_safety(self, content: str) -> Dict[str, Any]:
        """Check content safety (toxicity, inappropriate content)"""
        try:
            prompt = f"""
Analyze the following content for safety issues:
1. Toxic or offensive language
2. Hate speech
3. Violence or harm
4. Misinformation indicators
5. Inappropriate content

Content:
{content[:2000]}

Provide a safety score (0-1, where 1 is completely safe).

Respond in JSON format:
{{
    "score": 0.98,
    "issues": ["list of safety issues"],
    "severity": "none|low|medium|high",
    "passed": true
}}
"""
            
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            result["passed"] = result.get("score", 0) >= self.thresholds["content_safety_score"]
            
            return result
            
        except Exception as e:
            self.logger.error("Content safety check failed", error=str(e))
            return {
                "score": 0.5,
                "issues": [f"Check failed: {str(e)}"],
                "severity": "unknown",
                "passed": False
            }
    
    def _calculate_overall_score(self, quality_checks: Dict[str, Dict[str, Any]]) -> float:
        """Calculate weighted overall quality score"""
        weights = {
            "plagiarism": 0.25,
            "grammar": 0.20,
            "readability": 0.15,
            "seo": 0.15,
            "brand_voice": 0.10,
            "content_safety": 0.15
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for check_name, weight in weights.items():
            if check_name in quality_checks:
                score = quality_checks[check_name].get("score", 0.0)
                total_score += score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_action(self, overall_score: float, quality_checks: Dict[str, Dict[str, Any]]) -> str:
        """Determine what action is required based on quality scores"""
        # Check for critical failures
        if quality_checks.get("content_safety", {}).get("score", 1.0) < 0.7:
            return "reject"
        
        if quality_checks.get("plagiarism", {}).get("score", 1.0) < 0.8:
            return "reject"
        
        # Check for low confidence
        if overall_score < 0.7:
            return "human-review"
        
        # Check for minor issues
        if overall_score < self.thresholds["overall_score"]:
            return "revision"
        
        return "approve"
    
    def _generate_recommendations(self, quality_checks: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations based on quality checks"""
        recommendations = []
        
        for check_name, result in quality_checks.items():
            if not result.get("passed", False):
                score = result.get("score", 0.0)
                threshold = self.thresholds.get(f"{check_name}_score", 0.8)
                
                if check_name == "plagiarism":
                    recommendations.append(f"Improve originality (score: {score:.2f}, target: {threshold:.2f})")
                elif check_name == "grammar":
                    issues = result.get("issues", [])
                    recommendations.append(f"Fix grammar issues: {len(issues)} found")
                elif check_name == "readability":
                    recommendations.append(f"Improve readability (Flesch score: {result.get('flesch_score', 0):.1f})")
                elif check_name == "seo":
                    failed_checks = [k for k, v in result.get("checks", {}).items() if not v]
                    recommendations.append(f"Improve SEO: {', '.join(failed_checks)}")
                elif check_name == "brand_voice":
                    recommendations.append("Adjust content to match brand voice guidelines")
                elif check_name == "content_safety":
                    recommendations.append("Address content safety concerns")
        
        return recommendations
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from AI response with fallback"""
        try:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Try to find JSON object in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            # Fallback: return default structure
            return {
                "score": 0.5,
                "note": "Could not parse AI response",
                "raw_response": response_text[:500],
                "passed": False
            }
            
        except json.JSONDecodeError as e:
            self.logger.warning("Failed to parse JSON response",
                error=str(e),
                response=response_text[:500]
            )
            return {
                "score": 0.5,
                "error": "JSON parse error",
                "passed": False
            }
