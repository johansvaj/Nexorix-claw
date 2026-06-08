�
￼ 

�
￼ ￼ ￼ ￼ ￼ 

�
￼ 

🚀 Quick Start
# Clone repository
git clone https://github.com/user/nexcorix-claw.git
cd nexcorix-claw

# Install & run
chmod +x run.sh
./run.sh
📋 25+ Channel Integrations
No
Channel
Status
Credentials Diperlukan
Cara Penggunaan
1
Telegram
✅
Bot Token (dari @BotFather), Admin ID (opsional)
Kirim pesan ke bot, AI balas
2
Discord
✅
Discord Bot Token
Bot merespon di channel yang diundang
3
WhatsApp
🚧
-
Coming soon
4
Slack
✅
Slack Bot Token (OAuth)
Bot membalas mention
5
Matrix
✅
Homeserver URL + Access Token
Kirim pesan ke room
6
Microsoft Teams
✅
Webhook URL atau Bot Framework
Kirim pesan ke channel
7
Gmail
✅
OAuth 2.0 (credentials.json)
Baca/kirim email via command
8
Google Calendar
✅
OAuth 2.0
Buat/edit event
9
Google Drive
✅
OAuth 2.0
Upload/download file
10
Dropbox
✅
Dropbox Access Token
Manajemen file
11
GitHub
✅
GitHub Personal Access Token
Akses repo, issue, PR
12
GitLab
✅
Private Token + URL
Akses project
13
Notion
✅
Integration Token
Baca/tulis halaman
14
Trello
✅
API Key + Token
Manajemen board/card
15
Jira
✅
Server URL + Email + API Token
Akses issue
16
Airtable
✅
Personal Access Token
Baca/tulis base
17
Google Sheets
✅
OAuth 2.0
Baca/tulis spreadsheet
18
PostgreSQL
✅
Host, port, user, pass, db
Query database
19
MySQL
✅
Host, port, user, pass, db
Query database
20
MongoDB
✅
MongoDB URI
Query NoSQL
21
Redis
✅
Host, port, password
Perintah Redis
22
Webhook
✅
Port (default 5000)
Terima POST, balas AI
23
MQTT
✅
Broker, port
Subscribe/topik, aksi IoT
24
REST API
✅
Endpoint custom (gunakan webhook)
-
25
MCP Servers
✅
Model Context Protocol
Implementasi kustom
🛠️ Instalasi Detail
Prerequisites
Python 3.9+
pip
Git
Linux/Mac/Termux/WSL
Step-by-step
# 1. Clone repository
git clone https://github.com/user/nexcorix-claw.git
cd nexcorix-claw

# 2. Buat virtual environment (opsional tapi direkomendasikan)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables / config
# Pertama kali run, script akan membuat ~/.nexcorix_config.json
# Atau edit langsung:
cp .env.example .env
# Edit .env sesuai channel yang mau diaktifkan

# 5. Jalankan
python3 nexcorix_claw.py
# atau pakai run.sh
chmod +x run.sh
./run.sh
🔧 Konfigurasi ~/.nexcorix_config.json
File config otomatis dibuat saat pertama kali run. Contoh isi:
{
  "provider": "openrouter",
  "model": "openai/gpt-4o",
  "fallback_model": "deepseek/deepseek-chat",
  "openrouter_key": "sk-or-v1-xxxxxxxx",
  "openai_key": "",
  "anthropic_key": "",
  "google_key": "",
  "deepseek_key": "",
  "temperature": 0.7,
  "max_tokens": 4096,
  "context_window": "auto",
  "performance": "balanced",
  "admin_id": "123456789",
  "token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
  "base_url": "https://openrouter.ai/api/v1",
  "ollama_url": "http://localhost:11434",
  "custom_api_url": "",
  "custom_api_key": "",
  "chat_history": {},
  "channels": {}
}
🎮 Cara Menggunakan
Mode Chat (Menu 2)
You: install nmap
Nexcorix: OK nmap via apt
...

You: scan network
Nexcorix: [hasil scan nmap]

