from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.work_with_book import book


# Создание клавиатуры для управления закладками
def create_bookmark_keyboard(buttons: tuple) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    for button in sorted(buttons):
        kb_builder.row(InlineKeyboardButton(
            text=f'стр.{button} - {book[button][:50]}...',
            callback_data=f'bookmark,{button}'))
    return kb_builder.as_markup()
