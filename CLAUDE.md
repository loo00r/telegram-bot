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
## 🐞 Bugfix: Smart Agent Does Not React to Nearby Photo When Mentioned Separately

### 🔎 Problem Summary

The bot fails to analyze images that were just sent, even when it is directly mentioned immediately after. Instead, it only considers the message with the mention and ignores the nearby image, despite being part of the same user intent.

---

### 🧩 Case Example (from log + screenshot):

User sends:
1. A photo (e.g., face with name)
2. Message: `хто це`
3. Message: `@g00n3r_bot прокоментуй`

Bot responds with an introductory message and ignores the image.  
`GPT-4o-mini` is used instead of `GPT-4o`, which confirms no image was passed into the prompt.

---

### 📌 Issue Observed in Logs:

- At `13:15:39`, `PHOTO_HANDLER` logs a received image with `media_group_id=None`, 
  but skips it because the bot is not mentioned **in that message**.
- At `13:15:56`, `SMART_AGENT` handles `@mention`, but **does not associate it with the photo** from the same user.
- The photo is ignored, despite the clear user intent to refer to it.

---

### ✅ Fix Requirements

1. **Improve image-to-mention association**
   - When a message contains `@bot`, scan recent `image_message`s sent by the **same user** within the last ~30 seconds (or last 3 messages).
   - If found, attach those images to the GPT-4o prompt.

2. **Contextual mention handling**
   - Treat `@mention` as referring to recent visual content in the chat history, even if not in the same message.
   - Handle common interaction patterns:
     - Image
     - Question (e.g. "що це?")
     - Bot mention (e.g. `@bot коментуй`)

3. **Support for `media_group_id=None`**
   - Even single-photo messages should be available for visual context, not ignored when not part of a group.

4. **Pending media buffer (in-memory)**
   - Temporarily keep track of recent images per user.
   - If a mention arrives shortly after (within time or message window), link the buffered image(s) to the GPT prompt.

---

### 🧠 Expected Behavior After Fix

- Bot will react to recent images even if mentioned in a **subsequent message**.
- Smart agent will switch to `GPT-4o` and include base64 images.
- Prompts like `@bot прокоментуй` will respond **about the image**, not generically.


