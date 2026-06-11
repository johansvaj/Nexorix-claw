# modules/memory_store.py
import sqlite3
import json
import math
from datetime import datetime
from typing import List, Optional

class SimpleVector:
    @staticmethod
    def encode(text: str) -> List[float]:
        words = text.lower().split()
        if not words:
            return []
        word_counts = {}
        for w in words:
            word_counts[w] = word_counts.get(w, 0) + 1
        total = len(words)
        unique = list(set(words))[:200]
        return [word_counts.get(w, 0) / total for w in unique]
    
    @staticmethod
    def cosine(a: List[float], b: List[float]) -> float:
        if not a or not b:
            return 0.0
        dot = sum(x*y for x,y in zip(a,b))
        norm_a = math.sqrt(sum(x*x for x in a))
        norm_b = math.sqrt(sum(y*y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

class MemoryStore:
    def __init__(self, db_path: str = None):
        if db_path is None:
            import os
            db_path = os.path.expanduser("~/.nexcorix_memory.db")
        self.conn = sqlite3.connect(db_path)
        self._init_db()
    
    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                embedding TEXT,
                timestamp REAL,
                importance INTEGER DEFAULT 1
            )
        """)
        self.conn.commit()
    
    def add(self, content: str, importance: int = 1):
        embedding = SimpleVector.encode(content)
        emb_json = json.dumps(embedding)
        self.conn.execute(
            "INSERT INTO memories (content, embedding, timestamp, importance) VALUES (?, ?, ?, ?)",
            (content, emb_json, datetime.now().timestamp(), importance)
        )
        self.conn.commit()
    
    def search(self, query: str, limit: int = 5, min_similarity: float = 0.1) -> List[str]:
        q_emb = SimpleVector.encode(query)
        cursor = self.conn.execute("SELECT id, content, embedding FROM memories ORDER BY timestamp DESC LIMIT 100")
        results = []
        for row in cursor:
            try:
                emb = json.loads(row[2])
            except:
                emb = []
            sim = SimpleVector.cosine(q_emb, emb)
            if sim >= min_similarity:
                results.append((sim, row[1]))
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:limit]]
    
    def get_recent(self, limit: int = 10) -> List[str]:
        cursor = self.conn.execute("SELECT content FROM memories ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [row[0] for row in cursor.fetchall()]
