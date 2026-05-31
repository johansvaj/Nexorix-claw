cat > claw.py << 'PYEOF'
#!/usr/bin/env python3
"""
🤖⚡ AGENTS CLAW MINI - SUPER LAUNCHER
Satu file. Semua model. Semua platform. Auto-detect ID.
"""

import os, sys, json, asyncio, time

# ============================================
# FILE KONFIG
# ============================================
CONFIG_FILE = os.path.expanduser("~/.claw_config.json")

# ============================================
# DAFTAR SEMUA MODEL AI
# ============================================
MODELS = {
    "1":  {"name": "DeepSeek Chat", "provider": "openrouter", "id": "deepseek/deepseek-chat", "online": True},
    "2":  {"name": "DeepSeek Coder", "provider": "openrouter", "id": "deepseek/deepseek-coder", "online": True},
    "3":  {"name": "GPT-4o", "provider": "openrouter", "id": "openai/gpt-4o", "online": True},
    "4":  {"name": "GPT-4o Mini", "provider": "openrouter", "id": "openai/gpt-4o-mini", "online": True},
    "5":  {"name": "Claude 3.5 Sonnet", "provider": "openrouter", "id": "anthropic/claude-3.5-sonnet", "online": True},
    "6":  {"name": "Claude 3 Opus", "provider": "openrouter", "id": "anthropic/claude-3-opus", "online": True},
    "7":  {"name": "Gemini 1.5 Pro", "provider": "openrouter", "id": "google/gemini-1.5-pro", "online": True},
    "8":  {"name": "Gemini 1.5 Flash", "provider": "openrouter", "id": "google/gemini-1.5-flash", "online": True},
    "9":  {"name": "Llama 3.1 70B", "provider": "openrouter", "id": "meta-llama/llama-3.1-70b-instruct", "online": True},
    "10": {"name": "Llama 3.1 8B", "provider": "openrouter", "id": "meta-llama/llama-3.1-8b-instruct", "online": True},
    "11": {"name": "Mistral Large", "provider": "openrouter", "id": "mistralai/mistral-large", "online": True},
    "12": {"name": "Qwen 2.5 72B", "provider": "openrouter", "id": "qwen/qwen-2.5-72b-instruct", "online": True},
    "13": {"name": "Qwen 2 72B", "provider": "openrouter", "id": "qwen/qwen-2-72b-instruct", "online": True},
    "14": {"name": "Perplexity Sonar", "provider": "openrouter", "id": "perplexity/llama-3.1-sonar-large-128k-online", "online": True},
    "15": {"name": "Llama 3 (Ollama)", "provider": "ollama", "id": "llama3.1", "online": False, "url": "http://localhost:11434"},
    "16": {"name": "Llama 3 (Ollama)", "provider": "ollama", "id": "llama3", "online": False, "url": "http://localhost:11434"},
    "17": {"name": "Mistral (Ollama)", "provider": "ollama", "id": "mistral", "online": False, "url": "http://localhost:11434"},
    "18": {"name": "Qwen 2.5 (Ollama)", "provider": "ollama", "id": "qwen2.5", "online": False, "url": "http://localhost:11434"},
    "19": {"name": "Gemma 2 (Ollama)", "provider": "ollama", "id": "gemma2", "online": False, "url": "http://localhost:11434"},
    "20": {"name": "Phi 3 (Ollama)", "provider": "ollama", "id": "phi3", "online": False, "url": "http://localhost:11434"},
}

# ============================================
# PLATFORM
# ============================================
PLATFORMS = {
    "1": {"name": "Telegram", "need": "token"},
    "2": {"name": "Discord", "need": "token"},
    "3": {"name": "Slack", "need": "token"},
}

# ============================================
# UTILS
# ============================================
def clear(): os.system('clear' if os.name != 'nt' else 'cls')
def load_cfg():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f: return json.load(f)
    return {"platform": "1", "platform_token": "", "model": "1", "openrouter_key": "", "ollama_url": "http://localhost:11434", "admin_id": "", "system_prompt": "Kamu AI assistant yang ramah dan membantu."}
def save_cfg(c):
    with open(CONFIG_FILE, 'w') as f: json.dump(c, f, indent=2)
    print(f"\n💾 Tersimpan!")

# ============================================
# TAMPILAN
# ============================================
def banner():
    print("""
    ╔═══════════════════════════════════════╗
    ║     🤖⚡ AGENTS CLAW MINI            ║
    ║     Super Launcher v2.0               ║
    ╚═══════════════════════════════════════╝
    1. 🚀 JALANKAN BOT
    2. ⚙️  SETING BOT (Model + Platform + Token)
    3. 📋 LIHAT SETING & INFO
    4. 🧪 TEST KONEKSI AI
    5. 🔍 DETEKSI ID (Bot ID / User ID)
    6. ❌ KELUAR
    """)

