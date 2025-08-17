import os
import asyncio
from typing import List
from openai import OpenAI
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("⚠️  No OpenAI API key found. Using mock embeddings.")
            self.use_mock = True
        else:
            self.client = OpenAI(api_key=api_key)
            self.use_mock = False
            logger.info("✅ OpenAI API key loaded")
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI API or mock data"""
        if self.use_mock:
            return self._generate_mock_embedding(text)
        
        try:
            # Use OpenAI's text-embedding-ada-002 model
            response = await asyncio.to_thread(
                self.client.embeddings.create,
                input=text,
                model="text-embedding-ada-002"
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding for text: {text[:50]}...")
            
            return embedding
            
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            logger.info("Falling back to mock embeddings")
            return self._generate_mock_embedding(text)
    
    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts in batch"""
        if self.use_mock:
            return [self._generate_mock_embedding(text) for text in texts]
        
        try:
            response = await asyncio.to_thread(
                self.client.embeddings.create,
                input=texts,
                model="text-embedding-ada-002"
            )
            
            embeddings = [data.embedding for data in response.data]
            logger.debug(f"Generated {len(embeddings)} embeddings in batch")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"OpenAI batch embedding error: {e}")
            logger.info("Falling back to mock embeddings")
            return [self._generate_mock_embedding(text) for text in texts]
    
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """Generate deterministic mock embedding for demo purposes"""
        import hashlib
        
        # Create a deterministic hash-based embedding
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to 1536-dimensional vector
        embedding = []
        for i in range(1536):
            # Use hash to generate pseudo-random but deterministic values
            hash_seed = f"{text_hash}_{i}".encode()
            value = int(hashlib.md5(hash_seed).hexdigest()[:8], 16) / (16**8)  # 0-1
            # Normalize to roughly match cosine distance expectations
            value = (value - 0.5) * 2  # -1 to 1
            embedding.append(value)
        
        # Normalize to unit vector for cosine distance
        magnitude = sum(x*x for x in embedding) ** 0.5
        normalized = [x/magnitude for x in embedding]
        
        logger.debug(f"Generated mock embedding for: {text[:50]}...")
        return normalized
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        if len(embedding1) != len(embedding2):
            raise ValueError("Embeddings must have same dimension")
        
        # Dot product
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        
        # Magnitudes
        mag1 = sum(a * a for a in embedding1) ** 0.5
        mag2 = sum(b * b for b in embedding2) ** 0.5
        
        # Cosine similarity
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def find_most_similar(
        self, 
        query_embedding: List[float], 
        candidate_embeddings: List[List[float]], 
        top_k: int = 5
    ) -> List[tuple]:
        """Find top-k most similar embeddings"""
        similarities = []
        
        for i, candidate in enumerate(candidate_embeddings):
            similarity = self.calculate_similarity(query_embedding, candidate)
            similarities.append((i, similarity))
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
