from telegram import Update
from telegram.ext import ContextTypes
from config import EMOJIS
from .start import MAIN_MENU



async def show_diagrams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from .diagrams import show_diagrams as _show_diagrams
    return await _show_diagrams(update, context)

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from .settings import show_settings as _show_settings
    return await _show_settings(update, context)

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from .help import show_help as _show_help
    return await _show_help(update, context)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from .start import start as _start
    return await _start(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обробник кнопок"""
    if not update.callback_query:
        return MAIN_MENU
        
    query = update.callback_query
    await query.answer()
    
    if query.data == 'back':
        return await start(update, context)
    elif query.data == 'tasks':
        from .tasks import tasks
        return await tasks(update, context)
    elif query.data == 'diagrams':
        return await show_diagrams(update, context)
    elif query.data == 'settings':
        return await show_settings(update, context)
    elif query.data == 'help':
        return await show_help(update, context)
    
    # Якщо невідома команда, повертаємося в головне меню
    return await start(update, context)
