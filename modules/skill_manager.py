import os
from pathlib import Path
from typing import Dict, List, Optional

class Skill:
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = Path(path)
        self.description = ""
        self.prompt = ""
        self._load()
    def _load(self):
        skill_file = self.path / "SKILL.md"
        if skill_file.exists():
            self.prompt = skill_file.read_text()
            lines = self.prompt.splitlines()
            for line in lines:
                if line.startswith("description:"):
                    self.description = line.replace("description:", "").strip()
    def get_prompt(self) -> str:
        return self.prompt

class SkillManager:
    def __init__(self, skills_dir: str = None):
        if skills_dir is None:
            skills_dir = os.path.expanduser("~/.nexcorix/skills")
        self.dir = Path(skills_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.skills: Dict[str, Skill] = {}
        self._reload()
    def _reload(self):
        self.skills.clear()
        for item in self.dir.iterdir():
            if item.is_dir():
                self.skills[item.name] = Skill(item.name, str(item))
    def get(self, name: str) -> Optional[Skill]:
        return self.skills.get(name)
    def list(self) -> List[str]:
        return list(self.skills.keys())
    def create(self, name: str, description: str = "") -> bool:
        skill_dir = self.dir / name
        if skill_dir.exists():
            return False
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(f"---\ndescription: {description}\n---\n# {name}\n\nInstruksi skill di sini.")
        self._reload()
        return True
    def get_all_prompts(self) -> str:
        if not self.skills:
            return "No skills available."
        return "\n".join([f"- {n}: {s.description}" for n,s in self.skills.items()])
