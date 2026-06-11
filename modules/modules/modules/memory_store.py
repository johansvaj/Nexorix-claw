import sqlite3
import json
import math
from datetime import datetime
from typing import List

class SimpleVector:
    @staticmethod
    def encode(text: str) -> List[float]:
        words = text.lower().split()
        if not words: return []
        counts = {}
        for w in words: counts[w] = counts.get(w, 0) + 1
        total = len(words)
        unique = list(set(words))[:200]
        return [counts.get(w, 0) / total for w in unique]

class MemoryStore:
    def __init__(self, db_path: str = None):
        import os
        if db_path is None:
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
        emb = SimpleVector.encode(content)
        self.conn.execute(
            "INSERT INTO memories (content, embedding, timestamp, importance) VALUES (?,?,?,?)",
            (content, json.dumps(emb), datetime.now().timestamp(), importance)
        )
        self.conn.commit()
    def search(self, query: str, limit: int = 5) -> List[str]:
        q_emb = SimpleVector.encode(query)
        cursor = self.conn.execute("SELECT content, embedding FROM memories ORDER BY timestamp DESC LIMIT 200")
        results = []
        for row in cursor:
            try:
                emb = json.loads(row[1])
            except:
                emb = []
            sim = self._cosine(q_emb, emb)
            if sim > 0.05:
                results.append((sim, row[0]))
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:limit]]
    def get_recent(self, limit: int = 10) -> List[str]:
        cursor = self.conn.execute("SELECT content FROM memories ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [row[0] for row in cursor.fetchall()]
    @staticmethod
    def _cosine(a, b):
        if not a or not b: return 0
        dot = sum(x*y for x,y in zip(a,b))
        na = sum(x*x for x in a)**0.5
        nb = sum(y*y for y in b)**0.5
        return dot / (na * nb) if na and nb else 0
