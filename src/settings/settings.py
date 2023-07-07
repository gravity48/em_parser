import os

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from api import ApiWrapper, AuthData, AuthStatusResponse

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

LOGIN = os.environ['LOGIN']

PASSWORD = os.environ['PASSWORD']

API_URL = os.environ['URL']

SUCCESS_LOGIN = """{"success":true}"""

LOGOUT_ERROR = """{Action: 'logout'}"""

PAGE_LIMIT = int(os.environ['PAGE_LIMIT'])

TASK_INTERVAL = int(os.environ['INTERVAL'])

ApiWrapper.aiohttp_instance(
    API_URL,
    AuthData(LOGIN, PASSWORD),
    AuthStatusResponse(SUCCESS_LOGIN, LOGOUT_ERROR),
)

bot = Bot(os.environ['API_TOKEN'])

dp = Dispatcher(bot)

scheduler = AsyncIOScheduler()
