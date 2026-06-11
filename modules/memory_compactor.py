# modules/memory_compactor.py
import asyncio
from datetime import datetime, timedelta
from typing import List

class MemoryCompactor:
    def __init__(self, memory_store, llm_provider, interval_minutes: int = 60):
        self.memory = memory_store
        self.llm = llm_provider
        self.interval = interval_minutes
        self.last_compact = datetime.now()
    
    async def compact(self, force: bool = False):
        now = datetime.now()
        if not force and (now - self.last_compact) < timedelta(minutes=self.interval):
            return
        # Ambil memori lama (lebih dari 1 hari)
        # Di sini Anda perlu menambahkan field timestamp di memory store
        # Lalu minta LLM untuk merangkum
        old_memories = []  # ambil dari DB
        if not old_memories:
            return
        summary_prompt = f"Ringkas memori berikut menjadi poin-poin penting:\n" + "\n".join(old_memories)
        success, summary = await self.llm.generate([{"role": "user", "content": summary_prompt}], [])
        if success:
            # Hapus memori lama dan simpan ringkasan sebagai satu memori
            pass
        self.last_compact = now
