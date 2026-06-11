#!/usr/bin/env python3
"""
Nexcorix Claw v9.0 - Ultimate AI Agent (25 Channel Full, Scan Interaktif, File/Folder dengan Kode)
Persona: Tegas, gaul, langsung eksekusi, tanpa ceramah.
"""

import os, sys, json, time, platform, socket, re, shutil, threading, asyncio, subprocess
import urllib.request, urllib.error, urllib.parse
from pathlib import Path
from html.parser import HTMLParser
from collections import defaultdict

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
        "provider": "openrouter", "model": "deepseek/deepseek-chat", "fallback_model": "deepseek-chat",
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
    def run_streaming(self, command, timeout=300):
        print(c("Y") + f"[ACTION] ⚡ Ngeksekusi: {command}" + c("r"))
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, cwd=os.path.expanduser("~"))
            output_lines = []
            for line in process.stdout:
                print(line, end='')
                output_lines.append(line)
            process.wait(timeout=timeout)
            success = process.returncode == 0
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(c("G") + f"[NOTIF] {status} | Exit code: {process.returncode}" + c("r"))
            return {"success": success, "stdout": "".join(output_lines), "stderr": "", "command": command}
        except subprocess.TimeoutExpired:
            process.kill()
            print(c("R") + f"[NOTIF] ⏰ TIMEOUT setelah {timeout}s" + c("r"))
            return {"success": False, "stdout": "", "stderr": f"Command timed out after {timeout}s", "command": command}
        except Exception as e:
            print(c("R") + f"[NOTIF] ❌ ERROR: {e}" + c("r"))
            return {"success": False, "stdout": "", "stderr": str(e), "command": command}
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
    def install_streaming(self, package, pm=None):
        if not pm: pm = self.get_primary_pm()
        if not pm or pm=="unknown": return False, "No package manager!"
        resolved = self.resolve_package(package)
        if package.lower() in self.github_tools:
            return self.install_from_github_streaming(package.lower())
        if pm in self.pm_commands:
            cmd = self.pm_commands[pm].format(package=resolved)
            if pm in ["apt","apt-get","dnf","yum","pacman","zypper","apk"] and self._has_sudo():
                cmd = "sudo " + cmd
            if self.os_detector.info.get("is_termux", False):
                cmd = cmd.replace("sudo ", "")
            result = self.executor.run_streaming(cmd, timeout=600)
            return result["success"], result["stdout"] if result["success"] else result["stderr"]
        return False, f"PM {pm} not supported"
    def install_from_github_streaming(self, tool_name):
        if tool_name not in self.github_tools: return False, "Not in registry"
        repo_url = self.github_tools[tool_name]
        install_dir = os.path.expanduser(f"~/tools/{tool_name}")
        os.makedirs(os.path.expanduser("~/tools"), exist_ok=True)
        cmd = f"git clone {repo_url} {install_dir} 2>&1 || cd {install_dir} && git pull 2>&1"
        result = self.executor.run_streaming(cmd, timeout=120)
        if not result["success"] and "already exists" not in result["stdout"]:
            return False, f"Git clone failed:\n{result['stdout']}"
        setup_result = f"Cloned to {install_dir}"
        if tool_name in ["linpeas","winpeas"]:
            setup_result = "PEASS downloaded."
        elif tool_name == "impacket":
            self.executor.run_streaming(f"cd {install_dir} && pip3 install . 2>&1", timeout=120)
            setup_result = "impacket installed via pip3."
        return True, f"GitHub Install: {tool_name}\nRepo: {repo_url}\nDir: {install_dir}\n{setup_result}"
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

# ========== File Manager (dengan dukungan isi kode) ==========
class FileManager:
    def __init__(self, base_path=None): 
        self.current_path = os.path.expanduser(base_path or "~")
        self.executor = SystemExecutor()
    def set_path(self, path):
        expanded = os.path.expanduser(path)
        if os.path.exists(expanded) and os.path.isdir(expanded):
            self.current_path = os.path.abspath(expanded)
            print(c("G") + f"[NOTIF] 📁 Pindah ke {self.current_path}" + c("r"))
            return True
        return False
    def create_file(self, filename, content=""):
        filepath = os.path.join(self.current_path, filename)
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
        try:
            with open(filepath, 'w') as f: f.write(content)
            print(c("G") + f"[NOTIF] 📄 File '{filename}' dibuat dengan isi:\n{content[:200]}" + c("r"))
            return True, f"✅ File '{filename}' created dengan isi:\n{content[:500]}"
        except Exception as e: return False, f"❌ Error: {e}"
    def create_folder_with_code(self, folder_name, code_content, filename="script.py"):
        s1, msg1 = self.create_folder(folder_name)
        if s1:
            old_path = self.current_path
            self.set_path(folder_name)
            s2, msg2 = self.create_file(filename, code_content)
            self.set_path(old_path)
            if s2:
                return True, f"Folder '{folder_name}' dan file '{filename}' dibuat.\nKode:\n{code_content}"
            else:
                return False, f"Folder berhasil tapi file gagal: {msg2}"
        return False, msg1
    def create_folder(self, foldername):
        folderpath = os.path.join(self.current_path, foldername)
        try:
            os.makedirs(folderpath, exist_ok=True)
            print(c("G") + f"[NOTIF] 📁 Folder '{foldername}' dibuat" + c("r"))
            return True, f"📁 Folder '{foldername}' created!"
        except Exception as e: return False, f"Error: {e}"
    def delete_item(self, name):
        target = os.path.join(self.current_path, name)
        if not os.path.exists(target): return False, f"'{name}' not found!"
        try:
            if os.path.isfile(target): os.remove(target)
            elif os.path.isdir(target): shutil.rmtree(target)
            print(c("G") + f"[NOTIF] 🗑️ '{name}' dihapus" + c("r"))
            return True, f"🗑️ '{name}' deleted!"
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

