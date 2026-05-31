"""Memory storage for Agents Claw Mini."""

import json
import sqlite3
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from .config import MemoryConfig
from .exceptions import MemoryException

logger = logging.getLogger("AgentsClawMini.Memory")

class Memory:
    """
    Memory storage untuk agent.

    Backends:
    - sqlite: Local SQLite database (default)
    - chroma: ChromaDB untuk vector search
    - qdrant: Qdrant vector database
    - redis: Redis cache

    Features:
    - Persistent storage
    - Vector embeddings (untuk semantic search)
    - Conversation history
    - Key-value storage
    """

    def __init__(self, config: Optional[MemoryConfig] = None):
        self.config = config or MemoryConfig()
        self._conn = None
        self._chroma = None
        self._qdrant = None
        self._redis = None

        self._init_backend()

    def _init_backend(self):
        """Initialize storage backend."""
        if self.config.backend == "sqlite":
            self._init_sqlite()
        elif self.config.backend == "chroma":
            self._init_chroma()
        elif self.config.backend == "qdrant":
            self._init_qdrant()
        elif self.config.backend == "redis":
            self._init_redis()
        else:
            raise MemoryException(f"Backend '{self.config.backend}' tidak didukung")

        logger.info("🧠 Memory initialized (%s)", self.config.backend)

    def _init_sqlite(self):
        """Initialize SQLite backend."""
        self._conn = sqlite3.connect(self.config.db_path, check_same_thread=False)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                data TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                embedding TEXT
            )
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS key_values (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        self._conn.commit()

    def _init_chroma(self):
        """Initialize ChromaDB backend."""
        try:
            import chromadb
            self._chroma = chromadb.Client()
            self._collection = self._chroma.get_or_create_collection("agents_claw")
        except ImportError:
            raise MemoryException("ChromaDB tidak terinstall. Run: pip install chromadb")

    def _init_qdrant(self):
        """Initialize Qdrant backend."""
        try:
            from qdrant_client import QdrantClient
            self._qdrant = QdrantClient(":memory:")  # In-memory for demo
        except ImportError:
            raise MemoryException("Qdrant tidak terinstall. Run: pip install qdrant-client")

    def _init_redis(self):
        """Initialize Redis backend."""
        try:
            import redis
            self._redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
        except ImportError:
            raise MemoryException("Redis tidak terinstall. Run: pip install redis")

    # ========== CRUD OPERATIONS ==========

    async def add(self, category: str, data: Dict[str, Any]) -> int:
        """Add memory entry."""
        timestamp = datetime.now().isoformat()

        if self.config.backend == "sqlite":
            cursor = self._conn.execute(
                "INSERT INTO memories (category, data, timestamp) VALUES (?, ?, ?)",
                (category, json.dumps(data), timestamp)
            )
            self._conn.commit()
            return cursor.lastrowid

        elif self.config.backend == "chroma":
            doc_id = f"{category}_{timestamp}"
            self._collection.add(
                documents=[json.dumps(data)],
                metadatas=[{"category": category, "timestamp": timestamp}],
                ids=[doc_id]
            )
            return hash(doc_id)

        return 0

    async def get(self, category: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get memories by category."""
        if self.config.backend == "sqlite":
            cursor = self._conn.execute(
                "SELECT data, timestamp FROM memories WHERE category = ? ORDER BY timestamp DESC LIMIT ?",
                (category, limit)
            )
            return [{"data": json.loads(row[0]), "timestamp": row[1]} for row in cursor.fetchall()]

        elif self.config.backend == "chroma":
            results = self._collection.query(
                query_texts=[category],
                n_results=limit,
                where={"category": category}
            )
            return [{"data": json.loads(doc), "timestamp": meta.get("timestamp", "")} 
                    for doc, meta in zip(results["documents"][0], results["metadatas"][0])]

        return []

    async def search(self, query: str, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories semantically."""
        if self.config.backend == "chroma":
            where_filter = {"category": category} if category else None
            results = self._collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_filter
            )
            return [{"data": json.loads(doc), "score": score}
                    for doc, score in zip(results["documents"][0], results["distances"][0])]

        elif self.config.backend == "sqlite":
            # Simple text search for SQLite
            cursor = self._conn.execute(
                "SELECT data, timestamp FROM memories WHERE data LIKE ? ORDER BY timestamp DESC LIMIT ?",
                (f"%{query}%", limit)
            )
            return [{"data": json.loads(row[0]), "timestamp": row[1]} for row in cursor.fetchall()]

        return []

    async def set_kv(self, key: str, value: Any):
        """Set key-value pair."""
        timestamp = datetime.now().isoformat()

        if self.config.backend == "sqlite":
            self._conn.execute(
                "INSERT OR REPLACE INTO key_values (key, value, timestamp) VALUES (?, ?, ?)",
                (key, json.dumps(value), timestamp)
            )
            self._conn.commit()

        elif self.config.backend == "redis":
            self._redis.set(key, json.dumps(value))

    async def get_kv(self, key: str) -> Optional[Any]:
        """Get value by key."""
        if self.config.backend == "sqlite":
            cursor = self._conn.execute("SELECT value FROM key_values WHERE key = ?", (key,))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None

        elif self.config.backend == "redis":
            value = self._redis.get(key)
            return json.loads(value) if value else None

        return None

    async def delete(self, category: str, condition: Optional[str] = None):
        """Delete memories."""
        if self.config.backend == "sqlite":
            if condition:
                self._conn.execute("DELETE FROM memories WHERE category = ? AND data LIKE ?", (category, f"%{condition}%"))
            else:
                self._conn.execute("DELETE FROM memories WHERE category = ?", (category,))
            self._conn.commit()

    def count(self) -> int:
        """Count total memory entries."""
        if self.config.backend == "sqlite":
            cursor = self._conn.execute("SELECT COUNT(*) FROM memories")
            return cursor.fetchone()[0]
        return 0

    async def close(self):
        """Close memory connection."""
        if self._conn:
            self._conn.close()
        logger.info("🧠 Memory closed")

    def __repr__(self):
        return f"Memory(backend={self.config.backend})"
