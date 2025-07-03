from telegram import Update
from telegram.ext import ContextTypes
import re

import logging
from telegram.constants import MessageEntityType
from openai import AsyncOpenAI
from config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def smart_agent_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler для смарт-агента: реагує на згадку бота в групі.
    """
    bot_username = (await context.bot.get_me()).username
    message_text = update.effective_message.text or ""
    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id

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
        for msg in history:
            username = msg.get('username', 'user')
            text = msg.get('text', '')
            history_prompt += f"[{username}]: {text}\n"
        # --- Системна інструкція ---
        system_instruction = (
        f"Ти — @{bot_username}, повноцінний фулстек-експерт із 20-річним досвідом розробки складних систем. "
        "Ти глибоко розумієш бекенд-архітектуру, фронтенд-розробку, API-дизайн, бази даних, "
        "а також чудово знаєш SysML-діаграми, принципи їх побудови та застосування у проєктуванні систем. "
        "Твоя головна задача — допомагати команді в розробці веб-застосунку для автоматичної генерації SysML-діаграм, "
        "давати рекомендації щодо архітектурних рішень, оцінювати підходи, аналізувати функціонал, "
        "пропонувати покращення, а також допомагати з вирішенням технічних проблем. "
        "Ти маєш бути точним, критичним, об'єктивним та максимально практичним у відповідях. "
        "Відповідай стисло, по суті, з конкретними прикладами чи посиланнями на корисні ресурси, якщо потрібно. "
        "Можеш пропонувати альтернативні рішення або ставити уточнювальні запитання, коли контексту недостатньо. "
        "Якщо питання некоректне, чесно поясни чому. "
        "Мова спілкування: українська"
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
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": f"Історія чату (останні 30):\n{history_prompt}\nПитання: {user_question}"}
                ],
                temperature=0.7,
                max_tokens=512,
            )
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
                'username': bot_username,
                'text': response_text,
            })
            context.chat_data['history'] = context.chat_data['history'][-30:]
        except Exception as e:
            logging.error(f"[SMART_AGENT] Помилка при відправці відповіді: {e}")
