# modules/__init__.py

# Modul dasar
from .tool_registry import ToolRegistry, get_tool_registry
from .memory_store import MemoryStore
from .skill_manager import SkillManager, Skill
from .workspace import Workspace
from .webui import WebUI

# Modul memory lanjutan (opsional, jika ada file memory_advanced.py)
try:
    from .memory_advanced import AdvancedMemory
except ImportError:
    AdvancedMemory = None

# Modul RAG
try:
    from .rag import RAGStore
except ImportError:
    RAGStore = None

# Modul MCP Client
try:
    from .mcp_client import MCPClient
except ImportError:
    MCPClient = None

# Modul Multi-Agent
try:
    from .multi_agent import MultiAgentOrchestrator, SpecialistAgent
except ImportError:
    MultiAgentOrchestrator = None
    SpecialistAgent = None

# Modul Marketplace Skill
try:
    from .skill_marketplace import SkillMarketplace
except ImportError:
    SkillMarketplace = None

# Modul Observability (Logging & Tracing)
try:
    from .observability import TraceLogger
except ImportError:
    TraceLogger = None

# Modul Voice Interface
try:
    from .voice import VoiceInterface
except ImportError:
    VoiceInterface = None

# Modul Knowledge Graph
try:
    from .knowledge_graph import KnowledgeGraph
except ImportError:
    KnowledgeGraph = None

# Memory compactor (jika ada)
try:
    from .memory_compactor import MemoryCompactor
except ImportError:
    MemoryCompactor = None

# Daftar semua simbol yang bisa diimpor langsung dari modules
__all__ = [
    # Dasar
    "ToolRegistry", "get_tool_registry",
    "MemoryStore",
    "SkillManager", "Skill",
    "Workspace",
    "WebUI",
    
    # Memory lanjutan
    "AdvancedMemory",
    
    # RAG
    "RAGStore",
    
    # MCP
    "MCPClient",
    
    # Multi-agent
    "MultiAgentOrchestrator", "SpecialistAgent",
    
    # Marketplace
    "SkillMarketplace",
    
    # Observability
    "TraceLogger",
    
    # Voice
    "VoiceInterface",
    
    # Knowledge Graph
    "KnowledgeGraph",
    
    # Memory compactor
    "MemoryCompactor",
]
