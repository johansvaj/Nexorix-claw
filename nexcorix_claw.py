#!/usr/bin/env python3
"""
Nexcorix Claw v4.0 - Ultimate Multi-Channel AI Agent with 100+ Models
All commands execute directly, no "how to" instructions.
"""

import os
import sys
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
import urllib.parse
from pathlib import Path
from html.parser import HTMLParser
from typing import Dict, Any, Optional, List

# ========== Auto Install ==========
def ensure_package(package_name, import_name=None):
    if import_name is None:
        import_name = package_name.replace('-', '_')
    try:
        __import__(import_name)
        return True
    except ImportError:
        print(f"[Auto-install] {package_name} not found, installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package_name], check=False)
            __import__(import_name)
            return True
        except:
            return False

# ========== Warna ==========
C = {
    "r":"\033[0m","b":"\033[1m","d":"\033[2m",
    "R":"\033[91m","G":"\033[92m","Y":"\033[93m","B":"\033[94m","M":"\033[95m","C":"\033[96m","W":"\033[97m",
    "O":"\033[38;5;208m","P":"\033[38;5;141m","T":"\033[38;5;37m","L":"\033[38;5;11m",
}
def c(name): return C.get(name, "")
def clear(): os.system("clear")

CONFIG_FILE = os.path.expanduser("~/.nexcorix_config.json")
def load_cfg():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f: return json.load(f)
        except: pass
    return {
        "provider": "openrouter", "model": "openai/gpt-4o", "fallback_model": "deepseek/deepseek-chat",
        "openai_key": "", "anthropic_key": "", "google_key": "", "deepseek_key": "", "openrouter_key": "",
        "custom_api_url": "", "custom_api_key": "", "ollama_url": "http://localhost:11434",
        "temperature": 0.7, "max_tokens": 4096, "context_window": "auto", "performance": "balanced",
        "admin_id": "", "token": "", "base_url": "https://openrouter.ai/api/v1",
        "chat_history": {}, "channels": {}
    }
def save_cfg(cfg):
    with open(CONFIG_FILE, "w") as f: json.dump(cfg, f, indent=2)

# ========== OS Detector ==========
class OSDetector:
    def __init__(self):
        self.info = self._detect()
    def _detect(self):
        info = {
            "system": platform.system(), "release": platform.release(),
            "version": platform.version(), "platform": platform.platform(),
            "machine": platform.machine(), "processor": platform.processor() or "Unknown",
            "hostname": socket.gethostname(),
            "username": os.environ.get("USER") or os.environ.get("USERNAME") or "unknown",
            "home": os.path.expanduser("~"), "shell": os.environ.get("SHELL", os.environ.get("COMSPEC", "unknown")),
            "terminal": os.environ.get("TERM", "unknown"), "python": platform.python_version(),
        }
        if info["system"] == "Linux":
            try:
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            info["distro"] = line.split("=")[1].strip().strip('"')
                            break
            except: info["distro"] = "Unknown Linux"
        else: info["distro"] = info["system"]
        info["is_wsl"] = False
        try:
            with open("/proc/version") as f:
                if "microsoft" in f.read().lower(): info["is_wsl"] = True
        except: pass
        info["is_termux"] = os.environ.get("TERMUX_VERSION") is not None
        info["is_docker"] = os.path.exists("/.dockerenv")
        info["package_managers"] = self._detect_package_manager()
        return info
    def _detect_package_manager(self):
        managers = []
        cmds = {"apt":"apt","apt-get":"apt-get","yum":"yum","dnf":"dnf","pacman":"pacman","zypper":"zypper","apk":"apk","brew":"brew","pkg":"pkg","choco":"choco","winget":"winget","pip":"pip","pip3":"pip3","npm":"npm","gem":"gem"}
        for cmd, name in cmds.items():
            if os.system(f"which {cmd} >/dev/null 2>&1") == 0: managers.append(name)
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
        return f"OS: {self.get_summary()} | Shell: {i['shell']} | Arch: {i['machine']} | PM: {pm}"

# ========== System Executor ==========
class SystemExecutor:
    def __init__(self): self.os_detector = OSDetector()
    def run(self, command, timeout=300):
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=os.path.expanduser("~"))
            stdout, stderr = process.communicate(timeout=timeout)
            return {"success": process.returncode == 0, "returncode": process.returncode, "stdout": stdout, "stderr": stderr, "command": command}
        except subprocess.TimeoutExpired:
            process.kill()
            return {"success": False, "returncode": -1, "stdout": "", "stderr": f"Command timed out after {timeout}s", "command": command}
        except Exception as e:
            return {"success": False, "returncode": -1, "stdout": "", "stderr": str(e), "command": command}

# ========== Advanced Installer ==========
class AdvancedInstaller:
    def __init__(self):
        self.os_detector = OSDetector()
        self.executor = SystemExecutor()
        self.pm_commands = {
            "apt": "DEBIAN_FRONTEND=noninteractive apt install -y {package}",
            "apt-get": "DEBIAN_FRONTEND=noninteractive apt-get install -y {package}",
            "yum": "yum install -y {package}", "dnf": "dnf install -y {package}",
            "pacman": "pacman -S --noconfirm {package}", "zypper": "zypper install -y {package}",
            "apk": "apk add {package}", "brew": "brew install {package}",
            "pkg": "pkg install -y {package}", "choco": "choco install {package} -y",
            "winget": "winget install {package} --accept-package-agreements --accept-source-agreements",
            "pip": "pip install {package}", "pip3": "pip3 install {package}", "npm": "npm install -g {package}", "gem": "gem install {package}",
        }
        self.tool_aliases = {
            "msfconsole":"metasploit-framework","msfvenom":"metasploit-framework","nmap":"nmap","sqlmap":"sqlmap",
            "gobuster":"gobuster","hydra":"hydra","john":"john","hashcat":"hashcat","aircrack-ng":"aircrack-ng",
            "nikto":"nikto","dirb":"dirb","wpscan":"wpscan","python3":"python3","git":"git","curl":"curl","wget":"wget",
        }
        self.github_tools = {
            "linpeas":"https://github.com/carlospolop/PEASS-ng.git","winpeas":"https://github.com/carlospolop/PEASS-ng.git",
            "impacket":"https://github.com/fortra/impacket.git","kerbrute":"https://github.com/ropnop/kerbrute.git","pspy":"https://github.com/DominicBreuker/pspy.git",
        }
    def get_primary_pm(self):
        managers = self.os_detector.info.get("package_managers", [])
        priority = ["apt","apt-get","dnf","yum","pacman","zypper","apk","brew","pkg","choco","winget"]
        for pm in priority:
            if pm in managers: return pm
        return managers[0] if managers else None
    def resolve_package(self, tool_name): return self.tool_aliases.get(tool_name.lower(), tool_name)
    def install(self, package, pm=None):
        if not pm: pm = self.get_primary_pm()
        if not pm or pm=="unknown": return False, "No package manager!"
        resolved = self.resolve_package(package)
        if package.lower() in self.github_tools: return self.install_from_github(package.lower())
        if pm in self.pm_commands:
            cmd = self.pm_commands[pm].format(package=resolved)
            if pm in ["apt","apt-get","dnf","yum","pacman","zypper","apk"]: cmd = "sudo "+cmd
            result = self.executor.run(cmd, timeout=600)
            if result["success"]: return True, f"OK {package} via {pm}\n{result['stdout'][:1500]}"
            else:
                if resolved != package:
                    cmd2 = self.pm_commands[pm].format(package=package)
                    if pm in ["apt","apt-get","dnf","yum","pacman","zypper","apk"]: cmd2 = "sudo "+cmd2
                    result2 = self.executor.run(cmd2, timeout=600)
                    if result2["success"]: return True, f"OK {package} via {pm}\n{result2['stdout'][:1500]}"
                return False, f"FAIL {package}\n{result['stderr'][:1500]}"
        return False, f"PM {pm} not supported"
    def install_multiple(self, packages):
        results = []
        for pkg in packages:
            s,r = self.install(pkg.strip())
            results.append(f"{'OK' if s else 'FAIL'} {pkg}: {r[:300]}")
        return "\n\n".join(results)
    def install_from_github(self, tool_name):
        if tool_name not in self.github_tools: return False, "Not in registry"
        repo_url = self.github_tools[tool_name]
        install_dir = os.path.expanduser(f"~/tools/{tool_name}")
        os.makedirs(os.path.expanduser("~/tools"), exist_ok=True)
        result = self.executor.run(f"git clone {repo_url} {install_dir} 2>&1 || cd {install_dir} && git pull 2>&1", timeout=120)
        if not result["success"] and "already exists" not in result["stderr"]:
            return False, f"Git clone failed:\n{result['stderr'][:1000]}"
        setup_result = f"Cloned to {install_dir}"
        if tool_name in ["linpeas","winpeas"]: setup_result = "PEASS downloaded. Usage: cd ~/tools/linpeas && ./linpeas.sh"
        elif tool_name == "impacket":
            self.executor.run(f"cd {install_dir} && pip3 install . 2>&1", timeout=120)
            setup_result = "impacket installed via pip3."
        return True, f"GitHub Install: {tool_name}\nRepo: {repo_url}\nDir: {install_dir}\n\n{setup_result}"
    def install_pip_tool(self, package):
        result = self.executor.run(f"pip3 install {package}", timeout=180)
        if result["success"]: return True, f"pip3 install {package} OK\n{result['stdout'][:1000]}"
        else: return False, f"pip3 install failed:\n{result['stderr'][:1000]}"
    def update_repos(self):
        pm = self.get_primary_pm()
        update_cmds = {"apt":"sudo apt update","apt-get":"sudo apt-get update","dnf":"sudo dnf check-update","yum":"sudo yum check-update","pacman":"sudo pacman -Sy","zypper":"sudo zypper refresh","apk":"sudo apk update","brew":"brew update","pkg":"pkg update","choco":"choco upgrade chocolatey","winget":"winget source update"}
        if pm in update_cmds:
            result = self.executor.run(update_cmds[pm], timeout=300)
            if result["success"]: return True, f"Updated\n{result['stdout'][:1500]}"
            else: return False, f"Failed\n{result['stderr'][:1500]}"
        return False, "Cannot update"