You: create file test.py print("hello")
Nexcorix: File 'test.py' created!

You: browse google.com
Nexcorix: [konten halaman]

You: search "python tutorial"
Nexcorix: [hasil DuckDuckGo]

You: run ls -la
Nexcorix: [output command]

You: web server mysite 8080
Nexcorix: Web Server Started! URL: http://192.168.1.5:8080
Perintah Langsung yang Didukung
Perintah
Deskripsi
install <package>
Install via package manager
github <tool>
Install dari GitHub
pip <package>
Install via pip3
scan network [target]
Scan jaringan (nmap/arp-scan)
scan ports <target> [ports]
Scan port
wifi scan
Scan WiFi
browse <url>
Buka website
search <query>
Cari DuckDuckGo
create file <name> [content]
Buat file
create folder <name>
Buat folder
delete <name>
Hapus file/folder
read file <name>
Baca file
list files
List direktori
cd <path>
Ganti direktori
run <command>
Jalankan command
web server [folder] [port]
Start HTTP server
update system
Update package repos
🤖 100+ AI Models (15+ Providers)
Provider
Models
OpenAI
gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-4, gpt-3.5-turbo, o1-preview, o1-mini, o3-mini
Anthropic
claude-3.5-sonnet, claude-3-opus, claude-3-sonnet, claude-3-haiku
Google
gemini-1.5-pro, gemini-1.5-flash, gemini-1.0-pro, gemma-2-9b, gemma-2-27b
DeepSeek
deepseek-chat, deepseek-coder
Meta
llama-3.1-405b, llama-3.1-70b, llama-3.1-8b, llama-3-70b, llama-3-8b
Mistral
mistral-large, mistral-medium, mixtral-8x7b, mistral-7b, codestral-22b, mathstral-7b
Qwen
qwen-2.5-72b, qwen-2.5-32b, qwen-2.5-14b, qwen-2-7b
xAI
grok-2, grok-1, grok-beta
Cohere
command-r-plus, command-r
AI21
jamba-1.5
Databricks
dbrx-instruct
Upstage
solar-10.7b
NVIDIA
nemotron-4-340b
Perplexity
pplx-7b-online
Moonshot
kimi-v1
🖥️ Menu Utama
╔══════════════════════════════════════════════════════════╗
║ 🦂       N E X C O R I X   C L A W   v4.0       🦂 ║
╠══════════════════════════════════════════════════════════╣
║  Integrations                                            ║
║    ├─ Discord      ├─ Telegram    ├─ WhatsApp         ║
║    ├─ Slack        ├─ Matrix      ├─ Microsoft Teams  ║
║    ├─ Gmail        ├─ Google Calendar                  ║
║    ├─ Google Drive ├─ Dropbox     ├─ GitHub            ║
║    ├─ GitLab       ├─ Notion      ├─ Trello          ║
║    ├─ Jira         ├─ Airtable    ├─ Google Sheets    ║
║    ├─ PostgreSQL   ├─ MySQL       ├─ MongoDB          ║
║    ├─ Redis        ├─ n8n         ├─ Zapier           ║
║    ├─ Make         ├─ Home Assistant                   ║
║    ├─ MQTT         ├─ Webhook     ├─ REST API        ║
║    └─ MCP Servers  🚧 Soon                             ║
╠══════════════════════════════════════════════════════════╣
║        N E X C O R I X   M E N U                       ║
╠══════════════════════════════════════════════════════════╣
║  [1] Dashboard        [11] Workspace                   ║
║  [2] Chat             [12] API Keys                    ║
║  [3] Models           [13] Logs                        ║
║  [4] Agents           [14] Monitoring                  ║
║  [5] Memory           [15] Security                    ║
║  [6] Skills           [16] Backup                      ║
║  [7] Tools            [17] Updates                     ║
║  [8] Channels         [18] Settings                    ║
║  [9] Automation       [19] About                       ║
║  [10] Sandbox         [20] Exit                        ║
╚══════════════════════════════════════════════════════════╝
📁 Struktur Project
nexcorix-claw/
├── 📄 nexcorix_claw.py      # Main script
├── 📄 run.sh                # Auto-install & run
├── 📄 requirements.txt      # Dependencies
├── 📄 .env.example          # Environment template
├── 📄 README.md             # This file
├── 📁 channels/             # Channel adapters (opsional)
│   ├── telegram.py
│   ├── discord.py
│   └── ...
├── 📁 integrations/         # API integrations
│   ├── google/
│   ├── database/
│   └── ...
└── 📁 assets/               # Logo, GIF, media
    └── logo.gif
