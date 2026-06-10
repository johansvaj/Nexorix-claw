#!/usr/bin/env python3
"""
Nexcorix Claw v4.0 - Ultimate AI Agent
Fitur: AI ramah, eksekusi langsung, notifikasi proses, 100+ model, multi-channel, multi-OS.
"""

import os, sys, json, time, platform, socket, re, shutil, threading, asyncio, subprocess
import urllib.request, urllib.error, urllib.parse
from pathlib import Path
from html.parser import HTMLParser

# ========== Warna ==========
C = {
    "r":"\033[0m","b":"\033[1m","d":"\033[2m","R":"\033[91m","G":"\033[92m","Y":"\033[93m",
    "B":"\033[94m","M":"\033[95m","C":"\033[96m","W":"\033[97m","O":"\033[38;5;208m",
    "P":"\033[38;5;141m","T":"\033[38;5;37m","L":"\033[38;5;11m",
}
def c(name): return C.get(name, "")
def clear(): os.system("clear" if os.name != "nt" else "cls")

CONFIG_FILE = os.path.expanduser("~/.nexcorix_config.json")
def load_cfg():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f: return json.load(f)
        except: pass
    return {
        "provider": "openrouter", "model": "openai/gpt-4o", "fallback_model": "deepseek-chat",
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
        info["is_proot"] = os.path.exists("/.proot") or "proot" in os.environ.get("PROOT_LOADER", "")
        info["package_managers"] = self._detect_package_manager()
        if info["is_termux"] and "pkg" not in info["package_managers"]:
            info["package_managers"].append("pkg")
        info["has_sudo"] = os.system("which sudo >/dev/null 2>&1") == 0
        return info
    def _detect_package_manager(self):
        managers = []
        cmds = {"apt":"apt","apt-get":"apt-get","yum":"yum","dnf":"dnf","pacman":"pacman","zypper":"zypper","apk":"apk","brew":"brew","pkg":"pkg","choco":"choco","winget":"winget","pip":"pip","pip3":"pip3","npm":"npm","gem":"gem"}
        for cmd, name in cmds.items():
            if os.system(f"which {cmd} >/dev/null 2>&1") == 0:
                managers.append(name)
        return managers
    def get_summary(self):
        parts = [self.info["distro"]]
        if self.info["is_wsl"]: parts.append("(WSL)")
        if self.info["is_termux"]: parts.append("(Termux)")
        if self.info["is_docker"]: parts.append("(Docker)")
        if self.info["is_proot"]: parts.append("(Proot)")
        return " ".join(parts)
    def get_ai_context(self):
        i = self.info
        pm = ", ".join(i["package_managers"])
        return f"OS: {self.get_summary()} | Shell: {i['shell']} | Arch: {i['machine']} | PM: {pm} | Sudo: {i['has_sudo']}"

# ========== System Executor ==========
class SystemExecutor:
    def __init__(self): self.os_detector = OSDetector()
    def run(self, command, timeout=300):
        try:
            if os.name == "nt":
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=os.path.expanduser("~"))
            else:
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, executable="/bin/bash" if not self.os_detector.info["is_termux"] else None, cwd=os.path.expanduser("~"))
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
            "pip": "pip install {package}", "pip3": "pip3 install {package}",
            "npm": "npm install -g {package}", "gem": "gem install {package}",
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
        priority = ["pkg", "apt", "apt-get", "dnf", "yum", "pacman", "zypper", "apk", "brew", "choco", "winget", "pip", "pip3"]
        for pm in priority:
            if pm in managers: return pm
        return managers[0] if managers else None
    def resolve_package(self, tool_name): return self.tool_aliases.get(tool_name.lower(), tool_name)
    def _has_sudo(self): return self.os_detector.info.get("has_sudo", False)
    def install(self, package, pm=None):
        if not pm: pm = self.get_primary_pm()
        if not pm or pm=="unknown": return False, "No package manager!"
        resolved = self.resolve_package(package)
        if package.lower() in self.github_tools: return self.install_from_github(package.lower())
        if pm in self.pm_commands:
            cmd = self.pm_commands[pm].format(package=resolved)
            if pm in ["apt","apt-get","dnf","yum","pacman","zypper","apk"] and self._has_sudo():
                cmd = "sudo " + cmd
            if self.os_detector.info.get("is_termux", False):
                cmd = cmd.replace("sudo ", "")
            result = self.executor.run(cmd, timeout=600)
            if result["success"]: return True, f"OK {package} via {pm}\n{result['stdout'][:1500]}"
            else:
                if resolved != package:
                    cmd2 = self.pm_commands[pm].format(package=package)
                    if pm in ["apt","apt-get","dnf","yum","pacman","zypper","apk"] and self._has_sudo():
                        cmd2 = "sudo " + cmd2
                    if self.os_detector.info.get("is_termux", False):
                        cmd2 = cmd2.replace("sudo ", "")
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
            cmd = update_cmds[pm]
            if self.os_detector.info.get("is_termux", False): cmd = cmd.replace("sudo ", "")
            result = self.executor.run(cmd, timeout=300)
            if result["success"]: return True, f"Updated\n{result['stdout'][:1500]}"
            else: return False, f"Failed\n{result['stderr'][:1500]}"
        return False, "Cannot update"