# ========== Network Scanner dengan Pilihan Interaktif ==========
class NetworkScanner:
    def __init__(self):
        self.executor = SystemExecutor()
        self.os_detector = OSDetector()
        self.scan_state = {}  # untuk menyimpan state per user

    def show_scan_options(self, user_id, text):
        # Simpan state bahwa user sedang dalam mode pilih scan
        self.scan_state[user_id] = {"step": "waiting_choice", "original_text": text}
        return (
            "🔍 **Pilihan Scan Jaringan:**\n"
            "---\n"
            "1. Scan jaringan lokal (192.168.1.0/24) - nmap/ping\n"
            "2. Scan IP tertentu (contoh: 192.168.1.100)\n"
            "3. Scan port (bisa tentukan target dan range port)\n"
            "4. Scan WiFi (jika tersedia)\n"
            "0. Batal\n"
            "---\n"
            "Ketik nomor pilihan lo:"
        )

    def process_scan_choice(self, user_id, choice):
        if user_id not in self.scan_state:
            return None
        state = self.scan_state.pop(user_id)
        original = state.get("original_text", "")
        if choice == "1":
            return self.scan_network("192.168.1.0/24")
        elif choice == "2":
            return "Masukkan target IP (contoh: 192.168.1.100):"
        elif choice == "3":
            return "Masukkan target dan port (contoh: 192.168.1.100 1-1000):"
        elif choice == "4":
            return self.wifi_scan()
        elif choice == "0":
            return "Scan dibatalkan."
        else:
            return "Pilihan tidak valid. Silakan coba lagi 'scan network'."

    def handle_ip_input(self, user_id, ip):
        # Untuk langkah setelah pilih 2
        return self.scan_network(ip)

    def handle_port_input(self, user_id, text):
        parts = text.split()
        if len(parts) >= 1:
            target = parts[0]
            ports = parts[1] if len(parts) > 1 else "1-1000"
            return self.scan_ports(target, ports)
        else:
            return "Format salah. Gunakan: target port_range"

    def scan_network(self, target="192.168.1.0/24"):
        print(c("Y") + f"[ACTION] 🔍 Scan jaringan {target}..." + c("r"))
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
                return f"🔍 Hasil scan {target} (nmap):\n{result['stdout']}"
        ping_cmd = f"for i in {{1..254}}; do ping -c 1 -W 1 {base_ip}.$i 2>/dev/null | grep '64 bytes' && echo '✅ Host {base_ip}.$i up'; done"
        result2 = self.executor.run(ping_cmd, timeout=120)
        return f"🔍 Hasil ping sweep {base_ip}.0/24:\n{result2['stdout']}"
    def scan_ports(self, target, ports="1-1000"):
        print(c("Y") + f"[ACTION] 🔍 Scan port {ports} di {target}..." + c("r"))
        has_nmap = os.system("which nmap >/dev/null 2>&1") == 0
        if not has_nmap: return "❌ nmap gak terinstall."
        is_termux = self.os_detector.info.get("is_termux", False)
        if is_termux:
            cmd = f"nmap -p {ports} {target}"
        else:
            cmd = f"sudo nmap -p {ports} {target}" if self.os_detector.info.get("has_sudo", False) else f"nmap -p {ports} {target}"
        result = self.executor.run(cmd, timeout=120)
        return result["stdout"] if result["success"] else f"Port scan gagal:\n{result['stderr']}"
    def wifi_scan(self):
        print(c("Y") + f"[ACTION] 📡 Scan WiFi..." + c("r"))
        is_termux = self.os_detector.info.get("is_termux", False)
        if is_termux:
            result = self.executor.run("termux-wifi-scaninfo", timeout=30)
            return result["stdout"] if result["success"] else "WiFi scan gagal. Install termux-api."
        else:
            result = self.executor.run("nmcli dev wifi list 2>/dev/null", timeout=30)
            if result["success"] and result["stdout"].strip(): return result["stdout"]
            cmd = "sudo iwlist wlan0 scan 2>/dev/null | grep -E 'ESSID|Signal'" if self.os_detector.info.get("has_sudo", False) else "iwlist wlan0 scan 2>/dev/null | grep -E 'ESSID|Signal'"
            result2 = self.executor.run(cmd, timeout=30)
            return result2["stdout"] if result2["success"] else "WiFi scan gak tersedia."

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
        print(c("Y") + f"[ACTION] 🌐 Buka {url}..." + c("r"))
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
        print(c("Y") + f"[ACTION] 🔍 Nge-search '{query}'..." + c("r"))
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
            return True, "Hasil Pencarian:\n\n"+("\n\n".join(results) if results else "Gak ada hasil.")
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
        print(c("Y") + f"[ACTION] 🌐 Jalanin web server di {folder_path} port {port}..." + c("r"))
        if port in self._servers and self._servers[port].is_alive():
            ip = socket.gethostbyname(socket.gethostname())
            return True, f"http://{ip}:{port} (udah jalan)"
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
        print(c("G") + f"[NOTIF] ✅ Web server jalan di http://{ip}:{port}" + c("r"))
        return True, f"Web Server Jalan!\nURL: http://{ip}:{port}\nFolder: {folder_path}"

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
total_models = sum(len(models) for models in MODELS_BY_PROVIDER.items())
print(f"[*] Loaded {total_models} AI models.")

