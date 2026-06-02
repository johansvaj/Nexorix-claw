#!/usr/bin/env python3
"""
Nexcorix Claw v1.2 - AI Terminal Controller via Telegram
Conversational AI | Model Switcher | Full System Access | Free Tier Fallback
"""

import os
import json
import time
import platform
import socket
import re
import shutil
import threading
import asyncio
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    # Dummy minimal agar class NexcorixTelegramBot tetap bisa didefinisikan
    # tanpa NameError saat parse file, meskipun library belum terinstall
    class _DummyApp:
        def add_handler(self, *a, **k): pass
        def run_polling(self, *a, **k): pass
        def stop(self): pass
    class _DummyBuilder:
        def token(self, t): return self
        def build(self): return _DummyApp()
    class Application:
        @staticmethod
        def builder(): return _DummyBuilder()
    class CommandHandler:
        def __init__(self, *a, **k): pass
    class MessageHandler:
        def __init__(self, *a, **k): pass
    class filters:
        TEXT = None
        COMMAND = None
    class Update:
        ALL_TYPES = None
    class ContextTypes:
        DEFAULT_TYPE = None

CONFIG_FILE = os.path.expanduser("~/.nexcorix_config.json")

C = {
    "r": "\033[0m", "b": "\033[1m", "d": "\033[2m",
    "R": "\033[91m", "G": "\033[92m", "Y": "\033[93m",
    "B": "\033[94m", "M": "\033[95m", "C": "\033[96m",
    "W": "\033[97m", "O": "\033[38;5;208m",
}

def c(name): return C.get(name, "")

def clear():
    os.system("clear")

def box_top(w=52, title=""):
    t = c("C") + "╔" + "═" * w + "╗" + c("r")
    if title:
        pad = (w - len(title)) // 2
        t += "\n" + c("C") + "║" + " " * pad + c("b") + c("Y") + title + c("r") + c("C") + " " * (w - len(title) - pad) + "║" + c("r")
    return t

def box_mid(text="", w=52, align="left", color="W"):
    if align == "center":
        pad = (w - len(text)) // 2
        return c("C") + "║" + " " * pad + c(color) + text + c("r") + c("C") + " " * (w - len(text) - pad) + "║" + c("r")
    elif align == "right":
        return c("C") + "║" + " " * (w - len(text) - 1) + c(color) + text + c("r") + c("C") + " " + "║" + c("r")
    else:
        return c("C") + "║ " + c(color) + text + c("r") + c("C") + " " * (w - len(text) - 1) + "║" + c("r")

def box_sep(w=52):
    return c("C") + "╠" + "═" * w + "╣" + c("r")

def box_bot(w=52):
    return c("C") + "╚" + "═" * w + "╝" + c("r")

def menu_item(num, text, desc="", color="W"):
    num_part = c("b") + c("Y") + f"[{num}]" + c("r")
    txt_part = c("b") + c(color) + text + c("r")
    desc_part = c("d") + desc + c("r")
    return "  " + num_part + " " + txt_part + "  " + desc_part

def header():
    return "\n".join([
        "",
        box_top(52),
        box_mid("🦂  N E X C O R I X   C L A W  🦂", 52, "center", "Y"),
        box_mid("Conversational AI Terminal v1.2", 52, "center", "d"),
        box_mid("Full System | Multi-Model | Chat Mode", 52, "center", "C"),
        box_bot(52),
        "",
    ])

def load_cfg():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except:
            pass
    return {
        "token": "", "openrouter_key": "", "model": "deepseek_chat",
        "admin_id": "", "temperature": 0.7, "max_tokens": 4096,
        "context_window": "auto", "performance": "balanced",
        "fallback_model": "deepseek_chat", "base_url": "https://openrouter.ai/api/v1",
        "org_id": "", "integrations": [],
        "os_detected": False, "os_summary": "", "os_info": {},
        "chat_history": {}, "personality": "helpful_assistant"
    }

def save_cfg(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
    print(c("G") + "\n    💾 Configuration saved!" + c("r"))

class OSDetector:
    def __init__(self):
        self.info = self._detect()
    
    def _detect(self):
        info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor() or "Unknown",
            "hostname": socket.gethostname(),
            "username": os.environ.get("USER") or os.environ.get("USERNAME") or "unknown",
            "home": os.path.expanduser("~"),
            "shell": os.environ.get("SHELL", os.environ.get("COMSPEC", "unknown")),
            "terminal": os.environ.get("TERM", "unknown"),
            "python": platform.python_version(),
        }
        if info["system"] == "Linux":
            try:
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            info["distro"] = line.split("=")[1].strip().strip('"')
                            break
            except:
                info["distro"] = "Unknown Linux"
        else:
            info["distro"] = info["system"]
        info["is_wsl"] = False
        try:
            with open("/proc/version") as f:
                if "microsoft" in f.read().lower():
                    info["is_wsl"] = True
        except:
            pass
        info["is_termux"] = os.environ.get("TERMUX_VERSION") is not None
        info["is_docker"] = os.path.exists("/.dockerenv")
        info["package_managers"] = self._detect_package_manager()
        return info
    
    def _detect_package_manager(self):
        managers = []
        cmds = {"apt": "apt", "apt-get": "apt-get", "yum": "yum", "dnf": "dnf",
                "pacman": "pacman", "zypper": "zypper", "apk": "apk",
                "brew": "brew", "pkg": "pkg", "choco": "choco", "winget": "winget",
                "pip": "pip", "pip3": "pip3", "npm": "npm", "gem": "gem"}
        for cmd, name in cmds.items():
            if os.system(f"which {cmd} >/dev/null 2>&1") == 0:
                managers.append(name)
        return managers if managers else ["unknown"]
    
    def get_summary(self):
        parts = [self.info["distro"]]
        if self.info["is_wsl"]: parts.append("(WSL)")
        if self.info["is_termux"]: parts.append("(Termux)")
        if self.info["is_docker"]: parts.append("(Docker)")
        return " ".join(parts)
    
    def get_ai_context(self):
        i = self.info
        pm = ", ".join(i["package_managers"])
        return "OS: " + self.get_summary() + " | Shell: " + i['shell'] + " | Arch: " + i['machine'] + " | PM: " + pm
    
    def save_to_config(self):
        cfg = load_cfg()
        cfg["os_info"] = self.info
        cfg["os_summary"] = self.get_summary()
        cfg["os_detected"] = True
        save_cfg(cfg)

