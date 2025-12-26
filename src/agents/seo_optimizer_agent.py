"""
SEO Optimizer Agent - Optimizes content for search engines
"""

import json
import re
from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent


class SEOOptimizerAgent(BaseAgent):
    """Agent that optimizes content for search engine visibility"""
    
    def __init__(self):
        """Initialize SEO Optimizer Agent"""
        super().__init__(agent_name='seo_optimizer')
    
    def _execute_internal(self, **kwargs) -> Dict[str, Any]:
        """
        Optimize content for SEO
        
        Args:
            content: Content to optimize (dict with title, body, etc.)
            primary_keyword: Primary keyword to target
            secondary_keywords: List of secondary keywords (optional)
            
        Returns:
            SEO optimization results and recommendations
        """
        content = kwargs.get('content')
        primary_keyword = kwargs.get('primary_keyword')
        secondary_keywords = kwargs.get('secondary_keywords', [])
        
        if not content:
            raise ValueError("Content is required for SEO optimization")
        
        # Extract content
        title = content.get('title', '')
        body = content.get('body', '')
        
        if not body:
            raise ValueError("Content body is required for SEO optimization")
        
        # Auto-extract keywords if not provided
        if not primary_keyword:
            primary_keyword = self._extract_primary_keyword(title, body)
        
        # Build prompt from template
        prompt = self.user_prompt_template.format(
            title=title,
            body=body,
            primary_keyword=primary_keyword,
            secondary_keywords=', '.join(secondary_keywords) if secondary_keywords else 'auto-generate'
        )
        
        # Call AI model
        self.logger.info(
            "Starting SEO optimization",
            agent=self.agent_name,
            title=title,
            primary_keyword=primary_keyword
        )
        
        response = self._call_model(prompt)
        
        # Calculate cost
        cost = self._calculate_cost(prompt, response)
        self.logger.cost_tracking(
            project_id=kwargs.get('project_id', 'unknown'),
            operation='seo_optimization',
            cost=cost,
            model=self.model_name
        )
        
        # Parse JSON response
        try:
            seo_data = self._parse_seo_response(response)
        except Exception as e:
            self.logger.warning(
                f"Failed to parse JSON response: {e}",
                agent=self.agent_name
            )
            # Fallback to basic optimization
            seo_data = self._basic_seo_optimization(title, body, primary_keyword)
        
        # Add metadata
        seo_data['cost'] = cost
        seo_data['model_used'] = self.model_name
        seo_data['primary_keyword'] = primary_keyword
        seo_data['secondary_keywords'] = secondary_keywords
        
        # Calculate SEO metrics
        seo_data['seo_metrics'] = self._calculate_seo_metrics(
            title,
            body,
            seo_data.get('optimized_title', title),
            seo_data.get('optimized_body', body),
            primary_keyword,
            secondary_keywords
        )
        
        # Generate SEO score
        seo_data['seo_score'] = self._calculate_seo_score(seo_data['seo_metrics'])
        
        return seo_data
    
    def _parse_seo_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON SEO response
        
        Args:
            response: Model response
            
        Returns:
            Parsed SEO data
        """
        # Try to find JSON in response
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response[start_idx:end_idx]
            return json.loads(json_str)
        
        # If no JSON found, try parsing entire response
        return json.loads(response)
    
    def _extract_primary_keyword(self, title: str, body: str) -> str:
        """
        Extract primary keyword from title and body
        
        Args:
            title: Content title
            body: Content body
            
        Returns:
            Primary keyword
        """
        # Simple extraction: use first 2-3 words from title
        words = title.lower().split()
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        keywords = [w for w in words if w not in stop_words]
        
        if keywords:
            return ' '.join(keywords[:2])
        
        return ' '.join(words[:2])
    
    def _basic_seo_optimization(
        self,
        title: str,
        body: str,
        primary_keyword: str
    ) -> Dict[str, Any]:
        """
        Perform basic SEO optimization as fallback
        
        Args:
            title: Original title
            body: Original body
            primary_keyword: Primary keyword
            
        Returns:
            Basic SEO optimization data
        """
        # Generate meta description (first 160 chars)
        meta_description = body[:157] + '...' if len(body) > 160 else body
        
        # Generate slug
        slug = self._generate_slug(title)
        
        # Basic keyword suggestions
        words = body.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Only consider words longer than 4 chars
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Top keywords by frequency
        suggested_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        suggested_keywords = [k for k, v in suggested_keywords]
        
        return {
            'optimized_title': title,
            'optimized_body': body,
            'meta_description': meta_description,
            'title_tag': f"{title} | Blog",
            'slug': slug,
            'keywords': suggested_keywords,
            'internal_links': [],
            'schema_markup': self._generate_basic_schema(title, meta_description)
        }
    
    def _generate_slug(self, title: str) -> str:
        """
        Generate URL-friendly slug from title
        
        Args:
            title: Content title
            
        Returns:
            URL slug
        """
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = slug.strip('-')
        return slug
    
    def _generate_basic_schema(self, title: str, description: str) -> Dict[str, Any]:
        """
        Generate basic Schema.org markup
        
        Args:
            title: Content title
            description: Content description
            
        Returns:
            Schema markup as dict
        """
        return {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": title,
            "description": description,
            "author": {
                "@type": "Organization",
                "name": "AI Content Generator"
            }
        }
    
    def _calculate_seo_metrics(
        self,
        original_title: str,
        original_body: str,
        optimized_title: str,
        optimized_body: str,
        primary_keyword: str,
        secondary_keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate SEO metrics for content
        
        Args:
            original_title: Original title
            original_body: Original body
            optimized_title: Optimized title
            optimized_body: Optimized body
            primary_keyword: Primary keyword
            secondary_keywords: Secondary keywords
            
        Returns:
            SEO metrics
        """
        # Keyword density
        primary_count = optimized_body.lower().count(primary_keyword.lower())
        total_words = len(optimized_body.split())
        keyword_density = (primary_count / total_words * 100) if total_words > 0 else 0
        
        # Title optimization
        title_has_keyword = primary_keyword.lower() in optimized_title.lower()
        title_length = len(optimized_title)
        title_optimal = 50 <= title_length <= 60
        
        # Header analysis (looking for markdown headers)
        h1_count = optimized_body.count('# ')
        h2_count = optimized_body.count('## ')
        h3_count = optimized_body.count('### ')
        
        # Content length
        word_count = total_words
        
        # Readability (simple approximation)
        sentences = len(re.split(r'[.!?]+', optimized_body))
        avg_sentence_length = total_words / max(sentences, 1)
        
        return {
            'keyword_density': round(keyword_density, 2),
            'keyword_in_title': title_has_keyword,
            'title_length': title_length,
            'title_optimal_length': title_optimal,
            'h1_count': h1_count,
            'h2_count': h2_count,
            'h3_count': h3_count,
            'word_count': word_count,
            'average_sentence_length': round(avg_sentence_length, 1),
            'primary_keyword_count': primary_count
        }
    
    def _calculate_seo_score(self, metrics: Dict[str, Any]) -> float:
        """
        Calculate overall SEO score (0-100)
        
        Args:
            metrics: SEO metrics
            
        Returns:
            SEO score
        """
        score = 0
        max_score = 100
        
        # Keyword in title (20 points)
        if metrics.get('keyword_in_title'):
            score += 20
        
        # Title length (15 points)
        if metrics.get('title_optimal_length'):
            score += 15
        
        # Keyword density (20 points) - ideal 1-3%
        density = metrics.get('keyword_density', 0)
        if 1 <= density <= 3:
            score += 20
        elif 0.5 <= density < 1 or 3 < density <= 4:
            score += 10
        
        # Content length (15 points) - ideal 800-2000 words
        word_count = metrics.get('word_count', 0)
        if 800 <= word_count <= 2000:
            score += 15
        elif word_count >= 600:
            score += 10
        
        # Headers (15 points)
        has_h1 = metrics.get('h1_count', 0) > 0
        has_h2 = metrics.get('h2_count', 0) > 0
        if has_h1 and has_h2:
            score += 15
        elif has_h1 or has_h2:
            score += 8
        
        # Readability (15 points) - avg sentence length 15-20 words
        avg_length = metrics.get('average_sentence_length', 0)
        if 15 <= avg_length <= 20:
            score += 15
        elif 10 <= avg_length < 15 or 20 < avg_length <= 25:
            score += 10
        
        return round(score, 1)
    
    def validate_seo(self, seo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate SEO quality against thresholds
        
        Args:
            seo_data: SEO optimization data
            
        Returns:
            Validation results
        """
        seo_score = seo_data.get('seo_score', 0)
        metrics = seo_data.get('seo_metrics', {})
        
        validations = {
            'keyword_in_title': {
                'passed': metrics.get('keyword_in_title', False),
                'message': 'Primary keyword appears in title'
            },
            'optimal_title_length': {
                'passed': metrics.get('title_optimal_length', False),
                'message': 'Title length is optimal (50-60 chars)'
            },
            'keyword_density': {
                'passed': 1 <= metrics.get('keyword_density', 0) <= 3,
                'message': 'Keyword density is optimal (1-3%)'
            },
            'has_headers': {
                'passed': metrics.get('h2_count', 0) > 0,
                'message': 'Content has proper header structure'
            },
            'minimum_seo_score': {
                'passed': seo_score >= 70,
                'message': f'SEO score meets minimum threshold (score: {seo_score})'
            }
        }
        
        all_passed = all(v['passed'] for v in validations.values())
        
        return {
            'overall_passed': all_passed,
            'validations': validations,
            'seo_score': seo_score,
            'recommendation': 'ready_to_publish' if seo_score >= 80 else 
                            'needs_minor_improvements' if seo_score >= 70 else
                            'needs_major_improvements'
        }