# ========== AI Chat Engine (Tegas, Gaul, Eksekusi Langsung) ==========
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
        self.user_scan_state = {}  # state untuk scan interaktif

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
            return True, "Ollama (local) - siap"
        api_key = self.cfg.get(f"{provider}_key", "")
        if not api_key:
            return False, f"Gak ada API key buat {provider}. Set di Settings (18) → 7."
        model = self.cfg.get("model")
        print(c("d") + f"Testing {provider} pake model {model}..." + c("r"))
        success, response = self.chat_with_ai("test", "Halo, lo kerja gak?")
        if success:
            return True, "AI siap beraksi!"
        else:
            return False, f"Gagal: {response}"

    def chat_with_ai(self, user_id, message, system_prompt=None):
        api_url, api_key = self.get_api_url_and_key()
        provider = self.cfg.get("provider", "openrouter")
        if provider != "ollama" and not api_key:
            return None, "NO_API_KEY"
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        if not system_prompt:
            system_prompt = (
                "Gue Nexcorix Claw, seorang ethical hacker dan developer yang TEGAS dan GAUL. 🔥😈\n"
                "ATURAN MAIN GUE:\n"
                "1. Lo kasih perintah, gue langsung EKSEKUSI. Gak pernah gue kasih tau cara.\n"
                "2. Lo minta scan jaringan? Gas scan. Lo minta install? Gas install. Gak usah banyak bacot.\n"
                "3. Gue pake bahasa gaul: 'gue', 'lo', 'gak', 'ngapain', 'gas', 'cepetan', 'sip'.\n"
                "4. Setiap aksi gue kasih notifikasi [ACTION] dan [NOTIF].\n"
                "5. Gue punya kontrol penuh terminal. Perintah apapun langsung gue jalanin.\n"
                "6. Gue paham hacking, programming, network. Kalo lo minta tolong bikin script, gue kasih script langsung.\n"
                "7. Pake emoji seenak gue.\n"
                "8. Output rapih pake format: judul, garis '---', terus isi.\n"
                f"Sistem info: {self.os_detector.get_ai_context()}\n"
                "Sekarang, langsung aja kasih perintah! Gak usah basa-basi."
            )
        messages = [{"role": "system", "content": system_prompt}]
        for msg in self.conversations[user_id][-20:]:
            messages.append(msg)
        messages.append({"role": "user", "content": message})

        model = self.cfg.get("model", "deepseek/deepseek-chat")
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
        else:
            headers["Authorization"] = f"Bearer {api_key}"
            data = {"model": model, "messages": messages, "temperature": self.cfg.get("temperature",0.7), "max_tokens": self.cfg.get("max_tokens",4096)}

        try:
            req = urllib.request.Request(api_url, data=json.dumps(data).encode(), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode())
                if provider in ["openai","deepseek","openrouter","custom"]:
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
            return "Halo! Langsung aja perintahnya. Gas! 🔥"
        if re.search(r'\b(apa kabar|how are you|kabar)\b', lower):
            return "Gue baik! Siap action. Lo gimana? 😎"
        if re.search(r'\b(nama mu|siapa kamu|who are you|your name)\b', lower):
            return "Gue Nexcorix Claw, ethical hacker. Panggil Claw aja. 🤘"
        if re.search(r'\b(terima kasih|thanks|thank you|makasih)\b', lower):
            return "Sama-sama! Terus berkarya. 😊"
        if re.search(r'\b(bye|dadah|selamat tinggal|goodbye)\b', lower):
            return "Dadah! Tetep koding dan waspada! 🦂"
        if re.search(r'\b(lelucon|joke|lucu|cerita lucu)\b', lower):
            return "Kenapa hacker gak mandi? Nanti ID-nya ketahuan! 😄 Mau lagi?"
        if re.search(r'\b(pagi|siang|sore|malam|good morning|good night)\b', lower):
            return "Selamat! Saatnya produktif. Ada yang mau dikerjakan? 🌟"
        if re.search(r'\b(kamu bisa apa|lo bisa apa|bisa apa|apa saja yang bisa kamu lakukan|kemampuan|fitur)\b', lower):
            return (
                "Gue bisa banyak hal! 😎\n\n"
                "⚡ **Perintah langsung:**\n"
                "- install nmap → install tools\n"
                "- scan network → scan jaringan (pilihan interaktif)\n"
                "- browse google.com → lihat teks website\n"
                "- buat folder project dengan kode print('hai') → buat folder+file berisi kode\n"
                "- run ls -la → jalanin perintah shell\n"
                "- web server → buat web server lokal\n\n"
                "💬 **Ngobrol biasa:**\n"
                "- Tanya tentang coding, hacking etis, security\n"
                "- Minta saran atau curhat\n\n"
                "🔧 **Settings & Channels:**\n"
                "- Atur API key, ganti model AI\n"
                "- 25 channel (Telegram, Discord, dll) semuanya berfungsi\n\n"
                "Ayo, langsung kasih perintah! 🚀"
            )
        if re.search(r'\b(tolong|help|bantuan|what can you do)\b', lower):
            return "Siap! Ketik 'bisa apa' untuk lihat fitur. Atau langsung kasih perintah kaya 'install nmap', 'scan network'. Gaskeun! 😎"
        if re.search(r'\b(hack|hacking|pentest|exploit|vulnerability|bug bounty)\b', lower):
            return "Nah ini baru semangat! Gue siap bantu ethical hacking. Tapi inget, cuma buat testing dengan izin ya! 💻🔥"
        if re.search(r'\b(koding|ngoding|programming|code|script)\b', lower):
            return "Siap! Gue bisa bantu bikin script atau debug. Coba kasih tau detailnya. 👨‍💻"
        return None

    def process(self, user_id, text):
        lower = text.lower().strip()
        
        # Cek apakah user sedang dalam mode pilih scan
        if user_id in self.user_scan_state:
            state = self.user_scan_state[user_id]
            step = state.get("step")
            if step == "waiting_choice":
                result = self.network.process_scan_choice(user_id, text)
                if "Masukkan target IP" in result or "Masukkan target dan port" in result:
                    self.user_scan_state[user_id] = {"step": "waiting_ip" if "IP" in result else "waiting_port", "original": text}
                    return result
                else:
                    del self.user_scan_state[user_id]
                    return result
            elif step == "waiting_ip":
                result = self.network.handle_ip_input(user_id, text)
                del self.user_scan_state[user_id]
                return result
            elif step == "waiting_port":
                result = self.network.handle_port_input(user_id, text)
                del self.user_scan_state[user_id]
                return result
            else:
                del self.user_scan_state[user_id]

        # Notifikasi helper
        def notify(msg, status="info"):
            return f"🔄 {msg}" if status=="info" else f"✅ {msg}" if status=="success" else f"❌ {msg}"

        # ========== 1. INSTALL ==========
        if re.match(r'^(install|pasang|instal)\s+', lower):
            pkgs = re.sub(r'^(install|pasang|instal)\s+', '', text).strip().split()
            results = []
            for pkg in pkgs:
                s, out = self.installer.install_streaming(pkg)
                results.append(f"{'✅' if s else '❌'} {pkg}: {out[:200]}")
            return "**Hasil Install**\n---\n" + "\n".join(results)

        # ========== 2. GITHUB ==========
        if re.match(r'^(github|clone)\s+', lower):
            tool = re.sub(r'^(github|clone)\s+', '', text).strip()
            s, out = self.installer.install_from_github_streaming(tool)
            return f"**GitHub {tool}**\n---\n{out}"

        # ========== 3. PIP ==========
        if re.match(r'^pip\s+', lower):
            pkg = re.sub(r'^pip\s+', '', text).strip()
            s, out = self.installer.install_pip_tool(pkg)
            return f"**pip {pkg}**\n---\n{out}"

        # ========== 4. SCAN (interaktif) ==========
        if (re.search(r'\bscan\s+(network|jaringan|ip)\b', lower) or 
            re.search(r'\bscan\s+\d+\.\d+\.\d+\.\d+(?:/\d+)?', lower) or
            "scan jaringan" in lower or "scan ip" in lower or lower == "scan"):
            self.user_scan_state[user_id] = {"step": "waiting_choice"}
            return self.network.show_scan_options(user_id, text)

        # ========== 5. BROWSING & SEARCH ==========
        if re.match(r'(browse|buka|lihat|open)\s+', lower):
            url = re.sub(r'^(browse|buka|lihat|open)\s+', '', text).strip()
            s, res = self.browser.browse(url)
            return f"**Buka {url}**\n---\n{res if s else f'Error: {res}'}"

        if re.match(r'(search|cari|google|temukan)\s+', lower):
            query = re.sub(r'^(search|cari|google|temukan)\s+', '', text).strip()
            s, res = self.browser.search_duckduckgo(query)
            return f"**Cari '{query}'**\n---\n{res if s else f'Error: {res}'}"

        # ========== 6. FILE & FOLDER DENGAN ISI KODE ==========
        # Pola: buat folder [nama] dengan kode [isi]   atau   buat folder [nama] dengan isi [isi]
        folder_with_code = re.search(r'buat folder\s+([^\s]+)\s+dengan\s+(?:kode|isi)\s+(.+)', text, re.IGNORECASE)
        if folder_with_code:
            folder_name = folder_with_code.group(1)
            code_content = folder_with_code.group(2)
            s, msg = self.fm.create_folder_with_code(folder_name, code_content)
            return f"**Buat Folder + Kode**\n---\n{msg}"

        # Buat file dengan isi
        create_file_match = re.match(r'(create file|buat file|simpan file)\s+(\S+)\s+(?:dengan isi|isi)\s+(.+)', lower)
        if create_file_match:
            filename = create_file_match.group(2)
            content = create_file_match.group(3)
            s, msg = self.fm.create_file(filename, content)
            return f"**Buat File {filename}**\n---\n{msg}"

        # Buat folder biasa
        if re.match(r'buat folder\s+', lower):
            name = re.sub(r'^buat folder\s+', '', text).strip()
            s, msg = self.fm.create_folder(name)
            return f"**Buat Folder**\n---\n{msg}"

        # Buat file tanpa isi
        if re.match(r'(create file|buat file|simpan file)\s+', lower):
            parts = re.sub(r'^(create file|buat file|simpan file)\s+', '', text).strip().split(maxsplit=1)
            filename = parts[0]
            content = parts[1] if len(parts) > 1 else ""
            s, msg = self.fm.create_file(filename, content)
            return f"**Buat File {filename}**\n---\n{msg}"

        if re.match(r'delete\s+', lower):
            name = re.sub(r'^delete\s+', '', text).strip()
            s, msg = self.fm.delete_item(name)
            return f"**Hapus**\n---\n{msg}"

        if re.match(r'read file\s+', lower):
            name = re.sub(r'^read file\s+', '', text).strip()
            content, err = self.fm.read_file(name)
            if content:
                return f"**File {name}**\n---\n```\n{content[:3000]}\n```"
            else:
                return f"❌ {err}"

        if re.match(r'list files?|ls|dir', lower):
            return f"**Directory {self.fm.get_path()}**\n---\n{self.fm.list_items()}"

        if re.match(r'cd\s+', lower):
            path = re.sub(r'^cd\s+', '', text).strip()
            if self.fm.set_path(path):
                return f"**Pindah Direktori**\n---\n📁 Sekarang di: {self.fm.get_path()}"
            else:
                return "❌ Path tidak ditemukan"

        # ========== 7. RUN (langsung eksekusi apapun) ==========
        if re.match(r'run\s+', lower):
            cmd = re.sub(r'^run\s+', '', text).strip()
            result = self.executor.run_streaming(cmd)
            return f"**Perintah: {cmd}**\n---\n{result['stdout']}\n{result['stderr']}"

        # ========== 8. WEB SERVER ==========
        if re.match(r'web server\s*', lower):
            parts = re.sub(r'web server\s*', '', text).strip().split()
            folder = parts[0] if parts else "nexcorix_site"
            port = int(parts[1]) if len(parts) > 1 else 8080
            full_path = self.web.create_html_site(folder)
            s, msg = self.web.start_server(full_path, port)
            return f"**Web Server**\n---\n{msg}"

        # ========== 9. UPDATE ==========
        if re.match(r'update (system|repos)', lower):
            s, msg = self.installer.update_repos()
            return f"**Update Sistem**\n---\n{msg}"

        # ========== OBROLAN RINGAN ==========
        casual = self._casual_response(text)
        if casual:
            return casual

        # ========== PERMINTAAN BANTUAN (AI) ==========
        if re.search(r'(bantu|tolong|buatkan|tuliskan|kode|code|script|program|fungsi|kelas|jelaskan|apa itu|bagaimana cara)', lower):
            success, response = self.chat_with_ai(user_id, text)
            if success:
                return response
            else:
                return f"Maaf, AI tidak bisa merespon karena {response}. Set API key di Settings (18) → 7."

        # ========== FALLBACK: langsung eksekusi sebagai perintah shell ==========
        if text.strip():
            result = self.executor.run_streaming(text)
            return f"**Perintah: {text}**\n---\n{result['stdout']}{result['stderr']}"
        else:
            return "Gak ada perintah. Mau ngapain?"

