"""Custom exceptions for Agents Claw Mini."""

class AgentsClawMiniException(Exception):
    """Base exception for all Agents Claw Mini errors."""
    pass

class AgentException(AgentsClawMiniException):
    """Raised when agent operations fail."""
    pass

class BrowserException(AgentsClawMiniException):
    """Raised when browser automation fails."""
    pass

class ScrapingException(AgentsClawMiniException):
    """Raised when scraping operations fail."""
    pass

class ChannelException(AgentsClawMiniException):
    """Raised when channel operations fail."""
    pass

class MemoryException(AgentsClawMiniException):
    """Raised when memory operations fail."""
    pass

class ToolException(AgentsClawMiniException):
    """Raised when tool execution fails."""
    pass

class SandboxException(AgentsClawMiniException):
    """Raised when sandbox operations fail."""
    pass

class ConfigException(AgentsClawMiniException):
    """Raised when configuration is invalid."""
    pass

class LLMException(AgentsClawMiniException):
    """Raised when LLM API calls fail."""
    pass
