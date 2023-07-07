from unittest import IsolatedAsyncioTestCase

from src.database.database import DataBase


class DatabaseTest(IsolatedAsyncioTestCase):
    async def test_010_get_cookies(self):
        async with DataBase() as db:
            cookies = await db.get_cookies()
        self.assertIsInstance(cookies, str)

    async def test_015_update_cookies(self):
        async with DataBase() as db:
            cookies = await db.get_cookies()
            await db.update_cookies(cookies)
        self.assertIsInstance(cookies, str)