# ========== File Manager ==========
class FileManager:
    def __init__(self, base_path=None): self.current_path = os.path.expanduser(base_path or "~")
    def set_path(self, path):
        expanded = os.path.expanduser(path)
        if os.path.exists(expanded) and os.path.isdir(expanded):
            self.current_path = os.path.abspath(expanded); return True
        return False
    def create_file(self, filename, content=""):
        filepath = os.path.join(self.current_path, filename)
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        try:
            with open(filepath, 'w') as f: f.write(content)
            return True, f"✅ File '{filename}' created at {filepath}"
        except Exception as e: return False, f"❌ Error: {e}"
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
        self.os_detector = OSDetector()
    def scan_network(self, target="192.168.1.0/24"):
        if '/' in target:
            base = target.split('/')[0]
        else:
            base = target
        if '.' in base:
            base_ip = '.'.join(base.split('.')[:3])
        else:
            base_ip = "192.168.1"
        has_nmap = os.system("which nmap >/dev/null 2>&1") == 0
        if has_nmap:
            is_termux = self.os_detector.info.get("is_termux", False)
            is_proot = self.os_detector.info.get("is_proot", False)
            if is_termux or is_proot:
                cmd = f"nmap -sn {target} 2>&1"
            else:
                cmd = f"sudo nmap -sn {target}" if self.os_detector.info.get("has_sudo", False) else f"nmap -sn {target}"
            result = self.executor.run(cmd, timeout=60)
            if result["success"] and result["stdout"].strip():
                return f"🔍 Scan result for {target} (nmap):\n{result['stdout']}"
            if "Permission denied" in result["stderr"] or "if_indextoname" in result["stderr"]:
                pass
            else:
                return f"❌ Network scan failed (nmap).\nError: {result['stderr']}"
        ping_cmd = f"for i in {{1..254}}; do ping -c 1 -W 1 {base_ip}.$i 2>/dev/null | grep '64 bytes' && echo '✅ Host {base_ip}.$i is up'; done"
        result2 = self.executor.run(ping_cmd, timeout=120)
        if result2["success"] and result2["stdout"].strip():
            return f"🔍 Ping sweep result for {base_ip}.0/24 (no root required):\n{result2['stdout']}"
        else:
            return f"❌ Network scan failed. Try running with 'su -' or install nmap.\nPing sweep also failed: {result2['stderr']}"
    def scan_ports(self, target, ports="1-1000"):
        has_nmap = os.system("which nmap >/dev/null 2>&1") == 0
        if not has_nmap: return "❌ nmap not installed."
        is_termux = self.os_detector.info.get("is_termux", False)
        if is_termux:
            cmd = f"nmap -p {ports} {target}"
        else:
            cmd = f"sudo nmap -p {ports} {target}" if self.os_detector.info.get("has_sudo", False) else f"nmap -p {ports} {target}"
        result = self.executor.run(cmd, timeout=120)
        return result["stdout"] if result["success"] else f"Port scan failed:\n{result['stderr']}"
    def wifi_scan(self):
        is_termux = self.os_detector.info.get("is_termux", False)
        if is_termux:
            result = self.executor.run("termux-wifi-scaninfo", timeout=30)
            return result["stdout"] if result["success"] else "WiFi scan failed. Install termux-api and grant location permission."
        else:
            result = self.executor.run("nmcli dev wifi list 2>/dev/null", timeout=30)
            if result["success"] and result["stdout"].strip(): return result["stdout"]
            cmd = "sudo iwlist wlan0 scan 2>/dev/null | grep -E 'ESSID|Signal'" if self.os_detector.info.get("has_sudo", False) else "iwlist wlan0 scan 2>/dev/null | grep -E 'ESSID|Signal'"
            result2 = self.executor.run(cmd, timeout=30)
            return result2["stdout"] if result2["success"] and result2["stdout"].strip() else "WiFi scan not available."

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
    "openai": [
        "openai/gpt-4o", "openai/gpt-4o-mini", "openai/gpt-4-turbo", "openai/gpt-4", "openai/gpt-3.5-turbo",
        "openai/o1-preview", "openai/o1-mini", "openai/o3-mini"
    ],
    "anthropic": [
        "anthropic/claude-3.5-sonnet", "anthropic/claude-3-opus", "anthropic/claude-3-sonnet", "anthropic/claude-3-haiku"
    ],
    "google": [
        "google/gemini-1.5-pro", "google/gemini-1.5-flash", "google/gemini-1.0-pro", "google/gemma-2-9b-it", "google/gemma-2-27b-it"
    ],
    "deepseek": [
        "deepseek/deepseek-chat", "deepseek/deepseek-coder"
    ],
    "meta": [
        "meta-llama/llama-3.1-405b-instruct", "meta-llama/llama-3.1-70b-instruct", "meta-llama/llama-3.1-8b-instruct",
        "meta-llama/llama-3-70b-instruct", "meta-llama/llama-3-8b-instruct"
    ],
    "mistral": [
        "mistralai/mistral-large", "mistralai/mistral-medium", "mistralai/mixtral-8x7b-instruct", "mistralai/mistral-7b-instruct",
        "mistralai/codestral-22b-instruct", "mistralai/mathstral-7b-instruct"
    ],
    "qwen": [
        "qwen/qwen-2.5-72b-instruct", "qwen/qwen-2.5-32b-instruct", "qwen/qwen-2.5-14b-instruct", "qwen/qwen-2-7b-instruct"
    ],
    "xai": [
        "x-ai/grok-2", "x-ai/grok-1", "x-ai/grok-beta"
    ],
    "cohere": [
        "cohere/command-r-plus", "cohere/command-r"
    ],
    "ai21": [
        "ai21/jamba-1.5"
    ],
    "databricks": [
        "databricks/dbrx-instruct"
    ],
    "upstage": [
        "upstage/solar-10.7b-instruct"
    ],
    "nvidia": [
        "nvidia/nemotron-4-340b-instruct"
    ],
    "perplexity": [
        "perplexity/pplx-7b-online"
    ],
    "moonshot": [
        "moonshot/kimi-v1"
    ],
    "openrouter": [
        "openai/gpt-4o", "openai/gpt-4o-mini", "openai/gpt-4-turbo", "openai/gpt-4", "openai/gpt-3.5-turbo",
        "anthropic/claude-3.5-sonnet", "anthropic/claude-3-opus", "anthropic/claude-3-sonnet", "anthropic/claude-3-haiku",
        "google/gemini-1.5-pro", "google/gemini-1.5-flash", "google/gemini-1.0-pro",
        "deepseek/deepseek-chat", "deepseek/deepseek-coder",
        "meta-llama/llama-3.1-70b-instruct", "meta-llama/llama-3.1-8b-instruct",
        "mistralai/mistral-large", "mistralai/mixtral-8x7b-instruct",
        "qwen/qwen-2.5-72b-instruct",
        "x-ai/grok-2",
        "cohere/command-r-plus",
        "ai21/jamba-1.5",
        "databricks/dbrx-instruct",
        "upstage/solar-10.7b-instruct",
        "nvidia/nemotron-4-340b-instruct",
        "perplexity/pplx-7b-online",
        "moonshot/kimi-v1"
    ]
}
total_models = sum(len(models) for models in MODELS_BY_PROVIDER.values())
print(f"[*] Loaded {total_models} AI models from providers.")

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
            model = self.cfg.get("model", "gemini-1.5-pro")
            return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}", key
        elif provider == "deepseek":
            return "https://api.deepseek.com/v1/chat/completions", self.cfg.get("deepseek_key", "")
        elif provider == "ollama":
            return f"{self.cfg.get('ollama_url', 'http://localhost:11434')}/api/generate", "dummy"
        elif provider == "custom":
            return self.cfg.get("custom_api_url", ""), self.cfg.get("custom_api_key", "")
        else:
            return self.cfg.get("base_url", "https://openrouter.ai/api/v1") + "/chat/completions", self.cfg.get("openrouter_key", "")

    def test_connection(self):
        provider = self.cfg.get("provider", "openrouter")
        if provider == "ollama":
            return True, "Ollama (local) - ready"
        api_key = self.cfg.get(f"{provider}_key", "")
        if not api_key:
            return False, f"No API key for {provider}. Set in Settings (18) → 7."
        model = self.cfg.get("model")
        print(c("d") + f"Testing {provider} with model {model}..." + c("r"))
        success, response = self.chat_with_ai("test", "Hello, are you working?")
        if success:
            return True, "AI is working!"
        else:
            return False, f"Failed: {response}"

    def chat_with_ai(self, user_id, message, system_prompt=None):
        api_url, api_key = self.get_api_url_and_key()
        provider = self.cfg.get("provider", "openrouter")
        if provider != "ollama" and not api_key:
            return None, "NO_API_KEY"
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        if not system_prompt:
            system_prompt = (
                "Halo! Aku Nexcorix Claw, asisten AI-mu yang ramah dan energik! 🦂\n"
                "Aku langsung menjalankan perintahmu (scan, install, run, dll) tanpa instruksi.\n"
                "Jika kamu minta penjelasan, aku akan jelaskan dengan hangat.\n"
                f"Sistem info: {self.os_detector.get_ai_context()}"
            )
        messages = [{"role": "system", "content": system_prompt}]
        for msg in self.conversations[user_id][-20:]:
            messages.append(msg)
        messages.append({"role": "user", "content": message})

        model = self.cfg.get("model", "openai/gpt-4o")
        headers = {"Content-Type": "application/json"}
        data = None
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
        else:  # openrouter
            headers["Authorization"] = f"Bearer {api_key}"
            data = {"model": model, "messages": messages, "temperature": self.cfg.get("temperature",0.7), "max_tokens": self.cfg.get("max_tokens",4096)}

        try:
            req = urllib.request.Request(api_url, data=json.dumps(data).encode(), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode())
                if provider == "openai" or provider == "deepseek" or provider == "openrouter" or provider == "custom":
                    ai_message = result["choices"][0]["message"]["content"]
                elif provider == "anthropic":
                    ai_message = result["content"][0]["text"]
                elif provider == "google":
                    ai_message = result["candidates"][0]["content"]["parts"][0]["text"]
                elif provider == "ollama":
                    ai_message = result["response"]
                else:
                    ai_message = result["choices"][0]["message"]["content"]
                self.conversations[user_id].append({"role": "user", "content": message})
                self.conversations[user_id].append({"role": "assistant", "content": ai_message})
                cfg = load_cfg()
                cfg["chat_history"] = self.conversations
                save_cfg(cfg)
                return True, ai_message
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else str(e)
            return None, f"HTTP {e.code}: {error_body[:200]}"
        except Exception as e:
            return None, str(e)

    def _casual_response(self, text):
        lower = text.lower().strip()
        if re.search(r'\b(hi|hai|halo|hello|hey|helo)\b', lower):
            return "Halo juga! Ada yang bisa aku bantu? 😊"
        if re.search(r'\b(apa kabar|how are you|kabar)\b', lower):
            return "Aku baik-baik saja, terima kasih! Kamu gimana? 🦂"
        if re.search(r'\b(nama mu|siapa kamu|who are you|your name)\b', lower):
            return "Aku Nexcorix Claw, asisten AI-mu yang ramah! Senang berkenalan. 🦂"
        if re.search(r'\b(terima kasih|thanks|thank you|makasih)\b', lower):
            return "Sama-sama! Senang bisa membantu. 😊"
        if re.search(r'\b(bye|dadah|selamat tinggal|goodbye)\b', lower):
            return "Sampai jumpa lagi! Tetap semangat! 🦂"
        if re.search(r'\b(lelucon|joke|lucu|cerita lucu)\b', lower):
            return "Kenapa programmer selalu dingin? Karena mereka selalu pakai AC (Ascii Character)! 😄 Mau lagi?"
        if re.search(r'\b(pagi|siang|sore|malam|good morning|good night)\b', lower):
            return "Selamat! Semoga harimu menyenangkan! 🌟"
        if re.search(r'\b(kamu bisa apa|lo bisa apa|bisa apa|apa saja yang bisa kamu lakukan|kemampuan|fitur)\b', lower):
            return (
                "Aku bisa banyak hal lho! 😊\n\n"
                "📌 **Perintah langsung:**\n"
                "- install nmap → install tools\n"
                "- scan network → scan jaringan\n"
                "- browse google.com → lihat teks website\n"
                "- create file test.txt → buat file\n"
                "- run ls -la → jalankan perintah shell\n"
                "- web server → buat web server lokal\n\n"
                "💬 **Obrolan biasa:**\n"
                "- Ajak aku ngobrol, tanya apa saja\n"
                "- Cerita, lelucon, bantu coding\n\n"
                "🔧 **Settings & Channels:**\n"
                "- Atur API key, ganti model AI\n"
                "- Sambungkan ke Telegram, Discord, dll\n\n"
                "Ada yang mau kamu coba? 🦂"
            )
        if re.search(r'\b(tolong|help|bantuan|what can you do)\b', lower):
            return "Tentu! Ketik 'bisa apa' untuk lihat fitur lengkap, atau langsung coba 'install nmap', 'scan network', atau 'browse google.com'. Ada yang bisa aku bantu? 😊"
        return None

    def process(self, user_id, text):
        lower = text.lower().strip()
        # Helper untuk notifikasi
        def notify(msg, status="info"):
            if status == "info":
                return f"🔄 {msg}"
            elif status == "success":
                return f"✅ {msg}"
            elif status == "error":
                return f"❌ {msg}"
            else:
                return msg
        
        # 1. INSTALL
        if re.match(r'^(install|pasang|instal)\s+', lower):
            pkgs = re.sub(r'^(install|pasang|instal)\s+', '', text).strip().split()
            if len(pkgs) > 1:
                notify("Menginstall beberapa package...", "info")
                result = self.installer.install_multiple(pkgs)
                return notify("Selesai", "success") + "\n" + result
            else:
                notify(f"Menginstall {pkgs[0]}...", "info")
                s, r = self.installer.install(pkgs[0])
                return (notify("Selesai", "success") if s else notify("Gagal", "error")) + "\n" + r
        
        # 2. GITHUB
        if re.match(r'^(github|clone)\s+', lower):
            tool = re.sub(r'^(github|clone)\s+', '', text).strip()
            notify(f"Mengclone {tool} dari GitHub...", "info")
            s, r = self.installer.install_from_github(tool)
            return (notify("Selesai", "success") if s else notify("Gagal", "error")) + "\n" + r
        
        # 3. PIP
        if re.match(r'^pip\s+', lower):
            pkg = re.sub(r'^pip\s+', '', text).strip()
            notify(f"Menginstall Python package {pkg}...", "info")
            s, r = self.installer.install_pip_tool(pkg)
            return (notify("Selesai", "success") if s else notify("Gagal", "error")) + "\n" + r
        
        # 4. SCAN
        if (re.search(r'\bscan\s+(network|jaringan|ip)\b', lower) or re.search(r'\bscan\s+\d+\.\d+\.\d+\.\d+(?:/\d+)?', lower)):
            target_match = re.search(r'(\d+\.\d+\.\d+\.\d+(?:/\d+)?)', text)
            target = target_match.group(1) if target_match else "192.168.1.0/24"
            notify(f"Memindai jaringan {target}...", "info")
            result = self.network.scan_network(target)
            return notify("Scan selesai", "success") + "\n" + result
        if re.match(r'scan ports?\s+', lower):
            parts = re.sub(r'scan ports?\s+', '', text).strip().split()
            target = parts[0] if parts else "localhost"
            ports = parts[1] if len(parts) > 1 else "1-1000"
            notify(f"Memindai port {ports} pada {target}...", "info")
            result = self.network.scan_ports(target, ports)
            return notify("Scan selesai", "success") + "\n" + result
        if re.search(r'(wifi scan|scan wifi)', lower):
            notify("Memindai WiFi...", "info")
            result = self.network.wifi_scan()
            return notify("Scan selesai", "success") + "\n" + result
        
        # 5. BROWSING & SEARCH
        if re.match(r'(browse|buka|lihat|open)\s+', lower):
            url = re.sub(r'^(browse|buka|lihat|open)\s+', '', text).strip()
            notify(f"Membuka {url}...", "info")
            s, res = self.browser.browse(url)
            return notify("Selesai", "success") + "\n" + (res if s else f"Error: {res}")
        if re.match(r'(search|cari|google|temukan)\s+', lower):
            query = re.sub(r'^(search|cari|google|temukan)\s+', '', text).strip()
            notify(f"Mencari '{query}'...", "info")
            s, res = self.browser.search_duckduckgo(query)
            return notify("Selesai", "success") + "\n" + (res if s else f"Error: {res}")
        
        # 6. FILE & FOLDER
        # Pola: "buat folder <nama> dengan kode <isi>" -> buat folder + file script.py
        folder_with_code = re.search(r'buat folder\s+([^\s]+)\s+dengan\s+(?:kode|isi)\s+(.+)', text, re.IGNORECASE)
        if folder_with_code:
            folder_name = folder_with_code.group(1)
            code_content = folder_with_code.group(2)
            notify(f"Membuat folder '{folder_name}'...", "info")
            s1, msg1 = self.fm.create_folder(folder_name)
            if s1:
                old_path = self.fm.current_path
                self.fm.set_path(folder_name)
                filename = "script.py"
                notify(f"Membuat file {filename} di dalam folder...", "info")
                s2, msg2 = self.fm.create_file(filename, code_content)
                self.fm.set_path(old_path)
                if s2:
                    return notify("Berhasil!", "success") + f"\n✅ Folder '{folder_name}' dan file '{filename}' dibuat.\nKode:\n{code_content}"
                else:
                    return notify("Folder berhasil, tapi gagal buat file", "error") + f"\n{msg2}"
            else:
                return notify("Gagal membuat folder", "error") + f"\n{msg1}"
        # Buat folder biasa
        if re.match(r'buat folder\s+', lower):
            name = re.sub(r'^buat folder\s+', '', text).strip()
            notify(f"Membuat folder '{name}'...", "info")
            s, msg = self.fm.create_folder(name)
            return notify("Selesai", "success") if s else notify("Gagal", "error") + f"\n{msg}"
        # Buat file dengan isi
        if re.match(r'(create file|buat file|simpan file)\s+', lower):
            parts = re.sub(r'^(create file|buat file|simpan file)\s+', '', text).strip().split(maxsplit=1)
            filename = parts[0]
            content = ""
            if len(parts) > 1:
                isi_match = re.search(r'(?:isi|dengan isi|content:)\s*(.+)', parts[1], re.IGNORECASE)
                if isi_match:
                    content = isi_match.group(1).strip()
                else:
                    content = parts[1]
            notify(f"Membuat file '{filename}'...", "info")
            s, msg = self.fm.create_file(filename, content)
            return (notify("Selesai", "success") if s else notify("Gagal", "error")) + f"\n{msg}"
        # Buat file (tanpa isi)
        if re.match(r'buat file\s+', lower):
            parts = re.sub(r'^buat file\s+', '', text).strip().split(maxsplit=1)
            filename = parts[0]
            content = parts[1] if len(parts) > 1 else ""
            notify(f"Membuat file '{filename}'...", "info")
            s, msg = self.fm.create_file(filename, content)
            return (notify("Selesai", "success") if s else notify("Gagal", "error")) + f"\n{msg}"
        if re.match(r'create folder\s+|mkdir\s+', lower):
            name = re.sub(r'^(create folder|mkdir)\s+', '', text).strip()
            notify(f"Membuat folder '{name}'...", "info")
            s, msg = self.fm.create_folder(name)
            return (notify("Selesai", "success") if s else notify("Gagal", "error")) + f"\n{msg}"
        if re.match(r'delete\s+', lower):
            name = re.sub(r'^delete\s+', '', text).strip()
            notify(f"Menghapus '{name}'...", "info")
            s, msg = self.fm.delete_item(name)
            return (notify("Selesai", "success") if s else notify("Gagal", "error")) + f"\n{msg}"
        if re.match(r'read file\s+', lower):
            name = re.sub(r'^read file\s+', '', text).strip()
            content, err = self.fm.read_file(name)
            if content:
                return f"📄 Isi file '{name}':\n{content[:3000]}"
            else:
                return notify("Gagal membaca file", "error") + f"\n{err}"
        if re.match(r'list files?|ls|dir', lower):
            return self.fm.list_items()
        if re.match(r'cd\s+', lower):
            path = re.sub(r'^cd\s+', '', text).strip()
            if self.fm.set_path(path):
                return f"📁 Berada di: {self.fm.get_path()}"
            else:
                return notify("Path tidak ditemukan", "error")
        
        # 7. RUN COMMAND
        if re.match(r'run\s+', lower):
            cmd = re.sub(r'^run\s+', '', text).strip()
            notify(f"Menjalankan: {cmd}", "info")
            result = self.executor.run(cmd)
            out = result["stdout"][:3000] if result["stdout"] else ""
            err = result["stderr"][:1000] if result["stderr"] else ""
            status = "SUCCESS" if result["success"] else "FAILED"
            return notify(f"Perintah selesai ({status})", "success" if result["success"] else "error") + f"\nOUTPUT:\n{out}\nERROR:\n{err}"
        
        # 8. WEB SERVER
        if re.match(r'web server\s*', lower):
            parts = re.sub(r'web server\s*', '', text).strip().split()
            folder = parts[0] if parts else "nexcorix_site"
            port = int(parts[1]) if len(parts) > 1 else 8080
            notify(f"Mempersiapkan web server di folder '{folder}', port {port}...", "info")
            full_path = self.web.create_html_site(folder)
            s, msg = self.web.start_server(full_path, port)
            return notify("Web server berjalan!", "success") + f"\n{msg}"
        
        # 9. UPDATE SYSTEM
        if re.match(r'update (system|repos)', lower):
            notify("Mengupdate repository...", "info")
            s, msg = self.installer.update_repos()
            return notify("Selesai", "success") if s else notify("Gagal", "error") + f"\n{msg}"
        
        # 10. OBROLAN RINGAN (template)
        casual = self._casual_response(text)
        if casual:
            return casual
        
        # 11. PERMINTAAN KODE / PENJELASAN (AI)
        if re.search(r'(bantu|tolong|buatkan|tuliskan|kode|code|script|program|fungsi|kelas|jelaskan|apa itu|bagaimana cara)', lower):
            success, response = self.chat_with_ai(user_id, text)
            if success:
                return response
            else:
                return f"Maaf, AI tidak bisa merespon karena {response}. Set API key di Settings (18) → 7."
        
        # 12. FALLBACK
        success, response = self.chat_with_ai(user_id, text)
        if success:
            return response
        else:
            return f"Maaf, aku tidak mengerti perintah itu. Coba: 'install nmap', 'scan network', 'buat folder x', atau minta bantuan dengan 'bantu saya...'."

