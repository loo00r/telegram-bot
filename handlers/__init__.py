from .start import MAIN_MENU, TASKS, DIAGRAMS, SETTINGS
from .tasks import tasks_conv_handler

# Імпортуємо лише необхідні константи, щоб уникнути циклічних імпортів
__all__ = [
    'tasks_conv_handler',
    'MAIN_MENU',
    'TASKS',
    'DIAGRAMS',
    'SETTINGS'
]