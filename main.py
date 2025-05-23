import asyncio
import logging
import asyncpg
import contextlib

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command

from core.handlers.basic import get_start
from core.middlewares.dbmiddleware import DbSession
from core.settings import settings
from core.utils.commands import set_command
from core.handlers import sender
from core.utils.sender_list import SenderList
from core.utils.sender_state import Steps

async def start_bot(bot: Bot):
    await bot.send_message(settings.bots.admin_id, text='Бот запущен!')
    pass
async def stop_bot(bot: Bot):
    await bot.send_message(settings.bots.admin_id, text='Бот остановлен!')

async def create_pool():
    return await asyncpg.create_pool(user=settings.db.db_user, password=settings.db.db_password, database=settings.db.db_database, host=settings.db.db_host, port=5432, command_timeout=60)



async def start():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(name)s - ' "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")
    bot = Bot(token=settings.bots.bot_token, parse_mode='HTML')
    pool_connect = await create_pool()
    dp = Dispatcher()

    dp.update.middleware.register(DbSession(pool_connect))
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.message.register(sender.get_sender, Command(commands='sender', magic=F.args), F.chat.id==settings.bots.admin_id)

    dp.message.register(sender.get_message, Steps.get_message, F.chat.id == settings.bots.admin_id)

    dp.callback_query.register(sender.q_button,Steps.q_button)

    dp.message.register(sender.get_text_button, Steps.get_text_button, F.chat.id == settings.bots.admin_id)

    dp.message.register(sender.get_url_button, Steps.get_url_button, F.chat.id == settings.bots.admin_id, F.text)

    dp.callback_query.register(sender.sender_decide, F.data.in_(['confirm_sender', 'cancel_sender']))

    sender_list = SenderList(bot, pool_connect)




    dp.message.register(get_start)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), senderlist=sender_list)
    except Exception as ex:
        logging.error(f"[!!! Exception] - {ex}", exc_info=True)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(start())
