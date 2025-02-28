from aiogram import Bot
from aiogram.types import Message
from core.utils.dbconnect import Request

async def get_start(message: Message, bot: Bot, request: Request):
    await request.add_data(message.from_user.id, message.from_user.first_name)
    await bot.send_message(message.from_user.id, f'Привет {message.from_user.first_name}. Спасибо за подписку!')
