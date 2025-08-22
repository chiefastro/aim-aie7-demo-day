"""Vector Search Service for ACP Protocol

This module provides vector search capabilities including:
- Text embedding generation
- Vector similarity calculations
- Search optimization
"""

import os
import logging
from typing import List, Optional
import openai

logger = logging.getLogger(__name__)


class VectorSearchService:
    """Service for vector search operations"""
    
    def __init__(self):
        # Get OpenAI API key from environment
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ OPENAI_API_KEY not set - using mock embeddings")
            self.api_key = None
        
        # Initialize OpenAI client if API key is available
        if self.api_key:
            openai.api_key = self.api_key
            logger.info("✅ OpenAI client initialized")
        else:
            logger.info("ℹ️ Using mock embedding service")
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get vector embedding for text"""
        try:
            if not text or not text.strip():
                # Return zero vector for empty text
                return [0.0] * 1536
            
            if self.api_key:
                # Use OpenAI embeddings
                response = openai.Embedding.create(
                    input=text.strip(),
                    model="text-embedding-ada-002"
                )
                embedding = response['data'][0]['embedding']
                logger.debug(f"Generated OpenAI embedding for text: {text[:50]}...")
                return embedding
            else:
                # Use mock embeddings for demo/testing
                mock_embedding = self._generate_mock_embedding(text)
                logger.debug(f"Generated mock embedding for text: {text[:50]}...")
                return mock_embedding
                
        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {e}")
            # Fallback to mock embedding
            mock_embedding = self._generate_mock_embedding(text)
            logger.info(f"Using fallback mock embedding for: {text[:50]}...")
            return mock_embedding
    
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """Generate deterministic mock embedding for demo/testing"""
        import hashlib
        
        # Create deterministic hash-based embedding
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to 1536-dimensional vector
        embedding = []
        for i in range(1536):
            # Use hash to generate pseudo-random but deterministic values
            hash_index = i % len(text_hash)
            char_val = ord(text_hash[hash_index])
            # Normalize to [-1, 1] range
            normalized_val = (char_val / 255.0) * 2 - 1
            embedding.append(normalized_val)
        
        return embedding
    
    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts"""
        try:
            if self.api_key:
                # Use OpenAI batch embeddings
                response = openai.Embedding.create(
                    input=texts,
                    model="text-embedding-ada-002"
                )
                embeddings = [data['embedding'] for data in response['data']]
                logger.debug(f"Generated {len(embeddings)} OpenAI embeddings")
                return embeddings
            else:
                # Use mock embeddings
                embeddings = [self._generate_mock_embedding(text) for text in texts]
                logger.debug(f"Generated {len(embeddings)} mock embeddings")
                return embeddings
                
        except Exception as e:
            logger.error(f"❌ Batch embedding generation failed: {e}")
            # Fallback to mock embeddings
            embeddings = [self._generate_mock_embedding(text) for text in texts]
            logger.info(f"Using fallback mock embeddings for {len(texts)} texts")
            return embeddings
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            if len(embedding1) != len(embedding2):
                raise ValueError("Embeddings must have same dimensions")
            
            # Calculate dot product
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            
            # Calculate magnitudes
            mag1 = sum(a * a for a in embedding1) ** 0.5
            mag2 = sum(b * b for b in embedding2) ** 0.5
            
            # Avoid division by zero
            if mag1 == 0 or mag2 == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = dot_product / (mag1 * mag2)
            return similarity
            
        except Exception as e:
            logger.error(f"❌ Similarity calculation failed: {e}")
            return 0.0
    
    def find_most_similar(self, query_embedding: List[float], candidate_embeddings: List[List[float]], top_k: int = 5) -> List[tuple]:
        """Find top-k most similar embeddings"""
        try:
            similarities = []
            for i, candidate in enumerate(candidate_embeddings):
                similarity = self.calculate_similarity(query_embedding, candidate)
                similarities.append((i, similarity))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Return top-k results
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"❌ Similarity search failed: {e}")
            return []
