import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
from config import BOT_TOKEN, ADMIN_IDS, EMOJIS

# Імпортуємо стани з handlers
from handlers import MAIN_MENU, TASKS, DIAGRAMS, SETTINGS, tasks_conv_handler

# Імпортуємо обробники
from handlers.start import start
from handlers.help import show_help
from handlers.button_handler import button_handler
from handlers.tasks import tasks  # Імпортуємо функцію tasks з модуля tasks
from handlers.smart_agent import smart_agent_handler
from handlers.history_logger import history_logger

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Імпорт станів з модуля handlers

# --- Хендлери команд ---

# Функція start тепер імпортується з handlers.start

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обробник кнопок"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'tasks':
        from handlers.tasks import tasks
        return await tasks(update, context)
    elif query.data == 'diagrams':
        return await show_diagrams(update, context)
    elif query.data == 'settings':
        return await show_settings(update, context)
    elif query.data == 'help':
        return await show_help(update, context)
    elif query.data == 'back':
        return await start(update, context)
    
    return MAIN_MENU


async def show_diagrams(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Показати діаграми"""
    keyboard = [
        [InlineKeyboardButton(f"{EMOJIS['back']} Назад", callback_data='back')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"{EMOJIS['diagram']} *Розділ діаграм*\n\n"
        "Тут будуть відображатися ваші SysML діаграми.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return DIAGRAMS

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Показати налаштування"""
    keyboard = [
        [InlineKeyboardButton(f"{EMOJIS['back']} Назад", callback_data='back')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        f"{EMOJIS['settings']} *Налаштування*\n\n"
        "Тут будуть налаштування бота.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return SETTINGS

# Функція show_help тепер імпортується з handlers.help

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Логування помилок"""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    if update and hasattr(update, 'effective_message') and update.effective_message:
        await update.effective_message.reply_text(
            f"{EMOJIS['error']} Сталася помилка. Будь ласка, спробуйте пізніше."
        )
    elif update and hasattr(update, 'callback_query') and update.callback_query:
        await update.callback_query.message.reply_text(
            f"{EMOJIS['error']} Сталася помилка. Будь ласка, спробуйте пізніше."
        )

def main() -> None:
    """Запуск бота"""
    # Створюємо додаток
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Додаємо обробник команди /start
    application.add_handler(CommandHandler("start", start))
    
    # Додаємо обробник команди /help
    application.add_handler(CommandHandler("help", show_help))
    
    # Додаємо обробник команди /tasks
    application.add_handler(CommandHandler("tasks", tasks))
    
    # Додаємо обробник кнопок (має бути після команд)
    application.add_handler(CallbackQueryHandler(button_handler))

    # Додаємо handler для логування історії чату (всі текстові повідомлення)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), history_logger), group=0)

    # Додаємо handler смарт-агента (реагує на тег бота в тексті)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), smart_agent_handler), group=1)

    # Додаємо ConversationHandler для завдань (має бути після звичайних обробників)
    application.add_handler(tasks_conv_handler)
    
    # Додаємо обробник помилок
    application.add_error_handler(error_handler)
    
    # Запускаємо бота
    print("Бот запущений...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()