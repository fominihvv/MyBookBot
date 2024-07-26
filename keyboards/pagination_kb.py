from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON


# Создание клавиатуры для чтения книги (<< 1 / ... >>)
def create_pagination_keyboard(*buttons: str) -> InlineKeyboardMarkup:
    button_no_data = InlineKeyboardButton(text='    ', callback_data='no_data')
    kb_builder = InlineKeyboardBuilder()
    first_page, last_page = buttons[1].split(' / ')
    kb_buttons = []
    if first_page == '1':
        kb_buttons.append(button_no_data)
    else:
        kb_buttons.append(InlineKeyboardButton(
            text=LEXICON['backward'],
            callback_data=buttons[0]))
    kb_buttons.append(InlineKeyboardButton(
        text=buttons[1],
        callback_data=buttons[1])
    )
    if first_page == last_page:
        kb_buttons.append(button_no_data)
    else:
        kb_buttons.append(InlineKeyboardButton(
            text=LEXICON['forward'],
            callback_data=buttons[2]))

    kb_builder.row(*kb_buttons)
    return kb_builder.as_markup()
