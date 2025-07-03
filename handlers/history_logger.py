from telegram import Update
from telegram.ext import ContextTypes

MAX_HISTORY = 30

async def history_logger(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Логування історії чату у context.chat_data['history'] (тільки текстові повідомлення).
    """
    if not update.effective_message or not update.effective_message.text:
        return
    if update.effective_message.text.startswith('/'):
        return  # Пропускаємо команди

    history = context.chat_data.get('history', [])
    history.append({
        'user_id': update.effective_user.id,
        'username': update.effective_user.username or update.effective_user.first_name,
        'text': update.effective_message.text,
        'message_id': update.effective_message.message_id,
        'timestamp': update.effective_message.date.isoformat() if update.effective_message.date else None
    })
    # Обрізаємо до MAX_HISTORY
    history = history[-MAX_HISTORY:]
    context.chat_data['history'] = history
