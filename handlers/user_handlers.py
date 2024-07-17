import logging
from copy import deepcopy

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup

from config_data.config import MAX_BOOKMARK
from databases.db_methods import users_db, user_dict_template
from keyboards.bookmark_kb import create_bookmark_keyboard
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


# Проверка на нового пользователя и добавление его в базу данных
async def check_new_user(message) -> None:
    if message.from_user.id not in users_db:
        logger_user_handlers.info(f'Пользователь {message.from_user.id} добавлен в базу данных')
        users_db[message.from_user.id] = deepcopy(user_dict_template)


# Запуск бота
@router_user_handlers.message(CommandStart())
async def process_start_command(message: Message):
    logger_user_handlers.info(f'Пользователь {message.from_user.id} запустил бота')
    await check_new_user(message)
    await message.answer(text=LEXICON['/start'])


# Вызов подсказки
@router_user_handlers.message(Command('help'))
async def process_start_command(message: Message):
    logging_command(message)
    await message.answer(text=LEXICON['/help'])


@router_user_handlers.message(Command('cancel'))
async def process_start_command(message: Message):
    logging_command(message)
    await message.answer(text='Заглушка для команды /cancel')


# Вызов списка закладок
@router_user_handlers.message(Command('bookmarks'))
async def process_start_command(message: Message):
    logging_command(message)
    if users_db[message.from_user.id]['bookmarks']:
        await message.answer(text=LEXICON['/bookmarks'],
                             reply_markup=create_bookmark_keyboard(users_db[message.from_user.id]['bookmarks']))
    else:
        await message.answer(text=LEXICON['no_bookmarks'])


# Чтение книги с начала
@router_user_handlers.message(Command('beginning'))
async def process_start_command(message: Message):
    logging_command(message)
    await check_new_user(message)
    users_db[message.from_user.id]['page'] = 1
    await message.answer(text=book[users_db[message.from_user.id]['page']], reply_markup=make_bf_kb(message))


# Чтение книги с сохраненной страницы
@router_user_handlers.message(Command('continue'))
async def process_start_command(message: Message):
    logging_command(message)
    await check_new_user(message)
    await message.answer(text=book[users_db[message.from_user.id]['page']], reply_markup=make_bf_kb(message))


# Предыдущая страница
@router_user_handlers.callback_query(F.data == 'backward')
async def backward(callback: CallbackQuery):
    logging_command(callback.message)
    await check_new_user(callback)
    if users_db[callback.from_user.id]['page'] > 1:
        users_db[callback.from_user.id]['page'] -= 1
        await callback.message.edit_text(text=book[users_db[callback.from_user.id]['page']],
                                         reply_markup=make_bf_kb(callback))


# Следующая страница
@router_user_handlers.callback_query(F.data == 'forward')
async def forward(callback: CallbackQuery):
    logging_command(callback.message)
    await check_new_user(callback)
    if users_db[callback.from_user.id]['page'] < len(book):
        users_db[callback.from_user.id]['page'] += 1
        await callback.message.edit_text(text=book[users_db[callback.from_user.id]['page']],
                                         reply_markup=make_bf_kb(callback))


# Страница по номеру
@router_user_handlers.callback_query(lambda x: x.data.isdigit())
async def go_to_page(callback: CallbackQuery):
    logging_command(callback.message)
    await check_new_user(callback)
    page = int(callback.data)
    users_db[callback.from_user.id]['page'] = page
    await callback.message.edit_text(text=book[page], reply_markup=make_bf_kb(callback))


# Добавление закладки
@router_user_handlers.callback_query(lambda x: '/' in x.data and x.data.replace(' / ', '').isdigit())
async def add_bookmarks(callback: CallbackQuery):
    logging_command(callback.message)
    await check_new_user(callback)
    if len(users_db[callback.from_user.id]['bookmarks']) >= MAX_BOOKMARK:
        await callback.answer(text=LEXICON['max_bookmarks'])
    else:
        users_db[callback.from_user.id]['bookmarks'].add(users_db[callback.from_user.id]['page'])
        await callback.answer(text=LEXICON['added_bookmarks'])


# Редактирование закладок
@router_user_handlers.callback_query(F.data == 'edit_bookmarks')
async def cancel(callback: CallbackQuery):
    logging_command(callback.message)
    await callback.answer(text=LEXICON['edit_bookmarks'])