⚡ Features
✅ Auto-Install Libraries — pip install otomatis saat import gagal
✅ 100+ AI Models — 15+ provider (OpenAI, Anthropic, Google, DeepSeek, dll)
✅ 25+ Channel Integrations — Telegram, Discord, Slack, Matrix, dll
✅ System Executor — Jalankan command shell dengan timeout
✅ Advanced Installer — Install tools via apt/yum/pacman/brew/pip/GitHub
✅ File Manager — Create, read, delete, list files & folders
✅ Network Scanner — nmap, arp-scan, port scan, wifi scan
✅ Local Browser — Browse website & DuckDuckGo search tanpa browser
✅ Web Server — Start HTTP server instan
✅ OS Detector — Auto-detect Linux distro, WSL, Termux, Docker
✅ Multi-Provider Fallback — Ganti model otomatis jika gagal
✅ Chat History — Simpan percakapan di config
✅ Admin Security — Telegram admin ID filter
✅ Interactive Menu — TUI dengan warna & box drawing
📝 Catatan Penting
Status
Arti
✅
Sudah tersedia & stabil
🚧
Dalam pengembangan / placeholder
WhatsApp: Memerlukan konfigurasi tambahan (pywhatsapp)
Google services: Memerlukan OAuth 2.0 setup (credentials.json)
Database adapters: Memerlukan koneksi valid, auto-install library
MCP Servers: Implementasi kustom sesuai kebutuhan
🔒 Security
Semua command dijalankan dengan timeout (default 300s)
Admin ID filter untuk Telegram
Sandbox mode — perintah berjalan di home directory
API keys disimpan di ~/.nexcorix_config.json (chmod 600 direkomendasikan)
🐛 Troubleshooting
# Permission denied
chmod +x run.sh
chmod 600 ~/.nexcorix_config.json

# Module not found
pip install -r requirements.txt
# atau biarkan auto-install saat run

# Telegram bot tidak merespon
# Pastikan token valid dan bot tidak di-block

# API key invalid
# Cek di Settings → Test AI Connections (menu 12)
📜 License
MIT License — bebas modifikasi & distribusi.
�
￼ 

�
￼ 

�
Made with ❤️ by Nexcorix Team
�
￼ 

�
￼ ￼ ￼ ￼ ￼ 

�
￼ 

🚀 Quick Start
# Clone repository
git clone https://github.com/user/nexcorix-claw.git
cd nexcorix-claw

