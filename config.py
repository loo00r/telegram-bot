import os
from dotenv import load_dotenv

# Завантажуємо змінні середовища з .env файлу
load_dotenv()

# Токен бота отримуємо зі змінних середовища
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# ID адміністраторів (можна додати кілька через кому)
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(','))) if os.getenv('ADMIN_IDS') else []

# Jira налаштування
JIRA_SERVER = os.getenv('JIRA_SERVER', '')
JIRA_EMAIL = os.getenv('JIRA_EMAIL', '')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN', '')
JIRA_PROJECT_KEY = os.getenv('JIRA_PROJECT_KEY', '')

# Налаштування бази даних
DATABASE = 'data/chatik.db'

# Шляхи до директорій
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
TEMP_DIR = os.path.join(DATA_DIR, 'temp')

# Створюємо необхідні директорії
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Налаштування для візуалізації діаграм
DIAGRAM_SETTINGS = {
    'node_color': '#FF6B6B',  # Колір вузлів
    'edge_color': '#4ECDC4',   # Колір ребер
    'font_size': 10,          
    'node_size': 3000,
    'font_color': 'white',
    'bg_color': '#2D3436'     # Фоновий колір
}

# Емодзі для інтерфейсу
EMOJIS = {
    'robot': '🤖',
    'task': '📝',
    'diagram': '📊',
    'settings': '⚙️',
    'help': '❓',
    'back': '🔙',
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
}