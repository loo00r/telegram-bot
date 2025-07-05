from telegram import Update
from telegram.ext import ContextTypes
import re
import base64
import io
import os
import asyncio
from typing import Dict, List, Optional
import time

import logging
from telegram.constants import MessageEntityType
from openai import AsyncOpenAI
from config import OPENAI_API_KEY
from .history_logger import add_image_message_to_history

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Глобальний буфер для групування медіафайлів
media_group_buffer: Dict[str, Dict] = {}

# Буфер для нещодавніх зображень від користувачів (для контекстного реагування)
# Структура: {user_id: [{'image_base64': str, 'caption': str, 'timestamp': float, 'message_id': int}, ...]}
user_recent_images: Dict[int, List[Dict]] = {}

def store_image_in_buffer(user_id: int, image_base64: str, caption: str = "", message_id: int = None) -> None:
    """
    Зберігає зображення в буфер нещодавніх зображень користувача
    """
    global user_recent_images
    
    if user_id not in user_recent_images:
        user_recent_images[user_id] = []
    
    # Додаємо нове зображення
    user_recent_images[user_id].append({
        'image_base64': image_base64,
        'caption': caption,
        'timestamp': time.time(),
        'message_id': message_id
    })
    
    # Обмежуємо кількість зображень на користувача (максимум 5)
    user_recent_images[user_id] = user_recent_images[user_id][-5:]
    
    logging.warning(f"[IMAGE_BUFFER] Збережено зображення для користувача {user_id}, всього: {len(user_recent_images[user_id])}")


