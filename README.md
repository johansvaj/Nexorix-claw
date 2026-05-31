# 🤖⚡ Agents Claw Mini

> **A lightweight, modular AI Agent Framework for Python**  
> Inspired by [NullClaw](https://github.com/eythaann/Claw-Package-Manager) (Zig) - bringing the 678KB philosophy to Python

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)]()

## ✨ Features

- **🧠 Multi-LLM Support** - 9+ AI providers including OpenRouter (100+ models)
- **🌐 Browser Automation** - Selenium & Playwright support
- **🔍 Web Scraping** - BeautifulSoup + recursive crawling
- **🧠 Memory Storage** - SQLite, ChromaDB, Qdrant, Redis
- **📱 Messaging Channels** - Telegram, Discord, Slack bots
- **🔧 Tool Registry** - Pluggable tools with built-in functions
- **🔒 Security Sandbox** - Isolated code execution
- **⚡ Async-First** - High performance async/await
- **📦 Minimal** - Lightweight with optional dependencies

## 🤖 Supported AI Providers

| Provider | Models | Speed | Local |
|----------|--------|-------|-------|
| **OpenAI** | GPT-4o, GPT-4, GPT-3.5 | ⚡⚡⚡ | ❌ |
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Opus | ⚡⚡⚡ | ❌ |
| **Google** | Gemini 1.5 Pro, Gemini Flash | ⚡⚡⚡ | ❌ |
| **Mistral** | Mistral Large, Mixtral | ⚡⚡ | ❌ |
| **Cohere** | Command R+ | ⚡⚡ | ❌ |
| **Groq** | Llama 3, Mixtral | ⚡⚡⚡⚡ | ❌ |
| **DeepSeek** | DeepSeek Chat, Coder | ⚡⚡ | ❌ |
| **Ollama** | Llama 3, Phi, Mistral, Qwen | ⚡ | ✅ |
| **OpenRouter** | 100+ models (GPT-4o, Claude, Llama, Qwen, etc.) | ⚡⚡ | ❌ |

## 🚀 Quick Start

### Installation

```bash
# Basic install
pip install agents-claw-mini

# With all features
pip install agents-claw-mini[all]

# With specific provider
pip install agents-claw-mini[openai,anthropic]

# With browser support
pip install agents-claw-mini[browser]
```

### Basic Usage

```python
import asyncio
from agents_claw_mini import AgentsClawMini

async def main():
    # Initialize
    claw = AgentsClawMini()

    # Create agent with OpenAI
    agent = claw.create_agent(
        name="assistant",
        system_prompt="You are a helpful AI assistant."
    )

    # Chat
    response = await agent.chat("Hello! What can you do?")
    print(response.content)

asyncio.run(main())
```

### Using OpenRouter (100+ Models!)

```python
from agents_claw_mini import AgentsClawMini, Config

# Configure for OpenRouter
config = Config()
config.llm.provider = "openrouter"
config.llm.model = "anthropic/claude-3.5-sonnet"  # or any model!
config.llm.api_key = "your-openrouter-key"

claw = AgentsClawMini(config=config)
agent = claw.create_agent(name="super_agent")

response = await agent.chat("Explain quantum computing")
print(response.content)
```

### Browser Automation

```python
browser = claw.create_browser()
await browser.start()

page = await browser.goto("https://example.com")
print(page.title)
print(page.text[:500])

await browser.screenshot("page.png")
await browser.close()
```

### Web Scraping

```python
scraper = claw.create_scraper()

# Single page
data = await scraper.scrape("https://example.com")
print(data.title)
print(data.links)

# Crawl multiple pages
results = await scraper.crawl("https://example.com", max_pages=5)
for page in results:
    print(page.title)
```

### Telegram Bot

```python
@claw.channels.on_message
async def handle_message(msg):
    if msg.platform == "telegram":
        agent = claw.get_agent("assistant")
        response = await agent.chat(msg.text)
        await claw.channels.send_telegram(msg.chat_id, response.content)

await claw.channels.start_telegram()
```

## ⚙️ Configuration

### Environment Variables

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Google
export GOOGLE_API_KEY="..."

# OpenRouter (recommended for multi-model access)
export OPENROUTER_API_KEY="sk-or-..."

# Groq (super fast inference)
export GROQ_API_KEY="gsk_..."
```

### Config File (YAML)

```yaml
llm:
  provider: openrouter
  model: openai/gpt-4o
  api_key: ${OPENROUTER_API_KEY}
  temperature: 0.7
  max_tokens: 4096

browser:
  headless: true
  stealth_mode: true
  driver: selenium

memory:
  backend: sqlite
  db_path: ./memory.db

sandbox:
  enabled: true
  max_execution_time: 30
```

## 🌐 OpenRouter Models

Agents Claw Mini supports **100+ models** via OpenRouter:

```python
from agents_claw_mini.config import LLMConfig

# List all available models
models = LLMConfig.list_openrouter_models()
for model_id, name in models.items():
    print(f"{model_id}: {name}")

# Popular models:
# - openai/gpt-4o
# - anthropic/claude-3.5-sonnet
# - meta-llama/llama-3.1-70b-instruct
# - google/gemini-1.5-pro
# - mistralai/mistral-large
# - qwen/qwen-2.5-72b-instruct
# - deepseek/deepseek-chat
# - perplexity/llama-3.1-sonar-large-128k-online
```

## 📁 Project Structure

```
agents-claw-mini/
├── src/agents_claw_mini/
│   ├── __init__.py          # Package exports
│   ├── core.py              # Main engine
│   ├── agent.py             # AI Agent (9+ LLM providers)
│   ├── browser.py           # Browser automation
│   ├── scraper.py           # Web scraper
│   ├── channel.py           # Messaging channels
│   ├── memory.py            # Memory storage
│   ├── tools.py             # Tool registry
│   ├── sandbox.py           # Security sandbox
│   ├── config.py            # Configuration (with OpenRouter models)
│   ├── utils.py             # Utilities
│   └── exceptions.py        # Custom exceptions
├── examples/
│   ├── basic_agent.py
│   ├── browser_bot.py
│   ├── telegram_bot.py
│   ├── memory_chat.py
│   └── scraping_pipeline.py
├── tests/
├── docs/
├── setup.py
├── requirements.txt
└── README.md
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

Made with ⚡ by the Agents Claw Mini Team
