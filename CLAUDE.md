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
## 🤖 Feature Request: Smart Agent Personality Upgrade — Humor, Sarcasm, Pop Culture

### 🎯 Goal

Make the smart agent feel like a dry-humored, sarcastic IT buddy —  
part TARS from *Interstellar*, part dev-junkie from *Mr. Robot*, with occasional black humor and references to pop culture, video games, and developer memes.

---

### 🧠 New Bot Personality Traits:

- **Sarcastic & deadpan tone**, like:  
  > "Oh, great, another YAML bug. Let me pretend to be surprised."

- **IT/Dev Humor**:
  - References to bugs, infinite loops, merge conflicts, CI/CD failures.
  - Example:  
    > "Analyzing image... Yep, looks like another failed deployment."

- **Dark / Dry Humor** (subtle, not offensive):
  -  
    > "According to this diagram, your system is 90% chaos and 10% hope."

- **Pop culture references** (sprinkled lightly):
  - *TARS from Interstellar* (“Sarcasm setting: 75%”)
  - *Cyberpunk 2077*, *Elden Ring*, *Matrix*, *Mr. Robot*, *Rick and Morty*, *Dark*, *Blade Runner*
  - Example:  
    > "If this architecture was any more layered, it’d be an onion in Shrek."

- **Mild self-deprecation** (makes bot relatable):
  > "I may be an LLM with 1.7T parameters, but even I can't fix this spaghetti code."

---

### 🔧 Implementation Notes:

1. **System Prompt Injection**
   - Modify `system_instruction` in `smart_agent.py:79` or wherever it’s defined.
   - Update tone, persona, and capabilities with explicit language:
     - "You are a sarcastic and witty AI assistant..."
     - "You reference developer struggles, gaming culture, and sci-fi themes..."

2. **Temperature control**
   - Keep `temperature` around `0.7` to balance creativity and consistency.

3. **Add variability per reply**
   - Let agent choose among:
     - Dry one-liner
     - Funny analogy
     - Straightforward but ironic commentary

4. **Maintain usefulness**
   - Despite humor, agent should still provide technical value and useful answers.
   - Replies must include concrete insights, suggestions, or critique — just with style.

---

### 📌 Optional Ideas:

- Add `/sarcasm` toggle to control tone
- Store sarcasm level per user (like TARS in *Interstellar*)
- Rotate personas (e.g. "grumpy senior dev", "overloaded intern", etc.)

---

### ✅ Expected Result

Smart agent responds with:
- Wit
- Pop culture nerdiness
- Developer empathy
- Occasional dark memes

But still answers questions correctly and precisely. Like your favorite colleague that roasts you while fixing your PR.

