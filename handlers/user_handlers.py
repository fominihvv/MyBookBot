import logging
from copy import deepcopy

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup

from config_data.config import MAX_BOOKMARK
from databases.db_methods import users_db, user_dict_template
from keyboards.bookmark_kb import create_bookmark_keyboard, create_edit_bookmark_keyboard
from keyboards.pagination_kb import create_pagination_keyboard
from lexicon.lexicon import LEXICON
from services.work_with_book import book

logger_user_handlers = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')

router_user_handlers = Router()


# Создание клавиатуры для управления страницами
def make_bf_kb(message: (Message, CallbackQuery)) -> InlineKeyboardMarkup:
    return create_pagination_keyboard('backward', f'{users_db[message.from_user.id]["page"]} / {len(book)}', 'forward')


# Логирование команд
def logging_command(message) -> None:
    logger_user_handlers.debug(f'Пользователь {message.from_user.id} ввёл команду {message.text}')


# Проверка пользователя на наличие в базе данных
async def check_user(message) -> bool:
    logger_user_handlers.debug(f'Проверка пользователя {message.from_user.id} на наличие в базе данных')
    return message.from_user.id in users_db


# Создание нового пользователя
async def create_new_user(message) -> None:
    logger_user_handlers.info(f'Пользователь {message.from_user.id} добавлен в базу данных')
    users_db[message.from_user.id] = deepcopy(user_dict_template)


# Запуск бота
@router_user_handlers.message(CommandStart())
async def process_start_command(message: Message):
    logger_user_handlers.info(f'Пользователь {message.from_user.id} запустил бота')
    if not await check_user(message):
        await create_new_user(message)
    await message.answer(text=LEXICON['/start'])


# Вызов подсказки
@router_user_handlers.message(Command('help'))
async def process_start_command(message: Message):
    logging_command(message)
    await message.answer(text=LEXICON['/help'])


# Вызов списка закладок
@router_user_handlers.message(Command('bookmarks'))
async def process_start_command(message: Message):
    logging_command(message)
    if await check_user(message):
        if users_db[message.from_user.id]['bookmarks']:
            await message.answer(text=LEXICON['/bookmarks'],
                                 reply_markup=create_bookmark_keyboard(users_db[message.from_user.id]['bookmarks']))
        else:
            await message.answer(text=LEXICON['no_bookmarks'])
    else:
        await message.answer(text=LEXICON['no_bookmarks'])


# Чтение книги с начала
@router_user_handlers.message(Command('beginning'))
async def process_start_command(message: Message):
    logging_command(message)
    if not await check_user(message):
        await create_new_user(message)
    users_db[message.from_user.id]['page'] = 1
    await message.answer(text=book[users_db[message.from_user.id]['page']], reply_markup=make_bf_kb(message))


# Чтение книги с сохраненной страницы
@router_user_handlers.message(Command('continue'))
async def process_start_command(message: Message):
    logging_command(message)
    if not await check_user(message):
        await create_new_user(message)
    await message.answer(text=book[users_db[message.from_user.id]['page']], reply_markup=make_bf_kb(message))


# Предыдущая страница
@router_user_handlers.callback_query(F.data == 'backward')
async def backward(callback: CallbackQuery):
    logging_command(callback.message)
    if await check_user(callback):
        if users_db[callback.from_user.id]['page'] > 1:
            users_db[callback.from_user.id]['page'] -= 1
            await callback.message.edit_text(text=book[users_db[callback.from_user.id]['page']],
                                             reply_markup=make_bf_kb(callback))


# Следующая страница
@router_user_handlers.callback_query(F.data == 'forward')
async def forward(callback: CallbackQuery):
    logging_command(callback.message)
    if await check_user(callback):
        if users_db[callback.from_user.id]['page'] < len(book):
            users_db[callback.from_user.id]['page'] += 1
            await callback.message.edit_text(text=book[users_db[callback.from_user.id]['page']],
                                             reply_markup=make_bf_kb(callback))


# Страница по номеру
@router_user_handlers.callback_query(lambda x: x.data.isdigit())
async def go_to_page(callback: CallbackQuery):
    logging_command(callback.message)
    if await check_user(callback):
        page = int(callback.data)
        users_db[callback.from_user.id]['page'] = page
        await callback.message.edit_text(text=book[page], reply_markup=make_bf_kb(callback))


# Добавление закладки
@router_user_handlers.callback_query(lambda x: '/' in x.data and x.data.replace(' / ', '').isdigit())
async def add_bookmarks(callback: CallbackQuery):
    logging_command(callback.message)
    if await check_user(callback):
        if len(users_db[callback.from_user.id]['bookmarks']) >= MAX_BOOKMARK:
            await callback.answer(text=LEXICON['max_bookmarks'])
        else:
            users_db[callback.from_user.id]['bookmarks'].add(users_db[callback.from_user.id]['page'])
            await callback.answer(text=LEXICON['added_bookmarks'])


# Старт редактирование закладок
@router_user_handlers.callback_query(F.data == 'edit_bookmarks')
async def cancel(callback: CallbackQuery):
    logging_command(callback.message)
    if await check_user(callback):
        users_db[callback.from_user.id]['bookmarks_copy'] = users_db[callback.from_user.id]['bookmarks'].copy()
        await callback.message.edit_text(text=LEXICON['/bookmarks'],
                                         reply_markup=create_edit_bookmark_keyboard(
                                             users_db[callback.from_user.id]['bookmarks_copy']))


# Сохранение отредактированных закладок
@router_user_handlers.callback_query(F.data == 'save_edit_bookmarks')
async def save_edit_bookmarks(callback: CallbackQuery):
    logging_command(callback.message)
    if await check_user(callback):
        await callback.answer(text=LEXICON['save_bookmarks_edit'])
        users_db[callback.from_user.id]['bookmarks'] = users_db[callback.from_user.id]['bookmarks_copy']
        await callback.message.edit_text(text=book[users_db[callback.from_user.id]['page']],
                                         reply_markup=make_bf_kb(callback))


# Отмена редактирования закладок
@router_user_handlers.callback_query(F.data == 'cancel_edit_bookmarks')
async def cancel_edit_bookmarks(callback: CallbackQuery):
    logging_command(callback.message)
    if await check_user(callback):
        await callback.answer(text=LEXICON['cancel_bookmarks_edit'])
        await callback.message.edit_text(text=book[users_db[callback.from_user.id]['page']],
                                         reply_markup=make_bf_kb(callback))


# Удаление закладки
@router_user_handlers.callback_query(F.data.startswith(LEXICON['del']))
async def del_bookmark(callback: CallbackQuery):
    logging_command(callback.message)
    if await check_user(callback):
        page = int(callback.data[1:])
        users_db[callback.from_user.id]['bookmarks_copy'].remove(page)
        await callback.message.edit_text(text=LEXICON['/bookmarks'],
                                         reply_markup=create_edit_bookmark_keyboard(
                                             users_db[callback.from_user.id]['bookmarks_copy']))