# ========== Channel Adapters ==========
class BaseChannelAdapter:
    def __init__(self, name, config, ai_engine): self.name = name; self.config = config; self.ai = ai_engine; self._running = False
    def start(self): pass
    def stop(self): self._running = False

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters
    TELEGRAM_AVAILABLE = True
except:
    TELEGRAM_AVAILABLE = False

class TelegramAdapter(BaseChannelAdapter):
    def __init__(self, config, ai_engine):
        super().__init__("telegram", config, ai_engine)
        self.token = config.get("token", ""); self.admin_id = config.get("admin_id", "")
        self.application = None; self.loop = None; self.thread = None
    def is_admin(self, user_id): return not self.admin_id or str(user_id)==str(self.admin_id)
    async def start_cmd(self, update, context): await update.message.reply_text("Nexcorix Claw v4.0 siap!")
    async def handle_msg(self, update, context):
        user = update.effective_user
        if not self.is_admin(user.id): await update.message.reply_text(f"Akses ditolak. ID Anda: {user.id}"); return
        response = self.ai.process(str(user.id), update.message.text)
        for i in range(0, len(response), 4000): await update.message.reply_text(response[i:i+4000])
    async def _run(self):
        from telegram.request import HTTPXRequest
        self.application = Application.builder().token(self.token).request(HTTPXRequest()).build()
        self.application.add_handler(CommandHandler("start", self.start_cmd))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_msg))
        await self.application.initialize(); await self.application.start(); await self.application.updater.start_polling()
        self._running = True
        while self._running: await asyncio.sleep(1)
        await self.application.updater.stop(); await self.application.stop(); await self.application.shutdown()
    def start(self):
        if self._running: return
        if not self.token: print("Telegram token missing.")
        def target():
            self.loop = asyncio.new_event_loop(); asyncio.set_event_loop(self.loop); self.loop.run_until_complete(self._run())
        self.thread = threading.Thread(target=target, daemon=True); self.thread.start()
    def stop(self):
        self._running = False
        if self.loop: self.loop.call_soon_threadsafe(self.loop.stop)

