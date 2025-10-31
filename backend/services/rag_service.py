import os
from pathlib import Path
from typing import Dict, List

import chromadb
from chromadb.errors import InvalidCollectionException
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGService:
    """Service for managing RAG (Retrieval-Augmented Generation)"""

    def __init__(self):
        self.collection_name = os.getenv("COLLECTION_NAME", "documents")
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
        self.persist_directory = Path(os.getenv("CHROMA_DIR", "./chroma_db")).resolve()
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB persistent client
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))

        # Initialize embedding model
        logger.info("Loading embedding model: %s", self.embedding_model_name)
        self.embedding_model = SentenceTransformer(self.embedding_model_name)

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info("Loaded existing collection: %s", self.collection_name)
        except (InvalidCollectionException, ValueError):
            self.collection = self.client.create_collection(name=self.collection_name)
            logger.info("Created new collection: %s", self.collection_name)

    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap"""
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap

        return chunks

    def add_document(self, text: str, filename: str) -> int:
        """Add a document to the RAG system"""
        chunks = self.chunk_text(text)

        if not chunks:
            logger.warning("No chunks created for %s", filename)
            return 0

        embeddings = self.embedding_model.encode(chunks).tolist()

        doc_count = self.collection.count()
        ids = [f"{filename}_{doc_count}_{i}" for i in range(len(chunks))]

        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=[{"source": filename, "chunk": i} for i in range(len(chunks))],
            ids=ids,
        )

        logger.info("Added %d chunks from %s", len(chunks), filename)
        return len(chunks)

    def query(self, query_text: str, n_results: int = 3) -> List[Dict]:
        """Query the RAG system for relevant documents"""
        query_embedding = self.embedding_model.encode([query_text]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
        )

        sources = []
        if results.get("documents") and len(results["documents"]) > 0:
            docs = results["documents"][0]
            metas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            for i, doc in enumerate(docs):
                meta = metas[i] if i < len(metas) else {}
                sources.append(
                    {
                        "text": doc,
                        "source": meta.get("source", "unknown"),
                        "chunk": meta.get("chunk", 0),
                        "distance": distances[i] if i < len(distances) else None,
                    }
                )

        return sources

    def get_document_count(self) -> int:
        """Get the number of documents in the collection"""
        return self.collection.count()

    def clear_collection(self):
        """Clear all documents from the collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
        except (InvalidCollectionException, ValueError):
            logger.info("Collection %s not found; creating a new one.", self.collection_name)
        self.collection = self.client.create_collection(name=self.collection_name)
        logger.info("Cleared collection: %s", self.collection_name)