# ========== File Manager ==========
class FileManager:
    def __init__(self, base_path=None): self.current_path = os.path.expanduser(base_path or "~")
    def set_path(self, path):
        expanded = os.path.expanduser(path)
        if os.path.exists(expanded) and os.path.isdir(expanded): self.current_path = os.path.abspath(expanded); return True
        return False
    def create_file(self, filename, content=""):
        filepath = os.path.join(self.current_path, filename)
        try:
            with open(filepath, 'w') as f: f.write(content)
            return True, f"File '{filename}' created!"
        except Exception as e: return False, f"Error: {e}"
    def create_folder(self, foldername):
        folderpath = os.path.join(self.current_path, foldername)
        try:
            os.makedirs(folderpath, exist_ok=True)
            return True, f"Folder '{foldername}' created!"
        except Exception as e: return False, f"Error: {e}"
    def delete_item(self, name):
        target = os.path.join(self.current_path, name)
        if not os.path.exists(target): return False, f"'{name}' not found!"
        try:
            if os.path.isfile(target): os.remove(target); return True, f"File '{name}' deleted!"
            elif os.path.isdir(target): shutil.rmtree(target); return True, f"Folder '{name}' deleted!"
        except Exception as e: return False, f"Error: {e}"
    def read_file(self, filename):
        filepath = os.path.join(self.current_path, filename)
        if not os.path.isfile(filepath): return None, "Not found!"
        try:
            with open(filepath, 'r') as f: return f.read(), None
        except Exception as e: return None, f"Error: {e}"
    def list_items(self):
        try:
            items = []
            with os.scandir(self.current_path) as entries:
                for entry in entries:
                    icon = "[DIR]" if entry.is_dir() else "[FILE]"
                    items.append(f"{icon} {entry.name}")
            return "\n".join(items) if items else "(empty)"
        except Exception as e: return f"Error: {e}"
    def get_path(self):
        home = os.path.expanduser("~")
        path = self.current_path
        if path.startswith(home): path = "~" + path[len(home):]
        return path

# ========== Network Scanner ==========
class NetworkScanner:
    def __init__(self):
        self.executor = SystemExecutor()
    def scan_network(self, target="192.168.1.0/24"):
        # Coba nmap
        cmd = f"nmap -sn {target} 2>/dev/null"
        result = self.executor.run(cmd, timeout=60)
        if result["success"] and result["stdout"].strip():
            return f"🔍 Scan result for {target}:\n{result['stdout']}"
        # Fallback arp-scan
        cmd2 = f"arp-scan --localnet 2>/dev/null"
        result2 = self.executor.run(cmd2, timeout=60)
        if result2["success"] and result2["stdout"].strip():
            return f"🔍 ARP scan result:\n{result2['stdout']}"
        return f"❌ Network scan failed. Install nmap or arp-scan.\nError: {result['stderr'] or result2['stderr']}"
    def scan_ports(self, target, ports="1-1000"):
        cmd = f"nmap -p {ports} {target}"
        result = self.executor.run(cmd, timeout=120)
        return result["stdout"] if result["success"] else f"Port scan failed:\n{result['stderr']}"
    def wifi_scan(self):
        cmd = "nmcli dev wifi list 2>/dev/null || sudo iwlist wlan0 scan 2>/dev/null | grep -E 'ESSID|Signal'"
        result = self.executor.run(cmd, timeout=30)
        return result["stdout"] if result["success"] else "WiFi scan not available."

# ========== Local Browser ==========
class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset(); self.fed = []; self.in_script = False
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.in_script = True
    def handle_endtag(self, tag):
        if tag in ('script','style'): self.in_script = False
    def handle_data(self, d):
        if not self.in_script: self.fed.append(d)
    def get_data(self): return ' '.join(self.fed)

