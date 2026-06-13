import os
import yaml
from pathlib import Path
from typing import List, Dict

class SkillLoader:
    def __init__(self, skills_dir: str = "~/.nexcorix/skills"):
        self.skills_dir = Path(skills_dir).expanduser()
        self.skills_dir.mkdir(parents=True, exist_ok=True)
    def list_skills(self) -> List[Dict]:
        skills = []
        for item in self.skills_dir.iterdir():
            if item.is_dir() and (item / "SKILL.md").exists():
                content = (item / "SKILL.md").read_text()
                desc = ""
                if content.startswith("---"):
                    try:
                        _, front, _ = content.split("---", 2)
                        data = yaml.safe_load(front)
                        desc = data.get("description", "")
                    except: pass
                skills.append({"name": item.name, "description": desc})
        return skills
    def get_skill(self, name: str) -> str:
        skill_file = self.skills_dir / name / "SKILL.md"
        if skill_file.exists():
            content = skill_file.read_text()
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    return parts[2].strip()
            return content
        return f"Skill '{name}' tidak ditemukan."
    def create_skill(self, name: str, description: str, content: str) -> bool:
        skill_dir = self.skills_dir / name
        if skill_dir.exists(): return False
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        full = f"---\ndescription: {description}\n---\n\n{content}"
        skill_file.write_text(full)
        return True