# Install & run
chmod +x run.sh
./run.sh
📋 25+ Channel Integrations
No
Channel
Status
Credentials Diperlukan
Cara Penggunaan
1
Telegram
✅
Bot Token (dari @BotFather), Admin ID (opsional)
Kirim pesan ke bot, AI balas
2
Discord
✅
Discord Bot Token
Bot merespon di channel yang diundang
3
WhatsApp
🚧
-
Coming soon
4
Slack
✅
Slack Bot Token (OAuth)
Bot membalas mention
5
Matrix
✅
Homeserver URL + Access Token
Kirim pesan ke room
6
Microsoft Teams
✅
Webhook URL atau Bot Framework
Kirim pesan ke channel
7
Gmail
✅
OAuth 2.0 (credentials.json)
Baca/kirim email via command
8
Google Calendar
✅
OAuth 2.0
Buat/edit event
9
Google Drive
✅
OAuth 2.0
Upload/download file
10
Dropbox
✅
Dropbox Access Token
Manajemen file
11
GitHub
✅
GitHub Personal Access Token
Akses repo, issue, PR
12
GitLab
✅
Private Token + URL
Akses project
13
Notion
✅
Integration Token
Baca/tulis halaman
14
Trello
✅
API Key + Token
Manajemen board/card
15
Jira
✅
Server URL + Email + API Token
Akses issue
16
Airtable
✅
Personal Access Token
Baca/tulis base
17
Google Sheets
✅
OAuth 2.0
Baca/tulis spreadsheet
18
PostgreSQL
✅
Host, port, user, pass, db
Query database
19
MySQL
✅
Host, port, user, pass, db
Query database
20
MongoDB
✅
MongoDB URI
Query NoSQL
21
Redis
✅
Host, port, password
Perintah Redis
22
Webhook
✅
Port (default 5000)
Terima POST, balas AI
23
MQTT
✅
Broker, port
Subscribe/topik, aksi IoT
24
REST API
✅
Endpoint custom (gunakan webhook)
-
25
MCP Servers
✅
Model Context Protocol
Implementasi kustom
🛠️ Instalasi Detail
Prerequisites
Python 3.9+
pip
Git
Linux/Mac/Termux/WSL
Step-by-step
# 1. Clone repository
git clone https://github.com/user/nexcorix-claw.git
cd nexcorix-claw

# 2. Buat virtual environment (opsional tapi direkomendasikan)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables / config
# Pertama kali run, script akan membuat ~/.nexcorix_config.json
# Atau edit langsung:
cp .env.example .env
# Edit .env sesuai channel yang mau diaktifkan

# 5. Jalankan
python3 nexcorix_claw.py
# atau pakai run.sh
chmod +x run.sh
./run.sh
🔧 Konfigurasi ~/.nexcorix_config.json
File config otomatis dibuat saat pertama kali run. Contoh isi:
{
  "provider": "openrouter",
  "model": "openai/gpt-4o",
  "fallback_model": "deepseek/deepseek-chat",
  "openrouter_key": "sk-or-v1-xxxxxxxx",
  "openai_key": "",
  "anthropic_key": "",
  "google_key": "",
  "deepseek_key": "",
  "temperature": 0.7,
  "max_tokens": 4096,
  "context_window": "auto",
  "performance": "balanced",
  "admin_id": "123456789",
  "token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
  "base_url": "https://openrouter.ai/api/v1",
  "ollama_url": "http://localhost:11434",
  "custom_api_url": "",
  "custom_api_key": "",
  "chat_history": {},
  "channels": {}
}
🎮 Cara Menggunakan
Mode Chat (Menu 2)
You: install nmap
Nexcorix: OK nmap via apt
...

You: scan network
Nexcorix: [hasil scan nmap]

You: create file test.py print("hello")
Nexcorix: File 'test.py' created!

You: browse google.com
Nexcorix: [konten halaman]

You: search "python tutorial"
Nexcorix: [hasil DuckDuckGo]

You: run ls -la
Nexcorix: [output command]

