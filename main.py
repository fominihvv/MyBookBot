import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
# from databases import db_methods
from aiogram.enums import ParseMode

from config_data.config import config
from handlers import user_handlers, other_handlers
from keyboards.main_menu import set_main_menu
from services import work_with_book


async def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Инициализируем бот и диспетчер')
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # logger.info('Проверяем наличие баз данных')
    # await db_methods.db_check()

    logger.info('Настраиваем главное меню бота')
    await set_main_menu(bot)

    logger.info('Регистрируем роутеры в диспетчере')
    dp.include_router(user_handlers.router_user_handlers)
    dp.include_router(other_handlers.router_other_handlers)

    logger.info('Подготавливаем книгу')
    work_with_book.prepare_book()

    logger.info('Удаляем накопившиеся апдейты')
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info('Запускаем бота')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