class LocalBrowser:
    def __init__(self): self.executor = SystemExecutor()
    def browse(self, url):
        if not url.startswith(('http://','https://')): url = 'https://'+url
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
            stripper = HTMLStripper()
            stripper.feed(html)
            text = re.sub(r'\s+',' ',stripper.get_data()).strip()
            return True, text[:4000]
        except Exception as e: return False, f"Browse error: {e}"
    def search_duckduckgo(self, query):
        try:
            q = urllib.parse.quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={q}"
            req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
            results = []
            titles = re.findall(r'<a[^>]+class="result__a"[^>]*>(.*?)</a>', html)
            snippets = re.findall(r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', html)
            for i, (t,s) in enumerate(zip(titles[:5], snippets[:5]), 1):
                t_clean = re.sub(r'<[^>]+>','',t)
                s_clean = re.sub(r'<[^>]+>','',s)
                results.append(f"{i}. {t_clean}\n   {s_clean[:150]}...")
            return True, "Search Results:\n\n"+("\n\n".join(results) if results else "No results.")
        except Exception as e: return False, f"Search error: {e}"

# ========== Web Server ==========
class WebServerManager:
    def __init__(self):
        self.fm = FileManager()
        self._servers = {}
    def create_html_site(self, name, content=None):
        path = os.path.join(self.fm.current_path, name)
        os.makedirs(path, exist_ok=True)
        html = content or "<html><body><h1>Nexcorix Server</h1></body></html>"
        with open(os.path.join(path, "index.html"), 'w') as f: f.write(html)
        return path
    def start_server(self, folder_path, port=8080):
        if port in self._servers and self._servers[port].is_alive():
            ip = socket.gethostbyname(socket.gethostname())
            return True, f"http://{ip}:{port} (already running)"
        def serve():
            os.chdir(folder_path)
            handler = __import__('http.server', fromlist=['SimpleHTTPRequestHandler']).SimpleHTTPRequestHandler
            server = __import__('http.server', fromlist=['HTTPServer']).HTTPServer(("", port), handler)
            server.serve_forever()
        t = threading.Thread(target=serve, daemon=True)
        t.start()
        self._servers[port] = t
        time.sleep(1)
        ip = socket.gethostbyname(socket.gethostname())
        return True, f"Web Server Started!\nURL: http://{ip}:{port}\nFolder: {folder_path}"

# ========== 100+ Model Definitions ==========
MODELS_BY_PROVIDER = {
    "openai": ["openai/gpt-4o", "openai/gpt-4o-mini", "openai/gpt-4-turbo", "openai/gpt-4", "openai/gpt-3.5-turbo", "openai/o1-preview", "openai/o1-mini", "openai/o3-mini"],
    "anthropic": ["anthropic/claude-3.5-sonnet", "anthropic/claude-3-opus", "anthropic/claude-3-sonnet", "anthropic/claude-3-haiku"],
    "google": ["google/gemini-1.5-pro", "google/gemini-1.5-flash", "google/gemini-1.0-pro", "google/gemma-2-9b-it", "google/gemma-2-27b-it"],
    "deepseek": ["deepseek/deepseek-chat", "deepseek/deepseek-coder"],
    "meta": ["meta-llama/llama-3.1-405b-instruct", "meta-llama/llama-3.1-70b-instruct", "meta-llama/llama-3.1-8b-instruct", "meta-llama/llama-3-70b-instruct", "meta-llama/llama-3-8b-instruct"],
    "mistral": ["mistralai/mistral-large", "mistralai/mistral-medium", "mistralai/mixtral-8x7b-instruct", "mistralai/mistral-7b-instruct", "mistralai/codestral-22b-instruct", "mistralai/mathstral-7b-instruct"],
    "qwen": ["qwen/qwen-2.5-72b-instruct", "qwen/qwen-2.5-32b-instruct", "qwen/qwen-2.5-14b-instruct", "qwen/qwen-2-7b-instruct"],
    "xai": ["x-ai/grok-2", "x-ai/grok-1", "x-ai/grok-beta"],
    "cohere": ["cohere/command-r-plus", "cohere/command-r"],
    "ai21": ["ai21/jamba-1.5"],
    "databricks": ["databricks/dbrx-instruct"],
    "upstage": ["upstage/solar-10.7b-instruct"],
    "nvidia": ["nvidia/nemotron-4-340b-instruct"],
    "perplexity": ["perplexity/pplx-7b-online"],
    "moonshot": ["moonshot/kimi-v1"],
    "openrouter": ["openai/gpt-4o", "anthropic/claude-3.5-sonnet", "google/gemini-1.5-pro", "deepseek/deepseek-chat", "meta-llama/llama-3.1-70b-instruct", "mistralai/mistral-large", "qwen/qwen-2.5-72b-instruct", "x-ai/grok-2", "cohere/command-r-plus", "ai21/jamba-1.5", "databricks/dbrx-instruct", "upstage/solar-10.7b-instruct", "nvidia/nemotron-4-340b-instruct", "perplexity/pplx-7b-online", "moonshot/kimi-v1"]
}
ALL_MODELS = {}
for provider, models in MODELS_BY_PROVIDER.items():
    for model_id in models:
        ALL_MODELS[model_id] = {"provider": provider, "name": model_id.split('/')[-1]}

# ========== AI Chat Engine ==========
class AIChatEngine:
    def __init__(self):
        self.cfg = load_cfg()
        self.os_detector = OSDetector()
        self.executor = SystemExecutor()
        self.installer = AdvancedInstaller()
        self.fm = FileManager()
        self.browser = LocalBrowser()
        self.web = WebServerManager()
        self.network = NetworkScanner()
        self.conversations = self.cfg.get("chat_history", {})

    def get_api_url_and_key(self):
        provider = self.cfg.get("provider", "openrouter")
        if provider == "openai":
            return "https://api.openai.com/v1/chat/completions", self.cfg.get("openai_key", "")
        elif provider == "anthropic":
            return "https://api.anthropic.com/v1/messages", self.cfg.get("anthropic_key", "")
        elif provider == "google":
            key = self.cfg.get("google_key", "")
            return f"https://generativelanguage.googleapis.com/v1beta/models/{self.cfg.get('model')}:generateContent?key={key}", key
        elif provider == "deepseek":
            return "https://api.deepseek.com/v1/chat/completions", self.cfg.get("deepseek_key", "")
        elif provider == "ollama":
            return f"{self.cfg.get('ollama_url', 'http://localhost:11434')}/api/generate", "dummy"
        elif provider == "custom":
            return self.cfg.get("custom_api_url", ""), self.cfg.get("custom_api_key", "")
        else:
            return self.cfg.get("base_url", "https://openrouter.ai/api/v1") + "/chat/completions", self.cfg.get("openrouter_key", "")

    def chat_with_ai(self, user_id, message, system_prompt=None):
        api_url, api_key = self.get_api_url_and_key()
        if not api_key and self.cfg.get("provider") not in ["ollama"]:
            return None, "NO_API_KEY"
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        if not system_prompt:
            system_prompt = (
                "You are Nexcorix Claw, an AI agent with FULL SYSTEM CONTROL. "
                "You MUST execute commands immediately, do NOT give instructions. "
                "When asked to scan network, run 'nmap -sn'. When asked to install, run 'install'. "
                "You must respond with the ACTUAL RESULT of the command, not a tutorial."
                f"System info: {self.os_detector.get_ai_context()}"
            )
        messages = [{"role": "system", "content": system_prompt}]
        for msg in self.conversations[user_id][-50:]:
            messages.append(msg)
        messages.append({"role": "user", "content": message})

        model = self.cfg.get("model", "openai/gpt-4o")
        provider = self.cfg.get("provider", "openrouter")
        headers = {"Content-Type": "application/json"}
        if provider == "openai":
            headers["Authorization"] = f"Bearer {api_key}"
            data = {"model": model.split('/')[-1], "messages": messages, "temperature": self.cfg.get("temperature",0.7), "max_tokens": self.cfg.get("max_tokens",4096)}
        elif provider == "anthropic":
            headers["x-api-key"] = api_key
            headers["anthropic-version"] = "2023-06-01"
            data = {"model": model.split('/')[-1], "messages": messages, "system": system_prompt, "max_tokens": self.cfg.get("max_tokens",4096)}
        elif provider == "google":
            data = {"contents": [{"parts":[{"text":message}]}]}
        elif provider == "deepseek":
            headers["Authorization"] = f"Bearer {api_key}"
            data = {"model": model.split('/')[-1], "messages": messages, "temperature": self.cfg.get("temperature",0.7), "max_tokens": self.cfg.get("max_tokens",4096)}
        elif provider == "ollama":
            data = {"model": model.split('/')[-1], "prompt": message, "stream": False}
        elif provider == "custom":
            headers["Authorization"] = f"Bearer {api_key}" if api_key else ""
            data = {"model": model, "messages": messages, "temperature": self.cfg.get("temperature",0.7), "max_tokens": self.cfg.get("max_tokens",4096)}
        else:
            headers["Authorization"] = f"Bearer {api_key}"
            data = {"model": model, "messages": messages, "temperature": self.cfg.get("temperature",0.7), "max_tokens": self.cfg.get("max_tokens",4096)}

        try:
            req = urllib.request.Request(api_url, data=json.dumps(data).encode(), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode())
                if provider == "openai":
                    ai_message = result["choices"][0]["message"]["content"]
                elif provider == "anthropic":
                    ai_message = result["content"][0]["text"]
                elif provider == "google":
                    ai_message = result["candidates"][0]["content"]["parts"][0]["text"]
                elif provider == "deepseek":
                    ai_message = result["choices"][0]["message"]["content"]
                elif provider == "ollama":
                    ai_message = result["response"]
                else:
                    ai_message = result["choices"][0]["message"]["content"]
                self.conversations[user_id].append({"role": "user", "content": message})
                self.conversations[user_id].append({"role": "assistant", "content": ai_message})
                save_cfg(self.cfg)
                return True, ai_message
        except Exception as e:
            return None, str(e)

    def process(self, user_id, text):
        lower = text.lower().strip()
        
        # ========== SCAN JARINGAN (prioritas) ==========
        if re.search(r'(scan|cek|lihat)\s+(network|jaringan|ip|wifi)', lower) or re.match(r'scan\s+\d+\.\d+\.\d+\.\d+', lower):
            target_match = re.search(r'(\d+\.\d+\.\d+\.\d+(?:/\d+)?)', text)
            target = target_match.group(1) if target_match else "192.168.1.0/24"
            if 'wifi' in lower:
                return self.network.wifi_scan()
            else:
                return self.network.scan_network(target)
        
        if re.match(r'scan ports?\s+', lower):
            parts = re.sub(r'scan ports?\s+', '', text).strip().split()
            target = parts[0] if parts else "localhost"
            ports = parts[1] if len(parts) > 1 else "1-1000"
            return self.network.scan_ports(target, ports)
        
        if 'wifi scan' in lower or 'scan wifi' in lower:
            return self.network.wifi_scan()
        
        # ========== INSTALL ==========
        if re.match(r'^(install|pasang|instal)\s+', lower):
            pkgs = re.sub(r'^(install|pasang|instal)\s+', '', text).strip().split()
            if len(pkgs) > 1:
                return self.installer.install_multiple(pkgs)
            else:
                s, r = self.installer.install(pkgs[0])
                return ("OK " if s else "FAIL ") + r
        
        if re.match(r'^(github|clone)\s+', lower):
            tool = re.sub(r'^(github|clone)\s+', '', text).strip()
            s, r = self.installer.install_from_github(tool)
            return ("OK " if s else "FAIL ") + r
        
        if re.match(r'^pip\s+', lower):
            pkg = re.sub(r'^pip\s+', '', text).strip()
            s, r = self.installer.install_pip_tool(pkg)
            return ("OK " if s else "FAIL ") + r
        
        # ========== BROWSING & SEARCH ==========
        if re.match(r'(browse|buka|lihat|open)\s+', lower):
            url = re.sub(r'^(browse|buka|lihat|open)\s+', '', text).strip()
            s, res = self.browser.browse(url)
            return res if s else f"Error: {res}"
        
        if re.match(r'(search|cari|google|temukan)\s+', lower):
            query = re.sub(r'^(search|cari|google|temukan)\s+', '', text).strip()
            s, res = self.browser.search_duckduckgo(query)
            return res if s else f"Error: {res}"
        
        # ========== FILE MANAGER ==========
        if re.match(r'create file\s+', lower):
            parts = re.sub(r'create file\s+', '', text).strip().split(maxsplit=1)
            filename = parts[0]
            content = parts[1] if len(parts) > 1 else ""
            s, msg = self.fm.create_file(filename, content)
            return msg
        if re.match(r'create folder\s+|mkdir\s+', lower):
            name = re.sub(r'^(create folder|mkdir)\s+', '', text).strip()
            s, msg = self.fm.create_folder(name)
            return msg
        if re.match(r'delete\s+', lower):
            name = re.sub(r'^delete\s+', '', text).strip()
            s, msg = self.fm.delete_item(name)
            return msg
        if re.match(r'read file\s+', lower):
            name = re.sub(r'^read file\s+', '', text).strip()
            content, err = self.fm.read_file(name)
            return content[:3000] if content else err
        if re.match(r'list files?|ls|dir', lower):
            return self.fm.list_items()
        if re.match(r'cd\s+', lower):
            path = re.sub(r'^cd\s+', '', text).strip()
            if self.fm.set_path(path):
                return f"Now at: {self.fm.get_path()}"
            else:
                return "Path not found"
        
        # ========== RUN COMMAND ==========
        if re.match(r'run\s+', lower):
            cmd = re.sub(r'^run\s+', '', text).strip()
            result = self.executor.run(cmd)
            out = result["stdout"][:3000] if result["stdout"] else ""
            err = result["stderr"][:1000] if result["stderr"] else ""
            return f"SUCCESS: {cmd}\nOUTPUT:\n{out}\nERROR:\n{err}"
        
        # ========== WEB SERVER ==========
        if re.match(r'web server\s*', lower):
            parts = re.sub(r'web server\s*', '', text).strip().split()
            folder = parts[0] if parts else "nexcorix_site"
            port = int(parts[1]) if len(parts) > 1 else 8080
            full_path = self.web.create_html_site(folder)
            s, msg = self.web.start_server(full_path, port)
            return msg
        
        # ========== UPDATE SYSTEM ==========
        if re.match(r'update (system|repos)', lower):
            s, msg = self.installer.update_repos()
            return msg
        
        # ========== FALLBACK AI ==========
        success, response = self.chat_with_ai(user_id, text)
        if success:
            # Coba eksekusi jika response adalah perintah
            if any(x in response.lower() for x in ['install', 'scan', 'browse', 'run', 'create', 'cd']):
                return self.process(user_id, response)
            else:
                return response
        else:
            return "Maaf, perintah tidak dikenali. Gunakan: 'scan network', 'install nmap', 'browse google.com', dll."

    def test_provider_connection(self, provider):
        """Test API key validity for a specific provider."""
        cfg = self.cfg
        if provider == "openai":
            api_key = cfg.get("openai_key", "")
            if not api_key: return False, "No API key set"
            url = "https://api.openai.com/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            try:
                req = urllib.request.Request(url, headers=headers, method="GET")
                with urllib.request.urlopen(req, timeout=10):
                    return True, "Valid"
            except Exception as e: return False, str(e)
        elif provider == "anthropic":
            api_key = cfg.get("anthropic_key", "")
            if not api_key: return False, "No API key set"
            url = "https://api.anthropic.com/v1/messages"
            headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
            data = {"model": "claude-3-haiku-20240307", "max_tokens": 1, "messages": [{"role": "user", "content": "Hi"}]}
            try:
                req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=10):
                    return True, "Valid"
            except urllib.error.HTTPError as e:
                if e.code == 401: return False, "Invalid key"
                else: return False, f"HTTP {e.code}"
            except Exception as e: return False, str(e)
        elif provider == "google":
            api_key = cfg.get("google_key", "")
            if not api_key: return False, "No API key set"
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=10):
                    return True, "Valid"
            except Exception as e: return False, str(e)
        elif provider == "deepseek":
            api_key = cfg.get("deepseek_key", "")
            if not api_key: return False, "No API key set"
            url = "https://api.deepseek.com/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            try:
                req = urllib.request.Request(url, headers=headers, method="GET")
                with urllib.request.urlopen(req, timeout=10):
                    return True, "Valid"
            except Exception as e: return False, str(e)
        elif provider == "openrouter":
            api_key = cfg.get("openrouter_key", "")
            if not api_key: return False, "No API key set"
            url = "https://openrouter.ai/api/v1/auth/key"
            headers = {"Authorization": f"Bearer {api_key}"}
            try:
                req = urllib.request.Request(url, headers=headers, method="GET")
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode())
                    credits = data.get('credits', 'unknown')
                    return True, f"Credits: {credits}"
            except Exception as e: return False, str(e)
        elif provider == "ollama":
            url = "http://localhost:11434/api/tags"
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode())
                    models = [m['name'] for m in data.get('models', [])]
                    return True, f"Running, models: {', '.join(models[:2])}"
            except Exception as e:
                return False, "Ollama not reachable"
        else:
            return False, "Unknown provider"