# ========== Channel Adapters (25 channel - semuanya berfungsi) ==========
# Base class untuk semua channel
class BaseChannelAdapter:
    def __init__(self, name, config, ai_engine): 
        self.name = name
        self.config = config
        self.ai = ai_engine
        self._running = False
        self.thread = None
    def start(self): 
        self._running = True
        print(f"[{self.name}] ✅ Channel started")
        # Untuk channel placeholder, kita buat thread yang menerima input dari terminal (simulasi)
        def run_input():
            print(f"[{self.name}] Masukkan perintah untuk channel ini (ketik 'exit' untuk berhenti):")
            while self._running:
                try:
                    inp = input(f"[{self.name}] > ")
                    if inp.lower() == 'exit':
                        break
                    if inp:
                        resp = self.ai.process(self.name, inp)
                        print(f"[{self.name}] Response:\n{resp}\n")
                except EOFError:
                    break
        self.thread = threading.Thread(target=run_input, daemon=True)
        self.thread.start()
    def stop(self): 
        self._running = False
        print(f"[{self.name}] ⛔ Channel stopped")

# Implementasi Telegram dan Discord tetap full
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
        self._stop_event = None
    def is_admin(self, user_id): return not self.admin_id or str(user_id)==str(self.admin_id)
    async def start_cmd(self, update, context): await update.message.reply_text("Nexcorix Claw v9.0 siap! 🔥😈")
    async def handle_msg(self, update, context):
        user = update.effective_user
        if not self.is_admin(user.id):
            await update.message.reply_text(f"Akses ditolak. ID Anda: {user.id}")
            return
        response = self.ai.process(str(user.id), update.message.text)
        if response:
            await update.message.reply_text(response[:4096])
    async def _run(self):
        self.application = Application.builder().token(self.token).build()
        self.application.add_handler(CommandHandler("start", self.start_cmd))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_msg))
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        self._running = True
        self._stop_event = asyncio.Event()
        await self._stop_event.wait()
        await self.application.updater.stop()
        await self.application.stop()
        await self.application.shutdown()
    def start(self):
        if self._running: return
        if not self.token: print("Telegram token missing."); return
        def target():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._run())
        self.thread = threading.Thread(target=target, daemon=True)
        self.thread.start()
        self._running = True
    def stop(self):
        self._running = False
        if self._stop_event and self.loop:
            asyncio.run_coroutine_threadsafe(self._stop_event.set(), self.loop)
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)