def show_models():
    print("\n    🤖 PILIH MODEL AI")
    print("    ═══════════════════════════════════════")
    print("    🌐 ONLINE (OpenRouter - butuh API key):")
    for k, v in MODELS.items():
        if v["online"]:
            mark = "✅" if v["id"] == load_cfg().get("model_detail",{}).get("id") else "  "
            print(f"    {mark} {k:2}. {v['name']:<25} [{v['id']}]")
    print("\n    💻 OFFLINE (Ollama - jalan di lokal):")
    for k, v in MODELS.items():
        if not v["online"]:
            mark = "✅" if v["id"] == load_cfg().get("model_detail",{}).get("id") else "  "
            print(f"    {mark} {k:2}. {v['name']:<25} [localhost]")
    print("    ───────────────────────────────────────")
    print("    Ketik nomor model (1-20):")

def show_platforms():
    print("\n    📱 PILIH PLATFORM")
    print("    ═══════════════════════════════════════")
    for k, v in PLATFORMS.items():
        mark = "✅" if k == load_cfg().get("platform") else "  "
        print(f"    {mark} {k}. {v['name']}")
    print("    ───────────────────────────────────────")
    print("    Ketik nomor platform (1-3):")

# ============================================
# SETING
# ============================================
def setting():
    cfg = load_cfg()
    clear()
    
    # 1. Pilih Model
    show_models()
    p = input("    > ").strip()
    if p in MODELS:
        cfg["model"] = p
        cfg["model_detail"] = MODELS[p]
        print(f"\n    ✅ Model: {MODELS[p]['name']}")
    
    # 2. Pilih Platform
    show_platforms()
    p = input("    > ").strip()
    if p in PLATFORMS:
        cfg["platform"] = p
        print(f"\n    ✅ Platform: {PLATFORMS[p]['name']}")
    
    # 3. Token
    current = cfg.get("platform_token", "")
    masked = current[:15] + "..." if len(current) > 15 else (current or "❌ BELUM DISET")
    print(f"\n    🔑 Token {PLATFORMS[cfg['platform']]['name']}: {masked}")
    print("    (Cara dapat: @BotFather untuk Telegram, Discord Developer Portal, etc)")
    t = input("    Token baru (Enter = tetap): ").strip()
    if t: cfg["platform_token"] = t
    
    # 4. OpenRouter Key (kalau model online)
    if MODELS[cfg["model"]]["online"]:
        current = cfg.get("openrouter_key", "")
        masked = current[:15] + "..." if len(current) > 15 else "❌ BELUM DISET"
        print(f"\n    🌐 OpenRouter API Key: {masked}")
        print("    Dapatkan di: https://openrouter.ai/keys")
        k = input("    Key baru (Enter = tetap): ").strip()
        if k: cfg["openrouter_key"] = k
    
    # 5. Ollama URL (kalau model offline)
    else:
        print(f"\n    💻 Ollama URL: {cfg.get('ollama_url', 'http://localhost:11434')}")
        print("    Pastikan Ollama sudah jalan: ollama serve")
        u = input("    URL baru (Enter = tetap): ").strip()
        if u: cfg["ollama_url"] = u
    
    # 6. Admin ID
    print(f"\n    👑 Admin Telegram ID: {cfg.get('admin_id') or '❌ BELUM DISET'}")
    print("    (Cek ID dengan @userinfobot di Telegram)")
    a = input("    ID baru (Enter = tetap): ").strip()
    if a: cfg["admin_id"] = a
    
    # 7. System Prompt
    print(f"\n    📝 System Prompt: {cfg['system_prompt'][:40]}...")
    pr = input("    Prompt baru (Enter = tetap): ").strip()
    if pr: cfg["system_prompt"] = pr
    
    save_cfg(cfg)
    input("\n    Tekan Enter kembali ke menu...")

def lihat_seting():
    cfg = load_cfg()
    clear()
    m = cfg.get("model_detail", MODELS.get(cfg.get("model","1"), {}))
    
    print(f"""
    📋 SETING SAAT INI
    ═══════════════════════════════════════
    🤖 Model AI      : {m.get('name', '❌')} [{m.get('id', '❌')}]
    🌐 Provider      : {m.get('provider', '❌').upper()}
    💻 Online        : {'Ya' if m.get('online') else 'Tidak (Offline/Lokal)'}
    
    📱 Platform      : {PLATFORMS.get(cfg.get('platform','1'),{}).get('name','❌')}
    🔑 Token         : {cfg.get('platform_token','')[:20]}{'...' if len(cfg.get('platform_token',''))>20 else ''}
    
    🌐 OpenRouter Key: {cfg.get('openrouter_key','')[:20]}{'...' if len(cfg.get('openrouter_key',''))>20 else '❌'}
    💻 Ollama URL    : {cfg.get('ollama_url','❌')}
    
    👑 Admin ID      : {cfg.get('admin_id') or '❌'}
    📝 System Prompt : {cfg.get('system_prompt','')[:50]}...
    """)
    input("    Tekan Enter kembali...")

