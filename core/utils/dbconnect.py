from typing import List, Tuple, Any

import asyncpg
from asyncpg import Record

class Request:
    def __init__(self, connector: asyncpg.pool.Pool):
        self.connector = connector

    async def check_table(self, name_table):
        query = f"SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = '{name_table}')"
        return await self.connector.fetchval(query)

    async def create_table(self, name_table):
        query = f"CREATE TABLE {name_table} (user_id bigint NOT NULL, statuse text, PRIMARY KEY (user_id));"
        await self.connector.execute(query)
        query = f"INSERT INTO {name_table} (user_id, statuse) SELECT user_id, 'waiting' FROM datausers"
        await self.connector.execute(query)

    async def delete_table(self, name_table):
        query = f"DROP TABLE {name_table};"
        await self.connector.execute(query)




    async def add_data(self, user_id, user_name):
        query = f"INSERT INTO datausers (user_id, user_name) VALUES ({user_id}, '{user_name}')" f"ON CONFLICT (user_id) DO UPDATE SET user_name= '{user_name}'"
        await self.connector.execute(query)