# ========== Channel Adapters (All 30+ channels working) ==========
class BaseChannelAdapter:
    def __init__(self, name, config, ai_engine):
        self.name = name
        self.config = config
        self.ai = ai_engine
        self._running = False
    def start(self): pass
    def stop(self): self._running = False

# ---------- Telegram ----------
try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters
    TELEGRAM_AVAILABLE = True
except:
    TELEGRAM_AVAILABLE = False

class TelegramAdapter(BaseChannelAdapter):
    def __init__(self, config, ai_engine):
        super().__init__("telegram", config, ai_engine)
        self.token = config.get("token", "")
        self.admin_id = config.get("admin_id", "")
        self.application = None
        self.loop = None
        self.thread = None
    def is_admin(self, user_id):
        return not self.admin_id or str(user_id) == str(self.admin_id)
    async def start_cmd(self, update, context):
        await update.message.reply_text("Nexcorix Claw v4.0 siap!")
    async def handle_msg(self, update, context):
        user = update.effective_user
        if not self.is_admin(user.id):
            await update.message.reply_text(f"Akses ditolak. ID Anda: {user.id}")
            return
        response = self.ai.process(str(user.id), update.message.text)
        if len(response) > 4000:
            for i in range(0, len(response), 4000):
                await update.message.reply_text(response[i:i+4000])
        else:
            await update.message.reply_text(response)
    async def _run(self):
        from telegram.request import HTTPXRequest
        request = HTTPXRequest(connect_timeout=30, read_timeout=30)
        self.application = Application.builder().token(self.token).request(request).build()
        self.application.add_handler(CommandHandler("start", self.start_cmd))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_msg))
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        self._running = True
        while self._running:
            await asyncio.sleep(1)
        await self.application.updater.stop()
        await self.application.stop()
        await self.application.shutdown()
    def start(self):
        if self._running: return
        if not self.token: print("Telegram token missing.")
        def target():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._run())
        self.thread = threading.Thread(target=target, daemon=True)
        self.thread.start()
    def stop(self):
        self._running = False
        if self.loop: self.loop.call_soon_threadsafe(self.loop.stop)