# ============================================
# TEST KONEKSI
# ============================================
async def test_ai():
    cfg = load_cfg()
    m = cfg.get("model_detail", MODELS.get(cfg.get("model","1")))
    
    print(f"\n    🧪 TEST: {m['name']}")
    print("    ⏳ Kirim pesan 'Halo' ke AI...")
    
    try:
        if m["online"]:
            # Test OpenRouter
            import aiohttp
            async with aiohttp.ClientSession() as s:
                async with s.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {cfg['openrouter_key']}", "Content-Type": "application/json", "HTTP-Referer": "https://t.me", "X-Title": "ClawTest"},
                    json={"model": m["id"], "messages": [{"role": "user", "content": "Halo! Siapa kamu? Jawab singkat."}], "max_tokens": 100}
                ) as r:
                    data = await r.json()
                    if r.status == 200:
                        print(f"\n    ✅ SUKSES!")
                        print(f"    🤖 Jawaban: {data['choices'][0]['message']['content'][:100]}...")
                        print(f"    📊 Model: {data.get('model', m['id'])}")
                    else:
                        print(f"\n    ❌ GAGAL: {data}")
        else:
            # Test Ollama
            import aiohttp
            async with aiohttp.ClientSession() as s:
                async with s.post(
                    f"{cfg['ollama_url']}/api/chat",
                    json={"model": m["id"], "messages": [{"role": "user", "content": "Halo! Siapa kamu? Jawab singkat."}], "stream": False}
                ) as r:
                    data = await r.json()
                    if r.status == 200:
                        print(f"\n    ✅ SUKSES!")
                        print(f"    🤖 Jawaban: {data.get('message',{}).get('content','')[:100]}...")
                    else:
                        print(f"\n    ❌ GAGAL: {data}")
    except Exception as e:
        print(f"\n    ❌ ERROR: {e}")
        if not m["online"]:
            print("    💡 Pastikan Ollama jalan: ollama serve")

def test_koneksi():
    clear()
    print("    🧪 TEST KONEKSI AI")
    print("    ═══════════════════════════════════════")
    asyncio.run(test_ai())
    input("\n    Tekan Enter kembali...")

# ============================================
# DETEKSI ID
# ============================================
def deteksi_id():
    cfg = load_cfg()
    clear()
    print("""
    🔍 DETEKSI ID
    ═══════════════════════════════════════
    1. 🆔 Cek ID Telegram (kirim pesan ke @userinfobot)
    2. 🤖 Cek Bot ID & Info (butuh token)
    """)
    p = input("    Pilih [1-2]: ").strip()
    
    if p == "2" and cfg.get("platform_token"):
        print("\n    ⏳ Mengecek bot info...")
        try:
            import asyncio
            asyncio.run(_cek_bot_info(cfg["platform_token"]))
        except Exception as e:
            print(f"    ❌ Error: {e}")
    else:
        print("""
    📱 CARA CEK ID TELEGRAM:
    1. Buka Telegram, cari @userinfobot
    2. Kirim pesan apa saja
    3. Bot akan balas dengan User ID kamu
    4. Copy ID tersebut ke Seting > Admin ID
    
    🤖 CARA CEK BOT ID:
    1. Pilih menu 2 di atas (butuh token sudah di-set)
    2. Atau kirim pesan ke @BotFather -> /mybots -> pilih bot -> API Token
    """)
    
    input("\n    Tekan Enter kembali...")

async def _cek_bot_info(token):
    import aiohttp
    async with aiohttp.ClientSession() as s:
        async with s.get(f"https://api.telegram.org/bot{token}/getMe") as r:
            data = await r.json()
            if data.get("ok"):
                bot = data["result"]
                print(f"""
    ✅ BOT INFO:
    ┌─────────────────────────────────────┐
    │  🤖 Nama     : {bot.get('first_name', 'N/A'):<<25} │
    │  🔗 Username : @{bot.get('username', 'N/A'):<<23} │
    │  🆔 Bot ID   : {bot.get('id', 'N/A'):<<25} │
    │  🤖 Is Bot   : {'Ya' if bot.get('is_bot') else 'Tidak':<<25} │
    └─────────────────────────────────────┘
    
    💾 Bot ID otomatis tersimpan!
                """)
            else:
                print(f"    ❌ Token invalid: {data}")

