# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Telegram bot designed for SysML development teams (SysML Team Chat Bot). The bot provides task management functionality integrated with Jira, AI-powered smart agent capabilities, and a user interface inspired by Love, Death & Robots aesthetics.

## Key Commands

### Running the Bot
```bash
python main.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Architecture

### Core Components

**Entry Point**: `main.py` - Bot initialization and handler registration
- Registers command handlers, callback handlers, and conversation handlers
- Sets up error handling and message logging
- Configures bot polling

**Configuration**: `config.py` - Centralized configuration management
- Environment variables loading (.env file)
- Bot token, admin IDs, Jira credentials
- UI settings (colors, emojis, diagram preferences)
- Directory structure setup

**Handler System**: `handlers/` directory
- `start.py` - Main menu and bot states (MAIN_MENU, TASKS, DIAGRAMS, SETTINGS)
- `tasks.py` - Jira task management with ConversationHandler
- `smart_agent.py` - OpenAI-powered AI assistant that responds to @mentions
- `button_handler.py` - Callback query handling
- `history_logger.py` - Chat history logging for AI context
- `help.py` - Help system
- `settings.py` - Bot settings management

**Utilities**: `utils/` directory
- `jira_client.py` - Jira API integration (JiraClient class)
- `keyboards.py` - Telegram keyboard layouts
- `helpers.py` - Helper functions

### State Management

The bot uses telegram-python-bot's ConversationHandler for state management:
- `MAIN_MENU` - Main bot interface
- `TASKS` - Task management section
- `DIAGRAMS` - SysML diagram visualization
- `SETTINGS` - Bot configuration
- Task creation states: `TASK_ACTION`, `CREATE_TASK_SUMMARY`, `CREATE_TASK_DESCRIPTION`

### Key Features

**Jira Integration**:
- Create tasks through conversation flow
- Retrieve project tasks with status "TO DO"
- Automatically send task summaries to configured channels

**Smart Agent**:
- AI-powered assistant using OpenAI GPT-4o-mini
- Responds to @bot_username mentions in group chats
- Maintains 30-message chat history for context
- Specialized in full-stack development and SysML diagrams

**Multi-language Support**:
- Ukrainian language interface
- Emojis for visual feedback defined in `config.py`

## Environment Configuration

Required environment variables in `.env`:
- `BOT_TOKEN` - Telegram bot token
- `ADMIN_IDS` - Comma-separated admin user IDs
- `JIRA_SERVER` - Jira server URL
- `JIRA_EMAIL` - Jira account email
- `JIRA_API_TOKEN` - Jira API token
- `JIRA_PROJECT_KEY` - Jira project key
- `OPENAI_API_KEY` - OpenAI API key
- `CHANNEL_ID` - Telegram channel ID for task notifications

## Data Storage

- `data/` directory for local data storage
- `data/temp/` for temporary files
- SQLite database: `data/chatik.db`

## Handler Registration Order

Important: Handler registration order in `main.py` matters:
1. Command handlers first
2. Callback query handlers
3. Message handlers with groups (history_logger in group=0, smart_agent in group=1)
4. ConversationHandler last

## Smart Agent Context

The smart agent maintains chat history and has expertise in:
- Full-stack development (20+ years experience persona)
- SysML diagrams and system modeling
- Web application architecture
- API design and database management
- Technical problem-solving and code review

### New Task: 
## 📌 Task: Improve Bot Mood System (Phase 2) – Humor, Avatar Update, and Clean Responses

### ❗Context
The current bot mood system works well in principle — it detects emotional tone, adjusts response temperature, adds status headers, and selects appropriate avatars from `data/bot_status/`. However, there are issues:

1. **Avatar is not actually updated in Telegram** – only locally.
2. **Humor is weak and generic** – includes stale lines like “look at TARS from Interstellar”.
3. **Bot duplicates name and status lines** in its response:
   ```
   [g00n3r_bot]: [🤖 Status: Concerned 🤖 | ❄️ Temp: 0.65]
   ```

---

### ✅ Goals

#### 1. Implement Real Avatar Update (or simulate it correctly)
- Use Telegram-compatible method to **programmatically change bot’s profile picture**, using images in `data/bot_status/*.png`.
- Fallback gracefully if this is not possible (log an info message like):
  ```
  [INFO] Avatar update skipped — Telegram Bot API does not support setProfilePhoto.
  ```

#### 2. Fix Message Redundancy
- Ensure the bot does **not prepend itself twice**:
  - ❌ `g00n3r_bot: [g00n3r_bot]: [🤖 Status: Happy 😎 | 🔥 Temp: 0.85]`
  - ✅ Only the formatted prefix is needed:
    ```
    [🤖 Status: Happy 😎 | 🔥 Temp: 0.85]
    ```

#### 3. Improve Humor Engine
Replace outdated or generic phrases like:
- `"Look at TARS from Interstellar"`  
- `"Maybe it’s another YAML bug"`

With **funnier, more sarcastic, or black-humor IT jokes**, such as:

| Mood    | Examples |
|---------|----------|
| 😎 happy | “You did it! Almost like pushing to `main` on a Friday… but in a good way.” |
| 😔 sad   | “Your code is crying. I mean literally — it triggered 78 exceptions.” |
| 😈 evil  | “Deploying this would be illegal in 7 countries. I approve.” |
| 😐 neutral | “Nothing broke yet… suspicious.” |

Let humor vary by mood and keep it short, clever, and relevant to developers.

---

### 🧠 Implementation Details

- Extend `utils/mood_manager.py` to include a new `generate_humorous_response()` based on mood.
- Ensure `handlers/smart_agent.py` uses this instead of inserting hardcoded phrases.
- Clean up formatting logic so only one status prefix appears per message.
- Consider moving humor lines to external `json` or `yaml` file for easier edits.

---

### 🗂 Directory Structure (Reminder)
```
data/
  bot_status/
    happy.png
    sad.png
    evil.png
    neutral.png

utils/
  mood_manager.py

handlers/
  smart_agent.py
```

---

Once this is complete, the bot should feel much more alive — like TARS, but with better jokes and working avatar changes 😎