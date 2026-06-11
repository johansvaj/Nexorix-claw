import hashlib
try:
    import chromadb
    from chromadb.utils import embedding_functions
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

class RAGStore:
    def __init__(self, persist_dir: str = "~/.nexcorix/rag_db"):
        self.available = RAG_AVAILABLE
        if not self.available:
            return
        import os
        self.persist_dir = os.path.expanduser(persist_dir)
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.embed_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection("nexcorix_docs", embedding_function=self.embed_fn)
    def add_document(self, text: str, metadata: dict = None):
        if not self.available: return False
        doc_id = hashlib.md5(text.encode()).hexdigest()
        self.collection.upsert(documents=[text], metadatas=[metadata or {}], ids=[doc_id])
        return True
    def search(self, query: str, top_k: int = 3):
        if not self.available: return []
        results = self.collection.query(query_texts=[query], n_results=top_k)
        return results['documents'][0] if results['documents'] else []