You: web server mysite 8080
Nexcorix: Web Server Started! URL: http://192.168.1.5:8080
Perintah Langsung yang Didukung
Perintah
Deskripsi
install <package>
Install via package manager
github <tool>
Install dari GitHub
pip <package>
Install via pip3
scan network [target]
Scan jaringan (nmap/arp-scan)
scan ports <target> [ports]
Scan port
wifi scan
Scan WiFi
browse <url>
Buka website
search <query>
Cari DuckDuckGo
create file <name> [content]
Buat file
create folder <name>
Buat folder
delete <name>
Hapus file/folder
read file <name>
Baca file
list files
List direktori
cd <path>
Ganti direktori
run <command>
Jalankan command
web server [folder] [port]
Start HTTP server
update system
Update package repos
🤖 100+ AI Models (15+ Providers)
Provider
Models
OpenAI
gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-4, gpt-3.5-turbo, o1-preview, o1-mini, o3-mini
Anthropic
claude-3.5-sonnet, claude-3-opus, claude-3-sonnet, claude-3-haiku
Google
gemini-1.5-pro, gemini-1.5-flash, gemini-1.0-pro, gemma-2-9b, gemma-2-27b
DeepSeek
deepseek-chat, deepseek-coder
Meta
llama-3.1-405b, llama-3.1-70b, llama-3.1-8b, llama-3-70b, llama-3-8b
Mistral
mistral-large, mistral-medium, mixtral-8x7b, mistral-7b, codestral-22b, mathstral-7b
Qwen
qwen-2.5-72b, qwen-2.5-32b, qwen-2.5-14b, qwen-2-7b
xAI
grok-2, grok-1, grok-beta
Cohere
command-r-plus, command-r
AI21
jamba-1.5
Databricks
dbrx-instruct
Upstage
solar-10.7b
NVIDIA
nemotron-4-340b
Perplexity
pplx-7b-online
Moonshot
kimi-v1
🖥️ Menu Utama
╔══════════════════════════════════════════════════════════╗
║ 🦂       N E X C O R I X   C L A W   v4.0       🦂 ║
╠══════════════════════════════════════════════════════════╣
║  Integrations                                            ║
║    ├─ Discord      ├─ Telegram    ├─ WhatsApp         ║
║    ├─ Slack        ├─ Matrix      ├─ Microsoft Teams  ║
║    ├─ Gmail        ├─ Google Calendar                  ║
║    ├─ Google Drive ├─ Dropbox     ├─ GitHub            ║
║    ├─ GitLab       ├─ Notion      ├─ Trello          ║
║    ├─ Jira         ├─ Airtable    ├─ Google Sheets    ║
║    ├─ PostgreSQL   ├─ MySQL       ├─ MongoDB          ║
║    ├─ Redis        ├─ n8n         ├─ Zapier           ║
║    ├─ Make         ├─ Home Assistant                   ║
║    ├─ MQTT         ├─ Webhook     ├─ REST API        ║
║    └─ MCP Servers  🚧 Soon                             ║
╠══════════════════════════════════════════════════════════╣
║        N E X C O R I X   M E N U                       ║
╠══════════════════════════════════════════════════════════╣
║  [1] Dashboard        [11] Workspace                   ║
║  [2] Chat             [12] API Keys                    ║
║  [3] Models           [13] Logs                        ║
║  [4] Agents           [14] Monitoring                  ║
║  [5] Memory           [15] Security                    ║
║  [6] Skills           [16] Backup                      ║
║  [7] Tools            [17] Updates                     ║
║  [8] Channels         [18] Settings                    ║
║  [9] Automation       [19] About                       ║
║  [10] Sandbox         [20] Exit                        ║
╚══════════════════════════════════════════════════════════╝
📁 Struktur Project
nexcorix-claw/
├── 📄 nexcorix_claw.py      # Main script
├── 📄 run.sh                # Auto-install & run
├── 📄 requirements.txt      # Dependencies
├── 📄 .env.example          # Environment template
├── 📄 README.md             # This file
├── 📁 channels/             # Channel adapters (opsional)
│   ├── telegram.py
│   ├── discord.py
│   └── ...
├── 📁 integrations/         # API integrations
│   ├── google/
│   ├── database/
│   └── ...
└── 📁 assets/               # Logo, GIF, media
    └── logo.gif
⚡ Features
✅ Auto-Install Libraries — pip install otomatis saat import gagal
✅ 100+ AI Models — 15+ provider (OpenAI, Anthropic, Google, DeepSeek, dll)
✅ 25+ Channel Integrations — Telegram, Discord, Slack, Matrix, dll
✅ System Executor — Jalankan command shell dengan timeout
✅ Advanced Installer — Install tools via apt/yum/pacman/brew/pip/GitHub
✅ File Manager — Create, read, delete, list files & folders
✅ Network Scanner — nmap, arp-scan, port scan, wifi scan
✅ Local Browser — Browse website & DuckDuckGo search tanpa browser
✅ Web Server — Start HTTP server instan
✅ OS Detector — Auto-detect Linux distro, WSL, Termux, Docker
✅ Multi-Provider Fallback — Ganti model otomatis jika gagal
✅ Chat History — Simpan percakapan di config
✅ Admin Security — Telegram admin ID filter
✅ Interactive Menu — TUI dengan warna & box drawing
📝 Catatan Penting
Status
Arti
✅�
￼ 