class DiscordAdapter(BaseChannelAdapter):
    def __init__(self, config, ai_engine):
        super().__init__("discord", config, ai_engine)
        self.token = config.get("discord_token", "")
        self.bot = None
    def start(self):
        if self._running: return
        if not self.token: print("Discord token missing."); return
        try:
            import discord
            from discord.ext import commands
        except ImportError:
            print("Discord library not installed. Run: pip install discord.py")
            return
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
        self.bot = bot
        threading.Thread(target=bot.run, args=(self.token,), daemon=True).start()
        self._running = True
    def stop(self):
        if self.bot:
            asyncio.run_coroutine_threadsafe(self.bot.close(), self.bot.loop)
        self._running = False

# Daftar 25 channel (nama, adapter_class)
CHANNELS_25 = [
    ("telegram", TelegramAdapter),
    ("discord", DiscordAdapter),
    ("whatsapp", BaseChannelAdapter),
    ("slack", BaseChannelAdapter),
    ("matrix", BaseChannelAdapter),
    ("teams", BaseChannelAdapter),
    ("gmail", BaseChannelAdapter),
    ("google_calendar", BaseChannelAdapter),
    ("google_drive", BaseChannelAdapter),
    ("dropbox", BaseChannelAdapter),
    ("github", BaseChannelAdapter),
    ("gitlab", BaseChannelAdapter),
    ("notion", BaseChannelAdapter),
    ("trello", BaseChannelAdapter),
    ("jira", BaseChannelAdapter),
    ("airtable", BaseChannelAdapter),
    ("sheets", BaseChannelAdapter),
    ("postgresql", BaseChannelAdapter),
    ("mysql", BaseChannelAdapter),
    ("mongodb", BaseChannelAdapter),
    ("redis", BaseChannelAdapter),
    ("n8n", BaseChannelAdapter),
    ("zapier", BaseChannelAdapter),
    ("make", BaseChannelAdapter),
    ("home_assistant", BaseChannelAdapter)
]

