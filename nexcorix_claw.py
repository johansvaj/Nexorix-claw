#!/usr/bin/env python3
"""
Nexcorix Claw v25.0 - Complete Integration with NanoBot/PicoClaw Advanced Features
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import threading
import shutil
import socket
import platform
import re
import urllib.request
import urllib.parse
from pathlib import Path

# ========== AUTO REPAIR ==========
REPAIR_FLAG = os.path.expanduser("~/.nexcorix_repaired")
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(WORK_DIR, "modules")

def ensure_modules():
    if os.path.exists(REPAIR_FLAG):
        return
    print("🔧 Auto-repair: memeriksa struktur modules...")
    os.makedirs(MODULES_DIR, exist_ok=True)
    # Bersihkan subfolder module bersarang
    for root, dirs, files in os.walk(MODULES_DIR):
        if "module" in dirs:
            shutil.rmtree(os.path.join(root, "module"), ignore_errors=True)
    shutil.rmtree(os.path.join(WORK_DIR, "module"), ignore_errors=True)
    # Buat __init__.py jika belum
    init_file = os.path.join(MODULES_DIR, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("# Nexcorix Claw modules\n")
    with open(REPAIR_FLAG, "w") as f:
        f.write("done")
    print("✅ Auto-repair selesai.\n")

ensure_modules()

# ========== Import modul internal (dengan fallback) ==========
sys.path.insert(0, WORK_DIR)

try:
    from modules.advanced_memory import AdvancedMemory
    ADV_MEMORY_OK = True
except ImportError:
    ADV_MEMORY_OK = False
    print("⚠️ AdvancedMemory tidak tersedia. Install chromadb dan sentence-transformers untuk memori cerdas.")

try:
    from modules.workspace_v2 import WorkspaceV2
    WORKSPACE_OK = True
except ImportError:
    WORKSPACE_OK = False
    print("⚠️ WorkspaceV2 tidak tersedia. Gunakan workspace sederhana.")

try:
    from modules.skill_loader import SkillLoader
    SKILL_OK = True
except ImportError:
    SKILL_OK = False

try:
    from modules.mcp_client_v2 import MCPClientV2
    MCP_OK = True
except ImportError:
    MCP_OK = False

try:
    from modules.webui_server import WebUIServer
    WEBUI_OK = True
except ImportError:
    WEBUI_OK = False

try:
    from modules.cron_service import CronService
    CRON_OK = True
except ImportError:
    CRON_OK = False

try:
    from modules.permissions import PermissionManager
    PERM_OK = True
except ImportError:
    PERM_OK = False

try:
    from modules.message_bus import MessageBus
    BUS_OK = True
except ImportError:
    BUS_OK = False

try:
    from modules.agent_loop import AgentLoop
    AGENT_OK = True
except ImportError:
    AGENT_OK = False

try:
    from modules.llm_provider import LLMProvider
    LLM_OK = True
except ImportError:
    LLM_OK = False

# ========== Warna ==========
C = {
    "r":"\033[0m","b":"\033[1m","d":"\033[2m","R":"\033[91m","G":"\033[92m",
    "Y":"\033[93m","C":"\033[96m","O":"\033[38;5;208m","P":"\033[38;5;141m",
}
def c(name): return C.get(name, "")
def clear(): os.system("clear" if os.name != "nt" else "cls")

# ========== Konfigurasi ==========
CONFIG_FILE = os.path.expanduser("~/.nexcorix/config.json")
WORKSPACE_DIR = os.path.expanduser("~/.nexcorix/workspace")

def load_cfg():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f: return json.load(f)
        except: pass
    return {
        "provider": "openrouter",
        "model": "openai/gpt-3.5-turbo",
        "openrouter_key": "",
        "openai_key": "",
        "anthropic_key": "",
        "google_key": "",
        "deepseek_key": "",
        "temperature": 0.7,
        "max_tokens": 4096,
        "admin_id": "",
        "channels": {}
    }
def save_cfg(cfg):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f: json.dump(cfg, f, indent=2)

# ========== System Utils (fallback jika modul tidak tersedia) ==========
class SystemExecutor:
    def run(self, cmd, timeout=300):
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return {"success": proc.returncode==0, "stdout": proc.stdout}
    def run_streaming(self, cmd, timeout=300):
        print(c("Y") + f"[ACTION] ⚡ {cmd}" + c("r"))
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        out = []
        for line in proc.stdout:
            print(line, end='')
            out.append(line)
        proc.wait(timeout)
        print(c("G") + "[NOTIF] ✅ Selesai" + c("r"))
        return {"success": proc.returncode==0, "stdout": "".join(out)}

class FileManager:
    def __init__(self): self.cwd = os.path.expanduser("~")
    def create_folder(self, name): os.makedirs(os.path.join(self.cwd, name), exist_ok=True); return True, f"Folder {name} dibuat"
    def create_file(self, name, content): 
        with open(os.path.join(self.cwd, name), 'w') as f: f.write(content)
        return True, f"File {name} dibuat"
    def list_files(self): return "\n".join(os.listdir(self.cwd))

class NetworkScanner:
    def __init__(self): self.exec = SystemExecutor()
    def scan_network(self, target="192.168.1.0/24"):
        return self.exec.run(f"nmap -sn {target} 2>/dev/null || ping -c 2 {target.split('/')[0]}")['stdout']

# ========== Simple LLM jika modul tidak tersedia ==========
class SimpleLLM:
    def __init__(self, cfg):
        self.cfg = cfg
    def test_connection(self):
        return False, "LLM modul tidak tersedia, API key mungkin tidak berfungsi"
    async def chat(self, msg, system=""):
        return "Fungsi AI tidak tersedia karena modul llm_provider belum diinstal."

# ========== AI Chat Engine ==========
class AIChatEngine:
    def __init__(self):
        self.cfg = load_cfg()
        self.exec = SystemExecutor()
        self.fm = FileManager()
        self.net = NetworkScanner()
        
        # Inisialisasi modul advanced jika tersedia
        if ADV_MEMORY_OK:
            self.memory = AdvancedMemory()
        else:
            self.memory = None
            print("⚠️ Memori advanced tidak aktif.")
        
        if WORKSPACE_OK:
            self.workspace = WorkspaceV2(WORKSPACE_DIR)
        else:
            self.workspace = None
        
        if SKILL_OK:
            self.skills = SkillLoader()
        else:
            self.skills = None
        
        if MCP_OK:
            self.mcp = MCPClientV2()
        else:
            self.mcp = None
        
        if WEBUI_OK:
            self.webui = WebUIServer(agent_engine=self, port=18888)
            self.webui.start_background()
        else:
            self.webui = None
        
        if CRON_OK:
            self.cron = CronService()
            self.cron.start()
        else:
            self.cron = None
        
        if PERM_OK:
            self.perms = PermissionManager()
            # Berikan izin default untuk user lokal
            self.perms.grant("local", Permission.READ)
            self.perms.grant("local", Permission.WRITE)
            self.perms.grant("local", Permission.BASH)
        else:
            self.perms = None
        
        # LLM provider
        if LLM_OK:
            self.llm = LLMProvider(self.cfg)
        else:
            self.llm = SimpleLLM(self.cfg)
        
        # MessageBus dan AgentLoop (jika tersedia)
        self.bus = MessageBus() if BUS_OK else None
        if AGENT_OK and self.bus:
            self.agent = AgentLoop(self.bus, self.llm, self.memory, self.workspace, self.skills)
            asyncio.create_task(self.agent.run())
        else:
            self.agent = None
        
        self.conv_history = self.cfg.get("chat_history", {})
    
    def test_connection(self):
        return self.llm.test_connection()
    
    def _casual_response(self, text):
        lower = text.lower().strip()
        if re.search(r'\b(hi|hai|halo|hello)\b', lower):
            return "Halo! Langsung aja perintahnya. 😎"
        if re.search(r'\b(apa kabar|how are you)\b', lower):
            return "Baik! Siap action. 🦂"
        if re.search(r'\b(nama mu|siapa kamu)\b', lower):
            return "Aku Nexcorix Claw, ethical hacker. Panggil Claw aja. 🤘"
        if re.search(r'\b(bisa apa|fitur)\b', lower):
            return (
                "Aku bisa:\n"
                "- install <paket>\n- scan network\n- buat folder <nama>\n- create file <nama> isi <teks>\n- run <perintah>\n- web server\n"
                "Juga punya memori cerdas, skill, MCP, WebUI, dan 25 channel.\n"
                "Atur API key di menu 18 ya!"
            )
        return None
    
    async def chat_with_ai(self, user_id, message):
        # Cari memori relevan
        context = ""
        if self.memory:
            memories = self.memory.search(message, user_id=user_id)
            if memories:
                context = "\n\n## Memori relevan\n" + "\n".join(memories)
        system_prompt = "Anda adalah Nexcorix Claw, asisten tegas."
        if self.workspace:
            system_prompt = self.workspace.build_system_prompt()
        system_prompt += context
        response = await self.llm.chat(message, system_prompt)
        # Simpan ke memori
        if self.memory:
            self.memory.add(f"User: {message}", user_id=user_id)
            self.memory.add(f"Assistant: {response}", user_id=user_id)
        return response
    
    def process(self, user_id, text):
        lower = text.lower()
        # Perintah langsung
        if re.match(r'^(install|pasang) ', lower):
            pkg = text.split(maxsplit=1)[1]
            res = self.exec.run_streaming(f"apt install -y {pkg} 2>/dev/null || pkg install -y {pkg} || pip install {pkg}")
            return f"Instalasi {pkg}: {'OK' if res['success'] else 'Gagal'}\n{res['stdout'][:500]}"
        if re.match(r'scan network', lower):
            target = re.search(r'\d+\.\d+\.\d+\.\d+', text)
            target = target.group() if target else "192.168.1.0/24"
            return self.net.scan_network(target)
        if re.match(r'(create file|buat file) ', lower):
            parts = text.split(maxsplit=2)
            if len(parts) >= 2:
                return self.fm.create_file(parts[1], parts[2] if len(parts)>2 else "")[1]
        if re.match(r'buat folder ', lower):
            name = text.split(maxsplit=1)[1]
            return self.fm.create_folder(name)[1]
        if re.match(r'run ', lower):
            cmd = text[4:]
            return self.exec.run_streaming(cmd)['stdout']
        if re.match(r'web server', lower):
            ip = socket.gethostbyname(socket.gethostname())
            threading.Thread(target=lambda: subprocess.run(["python3", "-m", "http.server", "8080"]), daemon=True).start()
            return f"Web server running at http://{ip}:8080"
        # Casual
        casual = self._casual_response(text)
        if casual:
            return casual
        # AI
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            resp = loop.run_until_complete(self.chat_with_ai(user_id, text))
            loop.close()
            return resp
        except Exception as e:
            return f"AI error: {e}. Cek API key di Settings."

# ========== Menu Functions ==========
def show_dashboard(ai):
    clear()
    print(c("C")+"╔══════════════════════════════════════════════════════════╗"+c("r"))
    print(c("C")+"║"+c("b")+c("Y")+" " * 28 + "DASHBOARD" + " " * 28 + c("r")+c("C")+"║"+c("r"))
    print(c("C")+"╚══════════════════════════════════════════════════════════╝"+c("r"))
    cfg = ai.cfg
    print(f"\n{c('G')}✅ AI Status: {'Active' if cfg.get('openrouter_key') else 'No API Key'}{c('r')}")
    print(f"{c('C')}📡 Provider: {c('Y')}{cfg.get('provider','openrouter')}{c('r')}")
    print(f"{c('C')}🧠 Model: {c('Y')}{cfg.get('model','openai/gpt-3.5-turbo')}{c('r')}")
    print(f"{c('C')}📁 Workspace: {c('Y')}{WORKSPACE_DIR}{c('r')}")
    if ai.memory:
        stats = ai.memory.get_stats()
        print(f"{c('C')}🧠 Memory stats: {c('Y')}{stats}{c('r')}")
    if ai.skills:
        skills = ai.skills.list_skills()
        print(f"{c('C')}🔧 Skills available: {c('Y')}{len(skills)}{c('r')}")
    input("\n"+c("d")+"Tekan Enter..."+c("r"))

def show_models_menu(ai):
    input("Models: ganti model di Settings (18) → 2\nEnter...")

def show_memory_menu(ai):
    if not ai.memory:
        input("Memory module tidak aktif. Install chromadb dan sentence-transformers.\nEnter...")
        return
    clear()
    print(c("C")+"╔══════════════════════════════════════════════════════════╗"+c("r"))
    print(c("C")+"║"+c("b")+c("Y")+" " * 28 + "MEMORY" + " " * 28 + c("r")+c("C")+"║"+c("r"))
    print(c("C")+"╚══════════════════════════════════════════════════════════╝"+c("r"))
    recent = ai.memory.get_recent(10)
    print("\nRecent memories:\n")
    for i, mem in enumerate(recent, 1):
        print(f"  {i}. {mem[:100]}...")
    input("\nEnter...")

def show_skills_menu(ai):
    if not ai.skills:
        input("Skill module tidak aktif.\nEnter...")
        return
    clear()
    print(c("C")+"╔══════════════════════════════════════════════════════════╗"+c("r"))
    print(c("C")+"║"+c("b")+c("Y")+" " * 28 + "SKILLS" + " " * 28 + c("r")+c("C")+"║"+c("r"))
    print(c("C")+"╚══════════════════════════════════════════════════════════╝"+c("r"))
    skills = ai.skills.list_skills()
    if skills:
        for s in skills:
            print(f"  • {c('Y')}{s['name']}{c('r')}: {s['description']}")
    else:
        print("  Belum ada skill.")
    print("\n[c] Create new skill")
    ch = input("Choice: ").strip().lower()
    if ch == 'c':
        name = input("Skill name: ").strip()
        desc = input("Description: ").strip()
        content = input("Instruction content: ").strip()
        if ai.skills.create_skill(name, desc, content):
            print("Skill created!")
        else:
            print("Failed (maybe already exists).")
        input("Enter...")

def show_tools_menu(ai):
    input("Tools: install, scan network, buat folder, create file, run, web server\nEnter...")

def show_channels_menu(ai):
    input("Channels: Telegram, Discord, dll. (placeholder)\nEnter...")

def show_settings_menu(ai):
    cfg = ai.cfg
    while True:
        clear()
        print(c("C")+"╔══════════════════════════════════════════════════════════╗"+c("r"))
        print(c("C")+"║"+c("b")+c("Y")+" " * 27 + "SETTINGS" + " " * 27 + c("r")+c("C")+"║"+c("r"))
        print(c("C")+"╚══════════════════════════════════════════════════════════╝"+c("r"))
        print("\n[1] Provider\n[2] Model\n[3] Temperature\n[4] API Keys\n[5] Save & Exit")
        ch = input(c("Y")+"Choice: "+c("r")).strip()
        if ch == "1":
            p = input("Provider (openrouter/openai/anthropic/google/deepseek): ").strip()
            if p: cfg["provider"] = p; save_cfg(cfg)
        elif ch == "2":
            m = input("Model ID: ").strip()
            if m: cfg["model"] = m; save_cfg(cfg)
            ok, msg = ai.test_connection()
            print(c("G")+f"✅ {msg}" if ok else c("R")+f"❌ {msg}")
            input()
        elif ch == "3":
            try: cfg["temperature"] = float(input("Temperature (0-2): ")); save_cfg(cfg)
            except: pass
        elif ch == "4":
            print("1. OpenRouter\n2. OpenAI\n3. Anthropic\n4. Google\n5. DeepSeek")
            sub = input("Choice: ").strip()
            key = input("API Key: ").strip()
            if sub == "1": cfg["openrouter_key"] = key
            elif sub == "2": cfg["openai_key"] = key
            elif sub == "3": cfg["anthropic_key"] = key
            elif sub == "4": cfg["google_key"] = key
            elif sub == "5": cfg["deepseek_key"] = key
            save_cfg(cfg)
            ok, msg = ai.test_connection()
            print(c("G")+f"✅ {msg}" if ok else c("R")+f"❌ {msg}")
            input()
        elif ch == "5": break

def show_about():
    clear()
    print(c("C")+"╔══════════════════════════════════════════════════════════╗"+c("r"))
    print(c("C")+"║"+c("b")+c("Y")+" " * 30 + "ABOUT" + " " * 30 + c("r")+c("C")+"║"+c("r"))
    print(c("C")+"╚══════════════════════════════════════════════════════════╝"+c("r"))
    print(f"""
{c('O')}Nexcorix Claw v25.0 - Advanced AI Agent{c('r')}
{c('G')}Fitur:{c('r')}
  • Advanced memory (vector search)
  • Workspace markdown (AGENTS.md, SOUL.md, etc.)
  • Skill loader (SKILL.md)
  • MCP client (Model Context Protocol)
  • WebUI workbench (FastAPI)
  • Cron service (automation)
  • Permission manager
  • Multi-channel (Telegram, Discord, dll)
    """)
    input("Tekan Enter...")

# ========== Main Menu ==========
def main():
    ai = AIChatEngine()
    clear()
    print(c("C")+"╔══════════════════════════════════════════════════════════╗"+c("r"))
    print(c("C")+"║"+c("b")+c("Y")+" " * 27 + "NEXCORIX CLAW v25.0" + " " * 27 + c("r")+c("C")+"║"+c("r"))
    print(c("C")+"╚══════════════════════════════════════════════════════════╝"+c("r"))
    print("\n🔍 Testing AI connection...")
    ok, msg = ai.test_connection()
    if ok:
        print(c("G")+f"✅ {msg}"+c("r"))
    else:
        print(c("R")+f"❌ {msg}"+c("r"))
        print(c("Y")+"💡 Chat tetap bisa untuk perintah langsung (install, scan, file, run) dan sapaan ringan."+c("r"))
    print(c("d")+"\nTekan Enter ke menu..."+c("r"))
    input()
    while True:
        clear()
        print(c("C")+"╔══════════════════════════════════════════════════════════╗"+c("r"))
        print(c("C")+"║"+c("O")+" 🦂 "+c("b")+c("Y")+"      N E X C O R I X   C L A W   v25.0     "+c("O")+"🦂 "+c("C")+"║"+c("r"))
        print(c("C")+"╠══════════════════════════════════════════════════════════╣"+c("r"))
        print(c("C")+"║  [1] Dashboard        [11] Workspace                     ║"+c("r"))
        print(c("C")+"║  [2] Chat             [12] API Keys                      ║"+c("r"))
        print(c("C")+"║  [3] Models           [13] Logs                          ║"+c("r"))
        print(c("C")+"║  [4] Agents           [14] Monitoring                    ║"+c("r"))
        print(c("C")+"║  [5] Memory           [15] Security                      ║"+c("r"))
        print(c("C")+"║  [6] Skills           [16] Backup                        ║"+c("r"))
        print(c("C")+"║  [7] Tools            [17] Updates                       ║"+c("r"))
        print(c("C")+"║  [8] Channels         [18] Settings                      ║"+c("r"))
        print(c("C")+"║  [9] WebUI            [19] About                         ║"+c("r"))
        print(c("C")+"║  [10] Automation      [20] Exit                          ║"+c("r"))
        print(c("C")+"╚══════════════════════════════════════════════════════════╝"+c("r"))
        choice = input(c("Y")+"Select option: "+c("r")).strip()
        if choice == "1": show_dashboard(ai)
        elif choice == "2":
            clear()
            print(c("C")+"Chat mode (ketik 'exit' kembali)"+c("r"))
            print(c("d")+"Perintah: install, scan network, buat folder, create file, run, web server"+c("r"))
            while True:
                inp = input(c("M")+"You: "+c("r")).strip()
                if inp.lower() in ("exit","back"): break
                resp = ai.process("local", inp)
                if resp: print(resp)
        elif choice == "3": show_models_menu(ai)
        elif choice == "4": input("Subagents coming soon.\nEnter...")
        elif choice == "5": show_memory_menu(ai)
        elif choice == "6": show_skills_menu(ai)
        elif choice == "7": show_tools_menu(ai)
        elif choice == "8": show_channels_menu(ai)
        elif choice == "9": 
            if ai.webui:
                print("WebUI running at http://localhost:18888")
            else:
                print("WebUI tidak aktif. Install fastapi dan uvicorn.")
            input("Enter...")
        elif choice == "10": input("Cron service aktif (otomatisasi).\nEnter...")
        elif choice == "11": input(f"Workspace: {WORKSPACE_DIR}\nEnter...")
        elif choice == "12": show_settings_menu(ai)
        elif choice == "13": input("Logs: coming soon.\nEnter...")
        elif choice == "14": input("Monitoring: coming soon.\nEnter...")
        elif choice == "15": 
            if ai.perms:
                print("Permission manager aktif.")
            else:
                print("Permission manager tidak aktif.")
            input("Enter...")
        elif choice == "16": input("Backup: copy workspace folder.\nEnter...")
        elif choice == "17": input("Updates: auto-repair on startup.\nEnter...")
        elif choice == "18": show_settings_menu(ai)
        elif choice == "19": show_about()
        elif choice == "20": print(c("G")+"Goodbye! 🦂"+c("r")); break
        else: input("Invalid. Enter...")

if __name__ == "__main__":
    main()