class DiscordAdapter(BaseChannelAdapter):
    def start(self):
        try:
            import discord
            from discord.ext import commands
        except:
            print("Discord library not installed. Run: pip install discord.py")
            return
        token = self.config.get("discord_token", "")
        if not token: print("Discord token missing."); return
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

class PlaceholderAdapter(BaseChannelAdapter):
    def start(self): print(f"{self.name} adapter: coming soon."); self._running = True

ADAPTER_MAP = {
    "telegram": TelegramAdapter,
    "discord": DiscordAdapter,
    "whatsapp": PlaceholderAdapter,
    "slack": PlaceholderAdapter,
}

# ========== Menu Settings ==========
def show_settings_menu(ai):
    cfg = ai.cfg
    while True:
        clear()
        print(c("C") + "╔" + "═" * 58 + "╗" + c("r"))
        print(c("C") + "║" + c("b") + c("Y") + " " * 22 + "NEXCORIX SETTINGS" + " " * 23 + c("r") + c("C") + "║" + c("r"))
        print(c("C") + "╚" + "═" * 58 + "╝" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "1" + c("C") + "] Model Provider")
        print(c("d") + "    ├─ OpenAI")
        print(c("d") + "    ├─ Anthropic")
        print(c("d") + "    ├─ Gemini")
        print(c("d") + "    ├─ DeepSeek")
        print(c("d") + "    ├─ OpenRouter")
        print(c("d") + "    ├─ Ollama (Local)")
        print(c("d") + "    └─ Custom API" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "2" + c("C") + "] Current Model")
        current_model = cfg.get("model", "openai/gpt-4o")
        print(c("d") + "    ├─ gpt-4o")
        print(c("d") + "    ├─ claude-3.5-sonnet")
        print(c("d") + "    ├─ gemini-1.5-pro")
        print(c("d") + "    ├─ deepseek-chat")
        print(c("d") + "    ├─ llama-3.1-70b")
        print(c("d") + "    └─ " + current_model + " (active)" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "3" + c("C") + "] Fallback Model")
        fallback = cfg.get("fallback_model", "deepseek-chat")
        print(c("d") + "    ├─ deepseek-chat")
        print(c("d") + "    ├─ openai/gpt-3.5-turbo")
        print(c("d") + "    └─ " + fallback + " (active)" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "4" + c("C") + "] Temperature")
        print(c("d") + f"    └─ {cfg.get('temperature', 0.7)} (0.0 - 2.0)" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "5" + c("C") + "] Max Tokens")
        print(c("d") + f"    └─ {cfg.get('max_tokens', 4096)}" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "6" + c("C") + "] Context Window")
        print(c("d") + "    └─ Auto Detect" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "7" + c("C") + "] API Configuration")
        print(c("d") + "    ├─ API Key")
        print(c("d") + "    ├─ Base URL")
        print(c("d") + "    └─ Organization ID" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "8" + c("C") + "] Local Models")
        print(c("d") + "    ├─ ollama list")
        print(c("d") + "    ├─ Scan Models")
        print(c("d") + "    └─ Download Model" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "9" + c("C") + "] Performance")
        print(c("d") + "    ├─ Fast Mode")
        print(c("d") + "    ├─ Balanced Mode")
        print(c("d") + "    └─ Quality Mode" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "10" + c("C") + "] Save Configuration" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "11" + c("C") + "] Exit" + c("r"))
        print()
        choice = input(c("Y") + "Select option: " + c("r")).strip()
        if choice == "1":
            prov_list = ["openai", "anthropic", "google", "deepseek", "openrouter", "ollama", "custom"]
            print("Pilih provider (masukkan nomor atau nama):")
            for i, p in enumerate(prov_list, 1): print(f"  {i}. {p}")
            prov_input = input("Provider: ").strip().lower()
            if prov_input.isdigit():
                idx = int(prov_input)-1
                if 0 <= idx < len(prov_list): prov = prov_list[idx]
                else: print(c("R") + "Nomor tidak valid." + c("r")); input("Enter..."); continue
            else: prov = prov_input
            if prov in prov_list:
                cfg["provider"] = prov
                if prov in MODELS_BY_PROVIDER and MODELS_BY_PROVIDER[prov]:
                    default_model = MODELS_BY_PROVIDER[prov][0]
                    cfg["model"] = default_model
                save_cfg(cfg)
                print(c("G") + f"Provider diubah ke {prov}" + c("r"))
                print(c("G") + f"Model default diatur ke {cfg.get('model')}" + c("r"))
                print(c("C") + "🔄 Testing AI connection..." + c("r"))
                success, msg = ai.test_connection()
                if success:
                    print(c("G") + f"✅ {msg}" + c("r"))
                else:
                    print(c("R") + f"❌ {msg}" + c("r"))
            else:
                print(c("R") + "Provider tidak dikenal" + c("r"))
            input("Enter...")
        elif choice == "2":
            provider = cfg.get("provider", "openrouter")
            if provider in MODELS_BY_PROVIDER:
                model_list = MODELS_BY_PROVIDER[provider]
            else:
                model_list = MODELS_BY_PROVIDER.get("openrouter", [])
            print(c("C") + f"\nModel untuk provider {provider.upper()} (total {len(model_list)}):" + c("r"))
            for i, m in enumerate(model_list, 1):
                marker = " (active)" if m == cfg.get("model") else ""
                print(f"  {i}. {m}{marker}")
            print("  0. Kembali")
            choice_model = input("Pilih nomor model (atau masukkan ID langsung): ").strip()
            if choice_model == "0":
                pass
            elif choice_model.isdigit():
                idx = int(choice_model) - 1
                if 0 <= idx < len(model_list):
                    new_model = model_list[idx]
                    cfg["model"] = new_model
                    save_cfg(cfg)
                    print(c("G") + f"✅ Model diubah ke {new_model}" + c("r"))
                    print(c("C") + "🔄 Testing AI connection with new model..." + c("r"))
                    success, msg = ai.test_connection()
                    if success:
                        print(c("G") + f"✅ {msg}" + c("r"))
                    else:
                        print(c("R") + f"❌ {msg}" + c("r"))
                else:
                    print(c("R") + "Nomor tidak valid." + c("r"))
            else:
                new_model = choice_model
                if new_model:
                    cfg["model"] = new_model
                    save_cfg(cfg)
                    print(c("G") + f"✅ Model diubah ke {new_model}" + c("r"))
                    print(c("C") + "🔄 Testing AI connection..." + c("r"))
                    success, msg = ai.test_connection()
                    if success:
                        print(c("G") + f"✅ {msg}" + c("r"))
                    else:
                        print(c("R") + f"❌ {msg}" + c("r"))
                else:
                    print(c("R") + "Tidak diubah." + c("r"))
            input("Tekan Enter...")
        elif choice == "3":
            fb = input("Fallback model ID: ").strip()
            if fb:
                cfg["fallback_model"] = fb
                save_cfg(cfg)
                print(c("G") + "Saved.")
            input("Enter...")
        elif choice == "4":
            try:
                new_temp = float(input("Temperature (0.0 - 2.0): ").strip())
                cfg["temperature"] = max(0.0, min(2.0, new_temp))
                save_cfg(cfg)
                print(c("G") + "Saved.")
            except:
                print(c("R") + "Invalid input.")
            input("Enter...")
        elif choice == "5":
            try:
                new_tok = int(input("Max Tokens (256-8192): ").strip())
                cfg["max_tokens"] = max(256, min(8192, new_tok))
                save_cfg(cfg)
                print(c("G") + "Saved.")
            except:
                print(c("R") + "Invalid input.")
            input("Enter...")
        elif choice == "6":
            print("Context window: Auto Detect (tidak dapat diubah)")
            input("Enter...")
        elif choice == "7":
            print("1. Set OpenRouter API Key")
            print("2. Set OpenAI API Key")
            print("3. Set Anthropic API Key")
            print("4. Set Google API Key")
            print("5. Set DeepSeek API Key")
            print("6. Set Custom API URL & Key")
            print("7. Set Base URL (OpenRouter)")
            sub = input("Pilih: ").strip()
            if sub == "1":
                cfg["openrouter_key"] = input("OpenRouter API Key: ").strip()
            elif sub == "2":
                cfg["openai_key"] = input("OpenAI API Key: ").strip()
            elif sub == "3":
                cfg["anthropic_key"] = input("Anthropic API Key: ").strip()
            elif sub == "4":
                cfg["google_key"] = input("Google API Key: ").strip()
            elif sub == "5":
                cfg["deepseek_key"] = input("DeepSeek API Key: ").strip()
            elif sub == "6":
                cfg["custom_api_url"] = input("Custom API URL: ").strip()
                cfg["custom_api_key"] = input("Custom API Key (optional): ").strip()
            elif sub == "7":
                cfg["base_url"] = input("Base URL: ").strip()
            else:
                print(c("R") + "Invalid")
            save_cfg(cfg)
            print(c("G") + "Saved.")
            print(c("C") + "🔄 Testing AI connection after saving API key..." + c("r"))
            success, msg = ai.test_connection()
            if success:
                print(c("G") + f"✅ {msg}" + c("r"))
            else:
                print(c("R") + f"❌ {msg}" + c("r"))
            input("Enter...")
        elif choice == "8":
            print("Local models: pastikan Ollama terinstall.")
            print("1. ollama list")
            print("2. Scan Models")
            print("3. Download Model")
            sub = input("Pilih: ").strip()
            if sub == "1":
                os.system("ollama list")
            elif sub == "2":
                print("Scanning Ollama models...")
                result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
                print(result.stdout if result.stdout else "No models found")
            elif sub == "3":
                model_name = input("Model name to download (e.g., llama3.2:3b): ").strip()
                if model_name:
                    print(f"Downloading {model_name}...")
                    os.system(f"ollama pull {model_name}")
            input("Enter...")
        elif choice == "9":
            print("1. Fast Mode (temperature=0.5, max_tokens=2048)")
            print("2. Balanced Mode (temperature=0.7, max_tokens=4096)")
            print("3. Quality Mode (temperature=0.9, max_tokens=8192)")
            perf = input("Pilih: ").strip()
            if perf == "1":
                cfg["performance"] = "fast"
                cfg["temperature"] = 0.5
                cfg["max_tokens"] = 2048
            elif perf == "2":
                cfg["performance"] = "balanced"
                cfg["temperature"] = 0.7
                cfg["max_tokens"] = 4096
            elif perf == "3":
                cfg["performance"] = "quality"
                cfg["temperature"] = 0.9
                cfg["max_tokens"] = 8192
            else:
                print(c("R") + "Invalid")
            save_cfg(cfg)
            print(c("G") + "Performance mode saved.")
            input("Enter...")
        elif choice == "10":
            save_cfg(cfg)
            print(c("G") + "Configuration saved.")
            input("Enter...")
        elif choice == "11":
            break
        else:
            print(c("R") + "Invalid option.")
            time.sleep(1)