�
￼ ￼ ￼ ￼ ￼ 

�
￼ 

🚀 Quick Start
# Clone repository
git clone https://github.com/user/nexcorix-claw.git
cd nexcorix-claw

# Install & run
chmod +x run.sh
./run.sh
📋 25+ Channel Integrations
No
Channel
Status
Credentials Diperlukan
Cara Penggunaan
1
Telegram
✅
Bot Token (dari @BotFather), Admin ID (opsional)
Kirim pesan ke bot, AI balas
2
Discord
✅
Discord Bot Token
Bot merespon di channel yang diundang
3
WhatsApp
🚧
-
Coming soon
4
Slack
✅
Slack Bot Token (OAuth)
Bot membalas mention
5
Matrix
✅
Homeserver URL + Access Token
Kirim pesan ke room
6
Microsoft Teams
✅
Webhook URL atau Bot Framework
Kirim pesan ke channel
7
Gmail
✅
OAuth 2.0 (credentials.json)
Baca/kirim email via command
8
Google Calendar
✅
OAuth 2.0
Buat/edit event
9
Google Drive
✅
OAuth 2.0
Upload/download file
10
Dropbox
✅
Dropbox Access Token
Manajemen file
11
GitHub
✅
GitHub Personal Access Token
Akses repo, issue, PR
12
GitLab
✅
Private Token + URL
Akses project
13
Notion
✅
Integration Token
Baca/tulis halaman
14
Trello
✅
API Key + Token
Manajemen board/card
15
Jira
✅
Server URL + Email + API Token
Akses issue
16
Airtable
✅
Personal Access Token
Baca/tulis base
17
Google Sheets
✅
OAuth 2.0
Baca/tulis spreadsheet
18
PostgreSQL
✅
Host, port, user, pass, db
Query database
19
MySQL
✅
Host, port, user, pass, db
Query database
20
MongoDB
✅
MongoDB URI
Query NoSQL
21
Redis
✅
Host, port, password
Perintah Redis
22
Webhook
✅
Port (default 5000)
Terima POST, balas AI
23
MQTT
✅
Broker, port
Subscribe/topik, aksi IoT
24
REST API
✅
Endpoint custom (gunakan webhook)
-
25
MCP Servers
✅
Model Context Protocol
Implementasi kustom
🛠️ Instalasi Detail
Prerequisites
Python 3.9+
pip
Git
Linux/Mac/Termux/WSL
Step-by-step
# 1. Clone repository
git clone https://github.com/user/nexcorix-claw.git
cd nexcorix-claw

# 2. Buat virtual environment (opsional tapi direkomendasikan)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables / config
# Pertama kali run, script akan membuat ~/.nexcorix_config.json
# Atau edit langsung:
cp .env.example .env
# Edit .env sesuai channel yang mau diaktifkan

# 5. Jalankan
python3 nexcorix_claw.py
# atau pakai run.sh
chmod +x run.sh
./run.sh
🔧 Konfigurasi ~/.nexcorix_config.json
File config otomatis dibuat saat pertama kali run. Contoh isi:
{
  "provider": "openrouter",
  "model": "openai/gpt-4o",
  "fallback_model": "deepseek/deepseek-chat",
  "openrouter_key": "sk-or-v1-xxxxxxxx",
  "openai_key": "",
  "anthropic_key": "",
  "google_key": "",
  "deepseek_key": "",
  "temperature": 0.7,
  "max_tokens": 4096,
  "context_window": "auto",
  "performance": "balanced",
  "admin_id": "123456789",
  "token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
  "base_url": "https://openrouter.ai/api/v1",
  "ollama_url": "http://localhost:11434",
  "custom_api_url": "",
  "custom_api_key": "",
  "chat_history": {},
  "channels": {}
}
🎮 Cara Menggunakan
Mode Chat (Menu 2)
You: install nmap
Nexcorix: OK nmap via apt
...

