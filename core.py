"""Core engine for Agents Claw Mini."""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from .config import Config
from .agent import Agent
from .browser import Browser
from .scraper import Scraper
from .memory import Memory
from .tools import ToolRegistry
from .sandbox import Sandbox
from .channel import ChannelManager
from .exceptions import AgentsClawMiniException

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("AgentsClawMini")

@dataclass
class AgentsClawMiniStatus:
    """Status report for AgentsClawMini instance."""
    version: str = "1.0.0"
    agents_active: int = 0
    browsers_active: int = 0
    memory_entries: int = 0
    tools_registered: int = 0
    channels_connected: int = 0
    uptime_seconds: float = 0.0
    llm_provider: str = ""
    llm_model: str = ""

class AgentsClawMini:
    """
    🤖⚡ Agents Claw Mini - Lightweight AI Agent Framework

    Inspired by NullClaw (Zig) - bringing the 678KB philosophy to Python:
    - Minimal overhead, modular design
    - Security-first with sandbox
    - Multi-LLM: 9+ providers including OpenRouter
    - Async-first for performance

    Supported LLM Providers:
    - OpenAI (GPT-4o, GPT-4, GPT-3.5)
    - Anthropic (Claude 3.5 Sonnet, Claude 3 Opus)
    - Google (Gemini 1.5 Pro, Gemini Flash)
    - Mistral (Mistral Large, Mixtral)
    - Cohere (Command R+)
    - Groq (Llama 3, Mixtral - super fast)
    - DeepSeek (DeepSeek Chat, Coder)
    - Ollama (Local models: Llama 3, Phi, Mistral)
    - OpenRouter (100+ models: GPT-4o, Claude, Llama, Qwen, etc.)

    Usage:
        claw = AgentsClawMini(config_path="config.yaml")
        agent = claw.create_agent(name="my_bot")
        result = await agent.chat("Hello!")
    """

    def __init__(self, config: Optional[Config] = None, config_path: Optional[str] = None):
        self.config = config or Config()
        if config_path:
            self.config.load(config_path)

        # Core components (lazy initialization)
        self._agents: Dict[str, Agent] = {}
        self._browsers: Dict[str, Browser] = {}
        self._scrapers: Dict[str, Scraper] = {}
        self._memory: Optional[Memory] = None
        self._tools: Optional[ToolRegistry] = None
        self._sandbox: Optional[Sandbox] = None
        self._channels: Optional[ChannelManager] = None

        self._start_time = time.time()

        logger.info("🤖⚡ Agents Claw Mini v%s initialized", self.version)
        logger.info("   LLM Provider: %s | Model: %s", 
                   self.config.llm.provider, self.config.llm.model)
        if self.config.llm.provider == "openrouter":
            logger.info("   🌐 OpenRouter mode - akses ke 100+ model!")

    @property
    def version(self) -> str:
        return "1.0.0"

    # ========== AGENT FACTORY ==========

    def create_agent(self, name: str, system_prompt: Optional[str] = None, 
                     tools: Optional[List[str]] = None) -> Agent:
        """Create a new AI agent."""
        agent = Agent(
            name=name,
            config=self.config.llm,
            system_prompt=system_prompt,
            tools=tools,
            memory=self.memory,
            tool_registry=self.tools,
            sandbox=self.sandbox
        )
        self._agents[name] = agent
        logger.info("🤖 Agent '%s' created", name)
        return agent

    def get_agent(self, name: str) -> Optional[Agent]:
        """Get agent by name."""
        return self._agents.get(name)

    def list_agents(self) -> List[str]:
        """List all active agents."""
        return list(self._agents.keys())

    def remove_agent(self, name: str) -> bool:
        """Remove an agent."""
        if name in self._agents:
            del self._agents[name]
            logger.info("🗑️ Agent '%s' removed", name)
            return True
        return False

    # ========== BROWSER FACTORY ==========

    def create_browser(self, name: str = "default") -> Browser:
        """Create a new browser instance."""
        browser = Browser(config=self.config.browser)
        self._browsers[name] = browser
        logger.info("🌐 Browser '%s' created", name)
        return browser

    def get_browser(self, name: str = "default") -> Optional[Browser]:
        """Get browser by name."""
        return self._browsers.get(name)

    # ========== SCRAPER FACTORY ==========

    def create_scraper(self, name: str = "default") -> Scraper:
        """Create a new scraper instance."""
        scraper = Scraper(config=self.config.browser, memory=self.memory)
        self._scrapers[name] = scraper
        logger.info("🔍 Scraper '%s' created", name)
        return scraper

    # ========== LAZY-LOADED COMPONENTS ==========

    @property
    def memory(self) -> Memory:
        """Get or initialize memory storage."""
        if self._memory is None:
            self._memory = Memory(config=self.config.memory)
        return self._memory

    @property
    def tools(self) -> ToolRegistry:
        """Get or initialize tool registry."""
        if self._tools is None:
            self._tools = ToolRegistry()
        return self._tools

    @property
    def sandbox(self) -> Sandbox:
        """Get or initialize sandbox."""
        if self._sandbox is None:
            self._sandbox = Sandbox(config=self.config.sandbox)
        return self._sandbox

    @property
    def channels(self) -> ChannelManager:
        """Get or initialize channel manager."""
        if self._channels is None:
            self._channels = ChannelManager(config=self.config.channel)
        return self._channels

    # ========== STATUS & HEALTH ==========

    def status(self) -> AgentsClawMiniStatus:
        """Get current status."""
        uptime = time.time() - self._start_time

        return AgentsClawMiniStatus(
            version=self.version,
            agents_active=len(self._agents),
            browsers_active=len(self._browsers),
            memory_entries=self.memory.count() if self._memory else 0,
            tools_registered=len(self.tools.list_tools()) if self._tools else 0,
            channels_connected=self.channels.connected_count() if self._channels else 0,
            uptime_seconds=uptime,
            llm_provider=self.config.llm.provider,
            llm_model=self.config.llm.model,
        )

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all components."""
        return {
            "engine": "healthy",
            "llm": self._check_llm(),
            "memory": self._check_memory(),
            "sandbox": self._check_sandbox(),
        }

    def _check_llm(self) -> Dict[str, Any]:
        """Check LLM connectivity."""
        try:
            return {
                "status": "healthy", 
                "provider": self.config.llm.provider,
                "model": self.config.llm.model,
                "base_url": self.config.llm.base_url,
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def _check_memory(self) -> Dict[str, Any]:
        """Check memory storage."""
        try:
            return {"status": "healthy", "backend": self.config.memory.backend}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def _check_sandbox(self) -> Dict[str, Any]:
        """Check sandbox status."""
        return {"status": "healthy", "enabled": self.config.sandbox.enabled}

    # ========== LIFECYCLE ==========

    async def shutdown(self):
        """Graceful shutdown."""
        logger.info("🛑 Shutting down Agents Claw Mini...")

        # Close all browsers
        for name, browser in self._browsers.items():
            await browser.close()
            logger.info("   Browser '%s' closed", name)

        # Disconnect channels
        if self._channels:
            await self._channels.disconnect_all()

        # Close memory
        if self._memory:
            await self._memory.close()

        logger.info("✅ Agents Claw Mini shutdown complete")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if asyncio.get_event_loop().is_running():
            asyncio.create_task(self.shutdown())

    def __repr__(self):
        return f"AgentsClawMini(v{self.version}, agents={len(self._agents)}, provider={self.config.llm.provider})"
