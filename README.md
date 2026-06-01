🤖 AgentsClaw Mini

«AI-powered Telegram Bot with Terminal Control, File Management, and Multi-Model AI Support.»

---

📋 Table of Contents

- "Features" (#-features)
- "Installation" (#-installation)
- "Configuration" (#-configuration)
- "Usage" (#-usage)
- "Troubleshooting" (#-troubleshooting)
- "Project Structure" (#-project-structure)
- "Contributing" (#-contributing)
- "License" (#-license)

---

✨ Features

🤖 AI Engine

- Support 20+ AI Models
- OpenAI, Anthropic, Google, DeepSeek, Meta
- Smart Intent Detection
- Context-Aware Responses
- Conversation Memory
- OpenRouter Integration

📁 File Manager

- Create Files
- Read Files
- Edit Files
- Delete Files
- Upload & Download via Telegram

💻 Terminal Integration

- Execute Commands
- OS Detection
- Package Manager Detection
- System Dashboard
- Real-time Output

🔒 Security

- Admin ID Restriction
- Dangerous Command Filter
- User Access Control
- Command Blacklist

---

🌐 Supported Platforms

Platform| Status
Linux| ✅
Ubuntu| ✅
Kali Linux| ✅
Termux| ✅
macOS| ✅
Windows WSL| ✅
Docker| 🚧

---

📦 Installation

Linux / Debian / Ubuntu / Kali

sudo apt update && sudo apt upgrade -y

sudo apt install python3 python3-pip git -y

git clone https://github.com/yourusername/AgentsClaw-Mini.git

cd AgentsClaw-Mini

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

Termux

pkg update && pkg upgrade -y

pkg install python git -y

git clone https://github.com/yourusername/AgentsClaw-Mini.git

cd AgentsClaw-Mini

pip install -r requirements.txt

---

⚙️ Configuration

{
  "telegram": {
    "bot_token": "YOUR_BOT_TOKEN",
    "admin_id": 123456789
  },
  "openrouter": {
    "api_key": "YOUR_API_KEY",
    "model": "anthropic/claude-3.5-sonnet"
  }
}

---

🚀 Usage

python main.py

Commands

Command| Description
/start| Start Bot
/help| Help Menu
/ai| Ask AI
/cmd| Execute Command
/file| File Manager
/sys| System Information
/status| Bot Status

---

🛠️ Troubleshooting

ModuleNotFoundError

pip install -r requirements.txt

Invalid Bot Token

Check token from BotFather.

OpenRouter 401

Verify API Key.

---

📁 Project Structure

AgentsClaw-Mini/
├── main.py
├── bot/
├── config/
├── logs/
├── assets/
├── requirements.txt
└── README.md

---

🤝 Contributing

1. Fork Repository
2. Create Branch
3. Commit Changes
4. Push Branch
5. Open Pull Request

---

📜 License

MIT License

---

❤️ Credits

- OpenRouter
- Python Telegram Bot
- Termux
- Open Source Community

Made with ❤️ by AgentsClaw Team