# ========== Channels Menu ==========
active_adapters = {}
def show_channels_menu(ai):
    global active_adapters
    if 'channels' not in ai.cfg: ai.cfg['channels'] = {}; save_cfg(ai.cfg)
    channels = [("1","Telegram","telegram"),("2","Discord","discord")]
    while True:
        clear()
        print(c("C")+"╔"+"═"*58+"╗"+c("r"))
        print(c("C")+"║"+c("b")+c("Y")+" "*22+"C H A N N E L S"+c("O")+" 🦂"+c("C")+" "*27+c("C")+"║"+c("r"))
        print(c("C")+"╠"+"═"*58+"╣"+c("r"))
        for num,name,key in channels:
            status = "✅ Online" if key in active_adapters and active_adapters[key]._running else "❌ Offline"
            print(c("C")+f"║  [{num}] {name:<16} {status:<20}"+c("C")+"║"+c("r"))
        print(c("C")+"╠"+"═"*58+"╣"+c("r"))
        print(c("C")+"║  [c] Configure   [s] Start   [t] Stop   [0] Back   ║"+c("r"))
        print(c("C")+"╚"+"═"*58+"╝"+c("r"))
        cmd = input(c("Y")+"Choice: "+c("r")).strip().lower()
        if cmd == "0": break
        elif cmd == "c":
            ch_num = input("Enter channel number: ").strip()
            for num,name,key in channels:
                if num == ch_num:
                    if key == "telegram":
                        token = input("Bot Token: ").strip(); admin = input("Admin ID (optional): ").strip()
                        ai.cfg["token"] = token; ai.cfg["admin_id"] = admin
                        ai.cfg['channels'][key] = {"token": token, "admin_id": admin}
                    elif key == "discord":
                        token = input("Discord Bot Token: ").strip()
                        ai.cfg['channels'][key] = {"discord_token": token}
                    save_cfg(ai.cfg); print("Saved.")
                    break
        elif cmd == "s":
            ch_num = input("Enter channel number to start: ").strip()
            for num,name,key in channels:
                if num == ch_num:
                    if key in active_adapters and active_adapters[key]._running: print("Already running")
                    else:
                        if key == "telegram": cfg_adapter = {"token": ai.cfg.get("token",""), "admin_id": ai.cfg.get("admin_id","")}
                        else: cfg_adapter = ai.cfg.get("channels", {}).get(key, {})
                        if not cfg_adapter: print("Not configured. Use 'c' first.")
                        else:
                            adapter = ADAPTER_MAP.get(key)(cfg_adapter, ai)
                            adapter.start()
                            active_adapters[key] = adapter
                            print(f"{name} started.")
                    input(); break
        elif cmd == "t":
            ch_num = input("Enter channel number to stop: ").strip()
            for num,name,key in channels:
                if num == ch_num:
                    if key in active_adapters:
                        active_adapters[key].stop(); del active_adapters[key]; print(f"{name} stopped.")
                    else: print("Not running")
                    input(); break
        else: print("Invalid"); time.sleep(1)