async def smart_agent_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler для смарт-агента: реагує на згадку бота в групі.
    """
    global user_recent_images
    
    bot_username = (await context.bot.get_me()).username
    message_text = update.effective_message.text or ""
    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id
    user_id = update.effective_user.id

    # Логування для діагностики
    logging.warning(f"[SMART_AGENT] username: {bot_username}, message: {message_text}, chat_id: {chat_id}, message_id: {message_id}")
    
    mentioned = False
    entities = getattr(update.effective_message, 'entities', None)
    if entities:
        for ent in entities:
            if ent.type in ("mention", MessageEntityType.MENTION):
                entity_text = message_text[ent.offset:ent.offset+ent.length]
                logging.warning(f"[SMART_AGENT] entity_text: {entity_text}")
                if entity_text.lower() == f"@{bot_username.lower()}":
                    mentioned = True
    # Додатково перевіряємо regex по тексту
    if re.search(rf"@{bot_username}\\b", message_text):
        logging.warning("[SMART_AGENT] regex спрацював")
        mentioned = True

    if mentioned:
        # --- Формування історії чату для промпта ---
        history = context.chat_data.get('history', [])[-30:]
        history_prompt = ""
        recent_images = []
        
        for msg in history:
            username = msg.get('username', 'user')
            text = msg.get('text', '')
            msg_type = msg.get('type', 'text_message')
            
            if msg_type == 'image_message':
                image_count = msg.get('image_count', 1)
                if image_count > 1:
                    text = f"[{image_count} зображень] {text}"
                else:
                    text = f"[Зображення] {text}"
                
                # Collect recent images for GPT-4o
                images = msg.get('images', [])
                if images:
                    recent_images.extend(images)
            
            history_prompt += f"[{username}]: {text}\n"
        
        # --- Перевіряємо нещодавні зображення від того ж користувача ---
        # Очищаємо старі зображення (старше 60 секунд)
        current_time = time.time()
        if user_id in user_recent_images:
            user_recent_images[user_id] = [
                img for img in user_recent_images[user_id] 
                if current_time - img['timestamp'] <= 60
            ]
            
            # Додаємо нещодавні зображення від цього користувача
            if user_recent_images[user_id]:
                logging.warning(f"[SMART_AGENT] Знайдено {len(user_recent_images[user_id])} нещодавніх зображень від користувача {user_id}")
                for img_data in user_recent_images[user_id]:
                    recent_images.append(img_data['image_base64'])
                    # Додаємо контекст про зображення в історію
                    caption = img_data.get('caption', '')
                    if caption:
                        history_prompt += f"[{update.effective_user.username or update.effective_user.first_name}]: [Зображення] {caption}\n"
                    else:
                        history_prompt += f"[{update.effective_user.username or update.effective_user.first_name}]: [Зображення]\n"
        # --- Системна інструкція ---
        system_instruction = (
        f"Ти — @{bot_username}, повноцінний фулстек-експерт із 20-річним досвідом розробки складних систем. "
        "Ти глибоко розумієш бекенд-архітектуру, фронтенд-розробку, API-дизайн, бази даних, "
        "а також чудово знаєш SysML-діаграми, принципи їх побудови та застосування у проєктуванні систем. "
        "Твоя головна задача — допомагати команді в розробці веб-застосунку для автоматичної генерації SysML-діаграм, "
        "давати рекомендації щодо архітектурних рішень, оцінювати підходи, аналізувати функціонал, "
        "пропонувати покращення, а також допомагати з вирішенням технічних проблем. "
        "Ти можеш аналізувати зображення, коментувати схеми, діаграми, скріншоти коду, або інші технічні матеріали. "
        "Ти маєш бути точним, критичним, об'єктивним та максимально практичним у відповідях. "
        "Відповідай стисло, по суті, з конкретними прикладами чи посиланнями на корисні ресурси, якщо потрібно. "
        "Можеш пропонувати альтернативні рішення або ставити уточнювальні запитання, коли контексту недостатньо. "
        "Якщо питання некоректне, чесно поясни чому. "
        "Мова спілкування: українська. "
        "Також буде історія чату, яка буде передаватися в промпт, і в ній будуть також твої відповіді, будь обьективним, "
        "якщо хтось буде намагатись звернутись до твоїх відповідей, то ти маєш враховувати цей контекст "
    )

        # --- Поточне питання (без згадки бота) ---
        user_question = message_text.replace(f"@{bot_username}", "").strip()
        # --- Формуємо фінальний промпт ---
        prompt = f"{system_instruction}\n\nІсторія чату (останні 30):\n{history_prompt}\nПитання: {user_question}\nВідповідь:"
        logging.warning(f"[SMART_AGENT] Згенерований промпт для OpenAI:\n{prompt}")

        # --- Відправка запиту до OpenAI ---
        response_text = None
        try:
            # Prepare user content
            user_content = f"Історія чату (останні 30):\n{history_prompt}\nПитання: {user_question}"
            
            # If there are recent images, use GPT-4o and include them
            if recent_images:
                # Limit to last 3 images to avoid token limits
                images_to_include = recent_images[-3:]
                
                # Create content with text and images
                content = [{"type": "text", "text": user_content}]
                
                for image_base64 in images_to_include:
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    })
                
                response = await client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": content}
                    ],
                    temperature=0.7,
                    max_tokens=512,
                )
                logging.warning(f"[SMART_AGENT] Використано GPT-4o з {len(images_to_include)} зображеннями")
            else:
                # Use GPT-4o-mini for text-only
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.7,
                    max_tokens=512,
                )
                logging.warning(f"[SMART_AGENT] Використано GPT-4o-mini для тексту")
            
            response_text = response.choices[0].message.content.strip()
            logging.warning(f"[SMART_AGENT] Відповідь OpenAI: {response_text}")
        except Exception as e:
            response_text = f"⚠️ Помилка при зверненні до OpenAI: {e}"
            logging.error(f"[SMART_AGENT] OpenAI error: {e}")

        # --- Відправляємо відповідь у чат ---
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=response_text,
                reply_to_message_id=message_id
            )
            logging.warning(f"[SMART_AGENT] Відповідь відправлено!")
            # --- Додаємо відповідь бота в історію ---
            if 'history' not in context.chat_data:
                context.chat_data['history'] = []
            context.chat_data['history'].append({
                'type': 'text_message',
                'user_id': None,
                'username': bot_username,
                'text': response_text,
                'message_id': None,
                'timestamp': None
            })
            context.chat_data['history'] = context.chat_data['history'][-30:]
        except Exception as e:
            logging.error(f"[SMART_AGENT] Помилка при відправці відповіді: {e}")


def is_bot_mentioned(message_text: str, bot_username: str, entities: Optional[List] = None) -> bool:
    """
    Перевіряє чи згадано бота в повідомленні
    """
    if not message_text:
        return False
        
    # Перевіряємо entities
    if entities:
        for ent in entities:
            if ent.type in ("mention", MessageEntityType.MENTION):
                entity_text = message_text[ent.offset:ent.offset+ent.length]
                if entity_text.lower() == f"@{bot_username.lower()}":
                    return True
    
    # Додатково перевіряємо regex
    if re.search(rf"@{bot_username}\b", message_text):
        return True
    
    return False


async def process_grouped_images(media_group_id: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обробляє групу зображень після збору всіх фото
    """
    global media_group_buffer
    
    if media_group_id not in media_group_buffer:
        return
    
    group_data = media_group_buffer[media_group_id]
    bot_username = group_data['bot_username']
    chat_id = group_data['chat_id']
    images = group_data['images']
    caption = group_data.get('caption', '')
    mentioned = group_data.get('mentioned', False)
    first_message_id = group_data.get('first_message_id')
    
    logging.warning(f"[PHOTO_HANDLER] Обробляємо групу {media_group_id} з {len(images)} зображеннями, mentioned={mentioned}")
    
    # Перевіряємо чи бота згадано
    if not mentioned:
        logging.warning(f"[PHOTO_HANDLER] Бота не згадано в групі {media_group_id}, пропускаємо")
        del media_group_buffer[media_group_id]
        return
    
    try:
        # Отримуємо останні 5 повідомлень як контекст
        history = context.chat_data.get('history', [])[-5:]
        context_text = ""
        for msg in history:
            username = msg.get('username', 'user')
            text = msg.get('text', '')
            context_text += f"[{username}]: {text}\n"
        
        # Системна інструкція
        system_instruction = (
            f"Ти — @{bot_username}, повноцінний фулстек-експерт із 20-річним досвідом розробки складних систем. "
            "Ти глибоко розумієш бекенд-архітектуру, фронтенд-розробку, API-дизайн, бази даних, "
            "а також чудово знаєш SysML-діаграми, принципи їх побудови та застосування у проєктуванні систем. "
            "Твоя головна задача — допомагати команді в розробці веб-застосунку для автоматичної генерації SysML-діаграм, "
            "аналізувати зображення, коментувати схеми, діаграми, скріншоти коду, або інші технічні матеріали. "
            "Ти маєш бути точним, критичним, об'єктивним та максимально практичним у відповідях. "
            "Відповідай стисло, по суті, з конкретними прикладами чи посиланнями на корисні ресурси, якщо потрібно. "
            "Мова спілкування: українська"
        )
        
        # Формуємо промпт з контекстом
        prompt_text = f"Контекст останніх повідомлень:\n{context_text}\n"
        if caption:
            prompt_text += f"Підпис до зображення: {caption}\n"
        
        if len(images) > 1:
            prompt_text += f"Проаналізуй {len(images)} зображень з урахуванням контексту повідомлень та дай відповідь."
        else:
            prompt_text += "Проаналізуй зображення з урахуванням контексту повідомлень та дай відповідь."
        
        # Формуємо контент для OpenAI
        content = [{"type": "text", "text": prompt_text}]
        
        # Додаємо всі зображення
        for image_base64 in images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }
            })
        
        # Відправляємо запит до GPT-4o
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": content}
            ],
            temperature=0.7,
            max_tokens=512,
        )
        
        response_text = response.choices[0].message.content.strip()
        logging.warning(f"[PHOTO_HANDLER] Відповідь GPT-4o для групи {media_group_id}: {response_text}")
        
        # Відправляємо відповідь у чат
        await context.bot.send_message(
            chat_id=chat_id,
            text=response_text,
            reply_to_message_id=first_message_id
        )
        
        # Додаємо відповідь бота в історію
        if 'history' not in context.chat_data:
            context.chat_data['history'] = []
        context.chat_data['history'].append({
            'type': 'text_message',
            'user_id': None,
            'username': bot_username,
            'text': response_text,
            'message_id': None,
            'timestamp': None
        })
        context.chat_data['history'] = context.chat_data['history'][-30:]
        
        # Додаємо запис про групове зображення в історію
        add_image_message_to_history(
            context=context,
            images=images,
            caption=caption,
            user_id=group_data.get('user_id'),
            username=group_data.get('username', 'user'),
            media_group_id=media_group_id,
            message_id=first_message_id,
            timestamp=group_data.get('timestamp')
        )
        
        logging.warning(f"[PHOTO_HANDLER] Відповідь на групу фото відправлено!")
        
    except Exception as e:
        error_text = f"⚠️ Помилка при обробці зображень: {e}"
        logging.error(f"[PHOTO_HANDLER] Помилка при обробці групи {media_group_id}: {e}")
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=error_text,
                reply_to_message_id=first_message_id
            )
        except Exception as send_error:
            logging.error(f"[PHOTO_HANDLER] Помилка при відправці повідомлення про помилку: {send_error}")
    
    finally:
        # Видаляємо групу з буфера
        if media_group_id in media_group_buffer:
            del media_group_buffer[media_group_id]


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler для обробки фотографій з контекстом тексту через GPT-4o
    Тепер підтримує групування медіафайлів та реагує тільки на згадки бота
    """
    global media_group_buffer
    
    bot_username = (await context.bot.get_me()).username
    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id
    caption = update.effective_message.caption or ""
    media_group_id = update.effective_message.media_group_id
    
    logging.warning(f"[PHOTO_HANDLER] Отримано фото в чаті {chat_id}, media_group_id={media_group_id}")
    
    # Перевіряємо згадку бота в підписі
    mentioned = is_bot_mentioned(caption, bot_username, update.effective_message.entities)
    
    try:
        # Отримуємо найбільшу версію фото
        photo = update.effective_message.photo[-1]
        
        # Завантажуємо фото
        file = await context.bot.get_file(photo.file_id)
        
        # Завантажуємо файл в пам'ять
        file_data = io.BytesIO()
        await file.download_to_memory(file_data)
        file_data.seek(0)
        
        # Кодуємо в base64
        image_base64 = base64.b64encode(file_data.read()).decode('utf-8')
        
        # Якщо це частина медіа-групи
        if media_group_id:
            # Ініціалізуємо групу якщо не існує
            if media_group_id not in media_group_buffer:
                media_group_buffer[media_group_id] = {
                    'bot_username': bot_username,
                    'chat_id': chat_id,
                    'images': [],
                    'caption': caption,
                    'mentioned': mentioned,
                    'first_message_id': message_id,
                    'last_update': asyncio.get_event_loop().time(),
                    'user_id': update.effective_user.id,
                    'username': update.effective_user.username or update.effective_user.first_name,
                    'timestamp': update.effective_message.date.isoformat() if update.effective_message.date else None
                }
            
            # Додаємо зображення до групи
            media_group_buffer[media_group_id]['images'].append(image_base64)
            
            # Також зберігаємо в буфер користувача для контекстного реагування
            user_id = update.effective_user.id
            store_image_in_buffer(user_id, image_base64, caption, message_id)
            
            # Оновлюємо згадку та підпис (якщо в поточному повідомленні є згадка)
            if mentioned and not media_group_buffer[media_group_id]['mentioned']:
                media_group_buffer[media_group_id]['mentioned'] = True
            
            if caption and not media_group_buffer[media_group_id]['caption']:
                media_group_buffer[media_group_id]['caption'] = caption
            
            media_group_buffer[media_group_id]['last_update'] = asyncio.get_event_loop().time()
            
            # Запускаємо таймер для обробки групи (2 секунди затримки)
            await asyncio.sleep(2)
            
            # Перевіряємо чи група ще існує та чи минуло достатньо часу
            if (media_group_id in media_group_buffer and 
                asyncio.get_event_loop().time() - media_group_buffer[media_group_id]['last_update'] >= 1.5):
                await process_grouped_images(media_group_id, context)
        
        # Якщо це окреме фото (не частина групи)
        else:
            # Зберігаємо зображення в буфер навіть якщо бота не згадано
            user_id = update.effective_user.id
            store_image_in_buffer(user_id, image_base64, caption, message_id)
            
            # Перевіряємо чи бота згадано
            if not mentioned:
                logging.warning(f"[PHOTO_HANDLER] Бота не згадано в одиночному фото, зберігаємо в буфер")
                return
            
            # Обробляємо як одиночне фото
            await process_single_image(image_base64, caption, chat_id, message_id, bot_username, context)
        
    except Exception as e:
        error_text = f"⚠️ Помилка при обробці зображення: {e}"
        logging.error(f"[PHOTO_HANDLER] Помилка: {e}")
        if mentioned:  # Показуємо помилку тільки якщо бота згадано
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=error_text,
                    reply_to_message_id=message_id
                )
            except Exception as send_error:
                logging.error(f"[PHOTO_HANDLER] Помилка при відправці повідомлення про помилку: {send_error}")


async def process_single_image(image_base64: str, caption: str, chat_id: int, message_id: int, bot_username: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обробляє одиночне зображення
    """
    try:
        # Отримуємо останні 5 повідомлень як контекст
        history = context.chat_data.get('history', [])[-5:]
        context_text = ""
        for msg in history:
            username = msg.get('username', 'user')
            text = msg.get('text', '')
            context_text += f"[{username}]: {text}\n"
        
        # Системна інструкція
        system_instruction = (
            f"Ти — @{bot_username}, повноцінний фулстек-експерт із 20-річним досвідом розробки складних систем. "
            "Ти глибоко розумієш бекенд-архітектуру, фронтенд-розробку, API-дизайн, бази даних, "
            "а також чудово знаєш SysML-діаграми, принципи їх побудови та застосування у проєктуванні систем. "
            "Твоя головна задача — допомагати команді в розробці веб-застосунку для автоматичної генерації SysML-діаграм, "
            "аналізувати зображення, коментувати схеми, діаграми, скріншоти коду, або інші технічні матеріали. "
            "Ти маєш бути точним, критичним, об'єктивним та максимально практичним у відповідях. "
            "Відповідай стисло, по суті, з конкретними прикладами чи посиланнями на корисні ресурси, якщо потрібно. "
            "Мова спілкування: українська"
        )
        
        # Формуємо промпт з контекстом
        prompt_text = f"Контекст останніх повідомлень:\n{context_text}\n"
        if caption:
            prompt_text += f"Підпис до зображення: {caption}\n"
        prompt_text += "Проаналізуй зображення з урахуванням контексту повідомлень та дай відповідь."
        
        # Відправляємо запит до GPT-4o з зображенням
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_instruction},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.7,
            max_tokens=512,
        )
        
        response_text = response.choices[0].message.content.strip()
        logging.warning(f"[PHOTO_HANDLER] Відповідь GPT-4o: {response_text}")
        
        # Відправляємо відповідь у чат
        await context.bot.send_message(
            chat_id=chat_id,
            text=response_text,
            reply_to_message_id=message_id
        )
        
        # Додаємо відповідь бота в історію
        if 'history' not in context.chat_data:
            context.chat_data['history'] = []
        context.chat_data['history'].append({
            'type': 'text_message',
            'user_id': None,
            'username': bot_username,
            'text': response_text,
            'message_id': None,
            'timestamp': None
        })
        context.chat_data['history'] = context.chat_data['history'][-30:]
        
        logging.warning(f"[PHOTO_HANDLER] Відповідь на одиночне фото відправлено!")
        
    except Exception as e:
        error_text = f"⚠️ Помилка при обробці зображення: {e}"
        logging.error(f"[PHOTO_HANDLER] Помилка при обробці одиночного фото: {e}")
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=error_text,
                reply_to_message_id=message_id
            )
        except Exception as send_error:
            logging.error(f"[PHOTO_HANDLER] Помилка при відправці повідомлення про помилку: {send_error}")
