from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
import sqlite3
from utils.quest import answer_buttons

__all__ = ["reply_kb", "reply_kb_2","filter_teachers","reply_kb_3"]

reply_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ So'rovnomada qatnashish"),
        ],
    ],
    resize_keyboard=True
)

conn = sqlite3.connect("data/base.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM topics")
names = cursor.fetchall()

buttons = [[KeyboardButton(text=f"🏢 {name[0]}")] for name in names]

reply_kb_2 = ReplyKeyboardMarkup(
    keyboard=buttons,
    resize_keyboard=True
)
conn.close()

buttons = [KeyboardButton(text=answer) for answer in answer_buttons]
keyboard = [buttons[i:i+2] for i in range(0, len(buttons), 2)]

reply_kb_3 = ReplyKeyboardMarkup(
    keyboard=keyboard,
    resize_keyboard=True
)

def filter_teachers(topic_name: str) -> ReplyKeyboardMarkup:
    conn = sqlite3.connect("data/base.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.full_name
        FROM teachers t
        JOIN teacher_topics tt ON t.id = tt.teacher_id
        JOIN topics tp ON tt.topic_id = tp.id
        WHERE tp.name = ?
    """, (topic_name,))
    results = cursor.fetchall()
    conn.close()

    teachers = [full_name for (full_name,) in results]

    if not teachers:
        buttons = [[KeyboardButton(text="Ustoz lar yo'q")]]
    else:
        buttons_raw = []
        for teacher in teachers:
            last_name = teacher.split()[0]
            emoji = "👩‍🏫" if last_name.lower().endswith('a') else "👨‍🏫"
            buttons_raw.append(KeyboardButton(text=f"{emoji} {teacher}"))

        buttons = [buttons_raw[i:i+2] for i in range(0, len(buttons_raw), 2)]

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
