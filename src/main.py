import asyncio

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart, Text
from aiogram.utils.exceptions import BotBlocked
from apscheduler.triggers.interval import IntervalTrigger

from database import DataBase, Users
from keyboards import menu
from middlewares import AuthUserMiddleware
from pagination.paginator import Paginator
from parsers import PersonDetailView
from periodic_task import em_parser
from renders import render_patient_as_inline_buttons, render_patient_detail_view
from response_messages import (
    CURRENT_PAGE_MSG,
    GREETING_MESSAGE,
    NEW_PATIENT_MSG,
    NEXT_PAGE_MSG,
    PAGES_MSG,
    PREV_PAGE_MSG,
)
from settings import PAGE_LIMIT, TASK_INTERVAL, bot, dp, scheduler


async def send_notifications_to_users():
    try:
        notifications = await em_parser()
        async with DataBase() as db:
            users = await db.get_staff_users()
            chats = [(user.chat_id, user.id) for user in users]
            for notification in notifications:
                for chat_id, user_id in chats:
                    response = render_patient_detail_view(notification)
                    try:
                        await bot.send_message(text=NEW_PATIENT_MSG, chat_id=chat_id)
                        await bot.send_message(text=response, chat_id=chat_id)
                    except BotBlocked:
                        await db.delete_user(user_id)
    except Exception as e:
        async with DataBase() as db:
            await db.add_task(False, f'{e!r}')


dp.middleware.setup(AuthUserMiddleware())


@dp.message_handler(CommandStart())
async def help_command_handler(request: types.Message):
    await request.answer(GREETING_MESSAGE, reply_markup=menu)


@dp.message_handler(Text(CURRENT_PAGE_MSG))
async def current_page_view(request: types.Message, user: Users):
    async with DataBase() as db:
        patients = await db.get_patients()
    patients_view = [patient.to_tuple() for patient in patients]
    patients_cnt = len(patients_view)
    paginator = Paginator(patients_view, PAGE_LIMIT)
    patients_view = paginator.get_items(user.page_id)
    keyboard = render_patient_as_inline_buttons(patients_view)
    await request.answer(
        PAGES_MSG.format(
            page=user.page_id + 1,
            page_count=paginator.pages_count,
            patients_cnt=patients_cnt,
        ),
        reply_markup=keyboard,
    )


@dp.message_handler(Text(NEXT_PAGE_MSG))
async def next_page_view(request: types.Message, user: Users):
    async with DataBase() as db:
        patients = await db.get_patients()
        patients_view = [patient.to_tuple() for patient in patients]
        patients_cnt = len(patients_view)
        paginator = Paginator(patients_view, PAGE_LIMIT)
        page_id = user.page_id + 1
        if not paginator.page_exist(page_id):
            page_id = 0
        await db.update_page_id_user(page_id, user.id)
    patients_view = paginator.get_items(page_id)
    keyboard = render_patient_as_inline_buttons(patients_view)
    await request.answer(
        PAGES_MSG.format(
            page=page_id + 1,
            page_count=paginator.pages_count,
            patients_cnt=patients_cnt,
        ),
        reply_markup=keyboard,
    )


@dp.message_handler(Text(PREV_PAGE_MSG))
async def prev_page_view(request: types.Message, user: Users):
    async with DataBase() as db:
        patients = await db.get_patients()
        patients_view = [patient.to_tuple() for patient in patients]
        patients_cnt = len(patients_view)
        paginator = Paginator(patients_view, PAGE_LIMIT)
        page_id = user.page_id - 1
        if not paginator.page_exist(page_id):
            page_id = 0
        await db.update_page_id_user(page_id, user.id)
    patients_view = paginator.get_items(page_id)
    keyboard = render_patient_as_inline_buttons(patients_view)
    await request.answer(
        PAGES_MSG.format(
            page=page_id + 1,
            page_count=paginator.pages_count,
            patients_cnt=patients_cnt,
        ),
        reply_markup=keyboard,
    )


@dp.callback_query_handler(Text(startswith='patient_info_'))
async def patient_detail_view(callback: types.CallbackQuery):
    person_id = callback.data.split('_')[2]
    async with DataBase() as db:
        person = await db.get_patient_by_person_id(person_id)
        events = await db.get_patient_events_by_patient_id(person.id)
    patient = PersonDetailView(
        person.person_id,
        person.fio,
        person.birthday,
        {event.to_tuple() for event in events},
    )
    response = render_patient_detail_view(patient)
    await callback.message.answer(text=response)


async def main():
    await send_notifications_to_users()
    scheduler.add_job(send_notifications_to_users, IntervalTrigger(minutes=TASK_INTERVAL))
    try:
        scheduler.start()
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