class SystemExecutor:
    def __init__(self):
        self.os_detector = OSDetector()
        self.last_output = ""
        self.last_error = ""
    
    def run(self, command, timeout=300):
        try:
            if self.os_detector.info["system"] == "Windows":
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE, text=True, cwd=os.path.expanduser("~"))
            else:
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE, text=True, executable="/bin/bash",
                                         cwd=os.path.expanduser("~"))
            stdout, stderr = process.communicate(timeout=timeout)
            self.last_output = stdout
            self.last_error = stderr
            return {"success": process.returncode == 0, "returncode": process.returncode,
                    "stdout": stdout, "stderr": stderr, "command": command}
        except subprocess.TimeoutExpired:
            process.kill()
            return {"success": False, "returncode": -1, "stdout": self.last_output,
                    "stderr": "Command timed out after " + str(timeout) + "s", "command": command}
        except Exception as e:
            return {"success": False, "returncode": -1, "stdout": "", "stderr": str(e), "command": command}

class PackageInstaller:
    def __init__(self):
        self.os_detector = OSDetector()
        self.executor = SystemExecutor()
        self.pm_commands = {
            "apt": "apt install -y {package}", "apt-get": "apt-get install -y {package}",
            "yum": "yum install -y {package}", "dnf": "dnf install -y {package}",
            "pacman": "pacman -S --noconfirm {package}", "zypper": "zypper install -y {package}",
            "apk": "apk add {package}", "brew": "brew install {package}",
            "pkg": "pkg install -y {package}", "choco": "choco install {package} -y",
            "winget": "winget install {package} --accept-package-agreements --accept-source-agreements",
            "pip": "pip install {package}", "pip3": "pip3 install {package}",
            "npm": "npm install -g {package}", "gem": "gem install {package}",
        }
    
    def get_primary_pm(self):
        managers = self.os_detector.info.get("package_managers", [])
        priority = ["apt", "apt-get", "dnf", "yum", "pacman", "zypper", "apk", "brew", "pkg", "choco", "winget"]
        for pm in priority:
            if pm in managers:
                return pm
        return managers[0] if managers else None
    
    def install(self, package, pm=None):
        if not pm:
            pm = self.get_primary_pm()
        if not pm or pm == "unknown":
            return False, "No package manager detected!"
        if pm in self.pm_commands:
            cmd = self.pm_commands[pm].format(package=package)
            if pm in ["apt", "apt-get", "dnf", "yum", "pacman", "zypper", "apk"]:
                cmd = "sudo " + cmd
            result = self.executor.run(cmd, timeout=600)
            if result["success"]:
                return True, f"✅ {package} installed via {pm}\n```\n{result['stdout'][:1000]}\n```"
            else:
                return False, f"❌ Failed\n```\n{result['stderr'][:1000]}\n```"
        return False, f"Package manager {pm} not supported"
    
    def update_repos(self):
        pm = self.get_primary_pm()
        update_cmds = {"apt": "sudo apt update", "apt-get": "sudo apt-get update",
                       "dnf": "sudo dnf check-update", "yum": "sudo yum check-update",
                       "pacman": "sudo pacman -Sy", "zypper": "sudo zypper refresh",
                       "apk": "sudo apk update", "brew": "brew update", "pkg": "pkg update",
                       "choco": "choco upgrade chocolatey", "winget": "winget source update"}
        if pm in update_cmds:
            result = self.executor.run(update_cmds[pm], timeout=300)
            if result["success"]:
                return True, f"✅ Updated\n```\n{result['stdout'][:1000]}\n```"
            else:
                return False, f"❌ Failed\n```\n{result['stderr'][:1000]}\n```"
        return False, "Cannot update"

