# modules/memory_advanced.py
import os
import hashlib
from typing import List, Dict, Any
from datetime import datetime

try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

class AdvancedMemory:
    def __init__(self, persist_dir: str = "~/.nexcorix/memory_db"):
        if not CHROMA_AVAILABLE:
            raise ImportError("Install chromadb: pip install chromadb")
        self.persist_dir = os.path.expanduser(persist_dir)
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        # Gunakan embedding model yang lebih akurat
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(
            name="nexcorix_memory",
            embedding_function=self.embed_fn
        )
    
    def add(self, text: str, metadata: Dict[str, Any] = None, memory_id: str = None):
        if memory_id is None:
            memory_id = hashlib.md5(f"{text}{datetime.now().isoformat()}".encode()).hexdigest()
        self.collection.upsert(
            documents=[text],
            metadatas=[metadata or {"timestamp": datetime.now().isoformat()}],
            ids=[memory_id]
        )
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        results = self.collection.query(query_texts=[query], n_results=top_k)
        if results['documents'] and results['documents'][0]:
            return [{"content": doc, "metadata": meta} for doc, meta in zip(results['documents'][0], results['metadatas'][0])]
        return []
    
    def get_all(self, limit: int = 50) -> List[str]:
        results = self.collection.get(limit=limit)
        return results['documents']
