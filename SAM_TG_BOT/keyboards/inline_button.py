from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Button 1",
                callback_data="button_1"
            ),
            InlineKeyboardButton(
                text="Button 2",
                callback_data="button_2"
            )
        ],
        [
            InlineKeyboardButton(
                text="Button 3",
                callback_data="button_3"
            )
        ]
    ]
)