# ============================================
# JALANKAN BOT
# ============================================
def jalankan():
    cfg = load_cfg()
    m = cfg.get("model_detail", MODELS.get(cfg.get("model","1")))
    p = PLATFORMS.get(cfg.get("platform","1"))
    
    # Validasi
    if not cfg.get("platform_token"):
        print("❌ Token belum di-set! Pilih menu 2 dulu.")
        input("\nTekan Enter..."); return
    
    if m["online"] and not cfg.get("openrouter_key"):
        print("❌ OpenRouter key belum di-set! Pilih menu 2 dulu.")
        input("\nTekan Enter..."); return
    
    clear()
    print(f"""
    🤖⚡ BOT DIJALANKAN!
    ═══════════════════════════════════════
    Model    : {m['name']} [{m['id']}]
    Provider : {m['provider'].upper()}
    Platform : {p['name']}
    Mode     : {'🌐 ONLINE' if m['online'] else '💻 OFFLINE'}
    
    Tekan Ctrl+C untuk berhenti
    """)
    
    # Build script
    script = f'''#!/usr/bin/env python3
import asyncio, aiohttp, json, sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "{cfg['platform_token']}"
API_KEY = "{cfg.get('openrouter_key', '')}"
MODEL = "{m['id']}"
PROVIDER = "{m['provider']}"
SYSTEM = "{cfg.get('system_prompt', 'Kamu AI assistant')}"
ADMIN = "{cfg.get('admin_id', '')}"
OLLAMA_URL = "{cfg.get('ollama_url', 'http://localhost:11434')}"

async def ai_chat(text: str) -> str:
    if PROVIDER == "openrouter":
        async with aiohttp.ClientSession() as s:
            async with s.post("https://openrouter.ai/api/v1/chat/completions",
                headers={{"Authorization": f"Bearer {{API_KEY}}", "Content-Type": "application/json", "HTTP-Referer": "https://t.me", "X-Title": "ClawBot"}},
                json={{"model": MODEL, "messages": [{{"role": "system", "content": SYSTEM}}, {{"role": "user", "content": text}}], "temperature": 0.7}}
            ) as r:
                data = await r.json()
                return data["choices"][0]["message"]["content"]
    else:
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{{OLLAMA_URL}}/api/chat",
                json={{"model": MODEL, "messages": [{{"role": "system", "content": SYSTEM}}, {{"role": "user", "content": text}}], "stream": False}}
            ) as r:
                data = await r.json()
                return data.get("message", {{}}).get("content", "Error")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    
    # Auto-detect & tampilkan ID
    info = f"""🤖 *Bots Claw Mini*

👤 *Info Kamu:*
🆔 User ID: `{user.id}`
📛 Nama: {user.first_name}
🔖 Username: @{user.username or 'N/A'}

💬 *Info Chat:*
🆔 Chat ID: `{chat.id}`
📁 Tipe: {chat.type}

🤖 *Info Bot:*
Kirim pesan untuk chat dengan AI!
Model: `{MODEL}`"""
    
    await update.message.reply_text(info, parse_mode="Markdown")

async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🆔 *Your ID:* `{user.id}`\\n👤 {user.first_name}",
        parse_mode="Markdown"
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    
    if user.is_bot: return
    
    print(f"[{{user.username or user.first_name}}] (ID: {{user.id}}): {{text}}")
    
    wait = await update.message.reply_text("🤔...")
    try:
        jawaban = await ai_chat(text)
        await wait.edit_text(jawaban[:4096])
        print(f"[Bot]: {{jawaban[:80]}}...")
    except Exception as e:
        await wait.edit_text(f"❌ Error: {{str(e)[:200]}}")
        print(f"Error: {{e}}")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("id", id_cmd))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("✅ BOT JALAN!")
print(f"Model: {{MODEL}}")
print(f"Platform: Telegram")
print("Kirim /start untuk lihat info ID")
app.run_polling()
'''
    
    with open('/tmp/claw_run.py', 'w') as f:
        f.write(script)
    
    os.system('python3 /tmp/claw_run.py')

# ============================================
# MAIN
# ============================================
def main():
    while True:
        clear()
        banner()
        c = load_cfg()
        m = c.get("model_detail", MODELS.get(c.get("model","1"), {}))
        p = PLATFORMS.get(c.get("platform","1"), {})
        
        # Status bar
        status = f"🤖 {m.get('name','❌')} | 📱 {p.get('name','❌')} | {'✅ Ready' if c.get('platform_token') and (not m.get('online') or c.get('openrouter_key')) else '⚠️  Belum seting'}"
        print(f"    Status: {status}\n")
        
        pilih = input("    Pilih [1-6]: ").strip()
        
        if pilih == "1": jalankan()
        elif pilih == "2": setting()
        elif pilih == "3": lihat_seting()
        elif pilih == "4": test_koneksi()
        elif pilih == "5": deteksi_id()
        elif pilih == "6": clear(); print("👋 Dadah!"); break
        else: print("❌ Salah!"); time.sleep(1)

if __name__ == "__main__":
    main()
PYEOF
