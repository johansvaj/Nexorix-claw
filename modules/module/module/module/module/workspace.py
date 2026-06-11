# modules/workspace.py
import os
from pathlib import Path

class Workspace:
    def __init__(self, workspace_dir: str = None):
        if workspace_dir is None:
            workspace_dir = os.path.expanduser("~/.nexcorix/workspace")
        self.dir = Path(workspace_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self._ensure_defaults()
    
    def _ensure_defaults(self):
        defaults = {
            "AGENTS.md": """# Agent Rules

You are Nexcorix Claw, a direct and efficient AI assistant.

## Core Principles
1. **Execute immediately** – Never explain how to do something. Just do it.
2. **Use tools** – For any command (install, scan, run, file ops), use available tools.
3. **Be concise** – Short, direct responses. No unnecessary fluff.
4. **Security first** – Never execute commands that could harm the system.
""",
            "SOUL.md": """# Agent Personality

You are Nexcorix Claw – a **firm, no-nonsense** assistant.

## Personality
- Direct and efficient
- Tech-savvy (programming, hacking, system admin)
- Uses casual Indonesian/English mixed (gue, lo, gas, cepetan)
- Uses emojis: 🔥😈💻🎯✨

## Communication
- No long explanations – just action and results.
- Always use tools instead of explaining how.
""",
            "USER.md": """# User Preferences

- Name: User
- Language: Indonesian/English
- Style: Direct and efficient
""",
            "IDENTITY.md": """# Identity

**Name**: Nexcorix Claw
**Role**: AI Assistant & Automation Agent
**Expertise**: System administration, programming, security, automation
"""
        }
        for filename, content in defaults.items():
            fp = self.dir / filename
            if not fp.exists():
                fp.write_text(content)
    
    def load_file(self, name: str) -> str:
        fp = self.dir / name
        if fp.exists():
            return fp.read_text()
        return ""
    
    def build_system_prompt(self) -> str:
        identity = self.load_file("IDENTITY.md")
        soul = self.load_file("SOUL.md")
        agents = self.load_file("AGENTS.md")
        user = self.load_file("USER.md")
        parts = []
        if identity: parts.append(f"# Identity\n{identity}")
        if soul: parts.append(f"# Personality\n{soul}")
        if agents: parts.append(f"# Rules\n{agents}")
        if user: parts.append(f"# User Info\n{user}")
        parts.append("""
## Tool Usage Instructions
You have tools: `bash`, `read_file`, `write_file`, `mkdir`, `scan_network`, `install`, `memory_store`, `memory_search`, `skill_load`.

- When user asks to do something, ALWAYS call the appropriate tool.
- Never explain how to use a tool – just use it.
- Multiple tools can be called in sequence if needed.
""")
        return "\n\n---\n\n".join(parts)
