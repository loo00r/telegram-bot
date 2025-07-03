from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import EMOJIS
from .start import MAIN_MENU

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Показати довідку"""
    help_text = (
        f"{EMOJIS['help']} *Довідка*\n\n"
        "Цей бот призначений для роботи з SysML діаграмами у команді.\n\n"
        "*Доступні команди:*\n"
        f"{EMOJIS['task']} /tasks - Керування завданнями\n"
        f"{EMOJIS['diagram']} /diagrams - Робота з діаграмами\n"
        f"{EMOJIS['settings']} /settings - Налаштування\n"
        f"{EMOJIS['help']} /help - Довідка"
    )
    
    keyboard = [
        [InlineKeyboardButton(f"{EMOJIS['back']} Назад", callback_data='back')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            help_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif update.message:
        await update.message.reply_text(
            help_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    return MAIN_MENU
