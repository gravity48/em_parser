from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from response_messages import NEXT_PAGE_MSG, CURRENT_PAGE_MSG, PREV_PAGE_MSG

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=PREV_PAGE_MSG),
            KeyboardButton(text=CURRENT_PAGE_MSG),
            KeyboardButton(text=NEXT_PAGE_MSG)
        ]
    ],
    resize_keyboard=True
)

start_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='/start'),
        ]
    ],
    resize_keyboard=True
)

__all__ = ['menu', 'start_btn']