class FileManager:
    def __init__(self, base_path=None):
        self.current_path = os.path.expanduser(base_path or "~")
    
    def set_path(self, path):
        expanded = os.path.expanduser(path)
        if os.path.exists(expanded) and os.path.isdir(expanded):
            self.current_path = os.path.abspath(expanded)
            return True
        return False
    
    def create_file(self, filename, content=""):
        filepath = os.path.join(self.current_path, filename)
        try:
            with open(filepath, 'w') as f:
                f.write(content)
            return True, "File '" + filename + "' created!"
        except Exception as e:
            return False, "Error: " + str(e)
    
    def create_folder(self, foldername):
        folderpath = os.path.join(self.current_path, foldername)
        try:
            os.makedirs(folderpath, exist_ok=True)
            return True, "Folder '" + foldername + "' created!"
        except Exception as e:
            return False, "Error: " + str(e)
    
    def delete_item(self, name):
        target = os.path.join(self.current_path, name)
        if not os.path.exists(target):
            return False, "'" + name + "' not found!"
        try:
            if os.path.isfile(target):
                os.remove(target)
                return True, "File '" + name + "' deleted!"
            elif os.path.isdir(target):
                shutil.rmtree(target)
                return True, "Folder '" + name + "' deleted!"
        except Exception as e:
            return False, "Error: " + str(e)
    
    def read_file(self, filename):
        filepath = os.path.join(self.current_path, filename)
        if not os.path.isfile(filepath):
            return None, "Not found!"
        try:
            with open(filepath, 'r') as f:
                return f.read(), None
        except Exception as e:
            return None, "Error: " + str(e)
    
    def list_items(self):
        try:
            items = []
            with os.scandir(self.current_path) as entries:
                for entry in entries:
                    icon = "📁" if entry.is_dir() else "📄"
                    items.append(icon + " " + entry.name)
            return "\n".join(items) if items else "(empty)"
        except Exception as e:
            return "Error: " + str(e)
    
    def get_path(self):
        home = os.path.expanduser("~")
        path = self.current_path
        if path.startswith(home):
            path = "~" + path[len(home):]
        return path

