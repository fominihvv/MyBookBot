from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config_data.config import book
from lexicon.lexicon import LEXICON


# Создание клавиатуры для управления закладками
def create_bookmark_keyboard(buttons: tuple) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    for button in sorted(buttons):
        kb_builder.row(InlineKeyboardButton(
            text=f'стр.{button} - {book[button][:50]}...',
            callback_data=f'{button}')
        )

    kb_builder.row(InlineKeyboardButton(
        text=LEXICON['edit_bookmarks_button'],
        callback_data='edit_bookmarks')
    )
    return kb_builder.as_markup()
