# modules/multi_agent.py
from typing import Dict, Any, List

class SpecialistAgent:
    def __init__(self, name: str, system_prompt: str, parent_engine):
        self.name = name
        self.prompt = system_prompt
        self.engine = parent_engine  # reuse AIChatEngine

    async def process(self, task: str) -> str:
        # Gunakan chat_with_ai dengan system prompt khusus
        success, resp = self.engine.chat_with_ai(
            user_id=f"agent_{self.name}",
            message=task,
            system_prompt=self.prompt
        )
        return resp if success else f"[{self.name}] gagal: {resp}"

class MultiAgentOrchestrator:
    def __init__(self, main_engine):
        self.main = main_engine
        self.agents: Dict[str, SpecialistAgent] = {}

    def register_agent(self, name: str, prompt: str):
        self.agents[name] = SpecialistAgent(name, prompt, self.main)

    async def delegate(self, task: str, agent_name: str) -> str:
        if agent_name in self.agents:
            return await self.agents[agent_name].process(task)
        return f"Agent '{agent_name}' tidak ditemukan."

    async def orchestrate(self, user_input: str) -> str:
        # Contoh sederhana: deteksi keyword untuk memilih agen
        lower = user_input.lower()
        if "coding" in lower or "python" in lower:
            return await self.delegate(user_input, "coding")
        if "hack" in lower or "scan" in lower:
            return await self.delegate(user_input, "hacking")
        # fallback ke agen utama
        success, resp = self.main.chat_with_ai("multi_user", user_input)
        return resp if success else resp
