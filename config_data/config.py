import asyncio
import logging
from dataclasses import dataclass

from environs import Env

logger = logging.getLogger(__name__)
db_lock = asyncio.Lock()
MAX_BOOKMARK = 20

book_path = 'books/book.txt'
book: dict[int, str] = {}
PAGE_SIZE = 1050


@dataclass
class LocalDatabaseConfig:
    database: str
    database_path: str


@dataclass
class TgBot:
    token: str


@dataclass
class Config:
    tg_bot: TgBot
    db: LocalDatabaseConfig


def load_config(path: str | None = None) -> Config:
    try:
        logger.info('Загрузка конфигурации из .env')
        env: Env = Env()
        env.read_env(path)
    except FileNotFoundError:
        logger.critical('Файл .env отсутствует. Программа будет остановлена')
        raise SystemExit

    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN')
        ),
        db=LocalDatabaseConfig(
            database=env('database'),
            database_path=env('database_path')
        )
    )


config = load_config('.env')
