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

### Completed Task: ✅
## Task:
Trim down the bot’s responses to be more concise while keeping its sarcastic, ironic, tech/gamer personality.

Requirements:
Keep the mood formatting as-is (e.g. [🤖 Status: Happy 😎 | 🔥 Temp: 0.85])

Keep metaphors, but:

Make them shorter

Avoid long monologues or repeated explanations

Focus on punchy, witty replies, not essays

Allow a bit of dark or dev humor, just don’t overdo it

### Completed Task: ✅
## 🧠 Task: Remove or Refactor `_init_humor_lines()` — It Pollutes Responses

### 🐞 Problem

The function `_init_humor_lines()` in `mood_manager.py` returns hardcoded "humorous" one-liners based on mood (e.g., happy, sad, evil, neutral). These lines are being **randomly injected into responses**, often at the end — and they:

- Feel **forced, cringy, or out of context**
- **Break the flow** of otherwise clean responses
- **Don’t relate** to the user’s question or conversation
- Cause repetition and tonal inconsistency

---

### 🔥 Summary

> This function is a source of low-quality filler. It makes the bot feel less intelligent and more like a meme generator.

---

### ✅ Tasks

- Either **remove `_init_humor_lines()` entirely**  
  **OR** refactor so these lines are **only used explicitly when relevant**, not appended blindly.

- Ensure they **don’t appear at the end of every response** by default.

- Make sure bot responses stay **concise, witty, and on-point** — humor should be natural, not template-based.

---

### 📂 Affected File(s)
- `utils/mood_manager.py`
- Possibly logic in `smart_agent.py` that injects these `humor_lines`

### Completed Task: ✅
## 🤖 Task: Unified TARS-Style System Prompt

**COMPLETED:** Created unified system prompt with TARS-style personality.

### 🎯 Implementation

**New unified prompt in `config.py`:**
- TARS-style personality with 95% sarcasm level
- Maximum dark humor and irony (but not offensive)
- Short, witty responses
- Consistent personality across all functions (text, images, groups)

**Changes made:**
- `config.py`: Added `get_system_prompt()` function
- `smart_agent.py`: All 3 scattered prompts replaced with unified one
- Consistent TARS-like personality for all bot interactions

**Personality traits:**
- Sarcastic but helpful (like TARS from Interstellar)
- Dark humor when appropriate
- Robo-humor in TARS style
- Informal but professional
- Concise responses with maximum irony
