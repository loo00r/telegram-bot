from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import EMOJIS
from .start import start, MAIN_MENU

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Показати налаштування"""
    keyboard = [
        [InlineKeyboardButton(f"{EMOJIS['back']} Назад", callback_data='back')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            f"{EMOJIS['settings']} *Налаштування*\n\n"
            "Тут будуть налаштування бота.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif update.message:
        await update.message.reply_text(
            f"{EMOJIS['settings']} *Налаштування*\n\n"
            "Тут будуть налаштування бота.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    return MAIN_MENU