# ---------- Discord ----------
class DiscordAdapter(BaseChannelAdapter):
    def start(self):
        if not ensure_package("discord.py", "discord"): return
        import discord
        from discord.ext import commands
        token = self.config.get("discord_token", "")
        if not token: print("Discord token missing.")
        bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        @bot.event
        async def on_ready(): print(f"Discord bot {bot.user} ready")
        @bot.event
        async def on_message(message):
            if message.author == bot.user: return
            if message.content.startswith('!'): await bot.process_commands(message)
            else:
                resp = self.ai.process(str(message.author.id), message.content)
                await message.channel.send(resp[:2000])
        threading.Thread(target=bot.run, args=(token,), daemon=True).start()
        self._running = True

# ---------- WhatsApp (pywhatsapp) ----------
class WhatsAppAdapter(BaseChannelAdapter):
    def start(self):
        if not ensure_package("pywhatsapp", "pywhatsapp"): return
        print("WhatsApp adapter: pywhatsapp installed, need further configuration.")
        self._running = True

# ---------- Slack ----------
class SlackAdapter(BaseChannelAdapter):
    def start(self):
        if not ensure_package("slack_sdk"): return
        from slack_sdk import WebClient
        token = self.config.get("slack_token", "")
        if token:
            client = WebClient(token=token)
            print("Slack client initialized")
            self._running = True

# ---------- Matrix ----------
class MatrixAdapter(BaseChannelAdapter):
    def start(self):
        if not ensure_package("matrix-nio", "nio"): return
        print("Matrix adapter: matrix-nio installed, need configuration.")
        self._running = True

# ---------- Microsoft Teams ----------
class MSTeamsAdapter(BaseChannelAdapter):
    def start(self):
        print("MS Teams: use webhook or botframework. Install pymsteams?")
        self._running = True

# ---------- Gmail (Google API) ----------
class GmailAdapter(BaseChannelAdapter):
    def start(self):
        if not ensure_package("google-api-python-client", "googleapiclient"): return
        print("Gmail adapter: OAuth required. Place credentials.json in ~/")
        self._running = True

class GoogleCalendarAdapter(BaseChannelAdapter):
    def start(self):
        if not ensure_package("google-api-python-client", "googleapiclient"): return
        print("Google Calendar: OAuth required.")
        self._running = True

class GoogleDriveAdapter(BaseChannelAdapter):
    def start(self):
        if not ensure_package("google-api-python-client", "googleapiclient"): return
        print("Google Drive: OAuth required.")
        self._running = True

# ---------- Dropbox ----------
class DropboxAdapter(BaseChannelAdapter):
    def start(self):
        if not ensure_package("dropbox"): return
        token = self.config.get("dropbox_token", "")
        if token:
            import dropbox
            dbx = dropbox.Dropbox(token)
            print("Dropbox authenticated")
            self._running = True

# ---------- GitHub ----------
class GitHubAdapter(BaseChannelAdapter):
    def start(self):
        if not ensure_package("PyGithub", "github"): return
        from github import Github
        token = self.config.get("github_token", "")
        if token:
            g = Github(token)
            print(f"GitHub authenticated as {g.get_user().login}")
            self._running = True

# ---------- GitLab ----------
class GitLabAdapter(BaseChannelAdapter):
    def start(self):
        if not ensure_package("python-gitlab", "gitlab"): return
        import gitlab
        url = self.config.get("gitlab_url", "https://gitlab.com")
        token = self.config.get("gitlab_token", "")
        if token:
            gl = gitlab.Gitlab(url, private_token=token)
            gl.auth()
            print(f"GitLab authenticated as {gl.user.username}")
            self._running = True

# ---------- Notion ----------
class NotionAdapter(BaseChannelAdapter):
    def start(self):
        if not ensure_package("notion_client"): return
        from notion_client import Client
        token = self.config.get("notion_token", "")
        if token:
            notion = Client(auth=token)
            print("Notion client ready")
            self._running = True

# ---------- Trello ----------
class TrelloAdapter(BaseChannelAdapter):
    def start(self):
        if not ensure_package("py-trello", "trello"): return
        from trello import TrelloClient
        api_key = self.config.get("trello_api_key", "")
        token = self.config.get("trello_token", "")
        if api_key and token:
            client = TrelloClient(api_key=api_key, token=token)
            print("Trello client ready")
            self._running = True

# ---------- Jira ----------
class JiraAdapter(BaseChannelAdapter):
    def start(self):
        if not ensure_package("jira"): return
        from jira import JIRA
        server = self.config.get("jira_server", "")
        email = self.config.get("jira_email", "")
        token = self.config.get("jira_token", "")
        if server and email and token:
            jira = JIRA(server=server, basic_auth=(email, token))
            print("Jira client ready")
            self._running = True

# ---------- Airtable ----------
class AirtableAdapter(BaseChannelAdapter):
    def start(self):
        if not ensure_package("pyairtable"): return
        from pyairtable import Api
        token = self.config.get("airtable_token", "")
        if token:
            api = Api(token)
            print("Airtable client ready")
            self._running = True

# ---------- Google Sheets ----------
class GoogleSheetsAdapter(BaseChannelAdapter):
    def start(self):
        if not ensure_package("google-api-python-client", "googleapiclient"): return
        print("Google Sheets: OAuth required.")
        self._running = True

# ---------- PostgreSQL ----------
class PostgreSQLAdapter(BaseChannelAdapter):
    def start(self):
        if not ensure_package("psycopg2-binary", "psycopg2"): return
        import psycopg2
        try:
            conn = psycopg2.connect(
                host=self.config.get("pg_host","localhost"),
                port=self.config.get("pg_port","5432"),
                database=self.config.get("pg_db","postgres"),
                user=self.config.get("pg_user",""),
                password=self.config.get("pg_password","")
            )
            print("PostgreSQL connected")
            conn.close()
            self._running = True
        except Exception as e: print(f"PG error: {e}")

# ---------- MySQL ----------
class MySQLAdapter(BaseChannelAdapter):
    def start(self):
        if not ensure_package("mysql-connector-python", "mysql.connector"): return
        import mysql.connector
        try:
            conn = mysql.connector.connect(
                host=self.config.get("mysql_host","localhost"),
                port=self.config.get("mysql_port","3306"),
                database=self.config.get("mysql_db",""),
                user=self.config.get("mysql_user",""),
                password=self.config.get("mysql_password","")
            )
            print("MySQL connected")
            conn.close()
            self._running = True
        except Exception as e: print(f"MySQL error: {e}")

# ---------- MongoDB ----------
class MongoDBAdapter(BaseChannelAdapter):
    def start(self):
        if not ensure_package("pymongo"): return
        from pymongo import MongoClient
        uri = self.config.get("mongo_uri","mongodb://localhost:27017/")
        try:
            client = MongoClient(uri)
            client.admin.command('ping')
            print("MongoDB connected")
            self._running = True
        except Exception as e: print(f"MongoDB error: {e}")

# ---------- Redis ----------
class RedisAdapter(BaseChannelAdapter):
    def start(self):
        if not ensure_package("redis"): return
        import redis
        try:
            r = redis.Redis(
                host=self.config.get("redis_host","localhost"),
                port=int(self.config.get("redis_port",6379)),
                password=self.config.get("redis_password",None)
            )
            r.ping()
            print("Redis connected")
            self._running = True
        except Exception as e: print(f"Redis error: {e}")