class AIChatEngine:
    def __init__(self):
        self.cfg = load_cfg()
        self.os_detector = OSDetector()
        self.executor = SystemExecutor()
        self.installer = PackageInstaller()
        self.fm = FileManager()
        self.conversations = self.cfg.get("chat_history", {})
    
    def get_model_id(self, model_key=None):
        if not model_key:
            model_key = self.cfg.get("model", "deepseek_chat")
        return ALL_MODELS.get(model_key, {}).get("id", "deepseek/deepseek-chat")
    
    def check_ollama_available(self):
        try:
            result = subprocess.run(["which", "ollama"], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def chat_with_ai(self, user_id, message, model_key=None, system_prompt=None):
        api_key = self.cfg.get("openrouter_key", "")
        if not api_key:
            return None, "NO_API_KEY"
        
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        if not system_prompt:
            system_prompt = "You are Nexcorix Claw, an advanced AI assistant with full system access. You can chat naturally about any topic, tell jokes, help with homework, discuss philosophy, code, or anything. You also have access to the user's system and can execute commands when asked. Current system: " + self.os_detector.get_ai_context()
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in self.conversations[user_id][-10:]:
            messages.append(msg)
        messages.append({"role": "user", "content": message})
        
        try:
            data = json.dumps({
                "model": self.get_model_id(model_key),
                "messages": messages,
                "temperature": self.cfg.get("temperature", 0.7),
                "max_tokens": self.cfg.get("max_tokens", 4096)
            }).encode('utf-8')
            
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=data,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://nexcorix.claw",
                    "X-Title": "Nexcorix Claw"
                }
            )
            
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                ai_message = result["choices"][0]["message"]["content"]
                
                self.conversations[user_id].append({"role": "user", "content": message})
                self.conversations[user_id].append({"role": "assistant", "content": ai_message})
                
                cfg = load_cfg()
                cfg["chat_history"] = self.conversations
                save_cfg(cfg)
                
                return True, ai_message
                
        except urllib.error.HTTPError as e:
            if e.code == 402:
                return None, "PAYMENT_REQUIRED"
            elif e.code == 401:
                return None, "INVALID_KEY"
            elif e.code == 429:
                return None, "RATE_LIMIT"
            else:
                return None, f"HTTP_{e.code}"
        except Exception as e:
            return None, f"NETWORK_ERROR: {str(e)}"
    
    def detect_command_intent(self, text):
        text_lower = text.lower().strip()
        
        install_match = re.search(r'(?:install|pasang|instal)\s+([a-zA-Z0-9\-_\+]+(?:\s+[a-zA-Z0-9\-_\+]+)*)', text_lower)
        if install_match:
            return "install", install_match.group(1).strip()
        
        direct_cmds = ['nmap', 'sqlmap', 'nikto', 'gobuster', 'hydra', 'john', 'hashcat',
                      'python', 'python3', 'node', 'go', 'rustc', 'gcc', 'g++',
                      'ls', 'cd', 'cat', 'mkdir', 'rm', 'cp', 'mv', 'chmod',
                      'chown', 'sudo', 'systemctl', 'service', 'docker', 'kubectl',
                      'ifconfig', 'ip', 'netstat', 'ss', 'ping', 'traceroute',
                      'find', 'grep', 'awk', 'sed', 'tar', 'zip', 'unzip',
                      'git', 'nano', 'vim', 'htop', 'top', 'ps', 'kill',
                      'whoami', 'id', 'uname', 'df', 'du', 'free', 'uptime',
                      'apt', 'apt-get', 'yum', 'dnf', 'pacman', 'brew', 'pkg',
                      'pip', 'pip3', 'npm', 'wget', 'curl', 'ssh']
        
        words = text_lower.split()
        if words and words[0] in direct_cmds:
            return "execute", text_lower
        
        run_match = re.search(r'(?:run|execute|jalankan|eksekusi|exec)\s+(.+)', text_lower)
        if run_match:
            return "execute", run_match.group(1).strip()
        
        file_patterns = [
            (r'(?:buat|create|bikin|new)\s+file\s+([^\s]+)(?:\s+dengan\s+isi\s+)?(.*)?', 'create_file'),
            (r'(?:buat|create|bikin|new)\s+folder\s+([^\s]+)', 'create_folder'),
            (r'(?:hapus|delete|remove)\s+(?:file\s+|folder\s+)?([^\s]+)', 'delete'),
            (r'(?:baca|read|lihat|cat|show)\s+(?:file\s+)?([^\s]+)', 'read'),
            (r'(?:list|ls|dir|tampilkan)', 'list'),
            (r'(?:cd|pindah\s+ke|go\s+to|buka\s+folder)\s+([^\s]+)', 'cd'),
        ]
        for pattern, action in file_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return "file", (action, match.groups())
        
        return "chat", None
    
    def execute_command(self, intent, data):
        if intent == "install":
            pkgs = data.split()
            results = []
            for pkg in pkgs:
                success, result = self.installer.install(pkg.strip())
                results.append(f"{'✅' if success else '❌'} {pkg}: {result[:200]}")
            return "\n\n".join(results)
        
        elif intent == "execute":
            result = self.executor.run(data)
            output = ""
            if result["stdout"]:
                output += "📤 **STDOUT:**\n```\n" + result["stdout"][:2000] + "\n```\n"
            if result["stderr"]:
                output += "⚠️ **STDERR:**\n```\n" + result["stderr"][:1000] + "\n```\n"
            status = "✅" if result["success"] else "❌"
            return f"{status} **Executed:** `{data}`\n\n{output}"
        
        elif intent == "file":
            action, groups = data
            if action == "create_file":
                filename, content = groups[0], groups[1] if groups[1] else ""
                success, msg = self.fm.create_file(filename, content)
                return f"{'✅' if success else '❌'} {msg}"
            elif action == "create_folder":
                success, msg = self.fm.create_folder(groups[0])
                return f"{'✅' if success else '❌'} {msg}"
            elif action == "delete":
                success, msg = self.fm.delete_item(groups[0])
                return f"{'✅' if success else '❌'} {msg}"
            elif action == "read":
                content, error = self.fm.read_file(groups[0])
                if error:
                    return f"❌ {error}"
                return f"📄 **{groups[0]}:**\n```\n{content[:3000]}\n```"
            elif action == "list":
                return f"📂 **{self.fm.get_path()}**\n\n{self.fm.list_items()}"
            elif action == "cd":
                success = self.fm.set_path(groups[0])
                return f"{'✅' if success else '❌'} Now at: `{self.fm.get_path()}`"
        
        return None
    
    def process(self, user_id, text):
        intent, data = self.detect_command_intent(text)
        
        if intent in ["install", "execute", "file"]:
            return self.execute_command(intent, data)
        
        success, response = self.chat_with_ai(user_id, text)
        
        if not success:
            if response == "NO_API_KEY":
                return "🦂 **Nexcorix Claw**\n\n❌ **OpenRouter API Key belum diatur!**\n\nCara mengatasi:\n1. Buka https://openrouter.ai/keys\n2. Login (gratis) → Create API Key\n3. Di Nexcorix Claw, pilih menu **[5] API Keys → [1] Set OpenRouter Key**\n4. Paste key kamu\n\nAtau gunakan **Ollama (Local)** untuk tanpa API key:\n• Install: `curl -fsSL https://ollama.com/install.sh | sh`\n• Pull model: `ollama pull llama3.1`\n• Pilih model: Menu **[2] Models → [11] Ollama**"
            
            elif response == "PAYMENT_REQUIRED":
                return "🦂 **Nexcorix Claw**\n\n⚠️ **API Key valid tapi tidak punya credits!**\n\nSolusi:\n1. **Ganti ke model FREE tier** di menu [2] Models:\n   • `deepseek_chat` (DeepSeek V3 - free)\n   • `google_flash` (Gemini Flash - free tier)\n   • `meta_8b` (Llama 3.1 8B - free)\n\n2. **Isi credits** di https://openrouter.ai/credits (bisa $5 saja)\n\n3. **Pakai Ollama Local** (100% gratis, tanpa internet):\n   • `curl -fsSL https://ollama.com/install.sh | sh`\n   • `ollama pull llama3.1`\n   • Pilih menu [2] → [11] Ollama"
            
            elif response == "INVALID_KEY":
                return "🦂 **Nexcorix Claw**\n\n❌ **API Key salah atau tidak valid!**\n\nPastikan:\n• Key di-copy lengkap tanpa spasi\n• Key aktif di https://openrouter.ai/keys\n• Belum di-revoke atau expired"
            
            elif response == "RATE_LIMIT":
                return "🦂 **Nexcorix Claw**\n\n⏳ **Rate limit! Terlalu banyak request.**\n\nTunggu 1-2 menit atau ganti ke model lain."
            
            else:
                return f"🦂 **Nexcorix Claw**\n\n❌ **Error:** `{response}`\n\nTapi saya masih bisa bantu dengan:\n• 🖥️ System commands (install nmap, run ls -la)\n• 📁 File management\n• 📦 Package installation"
        
        return response

