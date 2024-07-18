from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config_data.config import book
from lexicon.lexicon import LEXICON


def create_bookmark_kb(buttons: tuple, letter: str) -> InlineKeyboardBuilder:
    kb_builder = InlineKeyboardBuilder()
    for button in sorted(buttons):
        kb_builder.row(InlineKeyboardButton(
            text=f'{letter}стр.{button} - {book[button][:50]}...',
            callback_data=f'{letter}{button}')
        )
    return kb_builder


# Создание клавиатуры для управления закладками
def create_bookmark_keyboard(buttons: tuple) -> InlineKeyboardMarkup:
    kb_builder = create_bookmark_kb(buttons, '')
    kb_builder.row(InlineKeyboardButton(
        text=LEXICON['edit_bookmarks_button'],
        callback_data='edit_bookmarks')
    )
    return kb_builder.as_markup()


def create_edit_bookmark_keyboard(buttons: tuple) -> InlineKeyboardMarkup:
    kb_builder = create_bookmark_kb(buttons, LEXICON['del'])
    kb_builder.row(InlineKeyboardButton(
            text=LEXICON['save'],
            callback_data='save_edit_bookmarks'),
        InlineKeyboardButton(
            text=LEXICON['cancel'],
            callback_data='cancel_edit_bookmarks')
    )
    return kb_builder.as_markup()
