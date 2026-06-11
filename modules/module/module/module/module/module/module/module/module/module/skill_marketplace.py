# modules/skill_marketplace.py
import os
import subprocess
import tempfile
from pathlib import Path
from .skill_manager import SkillManager

class SkillMarketplace:
    def __init__(self, skill_manager: SkillManager):
        self.skill_mgr = skill_manager

    def install_from_github(self, repo_url: str) -> str:
        # Clone repo ke temp, lalu copy folder skill ke ~/.nexcorix/skills/
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                subprocess.run(["git", "clone", repo_url, tmpdir], check=True, capture_output=True)
                skill_folder = Path(tmpdir)
                # Cari folder yang berisi SKILL.md
                for item in skill_folder.iterdir():
                    if item.is_dir() and (item / "SKILL.md").exists():
                        dest = self.skill_mgr.skills_dir / item.name
                        if dest.exists():
                            return f"Skill {item.name} already exists."
                        shutil.copytree(item, dest)
                        self.skill_mgr._load_all()
                        return f"Skill {item.name} installed from {repo_url}"
                return "No valid skill folder found."
        except Exception as e:
            return f"Install failed: {e}"