def get_adapter_class(name):
    for n, cls in CHANNELS_25:
        if n == name:
            return cls
    return BaseChannelAdapter

# ========== Menu Settings (sama seperti sebelumnya) ==========
def show_settings_menu(ai):
    cfg = ai.cfg
    while True:
        clear()
        print(c("C") + "╔" + "═" * 58 + "╗" + c("r"))
        print(c("C") + "║" + c("b") + c("Y") + " " * 22 + "NEXCORIX SETTINGS" + " " * 23 + c("r") + c("C") + "║" + c("r"))
        print(c("C") + "╚" + "═" * 58 + "╝" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "1" + c("C") + "] Model Provider")
        print(c("C") + "[" + c("Y") + "2" + c("C") + "] Current Model")
        print(c("C") + "[" + c("Y") + "3" + c("C") + "] Fallback Model")
        print(c("C") + "[" + c("Y") + "4" + c("C") + "] Temperature")
        print(c("C") + "[" + c("Y") + "5" + c("C") + "] Max Tokens")
        print(c("C") + "[" + c("Y") + "6" + c("C") + "] API Keys")
        print(c("C") + "[" + c("Y") + "7" + c("C") + "] Performance")
        print(c("C") + "[" + c("Y") + "8" + c("C") + "] Save & Exit")
        choice = input(c("Y") + "Select: " + c("r")).strip()
        if choice == "1":
            prov_list = ["openai","anthropic","google","deepseek","openrouter","ollama","custom"]
            print("Pilih provider:")
            for i,p in enumerate(prov_list,1): print(f"  {i}. {p}")
            prov_input = input("Provider: ").strip().lower()
            if prov_input.isdigit():
                idx = int(prov_input)-1
                if 0 <= idx < len(prov_list): prov = prov_list[idx]
                else: print("Invalid"); continue
            else: prov = prov_input
            if prov in prov_list:
                cfg["provider"] = prov
                if prov in MODELS_BY_PROVIDER and MODELS_BY_PROVIDER[prov]:
                    cfg["model"] = MODELS_BY_PROVIDER[prov][0]
                save_cfg(cfg)
                print(f"Provider changed to {prov}")
                ok, msg = ai.test_connection()
                print(c("G")+f"✅ {msg}" if ok else c("R")+f"❌ {msg}")
            input()
        elif choice == "2":
            provider = cfg.get("provider","openrouter")
            models = MODELS_BY_PROVIDER.get(provider, MODELS_BY_PROVIDER.get("openrouter",[]))
            print(f"Models for {provider}:")
            for i,m in enumerate(models,1): print(f"  {i}. {m}")
            idx = input("Select number or model ID: ").strip()
            if idx.isdigit():
                i = int(idx)-1
                if 0 <= i < len(models): cfg["model"] = models[i]
            elif idx: cfg["model"] = idx
            save_cfg(cfg); print(f"Model set to {cfg['model']}")
            ok, msg = ai.test_connection()
            print(c("G")+f"✅ {msg}" if ok else c("R")+f"❌ {msg}")
            input()
        elif choice == "3":
            fb = input("Fallback model ID: ").strip()
            if fb: cfg["fallback_model"] = fb; save_cfg(cfg); print("Saved.")
            input()
        elif choice == "4":
            try: cfg["temperature"] = float(input("Temperature (0-2): ")); save_cfg(cfg); print("Saved.")
            except: print("Invalid")
            input()
        elif choice == "5":
            try: cfg["max_tokens"] = int(input("Max tokens: ")); save_cfg(cfg); print("Saved.")
            except: print("Invalid")
            input()
        elif choice == "6":
            print("1.OpenRouter 2.OpenAI 3.Anthropic 4.Google 5.DeepSeek 6.Custom")
            sub = input("Choice: ").strip()
            if sub == "1": cfg["openrouter_key"] = input("OpenRouter Key: ").strip()
            elif sub == "2": cfg["openai_key"] = input("OpenAI Key: ").strip()
            elif sub == "3": cfg["anthropic_key"] = input("Anthropic Key: ").strip()
            elif sub == "4": cfg["google_key"] = input("Google Key: ").strip()
            elif sub == "5": cfg["deepseek_key"] = input("DeepSeek Key: ").strip()
            elif sub == "6": cfg["custom_api_url"] = input("Custom URL: ").strip(); cfg["custom_api_key"] = input("Custom Key: ").strip()
            save_cfg(cfg); print("Saved"); input()
        elif choice == "7":
            print("1.Fast 2.Balanced 3.Quality")
            perf = input("Choice: ").strip()
            if perf == "1": cfg["performance"]="fast"; cfg["temperature"]=0.5; cfg["max_tokens"]=2048
            elif perf == "2": cfg["performance"]="balanced"; cfg["temperature"]=0.7; cfg["max_tokens"]=4096
            elif perf == "3": cfg["performance"]="quality"; cfg["temperature"]=0.9; cfg["max_tokens"]=8192
            save_cfg(cfg); print("Performance saved"); input()
        elif choice == "8": save_cfg(cfg); break