class NexcorixTelegramBot:
    _active_instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        with NexcorixTelegramBot._lock:
            # Hentikan instance lama kalau ada (auto-kill conflict)
            if NexcorixTelegramBot._active_instance is not None:
                try:
                    NexcorixTelegramBot._active_instance.stop()
                except Exception:
                    pass
                # Tunggu sebentar supaya koneksi lama lepas dari server Telegram
                time.sleep(1.5)
                NexcorixTelegramBot._active_instance = None
            NexcorixTelegramBot._active_instance = self
        
        self.cfg = load_cfg()
        self.ai = AIChatEngine()
        self.os_detector = OSDetector()
        self.application = None
        self._thread = None
        self._running = False
    
    def is_admin(self, user_id):
        admin_id = self.cfg.get("admin_id", "")
        if not admin_id:
            return True
        return str(user_id) == str(admin_id)
    
    async def start(self, update, context):
        user = update.effective_user
        os_info = self.os_detector.get_summary()
        model_name = ALL_MODELS.get(self.cfg.get("model", "deepseek_chat"), {}).get("name", "Unknown")
        
        welcome = f"""🦂 **Welcome to Nexcorix Claw!**

👤 User: `{user.first_name}` (`{user.id}`)
🖥️ System: `{os_info}`
🤖 Model: `{model_name}`
🔓 Mode: **Full Access**

I'm your conversational AI assistant. You can:
• 💬 **Chat naturally** — ask me anything, tell stories, jokes, coding help
• 🖥️ **Run commands** — "install nmap", "run ls -la", "nmap localhost"
• 📁 **Manage files** — "create file test.txt", "delete old folder"
• 📝 **Code together** — I can write and explain code in any language

**Commands:**
/start — Start bot
/model — Check current model
/help — Show help

**Examples:**
• "Hello, how are you?"
• "Explain quantum computing simply"
• "install nmap sqlmap"
• "buat file hello.py dengan isi print('hi')"
• "run uname -a"
"""
        await update.message.reply_text(welcome, parse_mode='Markdown')
    
    async def model_cmd(self, update, context):
        model_name = ALL_MODELS.get(self.cfg.get("model", "deepseek_chat"), {}).get("name", "Unknown")
        await update.message.reply_text(
            f"🤖 **Current Model:** `{model_name}`\n\n"
            f"Use the launcher menu [2] to change models.",
            parse_mode='Markdown'
        )
    
    async def help_cmd(self, update, context):
        help_text = """📖 **Nexcorix Claw Help**

**💬 CHAT MODE (Natural Conversation):**
Just chat with me naturally! I can:
• Answer questions, tell stories, give advice
• Help with coding, debugging, explaining concepts
• Discuss any topic: science, philosophy, tech, life
• Remember context from our conversation

**🖥️ SYSTEM COMMANDS:**
• `install nmap` — Install tools
• `run ls -la` — Execute commands
• `nmap -sV localhost` — Direct tool execution
• `sudo apt update` — Admin commands
• `docker ps` — Docker commands

**📁 FILE MANAGER:**
• `create file test.txt` — Create file
• `buat folder projects` — Create folder
• `delete old.txt` — Delete
• `read file.txt` — Read content
• `list` — List directory
• `cd ~/downloads` — Change directory

**📝 CODING:**
Ask me to write code in any language:
• "Write a Python web scraper"
• "buat kode javascript calculator"
• "Explain recursion in C++"

**🌍 LANGUAGES:**
I speak: English, Bahasa Indonesia, 日本語, 中文, and many more!

**Commands:**
/start — Start
/model — Current AI model
/help — This help
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def handle_message(self, update, context):
        user = update.effective_user
        text = update.message.text
        
        if not self.is_admin(user.id):
            await update.message.reply_text(
                "🚫 **Access Denied**\n\nYour ID: `" + str(user.id) + "`",
                parse_mode='Markdown'
            )
            return
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        response = self.ai.process(user.id, text)
        
        if len(response) > 4000:
            parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for part in parts:
                await update.message.reply_text(part, parse_mode='Markdown')
        else:
            await update.message.reply_text(response, parse_mode='Markdown')
    
    def stop(self):
        """Hentikan bot dengan benar: signal stop ke application + cleanup."""
        if not self._running or self.application is None:
            return
        
        print(c("Y") + "    ⏹️ Stopping bot instance..." + c("r"))
        try:
            self.application.stop()
        except Exception as e:
            # Kalau bot belum sempat start polling, stop() bisa error — abaikan saja
            pass
        
        self._running = False
        
        with NexcorixTelegramBot._lock:
            if NexcorixTelegramBot._active_instance is self:
                NexcorixTelegramBot._active_instance = None
    
    def run(self):
        if self._running:
            print(c("Y") + "    ⚠️ Bot already running!" + c("r"))
            return True
        
        token = self.cfg.get("token", "")
        if not token:
            print(c("R") + "Telegram token not set!" + c("r"))
            return False
        
        print(c("G") + "Starting Nexcorix Claw Bot..." + c("r"))
        print("Model: " + ALL_MODELS.get(self.cfg.get("model"), {}).get("name", "Unknown"))
        print("OS: " + self.os_detector.get_summary())
        
        self.application = Application.builder().token(token).build()
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("model", self.model_cmd))
        self.application.add_handler(CommandHandler("help", self.help_cmd))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        def start_bot():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # allowed_updates=None artinya semua jenis update (sama dengan Update.ALL_TYPES)
                self.application.run_polling(close_loop=False, stop_signals=None)
            except Exception as e:
                print(c("R") + f"    Bot error: {e}" + c("r"))
            finally:
                self._running = False
        
        self._thread = threading.Thread(target=start_bot, daemon=True)
        self._thread.start()
        self._running = True
        return True

ALL_MODELS = {
    "openai_gpt4o": {"name": "GPT-4o", "id": "openai/gpt-4o", "provider": "OpenAI", "icon": "🌟"},
    "openai_gpt4omini": {"name": "GPT-4o Mini", "id": "openai/gpt-4o-mini", "provider": "OpenAI", "icon": "⭐"},
    "openai_gpt4turbo": {"name": "GPT-4 Turbo", "id": "openai/gpt-4-turbo", "provider": "OpenAI", "icon": "💎"},
    "openai_gpt5": {"name": "GPT-5", "id": "openai/gpt-5", "provider": "OpenAI", "icon": "🔥"},
    "anthropic_sonnet": {"name": "Claude 3.5 Sonnet", "id": "anthropic/claude-3.5-sonnet", "provider": "Anthropic", "icon": "🎭"},
    "anthropic_opus": {"name": "Claude 3 Opus", "id": "anthropic/claude-3-opus", "provider": "Anthropic", "icon": "👑"},
    "anthropic_claude4": {"name": "Claude 4", "id": "anthropic/claude-4", "provider": "Anthropic", "icon": "👑"},
    "google_pro": {"name": "Gemini 1.5 Pro", "id": "google/gemini-1.5-pro", "provider": "Google", "icon": "🔮"},
    "google_flash": {"name": "Gemini 1.5 Flash", "id": "google/gemini-1.5-flash", "provider": "Google", "icon": "⚡", "free": True},
    "google_gemini25": {"name": "Gemini 2.5 Pro", "id": "google/gemini-2.5-pro", "provider": "Google", "icon": "🔮"},
    "deepseek_chat": {"name": "DeepSeek Chat (Free)", "id": "deepseek/deepseek-chat", "provider": "DeepSeek", "icon": "🧠", "free": True},
    "deepseek_coder": {"name": "DeepSeek Coder (Free)", "id": "deepseek/deepseek-coder", "provider": "DeepSeek", "icon": "💻", "free": True},
    "deepseek_r1": {"name": "DeepSeek R1", "id": "deepseek/deepseek-r1", "provider": "DeepSeek", "icon": "🔥"},
    "deepseek_v4": {"name": "DeepSeek V4", "id": "deepseek/deepseek-v4", "provider": "DeepSeek", "icon": "🚀"},
    "meta_70b": {"name": "Llama 3.1 70B", "id": "meta-llama/llama-3.1-70b-instruct", "provider": "Meta", "icon": "🦙"},
    "meta_8b": {"name": "Llama 3.1 8B (Free)", "id": "meta-llama/llama-3.1-8b-instruct", "provider": "Meta", "icon": "🐑", "free": True},
    "meta_llama4": {"name": "Llama 4", "id": "meta-llama/llama-4", "provider": "Meta", "icon": "🦙"},
    "qwen_72b": {"name": "Qwen 2.5 72B", "id": "qwen/qwen-2.5-72b-instruct", "provider": "Qwen", "icon": "🐉"},
    "qwen_qwen3": {"name": "Qwen 3", "id": "qwen/qwen-3", "provider": "Qwen", "icon": "🐉"},
    "mistral_large": {"name": "Mistral Large", "id": "mistralai/mistral-large", "provider": "Mistral", "icon": "🌊"},
    "kimi_k25": {"name": "Kimi K2.5", "id": "moonshotai/kimi-k2-5", "provider": "Kimi", "icon": "🌙"},
    "perplexity_sonar": {"name": "Sonar Large", "id": "perplexity/llama-3.1-sonar-large-128k-online", "provider": "Perplexity", "icon": "🔍"},
    "microsoft_wizard": {"name": "WizardLM 2", "id": "microsoft/wizardlm-2-8x22b", "provider": "Microsoft", "icon": "🧙"},
    "ollama_llama": {"name": "Llama 3.1 (Local)", "id": "llama3.1", "provider": "Ollama", "icon": "🦙", "local": True},
    "ollama_mistral": {"name": "Mistral (Local)", "id": "mistral", "provider": "Ollama", "icon": "🌊", "local": True},
    "ollama_qwen": {"name": "Qwen 2.5 (Local)", "id": "qwen2.5", "provider": "Ollama", "icon": "🐉", "local": True},
    "ollama_coder": {"name": "CodeLlama (Local)", "id": "codellama", "provider": "Ollama", "icon": "💻", "local": True},
}

PROVIDERS = {
    "1": {"name": "OpenAI", "icon": "🅾️", "color": "G", "models": ["openai_gpt4o", "openai_gpt4omini", "openai_gpt4turbo", "openai_gpt5"]},
    "2": {"name": "Anthropic", "icon": "🅰️", "color": "M", "models": ["anthropic_sonnet", "anthropic_opus", "anthropic_claude4"]},
    "3": {"name": "Google", "icon": "🅶️", "color": "B", "models": ["google_pro", "google_flash", "google_gemini25"]},
    "4": {"name": "DeepSeek", "icon": "🐋", "color": "C", "models": ["deepseek_chat", "deepseek_coder", "deepseek_r1", "deepseek_v4"]},
    "5": {"name": "Meta", "icon": "Ⓜ️", "color": "B", "models": ["meta_70b", "meta_8b", "meta_llama4"]},
    "6": {"name": "Qwen", "icon": "🇶", "color": "Y", "models": ["qwen_72b", "qwen_qwen3"]},
    "7": {"name": "Mistral", "icon": "Ⓜ️", "color": "Y", "models": ["mistral_large"]},
    "8": {"name": "Kimi", "icon": "🌙", "color": "W", "models": ["kimi_k25"]},
    "9": {"name": "Perplexity", "icon": "🔍", "color": "G", "models": ["perplexity_sonar"]},
    "10": {"name": "Microsoft", "icon": "✨", "color": "W", "models": ["microsoft_wizard"]},
    "11": {"name": "Ollama (Local)", "icon": "💻", "color": "G", "models": ["ollama_llama", "ollama_mistral", "ollama_qwen", "ollama_coder"]},
}

def chat_screen():
    ai = AIChatEngine()
    os_detector = OSDetector()
    
    clear(); print(header())
    print(box_top(52, "💬 NEXCORIX CHAT"))
    print(box_mid(""))
    print(box_mid("Model: " + ALL_MODELS.get(load_cfg().get("model"), {}).get("name", "Unknown"), 52, "center", "Y"))
    print(box_mid("OS: " + os_detector.get_summary(), 52, "center", "G"))
    print(box_mid("Chat naturally or run commands", 52, "center", "d"))
    print(box_mid("Type /back to return", 52, "center", "d"))
    print(box_mid(""))
    print(box_bot(52))
    
    user_id = "local_user"
    
    while True:
        user_input = input("\n    🦂 You ➤ ").strip()
        if user_input.lower() == "/back":
            break
        
        if not user_input:
            continue
        
        print(c("d") + "    🤖 Thinking..." + c("r"))
        
        response = ai.process(user_id, user_input)
        
        print(c("G") + "\n    🦂 Nexcorix ➤" + c("r"))
        print(c("W") + "    " + response.replace('\n', '\n    ') + c("r"))
        print()

def models_screen():
    cfg = load_cfg()
    while True:
        clear(); print(header())
        print(box_top(52, "🤖 MODELS"))
        print(box_mid(""))
        current = ALL_MODELS.get(cfg.get("model"), {}).get("name", "Not Set")
        print(box_mid("Current: " + current, 52))
        print(box_mid(""))
        print(box_sep(52))
        
        for pid, p in PROVIDERS.items():
            tag = "💻 Local" if pid == "11" else "🌐 OpenRouter"
            print(box_mid("[" + pid + "] " + p["icon"] + " " + p["name"] + " " + tag, 52))
        print(box_mid(""))
        print(box_mid("[0] Back", 52))
        print(box_bot(52))
        
        prov = input("\n    ➤ Select provider: ").strip()
        if prov == "0": break
        if prov not in PROVIDERS: continue
        
        while True:
            clear(); print(header())
            print(box_top(52, "🤖 " + PROVIDERS[prov]["name"]))
            print(box_mid(""))
            for i, mid in enumerate(PROVIDERS[prov]["models"], 1):
                m = ALL_MODELS[mid]
                cur = " ← CURRENT" if cfg.get("model") == mid else ""
                free_tag = " [FREE]" if m.get("free") else ""
                print(box_mid("[" + str(i) + "] " + m["icon"] + " " + m["name"] + free_tag + cur, 52))
            print(box_mid(""))
            print(box_mid("[0] Back", 52))
            print(box_bot(52))
            
            choice = input("\n    ➤ Select: ").strip()
            if choice == "0": break
            try:
                mid = PROVIDERS[prov]["models"][int(choice) - 1]
                cfg["model"] = mid
                save_cfg(cfg)
                print(c("G") + "    ✅ Model set to: " + ALL_MODELS[mid]["name"] + c("r"))
                time.sleep(1)
            except:
                continue

def system_shell_screen():
    executor = SystemExecutor()
    clear(); print(header())
    print(box_top(52, "🖥️  SYSTEM SHELL"))
    print(box_mid(""))
    print(box_mid("🔓 UNRESTRICTED ACCESS", 52, "center", "R"))
    print(box_mid("Type /back to exit", 52, "center", "d"))
    print(box_mid(""))
    print(box_bot(52))
    
    while True:
        cmd = input(c("R") + "\n    shell# " + c("r")).strip()
        if cmd.lower() == "/back":
            break
        if not cmd:
            continue
        
        result = executor.run(cmd)
        if result["stdout"]:
            print(c("C") + "\n    📤 OUTPUT:" + c("r"))
            for line in result["stdout"].split('\n')[:30]:
                print("    " + line[:50])
        if result["stderr"]:
            print(c("R") + "\n    ⚠️ ERROR:" + c("r"))
            for line in result["stderr"].split('\n')[:15]:
                print("    " + line[:50])
        print(c("G" if result["success"] else "R") + "    Exit: " + str(result["returncode"]) + c("r"))

def install_tools_screen():
    installer = PackageInstaller()
    while True:
        clear(); print(header())
        print(box_top(52, "📦 INSTALL TOOLS"))
        print(box_mid(""))
        print(box_mid("PM: " + str(installer.get_primary_pm()), 52))
        print(box_mid("Enter package name", 52, "center", "Y"))
        print(box_mid("Type 'update' for repo update", 52, "center", "d"))
        print(box_mid("Type /back to return", 52, "center", "d"))
        print(box_mid(""))
        print(box_bot(52))
        
        pkg = input("\n    ➤ Package: ").strip()
        if pkg.lower() == "/back":
            break
        if pkg.lower() == "update":
            success, result = installer.update_repos()
            print(c("G") if success else c("R"))
            print(result[:2000])
            print(c("r"))
            input("\n    Press Enter...")
            continue
        
        if pkg:
            print(c("Y") + f"\n    Installing {pkg}..." + c("r"))
            success, result = installer.install(pkg)
            print(c("G") if success else c("R"))
            print(result[:2000])
            print(c("r"))
            input("\n    Press Enter...")

def api_keys_screen():
    cfg = load_cfg()
    clear(); print(header())
    print(box_top(52, "🔑 API KEYS"))
    print(box_mid(""))
    print(box_mid("OpenRouter: " + ("✅ Set" if cfg.get("openrouter_key") else "❌ Not Set"), 52))
    print(box_mid("Telegram:   " + ("✅ Set" if cfg.get("token") else "❌ Not Set"), 52))
    print(box_mid("Admin ID:   " + (cfg.get("admin_id") or "❌ Not Set"), 52))
    print(box_mid(""))
    print(box_mid("[1] Set OpenRouter Key", 52))
    print(box_mid("[2] Set Telegram Token", 52))
    print(box_mid("[3] Set Admin ID", 52))
    print(box_mid("[0] Back", 52))
    print(box_bot(52))
    
    p = input("\n    ➤ ").strip()
    if p == "1":
        k = input("    OpenRouter Key: ").strip()
        if k: cfg["openrouter_key"] = k; save_cfg(cfg)
    elif p == "2":
        t = input("    Telegram Token: ").strip()
        if t: cfg["token"] = t; save_cfg(cfg)
    elif p == "3":
        aid = input("    Admin ID: ").strip()
        if aid: cfg["admin_id"] = aid; save_cfg(cfg)

def main():
    OSDetector().save_to_config()
    bot_running = False
    active_bot = None  # Simpan instance bot yang sedang jalan
    
    while True:
        clear(); print(header())
        print(box_top(52))
        
        cfg = load_cfg()
        m = ALL_MODELS.get(cfg.get("model", "deepseek_chat"), {})
        ready = cfg.get("token") != "" and cfg.get("openrouter_key") != ""
        status = c("G") + "● ONLINE" if ready else c("R") + "● OFFLINE"
        os_summary = cfg.get("os_summary", "Unknown OS")
        os_icon = "🐧" if "Linux" in os_summary else "🍎" if "Darwin" in os_summary else "🪟" if "Windows" in os_summary else "🖥️"
        
        print(box_mid(status + c("r") + "  " + m.get("icon","") + " " + m.get("name","Not Set"), 52))
        print(box_mid(os_icon + " " + os_summary[:40], 52, "center", "C"))
        print(box_sep(52))
        
        print(box_mid(menu_item("1", "Chat", "Conversational AI"), 52))
        print(box_mid(menu_item("2", "Models", "Switch AI model"), 52))
        print(box_mid(menu_item("3", "System Shell", "Direct shell"), 52))
        print(box_mid(menu_item("4", "Install Tools", "Package manager"), 52))
        print(box_mid(menu_item("5", "API Keys", "Auth tokens"), 52))
        print(box_sep(52))
        print(box_mid(menu_item("6", "Start Bot", "Telegram bot"), 52))
        print(box_mid(menu_item("7", "Stop Bot", "Stop bot"), 52))
        print(box_sep(52))
        print(box_mid(menu_item("8", "Exit", "Close"), 52))
        print(box_bot(52))
        
        p = input("\n    ➤ Select [1-8]: ").strip()
        
        if p == "1": chat_screen()
        elif p == "2": models_screen()
        elif p == "3": system_shell_screen()
        elif p == "4": install_tools_screen()
        elif p == "5": api_keys_screen()
        elif p == "6":
            if not TELEGRAM_AVAILABLE:
                print(c("R") + "\n    ❌ pip install python-telegram-bot" + c("r"))
                time.sleep(2)
            elif not cfg.get("token"):
                print(c("R") + "\n    ❌ Telegram token not set!" + c("r"))
                time.sleep(2)
            else:
                # Hentikan bot lama kalau ada, baru start yang baru
                if active_bot is not None:
                    active_bot.stop()
                    active_bot = None
                    time.sleep(1)
                
                active_bot = NexcorixTelegramBot()
                bot_running = active_bot.run()
                if bot_running:
                    print(c("G") + "\n    ✅ Bot running in background!" + c("r"))
                time.sleep(2)
        elif p == "7":
            if active_bot is not None:
                active_bot.stop()
                active_bot = None
            bot_running = False
            print(c("Y") + "\n    ⏹️ Bot stopped" + c("r"))
            time.sleep(1)
        elif p == "8":
            # Bersihkan bot sebelum exit
            if active_bot is not None:
                active_bot.stop()
            clear(); print(header())
            print(box_top(52))
            print(box_mid("👋 Goodbye!", 52, "center", "G"))
            print(box_bot(52))
            break
        else:
            print(c("R") + "\n    ❌ Invalid!" + c("r"))
            time.sleep(1)

if __name__ == "__main__":
    main()
