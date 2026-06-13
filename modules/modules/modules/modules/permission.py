from enum import Enum
from typing import Set, List

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    BASH = "bash"
    SKILLS = "skills"
    WEB = "web"

class PermissionManager:
    def __init__(self):
        self.user_perms: dict = {}
    def grant(self, user_id: str, perm: Permission):
        if user_id not in self.user_perms:
            self.user_perms[user_id] = set()
        self.user_perms[user_id].add(perm)
    def revoke(self, user_id: str, perm: Permission):
        if user_id in self.user_perms:
            self.user_perms[user_id].discard(perm)
    def is_allowed(self, user_id: str, perm: Permission) -> bool:
        return perm in self.user_perms.get(user_id, set())
    def get_allowed_tools(self, user_id: str) -> List[str]:
        perms = self.user_perms.get(user_id, set())
        mapping = {
            Permission.READ: ["read_file", "list_files"],
            Permission.WRITE: ["write_file", "mkdir"],
            Permission.BASH: ["bash", "run"],
            Permission.SKILLS: ["skill_load", "list_skills"],
            Permission.WEB: ["web_fetch"]
        }
        tools = []
        for p, tl in mapping.items():
            if p in perms:
                tools.extend(tl)
        return tools
