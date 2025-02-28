import asyncio

from aiogram import Bot
import asyncpg
from aiogram.exceptions import TelegramRetryAfter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asyncpg import Record
from typing import List
from aiogram.types import InlineKeyboardMarkup

class SenderList:
    def __init__(self, bot: Bot, connector: asyncpg.pool.Pool):
        self.bot = bot
        self.connector = connector

    async def get_keyboard(self, text_button, url_button):
        keyboard_builder = InlineKeyboardBuilder()
        keyboard_builder.button(text=text_button, url = url_button)
        keyboard_builder.adjust(1)
        return keyboard_builder.as_markup()

    async def get_users(self, name_camp):
        async with self.connector.acquire() as connect:
            query = f"SELECT user_id FROM {name_camp} WHERE statuse = 'waiting'"
            results_query: List[Record] = await connect.fetch(query)
            return [result.get('user_id') for result in results_query]

    async def update_statuse(self, table_name, user_id, statuse):
        async with self.connector.acquire() as connect:
            query = f"UPDATE {table_name} SET statuse='{statuse}' WHERE user_id ={user_id}"
            await connect.execute(query)

    async def send_message(self, user_id: int, from_chat_id: int, message_id: int, name_camp: str, keyboard: InlineKeyboardMarkup):
        try:
            await self.bot.copy_message(user_id, from_chat_id, message_id, reply_markup=keyboard)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            return await self.send_message(user_id, from_chat_id, message_id, keyboard)
        except Exception as e:
            await self.update_statuse(name_camp, user_id, 'unsuccessful')
        else:
            await self.update_statuse(name_camp, user_id, 'success')
            return True

        return False

    async def broadcaster(self, name_camp: str, from_chat_id: int, message_id: int, text_button: str = None, url_button: str = None):
        keyboard = None

        if text_button and url_button:
            keyboard = await self.get_keyboard(text_button, url_button)

        users_ids = await self.get_users(name_camp)
        count = 0
        try:
            for users_id in users_ids:
                if await self.send_message(int(users_id), from_chat_id, message_id, name_camp, keyboard):
                    count += 1
                await asyncio.sleep(.05)

        finally:
            print(f"Разослано {count} сообщений")

        return count