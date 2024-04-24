import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fluentogram import TranslatorHub

from config_data.config import Config, load_config
from handlers import other, main_handler, lobby, game, tokens
from middlewares.i18n import TranslatorRunnerMiddleware
from utils.i18n import create_translator_hub

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s'
    )

    logger.info('Starting bot')

    config: Config = load_config()

    bot = Bot(token=config.tg_bot.token,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML)
              )
    dp = Dispatcher()

    translator_hub: TranslatorHub = create_translator_hub()

    dp.include_router(main_handler.router)
    dp.include_router(lobby.router)
    dp.include_router(tokens.router)
    dp.include_router(game.router)
    dp.include_router(other.router)

    dp.update.middleware(TranslatorRunnerMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, _translator_hub=translator_hub)

if __name__ == '__main__':
    asyncio.run(main())