You: scan network
Nexcorix: [hasil scan nmap]

You: create file test.py print("hello")
Nexcorix: File 'test.py' created!

You: browse google.com
Nexcorix: [konten halaman]

You: search "python tutorial"
Nexcorix: [hasil DuckDuckGo]

You: run ls -la
Nexcorix: [output command]

You: web server mysite 8080
Nexcorix: Web Server Started! URL: http://192.168.1.5:8080
Perintah Langsung yang Didukung
Perintah
Deskripsi
install <package>
Install via package manager
github <tool>
Install dari GitHub
pip <package>
Install via pip3
scan network [target]
Scan jaringan (nmap/arp-scan)
scan ports <target> [ports]
Scan port
wifi scan
Scan WiFi
browse <url>
Buka website
search <query>
Cari DuckDuckGo
create file <name> [content]
Buat file
create folder <name>
Buat folder
delete <name>
Hapus file/folder
read file <name>
Baca file
list files
List direktori
cd <path>
Ganti direktori
run <command>
Jalankan command
web server [folder] [port]
Start HTTP server
update system
Update package repos
🤖 100+ AI Models (15+ Providers)
Provider
Models
OpenAI
gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-4, gpt-3.5-turbo, o1-preview, o1-mini, o3-mini
Anthropic
claude-3.5-sonnet, claude-3-opus, claude-3-sonnet, claude-3-haiku
Google
gemini-1.5-pro, gemini-1.5-flash, gemini-1.0-pro, gemma-2-9b, gemma-2-27b
DeepSeek
deepseek-chat, deepseek-coder
Meta
llama-3.1-405b, llama-3.1-70b, llama-3.1-8b, llama-3-70b, llama-3-8b
Mistral
mistral-large, mistral-medium, mixtral-8x7b, mistral-7b, codestral-22b, mathstral-7b
Qwen
qwen-2.5-72b, qwen-2.5-32b, qwen-2.5-14b, qwen-2-7b
xAI
grok-2, grok-1, grok-beta
Cohere
command-r-plus, command-r
AI21
jamba-1.5
Databricks
dbrx-instruct
Upstage
solar-10.7b
NVIDIA
nemotron-4-340b
Perplexity
pplx-7b-online
Moonshot
kimi-v1
🖥️ Menu Utama
╔══════════════════════════════════════════════════════════╗
║ 🦂       N E X C O R I X   C L A W   v4.0       🦂 ║
╠══════════════════════════════════════════════════════════╣
║  Integrations                                            ║
║    ├─ Discord      ├─ Telegram    ├─ WhatsApp         ║
║    ├─ Slack        ├─ Matrix      ├─ Microsoft Teams  ║
║    ├─ Gmail        ├─ Google Calendar                  ║
║    ├─ Google Drive ├─ Dropbox     ├─ GitHub            ║
║    ├─ GitLab       ├─ Notion      ├─ Trello          ║
║    ├─ Jira         ├─ Airtable    ├─ Google Sheets    ║
║    ├─ PostgreSQL   ├─ MySQL       ├─ MongoDB          ║
║    ├─ Redis        ├─ n8n         ├─ Zapier           ║
║    ├─ Make         ├─ Home Assistant                   ║
║    ├─ MQTT         ├─ Webhook     ├─ REST API        ║
║    └─ MCP Servers  🚧 Soon                             ║
╠══════════════════════════════════════════════════════════╣
║        N E X C O R I X   M E N U                       ║
╠══════════════════════════════════════════════════════════╣
║  [1] Dashboard        [11] Workspace                   ║
║  [2] Chat             [12] API Keys                    ║
║  [3] Models           [13] Logs                        ║
║  [4] Agents           [14] Monitoring                  ║
║  [5] Memory           [15] Security                    ║
║  [6] Skills           [16] Backup                      ║
║  [7] Tools            [17] Updates                     ║
║  [8] Channels         [18] Settings                    ║
║  [9] Automation       [19] About                       ║
║  [10] Sandbox         [20] Exit                        ║
╚══════════════════════════════════════════════════════════╝
📁 Struktur Project
nexcorix-claw/
├── 📄 nexcorix_claw.py      # Main script
├── 📄 run.sh                # Auto-install & run
├── 📄 requirements.txt      # Dependencies
├── 📄 .env.example          # Environment template
├── 📄 README.md             # This file
├── 📁 channels/             # Channel adapters (opsional)
│   ├── telegram.py
│   ├── discord.py
│   └── ...
├── 📁 integrations/         # API integrations
│   ├── google/
│   ├── database/
│   └── ...
└── 📁 assets/               # Logo, GIF, media
    └── logo.gif
