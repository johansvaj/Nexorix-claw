import os
from pathlib import Path

class Workspace:
    def __init__(self, workspace_dir: str = None):
        if workspace_dir is None:
            workspace_dir = os.path.expanduser("~/.nexcorix/workspace")
        self.dir = Path(workspace_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self._create_defaults()
    def _create_defaults(self):
        defaults = {
            "AGENTS.md": "# Agent Rules\n- Execute immediately\n- Never explain how\n- Use tools",
            "SOUL.md": "# Personality\nFirm, direct, tech-savvy, uses casual Indonesian/English",
            "USER.md": "# User\nName: User\nLanguage: Indonesian",
            "IDENTITY.md": "# Identity\nNexcorix Claw - AI Assistant"
        }
        for name, content in defaults.items():
            fp = self.dir / name
            if not fp.exists():
                fp.write_text(content)
    def load_file(self, name: str) -> str:
        fp = self.dir / name
        return fp.read_text() if fp.exists() else ""
    def build_system_prompt(self) -> str:
        parts = []
        for f in ["IDENTITY.md", "SOUL.md", "AGENTS.md", "USER.md"]:
            content = self.load_file(f)
            if content:
                parts.append(f"# {f.replace('.md','')}\n{content}")
        parts.append("## Tools\nYou have bash, read_file, write_file, mkdir, scan_network, install, memory_store, memory_search, skill_load")
        return "\n\n---\n\n".join(parts)
