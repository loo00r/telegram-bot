from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import EMOJIS
from utils.jira_client import jira_client

# Імпортуємо стани з start
from .start import MAIN_MENU, TASKS, DIAGRAMS, SETTINGS

# Стани для ConversationHandler
TASK_ACTION, CREATE_TASK_SUMMARY, CREATE_TASK_DESCRIPTION = range(3)

import os

async def tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Головне меню завдань"""
    if not jira_client.is_connected():
        if update.message:
            await update.message.reply_text(
                f"{EMOJIS['error']} Помилка підключення до Jira. "
                "Перевірте налаштування Jira у файлі .env"
            )
        elif update.callback_query:
            await update.callback_query.message.reply_text(
                f"{EMOJIS['error']} Помилка підключення до Jira. "
                "Перевірте налаштування Jira у файлі .env"
            )
        return MAIN_MENU
    
    # Отримуємо задачі з Jira
    issues_text = jira_client.get_my_issues()

    # Виводимо chat_id для діагностики
    print(f"chat_id: {update.effective_chat.id}")

    # Надсилаємо задачі у канал
    channel_id = os.getenv("CHANNEL_ID", None)
    if channel_id:
        try:
            await context.bot.send_message(chat_id=channel_id, text=issues_text, parse_mode='Markdown')
            confirmation = f"{EMOJIS['success']} Завдання надіслано у канал!"
        except Exception as e:
            confirmation = f"{EMOJIS['error']} Не вдалося надіслати у канал: {e}"
    else:
        confirmation = f"{EMOJIS['error']} Не вказано CHANNEL_ID у .env"

    # Відповідаємо користувачу-початківцю
    if update.message:
        await update.message.reply_text(confirmation)
    elif update.callback_query:
        await update.callback_query.edit_message_text(confirmation)

    return TASK_ACTION

async def task_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка дій у меню завдань"""
    if not update.callback_query:
        return TASK_ACTION
        
    query = update.callback_query
    await query.answer()
    
    if query.data == 'my_tasks':
        try:
            issues = jira_client.get_my_issues()
            await query.edit_message_text(
                issues,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"{EMOJIS['back']} Назад", callback_data='back')]
                ])
            )
            return MAIN_MENU
        except Exception as e:
            await query.edit_message_text(
                f"{EMOJIS['error']} Помилка отримання завдань: {str(e)}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"{EMOJIS['back']} Назад", callback_data='back')]
                ])
            )
            return MAIN_MENU
        
    elif query.data == 'create_task':
        await query.edit_message_text(
            f"{EMOJIS['task']} Введіть короткий опис завдання:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{EMOJIS['cancel']} Скасувати", callback_data='cancel')]
            ])
        )
        return CREATE_TASK_SUMMARY
        
    elif query.data == 'back':
        from .start import start
        return await start(update, context)
        
    return TASK_ACTION

async def create_task_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка введення короткого опису завдання"""
    if not update.message or not update.message.text:
        return CREATE_TASK_SUMMARY
        
    summary = update.message.text
    context.user_data['task_summary'] = summary
    
    await update.message.reply_text(
        f"{EMOJIS['task']} Введіть детальний опис завдання:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{EMOJIS['cancel']} Скасувати", callback_data='cancel')]
        ])
    )
    
    return CREATE_TASK_DESCRIPTION

async def create_task_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка введення детального опису та створення завдання"""
    if not update.message or not update.message.text:
        return CREATE_TASK_DESCRIPTION
        
    description = update.message.text
    summary = context.user_data.get('task_summary', '')
    
    if not summary:
        await update.message.reply_text(
            f"{EMOJIS['error']} Помилка: не знайдено опис завдання. Спробуйте ще раз.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{EMOJIS['back']} Назад", callback_data='back')]
            ])
        )
        return CREATE_TASK_SUMMARY
    
    try:
        issue_key = jira_client.create_issue(summary, description)
        await update.message.reply_text(
            f"{EMOJIS['success']} Завдання створено: {issue_key}\n"
            f"{EMOJIS['task']} {summary}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{EMOJIS['back']} Назад до меню", callback_data='back')]
            ])
        )
    except Exception as e:
        await update.message.reply_text(
            f"{EMOJIS['error']} Помилка створення завдання: {str(e)}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{EMOJIS['back']} Назад", callback_data='back')]
            ])
        )
    
    # Очищаємо дані завдання
    if 'task_summary' in context.user_data:
        del context.user_data['task_summary']
    
    return MAIN_MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Скасування поточної операції"""
    if 'task_summary' in context.user_data:
        del context.user_data['task_summary']
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            f"{EMOJIS['info']} Операцію скасовано.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{EMOJIS['back']} Назад до меню", callback_data='back')]
            ])
        )
    elif update.message:
        await update.message.reply_text(
            f"{EMOJIS['info']} Операцію скасовано.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{EMOJIS['back']} Назад до меню", callback_data='back')]
            ])
        )
    
    return MAIN_MENU

# Створюємо ConversationHandler для роботи з завданнями
tasks_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('tasks', tasks)],
    states={
        TASK_ACTION: [CallbackQueryHandler(task_action)],
        CREATE_TASK_SUMMARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_task_summary)],
        CREATE_TASK_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_task_description)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)