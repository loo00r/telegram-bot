from telegram import Update
from telegram.ext import ContextTypes
from typing import List, Optional

MAX_HISTORY = 30

async def history_logger(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Логування історії чату у context.chat_data['history'] (текстові повідомлення та фото з підписами).
    Тепер підтримує групування фото з підписами як одне повідомлення.
    """
    if not update.effective_message:
        return
    
    # Пропускаємо команди
    if update.effective_message.text and update.effective_message.text.startswith('/'):
        return
    
    # Обробляємо тільки текстові повідомлення або фото з підписами
    if not update.effective_message.text and not (update.effective_message.photo and update.effective_message.caption):
        return
    
    history = context.chat_data.get('history', [])
    media_group_id = update.effective_message.media_group_id
    
    # Якщо це фото з підписом
    if update.effective_message.photo:
        # Якщо це частина медіа-групи
        if media_group_id:
            # Шукаємо існуючий запис для цієї медіа-групи
            existing_entry = None
            for entry in reversed(history):
                if entry.get('type') == 'image_message' and entry.get('media_group_id') == media_group_id:
                    existing_entry = entry
                    break
            
            if existing_entry:
                # Додаємо фото до існуючого запису
                existing_entry['image_count'] = existing_entry.get('image_count', 1) + 1
                # Оновлюємо підпис якщо є новий
                if update.effective_message.caption:
                    existing_entry['text'] = update.effective_message.caption
            else:
                # Створюємо новий запис для медіа-групи
                history.append({
                    'type': 'image_message',
                    'user_id': update.effective_user.id,
                    'username': update.effective_user.username or update.effective_user.first_name,
                    'text': update.effective_message.caption or '[Зображення]',
                    'image_count': 1,
                    'media_group_id': media_group_id,
                    'message_id': update.effective_message.message_id,
                    'timestamp': update.effective_message.date.isoformat() if update.effective_message.date else None
                })
        else:
            # Одиночне фото з підписом
            history.append({
                'type': 'image_message',
                'user_id': update.effective_user.id,
                'username': update.effective_user.username or update.effective_user.first_name,
                'text': update.effective_message.caption or '[Зображення]',
                'image_count': 1,
                'message_id': update.effective_message.message_id,
                'timestamp': update.effective_message.date.isoformat() if update.effective_message.date else None
            })
    
    # Якщо це звичайне текстове повідомлення
    elif update.effective_message.text:
        history.append({
            'type': 'text_message',
            'user_id': update.effective_user.id,
            'username': update.effective_user.username or update.effective_user.first_name,
            'text': update.effective_message.text,
            'message_id': update.effective_message.message_id,
            'timestamp': update.effective_message.date.isoformat() if update.effective_message.date else None
        })
    
    # Обрізаємо до MAX_HISTORY
    history = history[-MAX_HISTORY:]
    context.chat_data['history'] = history


def add_image_message_to_history(context: ContextTypes.DEFAULT_TYPE, images: List[str], 
                                 caption: str, user_id: int, username: str, 
                                 media_group_id: Optional[str] = None, 
                                 message_id: Optional[int] = None,
                                 timestamp: Optional[str] = None) -> None:
    """
    Додає повідомлення з зображеннями до історії чату.
    Використовується smart_agent.py для додавання групових зображень.
    ВАЖЛИВО: НЕ викликати для зображень від бота (user_id не повинен бути None)
    """
    if 'history' not in context.chat_data:
        context.chat_data['history'] = []
    
    # Захист: не зберігаємо зображення від бота
    if user_id is None:
        logging.warning(f"[HISTORY] Відхилено спробу зберегти зображення від бота в історію")
        return
    
    history = context.chat_data['history']
    
    # Створюємо запис для зображень
    image_entry = {
        'type': 'image_message',
        'user_id': user_id,
        'username': username,
        'text': caption or f'[{len(images)} зображень]',
        'image_count': len(images),
        'images': images,  # Store the actual base64 image data
        'message_id': message_id,
        'timestamp': timestamp
    }
    
    if media_group_id:
        image_entry['media_group_id'] = media_group_id
    
    history.append(image_entry)
    
    # Обрізаємо до MAX_HISTORY
    history = history[-MAX_HISTORY:]
    context.chat_data['history'] = history
