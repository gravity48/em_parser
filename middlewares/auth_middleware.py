from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from database import DataBase, Users
from keyboards import start_btn
from response_messages import LOGOUT_ERROR_MSG


class AuthUserMiddleware(BaseMiddleware):

    @staticmethod
    async def get_user_in_database(unregistered_user: types.User, request: types.Message) -> Users:
        async with DataBase() as db:
            user = await db.get_or_create_user(unregistered_user.id, unregistered_user.username,
                                               unregistered_user.first_name,
                                               unregistered_user.last_name, request.chat.id)
        if user.is_staff:
            return user
        else:
            await request.answer(LOGOUT_ERROR_MSG, reply_markup=start_btn)
            raise CancelHandler()

    async def on_process_message(self, request: types.Message, data: dict):
        data['user'] = await self.get_user_in_database(request.from_user, request)

    async def on_process_command(self, request: types.Message, data: dict):
        data['user'] = await self.get_user_in_database(request.from_user, request)


__all__ = ['AuthUserMiddleware', ]
