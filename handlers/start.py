from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import EMOJIS

# Стани для ConversationHandler
MAIN_MENU, TASKS, DIAGRAMS, SETTINGS = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обробник команди /start"""
    user = update.effective_user
    welcome_text = (
        f"{EMOJIS['robot']} *Вітаю, {user.first_name}!* \n\n"
        "Цей бот створений для роботи з SysML діаграмами у команді. "
        "Обирай розділ нижче:"
    )
    
    keyboard = [
        [InlineKeyboardButton(f"{EMOJIS['task']} Завдання", callback_data='tasks')],
        [InlineKeyboardButton(f"{EMOJIS['diagram']} Діаграми", callback_data='diagrams')],
        [InlineKeyboardButton(f"{EMOJIS['settings']} Налаштування", callback_data='settings')],
        [InlineKeyboardButton(f"{EMOJIS['help']} Допомога", callback_data='help')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.callback_query.edit_message_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    return MAIN_MENU