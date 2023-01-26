from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from api import ApiWrapper, AuthData, AuthStatusResponse
from database import DataBase
from .config_builder import TxtConfBuilder

CONF_BUILDER = TxtConfBuilder('config.txt')

LOGIN = CONF_BUILDER.get_login()

PASSWORD = CONF_BUILDER.get_password()

API_URL = CONF_BUILDER.get_api_url()

COOKIES = CONF_BUILDER.cookies()

SUCCESS_LOGIN = """{"success":true}"""

LOGOUT_ERROR = """{Action: 'logout'}"""

PAGE_LIMIT = 8

TASK_INTERVAL = CONF_BUILDER.get_task_timeout()

ApiWrapper.aiohttp_instance(API_URL, COOKIES, AuthData(LOGIN, PASSWORD),
                            AuthStatusResponse(SUCCESS_LOGIN, LOGOUT_ERROR), CONF_BUILDER.set_cookies)


bot = Bot(CONF_BUILDER.get_bot_token())

dp = Dispatcher(bot)

scheduler = AsyncIOScheduler()


__all__ = ['LOGIN', 'PASSWORD', 'API_URL', 'COOKIES', 'CONF_BUILDER', 'SUCCESS_LOGIN', 'LOGOUT_ERROR', 'DataBase',
           'ApiWrapper', 'bot', 'dp', 'scheduler', 'TASK_INTERVAL', 'PAGE_LIMIT']