⚡ Features
✅ Auto-Install Libraries — pip install otomatis saat import gagal
✅ 100+ AI Models — 15+ provider (OpenAI, Anthropic, Google, DeepSeek, dll)
✅ 25+ Channel Integrations — Telegram, Discord, Slack, Matrix, dll
✅ System Executor — Jalankan command shell dengan timeout
✅ Advanced Installer — Install tools via apt/yum/pacman/brew/pip/GitHub
✅ File Manager — Create, read, delete, list files & folders
✅ Network Scanner — nmap, arp-scan, port scan, wifi scan
✅ Local Browser — Browse website & DuckDuckGo search tanpa browser
✅ Web Server — Start HTTP server instan
✅ OS Detector — Auto-detect Linux distro, WSL, Termux, Docker
✅ Multi-Provider Fallback — Ganti model otomatis jika gagal
✅ Chat History — Simpan percakapan di config
✅ Admin Security — Telegram admin ID filter
✅ Interactive Menu — TUI dengan warna & box drawing
📝 Catatan Penting
Status
Arti
✅
Sudah tersedia & stabil
🚧
Dalam pengembangan / placeholder
WhatsApp: Memerlukan konfigurasi tambahan (pywhatsapp)
Google services: Memerlukan OAuth 2.0 setup (credentials.json)
Database adapters: Memerlukan koneksi valid, auto-install library
MCP Servers: Implementasi kustom sesuai kebutuhan
🔒 Security
Semua command dijalankan dengan timeout (default 300s)
Admin ID filter untuk Telegram
Sandbox mode — perintah berjalan di home directory
API keys disimpan di ~/.nexcorix_config.json (chmod 600 direkomendasikan)
🐛 Troubleshooting
# Permission denied
chmod +x run.sh
chmod 600 ~/.nexcorix_config.json

# Module not found
pip install -r requirements.txt
# atau biarkan auto-install saat run

# Telegram bot tidak merespon
# Pastikan token valid dan bot tidak di-block

# API key invalid
# Cek di Settings → Test AI Connections (menu 12)
📜 License
MIT License — bebas modifikasi & distribusi.
�
￼ 

�
￼ 

�
Made with ❤️ by Nexcorix Team

Sudah tersedia & stabil
🚧
Dalam pengembangan / placeholder
WhatsApp: Memerlukan konfigurasi tambahan (pywhatsapp)
Google services: Memerlukan OAuth 2.0 setup (credentials.json)
Database adapters: Memerlukan koneksi valid, auto-install library
MCP Servers: Implementasi kustom sesuai kebutuhan
🔒 Security
Semua command dijalankan dengan timeout (default 300s)
Admin ID filter untuk Telegram
Sandbox mode — perintah berjalan di home directory
API keys disimpan di ~/.nexcorix_config.json (chmod 600 direkomendasikan)
🐛 Troubleshooting
# Permission denied
chmod +x run.sh
chmod 600 ~/.nexcorix_config.json

# Module not found
pip install -r requirements.txt
# atau biarkan auto-install saat run

# Telegram bot tidak merespon
# Pastikan token valid dan bot tidak di-block

# API key invalid
# Cek di Settings → Test AI Connections (menu 12)
📜 License
MIT License — bebas modifikasi & distribusi.
�
￼ 

�
￼ 

�
Made with ❤️ by Nexcorix Team