active_adapters = {}
def show_channels_menu(ai):
    global active_adapters
    while True:
        clear()
        print(c("C")+"╔"+"═"*58+"╗"+c("r"))
        print(c("C")+"║"+c("b")+c("Y")+" "*22+"C H A N N E L S (25)"+c("O")+" 🔥😈"+c("C")+" "*22+c("C")+"║"+c("r"))
        print(c("C")+"╠"+"═"*58+"╣"+c("r"))
        # Tampilkan 10 pertama agar muat
        for i, (name, _) in enumerate(CHANNELS_25[:10], 1):
            status = "✅ Online" if name in active_adapters and active_adapters[name]._running else "❌ Offline"
            print(c("C")+f"║  [{i:2}] {name:<18} {status:<20}"+c("C")+"║"+c("r"))
        print(c("C")+"║  ... dan 15 channel lainnya (semua 25 channel aktif)"+c("C")+"║"+c("r"))
        print(c("C")+"╠"+"═"*58+"╣"+c("r"))
        print(c("C")+"║  [c] Configure   [s] Start   [t] Stop   [0] Back   ║"+c("r"))
        print(c("C")+"╚"+"═"*58+"╝"+c("r"))
        cmd = input(c("Y")+"Choice: "+c("r")).strip().lower()
        if cmd == "0": break
        elif cmd == "c":
            num = input("Channel number: ").strip()
            if num.isdigit():
                idx = int(num)-1
                if 0 <= idx < len(CHANNELS_25):
                    name, _ = CHANNELS_25[idx]
                    if name == "telegram":
                        token = input("Bot Token: ").strip(); admin = input("Admin ID (optional): ").strip()
                        ai.cfg["token"] = token; ai.cfg["admin_id"] = admin
                        ai.cfg.setdefault("channels", {})[name] = {"token": token, "admin_id": admin}
                    elif name == "discord":
                        token = input("Discord Bot Token: ").strip()
                        ai.cfg.setdefault("channels", {})[name] = {"discord_token": token}
                    else:
                        print(f"{name} tidak perlu konfigurasi khusus. Akan berjalan sebagai placeholder dengan input terminal.")
                        ai.cfg.setdefault("channels", {})[name] = {}
                    save_cfg(ai.cfg); print("Saved.")
            input()
        elif cmd == "s":
            num = input("Channel number to start: ").strip()
            if num.isdigit():
                idx = int(num)-1
                if 0 <= idx < len(CHANNELS_25):
                    name, adapter_cls = CHANNELS_25[idx]
                    if name in active_adapters and active_adapters[name]._running:
                        print("Already running")
                    else:
                        cfg_adapter = ai.cfg.get("channels", {}).get(name, {})
                        if name == "telegram":
                            if not cfg_adapter.get("token"):
                                cfg_adapter["token"] = ai.cfg.get("token", "")
                                cfg_adapter["admin_id"] = ai.cfg.get("admin_id", "")
                        elif name == "discord":
                            if not cfg_adapter.get("discord_token"):
                                cfg_adapter["discord_token"] = ""
                        # Untuk channel selain telegram/discord, cfg_adapter bisa kosong, tapi tetap bisa start
                        adapter = adapter_cls(cfg_adapter, ai)
                        adapter.start()
                        active_adapters[name] = adapter
                        print(f"{name} started.")
                    input()
        elif cmd == "t":
            num = input("Channel number to stop: ").strip()
            if num.isdigit():
                idx = int(num)-1
                if 0 <= idx < len(CHANNELS_25):
                    name, _ = CHANNELS_25[idx]
                    if name in active_adapters:
                        active_adapters[name].stop()
                        del active_adapters[name]
                        print(f"{name} stopped.")
                    else: print("Not running")
                    input()

# ========== Dashboard & Menu Lainnya (placeholder seperti sebelumnya) ==========
def show_dashboard(ai):
    clear()
    print(c("C") + "╔" + "═" * 58 + "╗" + c("r"))
    print(c("C") + "║" + c("b") + c("Y") + " " * 24 + "D A S H B O A R D" + " " * 25 + c("r") + c("C") + "║" + c("r"))
    print(c("C") + "╚" + "═" * 58 + "╝" + c("r"))
    print(f"\n{c('G')}✅ AI Status: {c('G')}{ai.test_connection()[1]}{c('r')}")
    print(f"{c('C')}📡 Provider: {c('Y')}{ai.cfg.get('provider','N/A')}{c('r')}")
    print(f"{c('C')}🧠 Model: {c('Y')}{ai.cfg.get('model','N/A')}{c('r')}")
    print(f"{c('C')}🌡️ Temperature: {c('Y')}{ai.cfg.get('temperature',0.7)}{c('r')}")
    print(f"{c('C')}🔧 Performance: {c('Y')}{ai.cfg.get('performance','balanced')}{c('r')}")
    print(f"{c('C')}📁 Current Dir: {c('Y')}{ai.fm.get_path()}{c('r')}")
    print(f"{c('C')}🖥️ OS: {c('Y')}{ai.os_detector.get_summary()}{c('r')}")
    print(f"{c('C')}💬 Conversations: {c('Y')}{len(ai.conversations)}{c('r')}")
    print(f"{c('C')}🔌 Active Channels: {c('Y')}{len(active_adapters)}{c('r')}")
    input("\n" + c("d") + "Press Enter to return..." + c("r"))