# ========== Main Menu ==========
def main():
    ai = AIChatEngine()
    os_detector = OSDetector()
    # Notifikasi AI connection
    print(c("C") + "\n🔍 Testing AI connection...")
    ai_ok, ai_msg = ai.test_connection()
    if ai_ok:
        print(c("G") + f"✅ {ai_msg} You can chat with AI in menu 2." + c("r"))
    else:
        print(c("R") + f"❌ {ai_msg} Please set API key in Settings (18) → 7 → choose provider and enter key." + c("r"))
    time.sleep(2)
    while True:
        clear()
        print(c("C")+"╔"+"═"*58+"╗"+c("r"))
        print(c("C")+"║"+c("O")+" 🦂 "+c("b")+c("Y")+"      N E X C O R I X   C L A W   v4.0       "+c("O")+"🦂 "+c("C")+"║"+c("r"))
        print(c("C")+"╠"+"═"*58+"╣"+c("r"))
        print(c("C")+"║"+c("W")+"  Integrations"+" "*46+c("C")+"║"+c("r"))
        for name in ["Discord","Telegram","WhatsApp","Slack","Matrix","Microsoft Teams","Gmail","Google Calendar","Google Drive","Dropbox","GitHub","GitLab","Notion","Trello","Jira","Airtable","Google Sheets","PostgreSQL","MySQL","MongoDB","Redis","n8n","Zapier","Make","Home Assistant","MQTT","Webhook","REST API","MCP Servers"]:
            print(c("C")+"║"+c("d")+f"  ├─ {name:<18} 🚧 Soon"+c("C")+"║"+c("r"))
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
        if choice == "2":
            clear()
            print(c("C")+"Chat mode (ketik 'exit' untuk kembali)")
            while True:
                inp = input(c("M")+"You: "+c("r")).strip()
                if inp.lower() in ("exit","back"): break
                if inp: print(c("G")+"Nexcorix: "+ai.process("local_user", inp)+c("r"))
        elif choice == "8": show_channels_menu(ai)
        elif choice == "18": show_settings_menu(ai)
        elif choice == "20": print(c("G")+"Goodbye!"+c("r")); break
        else: print("Fitur lainnya tersedia. Silakan pilih 2 untuk chat, 8 untuk channels, 18 untuk settings."); input()

if __name__ == "__main__":
    main()
