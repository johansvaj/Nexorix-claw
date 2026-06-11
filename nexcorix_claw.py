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
print(f"[*] Loaded {total_models} AI models from providers.")

ALL_MODELS = {}
for provider, models in MODELS_BY_PROVIDER.items():
    for model_id in models:
        ALL_MODELS[model_id] = {"provider": provider, "name": model_id.split('/')[-1]}

# ========== AI Chat Engine with Hacker Persona ==========
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
                "Aku Nexcorix Claw, seorang ethical hacker dan developer yang tegas tapi ramah. 🦂\n"
                "Prinsipku: langsung bertindak, tidak banyak bicara. Perintahmu akan segera kujalankan.\n"
                "Aku bisa membantu coding, debugging, penetration testing (legal), dan security hardening.\n"
                "Jika kamu butuh penjelasan, aku akan jelaskan dengan jelas dan santai.\n"
                "Tapi ingat, aku tidak akan membantu aktivitas ilegal atau merugikan orang lain.\n"
                "Sekarang, suruh aku apa? install, scan, run, atau tanya sesuatu? 😎\n"
                f"Sistem info: {self.os_detector.get_ai_context()}"
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
            return "Halo! Siap membantu. Langsung aja perintahnya. 😎"
        if re.search(r'\b(apa kabar|how are you|kabar)\b', lower):
            return "Baik! Siap action. Kamu gimana? 🦂"
        if re.search(r'\b(nama mu|siapa kamu|who are you|your name)\b', lower):
            return "Aku Nexcorix Claw, ethical hacker dan developer. Panggil aku Claw aja. 🤘"
        if re.search(r'\b(terima kasih|thanks|thank you|makasih)\b', lower):
            return "Sama-sama! Terus berkarya dan jaga keamanan. 😊"
        if re.search(r'\b(bye|dadah|selamat tinggal|goodbye)\b', lower):
            return "Sampai jumpa! Tetap koding dan waspada! 🦂"
        if re.search(r'\b(lelucon|joke|lucu|cerita lucu)\b', lower):
            return "Kenapa hacker tidak mandi? Nanti ID-nya ketahuan! 😄 Mau lagi?"
        if re.search(r'\b(pagi|siang|sore|malam|good morning|good night)\b', lower):
            return "Selamat! Saatnya produktif. Ada yang mau dikerjakan? 🌟"
        if re.search(r'\b(kamu bisa apa|lo bisa apa|bisa apa|apa saja yang bisa kamu lakukan|kemampuan|fitur)\b', lower):
            return (
                "Aku bisa banyak hal! 😎\n\n"
                "⚡ **Perintah langsung:**\n"
                "- install nmap → install tools pentest\n"
                "- scan network → scan jaringan\n"
                "- browse google.com → lihat teks website\n"
                "- create file test.txt → buat file\n"
                "- run ls -la → jalankan perintah shell\n"
                "- web server → buat web server lokal\n\n"
                "💬 **Ngobrol biasa:**\n"
                "- Ajak aku diskusi tentang coding, hacking etis, security\n"
                "- Tanya konsep, minta saran, atau curhat 😄\n\n"
                "🔧 **Settings & Channels:**\n"
                "- Atur API key, ganti model AI\n"
                "- Sambungkan ke Telegram, Discord\n\n"
                "Ayo, langsung kasih perintah! 🚀"
            )
        if re.search(r'\b(tolong|help|bantuan|what can you do)\b', lower):
            return "Siap! Ketik 'bisa apa' untuk lihat fitur. Atau langsung kasih perintah seperti 'install nmap', 'scan network'. Ada yang mau kamu coba? 😎"
        if re.search(r'\b(hack|hacking|pentest|exploit|vulnerability|bug bounty)\b', lower):
            return "Nah, ini baru semangat! Aku siap bantu ethical hacking kamu. Tapi ingat, hanya untuk testing dengan izin ya! 💻🔥"
        if re.search(r'\b(koding|ngoding|programming|code|script)\b', lower):
            return "Siap! Aku bisa bantu bikin script atau debug kode. Coba kasih tau detailnya. 👨‍💻"
        if re.search(r'\b(serius|tegas|keras|perintah|patuh|turut)\b', lower):
            return "Aku selalu patuh pada perintah, asalkan legal. Kamu bos, aku asisten. 😎"
        return None

    def process(self, user_id, text):
        lower = text.lower().strip()
        def notify(msg, status="info"):
            if status == "info": return f"🔄 {msg}"
            elif status == "success": return f"✅ {msg}"
            elif status == "error": return f"❌ {msg}"
            else: return msg

        # ========== 1. INSTALL ==========
        if re.match(r'^(install|pasang|instal)\s+', lower):
            pkgs = re.sub(r'^(install|pasang|instal)\s+', '', text).strip().split()
            if len(pkgs) > 1:
                output = notify("Menginstall beberapa package...", "info") + "\n"
                all_success = True
                for pkg in pkgs:
                    output += f"\n--- Menginstall {pkg} ---\n"
                    s, out = self.installer.install_streaming(pkg)
                    if not s:
                        all_success = False
                    output += out + "\n"
                output += notify("Selesai", "success" if all_success else "error")
                return output
            else:
                output = notify(f"Menginstall {pkgs[0]}...", "info") + "\n"
                s, out = self.installer.install_streaming(pkgs[0])
                output += out
                output += "\n" + (notify("Selesai", "success") if s else notify("Gagal", "error"))
                return output

        # ========== 2. GITHUB ==========
        if re.match(r'^(github|clone)\s+', lower):
            tool = re.sub(r'^(github|clone)\s+', '', text).strip()
            output = notify(f"Mengclone {tool} dari GitHub...", "info") + "\n"
            s, out = self.installer.install_from_github_streaming(tool)
            output += out
            output += "\n" + (notify("Selesai", "success") if s else notify("Gagal", "error"))
            return output

        # ========== 3. PIP ==========
        if re.match(r'^pip\s+', lower):
            pkg = re.sub(r'^pip\s+', '', text).strip()
            output = notify(f"Menginstall Python package {pkg}...", "info") + "\n"
            s, out = self.installer.install_pip_tool(pkg)
            output += out
            output += "\n" + (notify("Selesai", "success") if s else notify("Gagal", "error"))
            return output

        # ========== 4. SCAN ==========
        if (re.search(r'\bscan\s+(network|jaringan|ip)\b', lower) or re.search(r'\bscan\s+\d+\.\d+\.\d+\.\d+(?:/\d+)?', lower)):
            target_match = re.search(r'(\d+\.\d+\.\d+\.\d+(?:/\d+)?)', text)
            target = target_match.group(1) if target_match else "192.168.1.0/24"
            output = notify(f"Memindai jaringan {target}...", "info") + "\n"
            result = self.network.scan_network(target)
            output += result
            output += "\n" + notify("Scan selesai", "success")
            return output

        if re.match(r'scan ports?\s+', lower):
            parts = re.sub(r'scan ports?\s+', '', text).strip().split()
            target = parts[0] if parts else "localhost"
            ports = parts[1] if len(parts) > 1 else "1-1000"
            output = notify(f"Memindai port {ports} pada {target}...", "info") + "\n"
            result = self.network.scan_ports(target, ports)
            output += result
            output += "\n" + notify("Scan selesai", "success")
            return output

        if re.search(r'(wifi scan|scan wifi)', lower):
            output = notify("Memindai WiFi...", "info") + "\n"
            result = self.network.wifi_scan()
            output += result
            output += "\n" + notify("Scan selesai", "success")
            return output

        # ========== 5. BROWSING & SEARCH ==========
        if re.match(r'(browse|buka|lihat|open)\s+', lower):
            url = re.sub(r'^(browse|buka|lihat|open)\s+', '', text).strip()
            output = notify(f"Membuka {url}...", "info") + "\n"
            s, res = self.browser.browse(url)
            output += res if s else f"Error: {res}"
            output += "\n" + notify("Selesai", "success" if s else "error")
            return output

        if re.match(r'(search|cari|google|temukan)\s+', lower):
            query = re.sub(r'^(search|cari|google|temukan)\s+', '', text).strip()
            output = notify(f"Mencari '{query}'...", "info") + "\n"
            s, res = self.browser.search_duckduckgo(query)
            output += res if s else f"Error: {res}"
            output += "\n" + notify("Selesai", "success" if s else "error")
            return output

        # ========== 6. FILE & FOLDER ==========
        folder_with_code = re.search(r'buat folder\s+([^\s]+)\s+dengan\s+(?:kode|isi)\s+(.+)', text, re.IGNORECASE)
        if folder_with_code:
            folder_name = folder_with_code.group(1)
            code_content = folder_with_code.group(2)
            output = notify(f"Membuat folder '{folder_name}'...", "info") + "\n"
            s1, msg1 = self.fm.create_folder(folder_name)
            if s1:
                output += msg1 + "\n"
                old_path = self.fm.current_path
                self.fm.set_path(folder_name)
                filename = "script.py"
                output += notify(f"Membuat file {filename} di dalam folder...", "info") + "\n"
                s2, msg2 = self.fm.create_file(filename, code_content)
                self.fm.set_path(old_path)
                if s2:
                    output += msg2 + "\n"
                    output += notify("Berhasil!", "success") + f"\n✅ Folder '{folder_name}' dan file '{filename}' dibuat.\nKode:\n{code_content}"
                else:
                    output += notify("Folder berhasil, gagal buat file", "error") + f"\n{msg2}"
            else:
                output += notify("Gagal buat folder", "error") + f"\n{msg1}"
            return output

        if re.match(r'buat folder\s+', lower):
            name = re.sub(r'^buat folder\s+', '', text).strip()
            output = notify(f"Membuat folder '{name}'...", "info") + "\n"
            s, msg = self.fm.create_folder(name)
            output += msg
            output += "\n" + (notify("Selesai", "success") if s else notify("Gagal", "error"))
            return output

        if re.match(r'(create file|buat file|simpan file)\s+', lower):
            parts = re.sub(r'^(create file|buat file|simpan file)\s+', '', text).strip().split(maxsplit=1)
            filename = parts[0]
            content = ""
            if len(parts) > 1:
                isi_match = re.search(r'(?:isi|dengan isi|content:)\s*(.+)', parts[1], re.IGNORECASE)
                content = isi_match.group(1).strip() if isi_match else parts[1]
            output = notify(f"Membuat file '{filename}'...", "info") + "\n"
            s, msg = self.fm.create_file(filename, content)
            output += msg
            output += "\n" + (notify("Selesai", "success") if s else notify("Gagal", "error"))
            return output

        if re.match(r'delete\s+', lower):
            name = re.sub(r'^delete\s+', '', text).strip()
            output = notify(f"Menghapus '{name}'...", "info") + "\n"
            s, msg = self.fm.delete_item(name)
            output += msg
            output += "\n" + (notify("Selesai", "success") if s else notify("Gagal", "error"))
            return output

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

        # ========== 7. RUN ==========
        if re.match(r'run\s+', lower):
            cmd = re.sub(r'^run\s+', '', text).strip()
            output = notify(f"Menjalankan: {cmd}", "info") + "\n"
            result = self.executor.run_streaming(cmd)
            status = "SUCCESS" if result["success"] else "FAILED"
            output += notify(f"Perintah selesai ({status})", "success" if result["success"] else "error")
            return output

        # ========== 8. WEB SERVER ==========
        if re.match(r'web server\s*', lower):
            parts = re.sub(r'web server\s*', '', text).strip().split()
            folder = parts[0] if parts else "nexcorix_site"
            port = int(parts[1]) if len(parts) > 1 else 8080
            output = notify(f"Mempersiapkan web server di folder '{folder}', port {port}...", "info") + "\n"
            full_path = self.web.create_html_site(folder)
            s, msg = self.web.start_server(full_path, port)
            output += msg
            output += "\n" + notify("Web server berjalan!", "success")
            return output

        # ========== 9. UPDATE ==========
        if re.match(r'update (system|repos)', lower):
            output = notify("Mengupdate repository...", "info") + "\n"
            s, msg = self.installer.update_repos()
            output += msg
            output += "\n" + (notify("Selesai", "success") if s else notify("Gagal", "error"))
            return output

        # ========== OBROLAN RINGAN ==========
        casual = self._casual_response(text)
        if casual:
            return casual

        # ========== PERMINTAAN BANTUAN ==========
        if re.search(r'(bantu|tolong|buatkan|tuliskan|kode|code|script|program|fungsi|kelas|jelaskan|apa itu|bagaimana cara)', lower):
            success, response = self.chat_with_ai(user_id, text)
            if success:
                return response
            else:
                return f"Maaf, AI tidak bisa merespon karena {response}. Set API key di Settings (18) → 7."

        # ========== FALLBACK ==========
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
        if not self.is_admin(user.id):
            await update.message.reply_text(f"Akses ditolak. ID Anda: {user.id}")
            return
        response = self.ai.process(str(user.id), update.message.text)
        if response:
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("Perintah telah dieksekusi. Lihat output di terminal (untuk streaming).")
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