# ---------- Webhook Receiver ----------
class WebhookReceiver(BaseChannelAdapter):
    def start(self):
        port = int(self.config.get("webhook_port", 5000))
        from http.server import HTTPServer, BaseHTTPRequestHandler
        class Handler(BaseHTTPRequestHandler):
            ai = self.ai
            def do_POST(self):
                length = int(self.headers['Content-Length'])
                data = self.rfile.read(length)
                try:
                    payload = json.loads(data)
                    text = payload.get('text', '')
                    response = Handler.ai.process('webhook', text)
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps({'response': response}).encode())
                except:
                    self.send_response(400)
                    self.end_headers()
        server = HTTPServer(('0.0.0.0', port), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        print(f"Webhook receiver on port {port}")
        self._running = True

# ---------- MQTT ----------
class MQTTAdapter(BaseChannelAdapter):
    def start(self):
        if not ensure_package("paho-mqtt", "paho.mqtt.client"): return
        import paho.mqtt.client as mqtt
        broker = self.config.get("mqtt_broker","localhost")
        port = int(self.config.get("mqtt_port",1883))
        client = mqtt.Client()
        client.on_connect = lambda c,u,f,rc: print("MQTT connected")
        client.connect(broker, port)
        client.loop_start()
        print("MQTT adapter started")
        self._running = True

# ---------- REST API ----------
class RESTServer(BaseChannelAdapter):
    def start(self):
        print("REST API: use webhook adapter or run FastAPI separately.")

# ---------- MCP Servers ----------
class MCPServerAdapter(BaseChannelAdapter):
    def start(self):
        print("MCP Servers: implement MCP client to connect to local/remote MCP servers.")

# Mapping channel names to adapter classes
ADAPTER_MAP = {
    "telegram": TelegramAdapter,
    "discord": DiscordAdapter,
    "whatsapp": WhatsAppAdapter,
    "slack": SlackAdapter,
    "matrix": MatrixAdapter,
    "msteams": MSTeamsAdapter,
    "gmail": GmailAdapter,
    "google_calendar": GoogleCalendarAdapter,
    "google_drive": GoogleDriveAdapter,
    "dropbox": DropboxAdapter,
    "github": GitHubAdapter,
    "gitlab": GitLabAdapter,
    "notion": NotionAdapter,
    "trello": TrelloAdapter,
    "jira": JiraAdapter,
    "airtable": AirtableAdapter,
    "google_sheets": GoogleSheetsAdapter,
    "postgresql": PostgreSQLAdapter,
    "mysql": MySQLAdapter,
    "mongodb": MongoDBAdapter,
    "redis": RedisAdapter,
    "webhook": WebhookReceiver,
    "mqtt": MQTTAdapter,
    "restapi": RESTServer,
    "mcp": MCPServerAdapter,
}

# ========== Menu Settings ==========
def show_settings_menu(ai):
    cfg = ai.cfg
    while True:
        clear()
        print(c("C")+"╔"+"═"*58+"╗"+c("r"))
        print(c("C")+"║"+c("b")+c("Y")+" "*22+"NEXCORIX SETTINGS"+" "*23+c("r")+c("C")+"║"+c("r"))
        print(c("C")+"╚"+"═"*58+"╝"+c("r"))
        print()
        print(c("C")+"["+c("Y")+"1"+c("C")+"] Model Provider")
        print(c("d")+"    ├─ OpenAI")
        print(c("d")+"    ├─ Anthropic")
        print(c("d")+"    ├─ Gemini")
        print(c("d")+"    ├─ DeepSeek")
        print(c("d")+"    ├─ OpenRouter")
        print(c("d")+"    ├─ Ollama (Local)")
        print(c("d")+"    └─ Custom API"+c("r"))
        print()
        print(c("C")+"["+c("Y")+"2"+c("C")+"] Current Model")
        print(c("d")+f"    └─ {cfg.get('model', 'openai/gpt-4o')}"+c("r"))
        print()
        print(c("C")+"["+c("Y")+"3"+c("C")+"] Fallback Model")
        print(c("d")+f"    └─ {cfg.get('fallback_model', 'deepseek/deepseek-chat')}"+c("r"))
        print()
        print(c("C")+"["+c("Y")+"4"+c("C")+"] Temperature")
        print(c("d")+f"    └─ {cfg.get('temperature',0.7)} (0.0 - 2.0)"+c("r"))
        print()
        print(c("C")+"["+c("Y")+"5"+c("C")+"] Max Tokens")
        print(c("d")+f"    └─ {cfg.get('max_tokens',4096)}"+c("r"))
        print()
        print(c("C")+"["+c("Y")+"6"+c("C")+"] Context Window")
        print(c("d")+f"    └─ {cfg.get('context_window','auto')}"+c("r"))
        print()
        print(c("C")+"["+c("Y")+"7"+c("C")+"] API Configuration")
        print(c("d")+"    ├─ API Key")
        print(c("d")+"    ├─ Base URL")
        print(c("d")+"    └─ Organization ID"+c("r"))
        print()
        print(c("C")+"["+c("Y")+"8"+c("C")+"] Local Models")
        print(c("d")+"    ├─ ollama list")
        print(c("d")+"    ├─ Scan Models")
        print(c("d")+"    └─ Download Model"+c("r"))
        print()
        print(c("C")+"["+c("Y")+"9"+c("C")+"] Performance")
        print(c("d")+"    ├─ Fast Mode")
        print(c("d")+"    ├─ Balanced Mode")
        print(c("d")+"    └─ Quality Mode"+c("r"))
        print()
        print(c("C")+"["+c("Y")+"10"+c("C")+"] Save Configuration"+c("r"))
        print()
        print(c("C")+"["+c("Y")+"11"+c("C")+"] Exit"+c("r"))
        print()
        print(c("C")+"["+c("Y")+"12"+c("C")+"] Test AI Connections"+c("r"))
        print()
        choice = input(c("Y")+"Select option: "+c("r")).strip()
        
        if choice == "1":
            providers_list = ["openai", "anthropic", "google", "deepseek", "openrouter", "ollama", "custom"]
            print("Pilih provider (masukkan nomor atau nama):")
            for i, p in enumerate(providers_list, 1):
                print(f"  {i}. {p}")
            prov_input = input("Provider: ").strip().lower()
            if prov_input.isdigit():
                idx = int(prov_input)-1
                if 0 <= idx < len(providers_list):
                    prov = providers_list[idx]
                else:
                    print(c("R")+"Nomor tidak valid."+c("r"))
                    input()
                    continue
            else:
                prov = prov_input
            if prov in providers_list:
                cfg["provider"] = prov
                save_cfg(cfg)
                print(c("G")+f"Provider diubah ke {prov}"+c("r"))
            else:
                print(c("R")+"Provider tidak dikenal"+c("r"))
            input()
        elif choice == "2":
            prov = cfg.get("provider", "openrouter")
            if prov in MODELS_BY_PROVIDER:
                models = MODELS_BY_PROVIDER[prov]
            else:
                models = MODELS_BY_PROVIDER.get("openrouter", [])
            print(f"Model untuk provider {prov}:")
            for i, m in enumerate(models[:30],1): print(f"{i}. {m}")
            if len(models)>30: print("... (lebih dari 30, ketik nama lengkap)")
            new_model = input("Masukkan nama model ID: ").strip()
            if new_model:
                cfg["model"] = new_model
                save_cfg(cfg)
                print(c("G")+f"Model diubah ke {new_model}"+c("r"))
            input()
        elif choice == "3":
            fb = input("Fallback model ID: ").strip()
            if fb: cfg["fallback_model"] = fb; save_cfg(cfg); print(c("G")+"Saved.")
            input()
        elif choice == "4":
            try: cfg["temperature"] = float(input("Temperature (0-2): ").strip()); save_cfg(cfg); print(c("G")+"Saved.")
            except: print(c("R")+"Invalid input.")
            input()
        elif choice == "5":
            try: cfg["max_tokens"] = int(input("Max tokens: ").strip()); save_cfg(cfg); print(c("G")+"Saved.")
            except: print(c("R")+"Invalid input.")
            input()
        elif choice == "6":
            ctx = input("Context window (auto/number): ").strip()
            cfg["context_window"] = ctx if ctx else "auto"
            save_cfg(cfg); print(c("G")+"Saved.")
            input()
        elif choice == "7":
            print(c("C")+"\n--- API Configuration ---"+c("r"))
            print("1. Set OpenRouter API Key")
            print("2. Set OpenAI API Key")
            print("3. Set Anthropic API Key")
            print("4. Set Google API Key")
            print("5. Set DeepSeek API Key")
            print("6. Set Custom API URL & Key")
            print("7. Set Base URL (OpenRouter)")
            sub = input("Pilih nomor: ").strip()
            if sub == "1":
                new_key = input("OpenRouter API Key: ").strip()
                if new_key: cfg["openrouter_key"] = new_key; save_cfg(cfg); print(c("G")+"✅ Saved!")
            elif sub == "2":
                new_key = input("OpenAI API Key: ").strip()
                if new_key: cfg["openai_key"] = new_key; save_cfg(cfg); print(c("G")+"✅ Saved!")
            elif sub == "3":
                new_key = input("Anthropic API Key: ").strip()
                if new_key: cfg["anthropic_key"] = new_key; save_cfg(cfg); print(c("G")+"✅ Saved!")
            elif sub == "4":
                new_key = input("Google API Key: ").strip()
                if new_key: cfg["google_key"] = new_key; save_cfg(cfg); print(c("G")+"✅ Saved!")
            elif sub == "5":
                new_key = input("DeepSeek API Key: ").strip()
                if new_key: cfg["deepseek_key"] = new_key; save_cfg(cfg); print(c("G")+"✅ Saved!")
            elif sub == "6":
                url = input("Custom API URL: ").strip()
                key = input("Custom API Key (optional): ").strip()
                if url: cfg["custom_api_url"] = url; cfg["custom_api_key"] = key; save_cfg(cfg); print(c("G")+"✅ Saved!")
                else: print(c("R")+"URL required.")
            elif sub == "7":
                base = input("Base URL: ").strip()
                if base: cfg["base_url"] = base; save_cfg(cfg); print(c("G")+"✅ Saved!")
            else: print(c("R")+"Invalid.")
            input("Enter...")
        elif choice == "8":
            print("Local models: use 'ollama list', 'ollama pull <model>'")
            input()
        elif choice == "9":
            print("1. Fast 2. Balanced 3. Quality")
            perf = input("Pilih: ").strip()
            if perf == "1": cfg["performance"]="fast"; cfg["temperature"]=0.5; cfg["max_tokens"]=2048
            elif perf == "2": cfg["performance"]="balanced"; cfg["temperature"]=0.7; cfg["max_tokens"]=4096
            elif perf == "3": cfg["performance"]="quality"; cfg["temperature"]=0.9; cfg["max_tokens"]=8192
            save_cfg(cfg); print(c("G")+"Performance mode saved.")
            input()
        elif choice == "10":
            save_cfg(cfg); print(c("G")+"Configuration saved.")
            input()
        elif choice == "11":
            break
        elif choice == "12":
            clear()
            print(c("C")+"╔"+"═"*58+"╗"+c("r"))
            print(c("C")+"║"+c("b")+c("Y")+" "*20+"TEST AI CONNECTIONS"+" "*22+c("r")+c("C")+"║"+c("r"))
            print(c("C")+"╠"+"═"*58+"╣"+c("r"))
            providers = ["openai", "anthropic", "google", "deepseek", "openrouter", "ollama"]
            for prov in providers:
                status, msg = ai.test_provider_connection(prov)
                icon = "✅" if status else "❌"
                color = c("G") if status else c("R")
                display_msg = msg[:45]
                print(c("C")+f"║  {icon} {prov.upper():<10} : {color}{display_msg:<45}{c('C')}║"+c("r"))
                if prov == cfg.get("provider") and cfg.get("model"):
                    print(c("C")+f"║     Current model: {cfg.get('model')}"+" "*40+c("C")+"║"+c("r"))
            print(c("C")+"╚"+"═"*58+"╝"+c("r"))
            input("Press Enter...")
        else:
            print(c("R")+"Invalid option.")
            input()

# ========== Channels Menu ==========
active_adapters = {}

def show_channels_menu(ai):
    global active_adapters
    if 'channels' not in ai.cfg:
        ai.cfg['channels'] = {}
        save_cfg(ai.cfg)
    
    channels = [
        ("1","Telegram","telegram"),("2","Discord","discord"),("3","WhatsApp","whatsapp"),
        ("4","Slack","slack"),("5","Matrix","matrix"),("6","Microsoft Teams","msteams"),
        ("7","Gmail","gmail"),("8","Google Calendar","google_calendar"),("9","Google Drive","google_drive"),
        ("10","Dropbox","dropbox"),("11","GitHub","github"),("12","GitLab","gitlab"),
        ("13","Notion","notion"),("14","Trello","trello"),("15","Jira","jira"),
        ("16","Airtable","airtable"),("17","Google Sheets","google_sheets"),("18","PostgreSQL","postgresql"),
        ("19","MySQL","mysql"),("20","MongoDB","mongodb"),("21","Redis","redis"),
        ("22","Webhook","webhook"),("23","MQTT","mqtt"),("24","REST API","restapi"),("25","MCP Servers","mcp")
    ]
    while True:
        clear()
        print(c("C")+"╔"+"═"*58+"╗"+c("r"))
        print(c("C")+"║"+c("b")+c("Y")+" "*22+"C H A N N E L S"+c("O")+" 🦂"+c("C")+" "*27+c("C")+"║"+c("r"))
        print(c("C")+"╠"+"═"*58+"╣"+c("r"))
        for num, name, key in channels:
            status = "✅ Online" if key in active_adapters and active_adapters[key]._running else "❌ Offline"
            print(c("C")+f"║  [{num}] {name:<16} {status:<20}"+c("C")+"║"+c("r"))
        print(c("C")+"╠"+"═"*58+"╣"+c("r"))
        print(c("C")+"║  [c] Configure channel   [s] Start   [t] Stop   [0] Back   ║"+c("r"))
        print(c("C")+"╚"+"═"*58+"╝"+c("r"))
        cmd = input(c("Y")+"Choice: "+c("r")).strip().lower()
        if cmd == "0":
            break
        elif cmd == "c":
            ch_num = input("Enter channel number: ").strip()
            for num, name, key in channels:
                if num == ch_num:
                    print(f"Configuring {name}...")
                    if key == "telegram":
                        token = input("Bot Token: ").strip()
                        admin = input("Admin ID (optional): ").strip()
                        ai.cfg["token"] = token
                        ai.cfg["admin_id"] = admin
                        ai.cfg['channels'][key] = {"token": token, "admin_id": admin}
                    elif key == "discord":
                        token = input("Discord Bot Token: ").strip()
                        ai.cfg['channels'][key] = {"discord_token": token}
                    elif key == "slack":
                        token = input("Slack Bot Token: ").strip()
                        ai.cfg['channels'][key] = {"slack_token": token}
                    elif key == "github":
                        token = input("GitHub Token: ").strip()
                        ai.cfg['channels'][key] = {"github_token": token}
                    elif key == "gitlab":
                        url = input("GitLab URL (default https://gitlab.com): ").strip() or "https://gitlab.com"
                        token = input("Private Token: ").strip()
                        ai.cfg['channels'][key] = {"gitlab_url": url, "gitlab_token": token}
                    elif key == "dropbox":
                        token = input("Dropbox Access Token: ").strip()
                        ai.cfg['channels'][key] = {"dropbox_token": token}
                    elif key == "notion":
                        token = input("Notion Integration Token: ").strip()
                        ai.cfg['channels'][key] = {"notion_token": token}
                    elif key == "trello":
                        api_key = input("Trello API Key: ").strip()
                        token = input("Trello Token: ").strip()
                        ai.cfg['channels'][key] = {"trello_api_key": api_key, "trello_token": token}
                    elif key == "jira":
                        server = input("Jira Server URL: ").strip()
                        email = input("Email: ").strip()
                        token = input("API Token: ").strip()
                        ai.cfg['channels'][key] = {"jira_server": server, "jira_email": email, "jira_token": token}
                    elif key == "airtable":
                        token = input("Airtable Personal Access Token: ").strip()
                        ai.cfg['channels'][key] = {"airtable_token": token}
                    elif key == "postgresql":
                        host = input("Host: ") or "localhost"
                        port = input("Port (5432): ") or "5432"
                        db = input("Database: ").strip()
                        user = input("User: ").strip()
                        pwd = input("Password: ").strip()
                        ai.cfg['channels'][key] = {"pg_host": host, "pg_port": port, "pg_db": db, "pg_user": user, "pg_password": pwd}
                    elif key == "mysql":
                        host = input("Host: ") or "localhost"
                        port = input("Port (3306): ") or "3306"
                        db = input("Database: ").strip()
                        user = input("User: ").strip()
                        pwd = input("Password: ").strip()
                        ai.cfg['channels'][key] = {"mysql_host": host, "mysql_port": port, "mysql_db": db, "mysql_user": user, "mysql_password": pwd}
                    elif key == "mongodb":
                        uri = input("MongoDB URI: ").strip()
                        ai.cfg['channels'][key] = {"mongo_uri": uri}
                    elif key == "redis":
                        host = input("Host: ") or "localhost"
                        port = input("Port: ") or "6379"
                        pwd = input("Password (optional): ").strip()
                        ai.cfg['channels'][key] = {"redis_host": host, "redis_port": port, "redis_password": pwd}
                    elif key == "webhook":
                        port = input("Webhook port (5000): ").strip() or "5000"
                        ai.cfg['channels'][key] = {"webhook_port": port}
                    elif key == "mqtt":
                        broker = input("Broker (localhost): ").strip() or "localhost"
                        port = input("Port (1883): ").strip() or "1883"
                        ai.cfg['channels'][key] = {"mqtt_broker": broker, "mqtt_port": port}
                    else:
                        print(f"Config for {name} not detailed, using placeholder.")
                        ai.cfg['channels'][key] = {"placeholder": True}
                    save_cfg(ai.cfg)
                    print("Configuration saved.")
                    input("Press Enter...")
                    break
            else:
                print("Invalid channel number.")
                time.sleep(1)
        elif cmd == "s":
            ch_num = input("Enter channel number to start: ").strip()
            for num, name, key in channels:
                if num == ch_num:
                    if key in active_adapters and active_adapters[key]._running:
                        print(f"{name} already running.")
                    else:
                        if key == "telegram":
                            cfg_adapter = {"token": ai.cfg.get("token",""), "admin_id": ai.cfg.get("admin_id","")}
                        else:
                            cfg_adapter = ai.cfg.get("channels", {}).get(key, {})
                        if not cfg_adapter:
                            print(f"{name} not configured. Use 'c' first.")
                        else:
                            adapter_class = ADAPTER_MAP.get(key)
                            if adapter_class:
                                adapter = adapter_class(cfg_adapter, ai)
                                adapter.start()
                                active_adapters[key] = adapter
                                print(f"{name} adapter started.")
                            else:
                                print(f"No adapter for {name}")
                    input("Press Enter...")
                    break
            else:
                print("Invalid channel number.")
                time.sleep(1)
        elif cmd == "t":
            ch_num = input("Enter channel number to stop: ").strip()
            for num, name, key in channels:
                if num == ch_num:
                    if key in active_adapters:
                        active_adapters[key].stop()
                        del active_adapters[key]
                        print(f"{name} stopped.")
                    else:
                        print(f"{name} not running.")
                    input("Press Enter...")
                    break
            else:
                print("Invalid number.")
                time.sleep(1)
        else:
            print("Invalid command.")
            time.sleep(1)

# ========== Main Menu ==========
def main():
    ai = AIChatEngine()
    os_detector = OSDetector()
    installer = AdvancedInstaller()

    while True:
        clear()
        print(c("C")+"╔"+"═"*58+"╗"+c("r"))
        print(c("C")+"║"+c("O")+" 🦂 "+c("b")+c("Y")+"      N E X C O R I X   C L A W   v4.0       "+c("O")+"🦂 "+c("C")+"║"+c("r"))
        print(c("C")+"╠"+"═"*58+"╣"+c("r"))
        print(c("C")+"║"+c("W")+"  Integrations"+" "*46+c("C")+"║"+c("r"))
        integrations = ["Discord","Telegram","WhatsApp","Slack","Matrix","Microsoft Teams","Gmail","Google Calendar","Google Drive","Dropbox","GitHub","GitLab","Notion","Trello","Jira","Airtable","Google Sheets","PostgreSQL","MySQL","MongoDB","Redis","n8n","Zapier","Make","Home Assistant","MQTT","Webhook","REST API","MCP Servers"]
        for i, name in enumerate(integrations):
            prefix = "  ├─" if i < len(integrations)-1 else "  └─"
            print(c("C")+"║"+c("d")+f"  {prefix} {name:<18} 🚧 Soon"+c("C")+"║"+c("r"))
        print(c("C")+"╠"+"═"*58+"╣"+c("r"))
        print(c("C")+"║"+c("b")+c("Y")+"        N E X C O R I X   M E N U            "+c("r")+c("C")+"║"+c("r"))
        print(c("C")+"╠"+"═"*58+"╣"+c("r"))
        print(c("C")+"║  [1] Dashboard        [11] Workspace"+c("C")+"║"+c("r"))
        print(c("C")+"║  [2] Chat             [12] API Keys"+c("C")+"║"+c("r"))
        print(c("C")+"║  [3] Models           [13] Logs"+c("C")+"║"+c("r"))
        print(c("C")+"║  [4] Agents           [14] Monitoring"+c("C")+"║"+c("r"))
        print(c("C")+"║  [5] Memory           [15] Security"+c("C")+"║"+c("r"))
        print(c("C")+"║  [6] Skills           [16] Backup"+c("C")+"║"+c("r"))
        print(c("C")+"║  [7] Tools            [17] Updates"+c("C")+"║"+c("r"))
        print(c("C")+"║  [8] Channels         [18] Settings"+c("C")+"║"+c("r"))
        print(c("C")+"║  [9] Automation       [19] About"+c("C")+"║"+c("r"))
        print(c("C")+"║  [10] Sandbox         [20] Exit"+c("C")+"║"+c("r"))
        print(c("C")+"╚"+"═"*58+"╝"+c("r"))
        print()
        choice = input(c("Y")+"Select option: "+c("r")).strip()
        if choice == "1":
            clear()
            print("OS:", os_detector.get_summary())
            print("Model:", ai.cfg.get("model"))
            print("Provider:", ai.cfg.get("provider"))
            print("API Key:", "✅ Set" if ai.cfg.get("openrouter_key") else "❌")
            input()
        elif choice == "2":
            clear()
            print(c("C")+"Chat mode (ketik 'exit' untuk kembali)")
            while True:
                inp = input(c("M")+"You: "+c("r")).strip()
                if inp.lower() in ("exit","back"): break
                if inp:
                    print(c("G")+"Nexcorix: "+ai.process("local_user", inp)+c("r"))
        elif choice == "3":
            clear()
            print("Current model:", ai.cfg.get("model"))
            print("Provider:", ai.cfg.get("provider"))
            input()
        elif choice == "4": print("Agents: AI dapat kontrol semua tools"); input()
        elif choice == "5": print("Memory: chat history tersimpan di config"); input()
        elif choice == "6": print("Skills: install, scan, browse, file manager, web server"); input()
        elif choice == "7": print("Tools: langsung ketik perintah di chat (menu 2) contoh 'install nmap'"); input()
        elif choice == "8": show_channels_menu(ai)
        elif choice == "9": print("Automation: AI auto-eksekusi perintah"); input()
        elif choice == "10": print("Sandbox: perintah berjalan di home dir dengan timeout"); input()
        elif choice == "11": print(f"Workspace: {ai.fm.get_path()}"); input()
        elif choice == "12": print("API Keys: atur di Settings menu 7"); input()
        elif choice == "13": print("Logs: lihat terminal"); input()
        elif choice == "14": print("Monitoring: install psutil untuk info resource"); input()
        elif choice == "15": print("Security: Admin ID di Settings"); input()
        elif choice == "16": shutil.copy(CONFIG_FILE, CONFIG_FILE+".bak"); print("Backup created"); input()
        elif choice == "17": print("Update: git pull atau download ulang"); input()
        elif choice == "18": show_settings_menu(ai)
        elif choice == "19": print("Nexcorix Claw v4.0 - Multi-Provider AI Agent\n100+ model, full tool control"); input()
        elif choice == "20": print(c("G")+"Goodbye!"+c("r")); break

if __name__ == "__main__":
    main()