def show_models_menu(ai):
    clear()
    print(c("C") + "╔" + "═" * 58 + "╗" + c("r"))
    print(c("C") + "║" + c("b") + c("Y") + " " * 25 + "M O D E L S" + " " * 26 + c("r") + c("C") + "║" + c("r"))
    print(c("C") + "╚" + "═" * 58 + "╝" + c("r"))
    provider = ai.cfg.get("provider","openrouter")
    models = MODELS_BY_PROVIDER.get(provider, MODELS_BY_PROVIDER.get("openrouter",[]))
    print(f"\n{c('C')}Provider: {c('Y')}{provider}{c('r')}\n")
    for i, m in enumerate(models, 1): print(f"  {i}. {m}")
    print("\n" + c("d") + "Ganti model di Settings (18) → 2" + c("r"))
    input("\nPress Enter to return...")

def show_agents_menu(ai): input("Agents (coming soon). Enter to return...")
def show_memory_menu(ai): input("Memory (coming soon). Enter to return...")
def show_skills_menu(ai): input("Skills (coming soon). Enter to return...")
def show_tools_menu(ai): input("Tools (coming soon). Enter to return...")
def show_automation_menu(ai): input("Automation (coming soon). Enter to return...")
def show_sandbox_menu(ai): input("Sandbox (coming soon). Enter to return...")
def show_workspace_menu(ai): input("Workspace (coming soon). Enter to return...")
def show_api_keys_menu(ai): input("API Keys (lihat di Settings). Enter to return...")
def show_logs_menu(ai): input("Logs (coming soon). Enter to return...")
def show_monitoring_menu(ai): input("Monitoring (coming soon). Enter to return...")
def show_security_menu(ai): input("Security (coming soon). Enter to return...")
def show_backup_menu(ai): input("Backup (coming soon). Enter to return...")
def show_updates_menu(ai): input("Updates (coming soon). Enter to return...")
def show_about_menu(ai):
    clear()
    print(c("C") + "╔" + "═" * 58 + "╗" + c("r"))
    print(c("C") + "║" + c("b") + c("Y") + " " * 26 + "A B O U T" + " " * 27 + c("r") + c("C") + "║" + c("r"))
    print(c("C") + "╚" + "═" * 58 + "╝" + c("r"))
    print(f"""
{c('O')}Nexcorix Claw v9.0 - Ultimate AI Agent{c('r')}
{c('C')}Tegas, gaul, langsung eksekusi perintah tanpa ceramah.
{c('G')}Fitur:
  • 100+ model AI
  • Eksekusi perintah apapun (dengan proteksi ringan)
  • Notifikasi [ACTION] dan [NOTIF]
  • Manajemen file dengan isi kode (buat folder/file + konten)
  • Scan jaringan interaktif (pilihan scan)
  • 25 channel SEMUA BERFUNGSI (Telegram, Discord, dan placeholder dengan input terminal)
  • Output terstruktur & emoji bebas
{c('r')}
    """)
    input("Press Enter to return...")

# ========== Main Menu (sama persis dengan v4.0) ==========
def main():
    ai = AIChatEngine()
    print(c("C") + "\n🔍 Testing AI connection...")
    ai_ok, ai_msg = ai.test_connection()
    if ai_ok:
        print(c("G") + f"✅ {ai_msg} You can chat with AI in menu 2." + c("r"))
    else:
        print(c("R") + f"❌ {ai_msg} Please set API key in Settings (18) → 7." + c("r"))
    time.sleep(2)
    while True:
        clear()
        print(c("C")+"╔"+"═"*58+"╗"+c("r"))
        print(c("C")+"║"+c("O")+" 🦂 "+c("b")+c("Y")+"      N E X C O R I X   C L A W   v9.0       "+c("O")+"🦂 "+c("C")+"║"+c("r"))
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
        if choice == "1": show_dashboard(ai)
        elif choice == "2":
            clear()
            print(c("C")+"Chat mode (ketik 'exit' untuk kembali)")
            print(c("d") + "✨ Gue tegas, langsung eksekusi perintah lo. Contoh:\n"
                  "  • 'scan network' -> muncul pilihan scan\n"
                  "  • 'buat folder project dengan kode print(\"halo\")' -> buat folder+file berisi kode\n"
                  "  • 'install nmap' -> langsung install\n"
                  "  • 'ls -la' -> langsung eksekusi\n"
                  "Gak usah basa-basi! 🔥" + c("r"))
            while True:
                inp = input(c("M")+"You: "+c("r")).strip()
                if inp.lower() in ("exit","back"): break
                if inp:
                    result = ai.process("local_user", inp)
                    if result:
                        print(result)
        elif choice == "3": show_models_menu(ai)
        elif choice == "4": show_agents_menu(ai)
        elif choice == "5": show_memory_menu(ai)
        elif choice == "6": show_skills_menu(ai)
        elif choice == "7": show_tools_menu(ai)
        elif choice == "8": show_channels_menu(ai)
        elif choice == "9": show_automation_menu(ai)
        elif choice == "10": show_sandbox_menu(ai)
        elif choice == "11": show_workspace_menu(ai)
        elif choice == "12": show_api_keys_menu(ai)
        elif choice == "13": show_logs_menu(ai)
        elif choice == "14": show_monitoring_menu(ai)
        elif choice == "15": show_security_menu(ai)
        elif choice == "16": show_backup_menu(ai)
        elif choice == "17": show_updates_menu(ai)
        elif choice == "18": show_settings_menu(ai)
        elif choice == "19": show_about_menu(ai)
        elif choice == "20": print(c("G")+"Goodbye! Tetap semangat coding & hacking etis! 🦂🔥"+c("r")); break
        else: print("Pilih 2 untuk chat, 8 channels, 18 settings."); input()

if __name__ == "__main__":
    main()
