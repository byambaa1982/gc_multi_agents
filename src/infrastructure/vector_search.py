"""
Vector Search Service

Implements semantic search using Vertex AI Vector Search for:
- Duplicate content detection
- Similar content discovery
- Content clustering
- Research result ranking
"""

import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np

import vertexai
from vertexai.language_models import TextEmbeddingModel

from ..monitoring.logger import StructuredLogger
from ..infrastructure.cost_tracker import CostTracker
from ..infrastructure.quota_manager import QuotaManager


class VectorSearchService:
    """Service for semantic content search using embeddings"""
    
    def __init__(
        self,
        project_id: str,
        location: str,
        config: Dict[str, Any],
        cost_tracker: CostTracker,
        quota_manager: QuotaManager
    ):
        """
        Initialize Vector Search Service
        
        Args:
            project_id: GCP project ID
            location: GCP location
            config: Service configuration
            cost_tracker: Cost tracking service
            quota_manager: Quota management service
        """
        self.project_id = project_id
        self.location = location
        self.config = config
        self.cost_tracker = cost_tracker
        self.quota_manager = quota_manager
        self.logger = StructuredLogger("VectorSearchService")
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Initialize embedding model
        self.embedding_model_name = config.get("embedding_model", "textembedding-gecko@003")
        self.embedding_model = TextEmbeddingModel.from_pretrained(self.embedding_model_name)
        
        # In-memory vector store (for development/testing)
        # In production, this would use Vertex AI Vector Search
        self.vector_store: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.similarity_threshold = config.get("similarity_threshold", 0.85)
        self.embedding_dimensions = config.get("embedding_dimensions", 768)
        
        self.logger.info("Vector Search Service initialized",
            model=self.embedding_model_name,
            similarity_threshold=self.similarity_threshold
        )
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding vector for text
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector as numpy array
        """
        try:
            # Check quota
            if not self.quota_manager.check_quota("vertex-ai", tokens=1):
                raise Exception("Quota exceeded for Vertex AI")
            
            # Truncate text if too long (API limit is ~20k characters)
            text = text[:20000]
            
            # Generate embedding
            embeddings = self.embedding_model.get_embeddings([text])
            embedding_vector = embeddings[0].values
            
            # Track cost
            self.cost_tracker.track_operation(
                operation_name="vertex-ai-embeddings",
                model_name="text-embedding-004",
                input_chars=len(text),
                output_chars=0
            )
            
            self.logger.debug("Generated embedding",
                text_length=len(text),
                vector_dimensions=len(embedding_vector)
            )
            
            return np.array(embedding_vector)
            
        except Exception as e:
            self.logger.error("Failed to generate embedding",
                error=str(e),
                text_length=len(text)
            )
            raise
    
    def add_content(
        self,
        content_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add content to vector store
        
        Args:
            content_id: Unique content identifier
            content: Content text
            metadata: Optional metadata about the content
        
        Returns:
            True if successful
        """
        try:
            # Generate embedding
            embedding = self.generate_embedding(content)
            
            # Store in vector store
            self.vector_store[content_id] = {
                "content_id": content_id,
                "content": content,
                "embedding": embedding,
                "metadata": metadata or {},
                "added_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info("Content added to vector store",
                content_id=content_id,
                content_length=len(content)
            )
            
            return True
            
        except Exception as e:
            self.logger.error("Failed to add content to vector store",
                content_id=content_id,
                error=str(e)
            )
            return False
    
    def find_similar(
        self,
        content: str,
        top_k: int = 5,
        threshold: Optional[float] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Find similar content using semantic search
        
        Args:
            content: Content to search for
            top_k: Number of similar items to return
            threshold: Similarity threshold (0-1), defaults to config value
        
        Returns:
            List of (content_id, similarity_score, metadata) tuples
        """
        try:
            if not self.vector_store:
                self.logger.warning("Vector store is empty")
                return []
            
            # Generate embedding for query content
            query_embedding = self.generate_embedding(content)
            
            # Calculate similarity with all stored embeddings
            similarities = []
            for content_id, stored_data in self.vector_store.items():
                stored_embedding = stored_data["embedding"]
                similarity = self._cosine_similarity(query_embedding, stored_embedding)
                
                similarities.append((
                    content_id,
                    similarity,
                    stored_data["metadata"]
                ))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Filter by threshold
            threshold = threshold if threshold is not None else self.similarity_threshold
            filtered = [(cid, sim, meta) for cid, sim, meta in similarities if sim >= threshold]
            
            # Return top K
            results = filtered[:top_k]
            
            self.logger.info("Similarity search complete",
                query_length=len(content),
                total_candidates=len(similarities),
                results_returned=len(results),
                threshold=threshold
            )
            
            return results
            
        except Exception as e:
            self.logger.error("Similarity search failed", error=str(e))
            return []
    
    def check_duplicate(
        self,
        content: str,
        threshold: float = 0.90
    ) -> Optional[Dict[str, Any]]:
        """
        Check if content is a duplicate or near-duplicate
        
        Args:
            content: Content to check
            threshold: Similarity threshold for duplicate detection
        
        Returns:
            Duplicate information if found, None otherwise
        """
        similar_items = self.find_similar(content, top_k=1, threshold=threshold)
        
        if similar_items:
            content_id, similarity, metadata = similar_items[0]
            
            self.logger.warning("Potential duplicate detected", {
                "similarity": similarity,
                "original_content_id": content_id,
                "threshold": threshold
            })
            
            return {
                "is_duplicate": True,
                "original_content_id": content_id,
                "similarity_score": similarity,
                "metadata": metadata,
                "threshold": threshold
            }
        
        return None
    
    def find_related_content(
        self,
        content: str,
        min_similarity: float = 0.70,
        max_similarity: float = 0.90,
        top_k: int = 10
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Find related but not duplicate content
        
        Useful for:
        - Finding content for cross-linking
        - Discovering related topics
        - Building content clusters
        
        Args:
            content: Content to find relations for
            min_similarity: Minimum similarity threshold
            max_similarity: Maximum similarity threshold (to exclude duplicates)
            top_k: Maximum results to return
        
        Returns:
            List of (content_id, similarity_score, metadata) tuples
        """
        all_similar = self.find_similar(content, top_k=top_k * 2, threshold=min_similarity)
        
        # Filter to exclude very similar (potential duplicates)
        related = [
            (cid, sim, meta) for cid, sim, meta in all_similar
            if min_similarity <= sim <= max_similarity
        ]
        
        return related[:top_k]
    
    def cluster_content(
        self,
        content_ids: Optional[List[str]] = None,
        num_clusters: int = 5
    ) -> Dict[int, List[str]]:
        """
        Cluster content into groups using K-means
        
        Args:
            content_ids: List of content IDs to cluster (None = all)
            num_clusters: Number of clusters to create
        
        Returns:
            Dictionary mapping cluster ID to list of content IDs
        """
        try:
            # Get content to cluster
            if content_ids is None:
                content_ids = list(self.vector_store.keys())
            
            if len(content_ids) < num_clusters:
                self.logger.warning("Not enough content for clustering", {
                    "content_count": len(content_ids),
                    "num_clusters": num_clusters
                })
                return {0: content_ids}
            
            # Get embeddings
            embeddings = []
            valid_content_ids = []
            
            for content_id in content_ids:
                if content_id in self.vector_store:
                    embeddings.append(self.vector_store[content_id]["embedding"])
                    valid_content_ids.append(content_id)
            
            embeddings = np.array(embeddings)
            
            # Perform K-means clustering
            from sklearn.cluster import KMeans
            
            kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(embeddings)
            
            # Group content by cluster
            clusters = {}
            for content_id, cluster_id in zip(valid_content_ids, cluster_labels):
                cluster_id = int(cluster_id)
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                clusters[cluster_id].append(content_id)
            
            self.logger.info("Content clustering complete",
                num_clusters=num_clusters,
                content_count=len(valid_content_ids)
            )
            
            return clusters
            
        except Exception as e:
            self.logger.error("Clustering failed", error=str(e))
            return {0: content_ids or []}
    
    def remove_content(self, content_id: str) -> bool:
        """Remove content from vector store"""
        try:
            if content_id in self.vector_store:
                del self.vector_store[content_id]
                self.logger.info("Content removed from vector store",
                    content_id=content_id
                )
                return True
            return False
            
        except Exception as e:
            self.logger.error("Failed to remove content",
                content_id=content_id,
                error=str(e)
            )
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        if not self.vector_store:
            return {
                "total_embeddings": 0,
                "oldest_entry": None,
                "newest_entry": None
            }
        
        timestamps = [
            data["added_at"] for data in self.vector_store.values()
        ]
        
        return {
            "total_embeddings": len(self.vector_store),
            "oldest_entry": min(timestamps),
            "newest_entry": max(timestamps),
            "model": self.embedding_model_name,
            "similarity_threshold": self.similarity_threshold
        }
    
    def clear(self):
        """Clear all embeddings from vector store"""
        count = len(self.vector_store)
        self.vector_store.clear()
        
        self.logger.info("Vector store cleared",
            embeddings_removed=count
        )
    
    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
        
        Returns:
            Similarity score (0-1)
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Clamp to [0, 1] range
        return max(0.0, min(1.0, similarity))
    
    def batch_add_content(
        self,
        contents: List[Dict[str, Any]],
        batch_size: int = 10
    ) -> Dict[str, Any]:
        """
        Add multiple contents in batches
        
        Args:
            contents: List of dicts with 'content_id', 'content', 'metadata'
            batch_size: Number of items to process per batch
        
        Returns:
            Summary of batch operation
        """
        total = len(contents)
        successful = 0
        failed = 0
        
        self.logger.info("Starting batch add",
            total_items=total,
            batch_size=batch_size
        )
        
        for i in range(0, total, batch_size):
            batch = contents[i:i + batch_size]
            
            for item in batch:
                try:
                    success = self.add_content(
                        content_id=item["content_id"],
                        content=item["content"],
                        metadata=item.get("metadata")
                    )
                    
                    if success:
                        successful += 1
                    else:
                        failed += 1
                        
                except Exception as e:
                    self.logger.error("Batch add item failed",
                        content_id=item.get("id"),
                        error=str(e)
                    )
                    failed += 1
        
        summary = {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0
        }
        
        self.logger.info("Batch add complete", summary)
        
        return summary