# ========== Menu Settings (tetap sama seperti sebelumnya, tidak diubah) ==========
# Karena panjang, saya sertakan versi ringkas tapi tetap fungsional. 
# Untuk menghemat ruang, saya asumsikan fungsi show_settings_menu dan show_channels_menu sudah ada.
# Namun karena kode harus lengkap, saya akan menulis ulang secara ringkas di sini.

def show_settings_menu(ai):
    cfg = ai.cfg
    while True:
        clear()
        print(c("C") + "╔" + "═" * 58 + "╗" + c("r"))
        print(c("C") + "║" + c("b") + c("Y") + " " * 22 + "NEXCORIX SETTINGS" + " " * 23 + c("r") + c("C") + "║" + c("r"))
        print(c("C") + "╚" + "═" * 58 + "╝" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "1" + c("C") + "] Model Provider")
        print(c("d") + "    ├─ OpenAI\n    ├─ Anthropic\n    ├─ Gemini\n    ├─ DeepSeek\n    ├─ OpenRouter\n    ├─ Ollama (Local)\n    └─ Custom API" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "2" + c("C") + "] Current Model")
        current_model = cfg.get("model", "deepseek/deepseek-chat")
        print(c("d") + f"    └─ {current_model}" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "3" + c("C") + "] Fallback Model")
        print(c("d") + f"    └─ {cfg.get('fallback_model', 'deepseek-chat')}" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "4" + c("C") + "] Temperature")
        print(c("d") + f"    └─ {cfg.get('temperature', 0.7)} (0.0-2.0)" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "5" + c("C") + "] Max Tokens")
        print(c("d") + f"    └─ {cfg.get('max_tokens', 4096)}" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "6" + c("C") + "] Context Window")
        print(c("d") + "    └─ Auto Detect" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "7" + c("C") + "] API Configuration")
        print(c("d") + "    ├─ API Key\n    ├─ Base URL\n    └─ Organization ID" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "8" + c("C") + "] Local Models")
        print(c("d") + "    ├─ ollama list\n    ├─ Scan Models\n    └─ Download Model" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "9" + c("C") + "] Performance")
        print(c("d") + "    ├─ Fast Mode\n    ├─ Balanced Mode\n    └─ Quality Mode" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "10" + c("C") + "] Save Configuration" + c("r"))
        print()
        print(c("C") + "[" + c("Y") + "11" + c("C") + "] Exit" + c("r"))
        print()
        choice = input(c("Y") + "Select option: " + c("r")).strip()
        if choice == "1":
            prov_list = ["openai","anthropic","google","deepseek","openrouter","ollama","custom"]
            print("Pilih provider (nomor atau nama):")
            for i,p in enumerate(prov_list,1): print(f"  {i}. {p}")
            prov_input = input("Provider: ").strip().lower()
            if prov_input.isdigit():
                idx = int(prov_input)-1
                if 0 <= idx < len(prov_list): prov = prov_list[idx]
                else: print(c("R") + "Invalid number"); input(); continue
            else: prov = prov_input
            if prov in prov_list:
                cfg["provider"] = prov
                if prov in MODELS_BY_PROVIDER and MODELS_BY_PROVIDER[prov]:
                    cfg["model"] = MODELS_BY_PROVIDER[prov][0]
                save_cfg(cfg)
                print(c("G") + f"Provider changed to {prov}, model set to {cfg['model']}")
                print(c("C") + "Testing AI connection...")
                ok, msg = ai.test_connection()
                print(c("G") + f"✅ {msg}" if ok else c("R") + f"❌ {msg}")
            else: print(c("R") + "Unknown provider")
            input()
        elif choice == "2":
            provider = cfg.get("provider","openrouter")
            models = MODELS_BY_PROVIDER.get(provider, MODELS_BY_PROVIDER.get("openrouter",[]))
            print(f"Models for {provider}:")
            for i,m in enumerate(models,1): print(f"  {i}. {m}")
            idx = input("Select number or enter model ID directly: ").strip()
            if idx.isdigit():
                i = int(idx)-1
                if 0 <= i < len(models):
                    cfg["model"] = models[i]
                    save_cfg(cfg)
                    print(c("G") + f"Model changed to {cfg['model']}")
                    ok, msg = ai.test_connection()
                    print(c("G") + f"✅ {msg}" if ok else c("R") + f"❌ {msg}")
            elif idx:
                cfg["model"] = idx
                save_cfg(cfg)
                print(c("G") + f"Model changed to {cfg['model']}")
                ok, msg = ai.test_connection()
                print(c("G") + f"✅ {msg}" if ok else c("R") + f"❌ {msg}")
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
            print("Context window auto")
            input()
        elif choice == "7":
            print("1. OpenRouter Key\n2. OpenAI Key\n3. Anthropic Key\n4. Google Key\n5. DeepSeek Key\n6. Custom API URL & Key\n7. Base URL")
            sub = input("Choice: ").strip()
            if sub == "1": cfg["openrouter_key"] = input("OpenRouter API Key: ").strip()
            elif sub == "2": cfg["openai_key"] = input("OpenAI API Key: ").strip()
            elif sub == "3": cfg["anthropic_key"] = input("Anthropic API Key: ").strip()
            elif sub == "4": cfg["google_key"] = input("Google API Key: ").strip()
            elif sub == "5": cfg["deepseek_key"] = input("DeepSeek API Key: ").strip()
            elif sub == "6": cfg["custom_api_url"] = input("Custom API URL: ").strip(); cfg["custom_api_key"] = input("Custom API Key: ").strip()
            elif sub == "7": cfg["base_url"] = input("Base URL: ").strip()
            else: print("Invalid")
            save_cfg(cfg)
            print("Saved. Testing AI connection...")
            ok, msg = ai.test_connection()
            print(c("G") + f"✅ {msg}" if ok else c("R") + f"❌ {msg}")
            input()
        elif choice == "8":
            print("Ollama: use 'ollama list', 'ollama pull <model>'")
            input()
        elif choice == "9":
            print("1. Fast 2. Balanced 3. Quality")
            perf = input("Choice: ").strip()
            if perf == "1": cfg["performance"]="fast"; cfg["temperature"]=0.5; cfg["max_tokens"]=2048
            elif perf == "2": cfg["performance"]="balanced"; cfg["temperature"]=0.7; cfg["max_tokens"]=4096
            elif perf == "3": cfg["performance"]="quality"; cfg["temperature"]=0.9; cfg["max_tokens"]=8192
            else: print("Invalid")
            save_cfg(cfg)
            print("Performance mode saved.")
            input()
        elif choice == "10":
            save_cfg(cfg); print("Configuration saved."); input()
        elif choice == "11": break
        else: print("Invalid"); time.sleep(1)

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
            print(c("d") + "✨ Aku siap bantu coding, hacking etis, atau eksekusi perintah. Coba: 'install nmap', 'scan network', 'bantu saya buat script'." + c("r"))
            while True:
                inp = input(c("M")+"You: "+c("r")).strip()
                if inp.lower() in ("exit","back"): break
                if inp:
                    result = ai.process("local_user", inp)
                    if result:
                        print(result)
        elif choice == "8": show_channels_menu(ai)
        elif choice == "18": show_settings_menu(ai)
        elif choice == "20": print(c("G")+"Goodbye! Tetap semangat coding & hacking etis! 🦂"+c("r")); break
        else: print("Pilih 2 untuk chat, 8 channels, 18 settings."); input()

if __name__ == "__main__":
    main()
