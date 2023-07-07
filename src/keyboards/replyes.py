from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from src.response_messages import CURRENT_PAGE_MSG, NEXT_PAGE_MSG, PREV_PAGE_MSG

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=PREV_PAGE_MSG),
            KeyboardButton(text=CURRENT_PAGE_MSG),
            KeyboardButton(text=NEXT_PAGE_MSG),
        ],
    ],
    resize_keyboard=True,
)

start_btn = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='/start'),
        ],
    ],
    resize_keyboard=True,
)
