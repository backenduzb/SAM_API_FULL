from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import types
from keyboards.reply_button import *
from aiogram import F
from utils.user_data import answered_questions, total_answer
from utils.quest import queastions
from utils.teacher_id import get_teacher_telegram_id, get_teacher_id
import requests
from data.config import url_edit_teacher
from data.bot import bot
from utils.teacher_data import get_teacher_status
from utils.teacher import TEACHERS_IDS
import asyncio


router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    
    if message.from_user.id not in TEACHERS_IDS:

        global total_answer
        answered_questions[message.from_user.username] = ""
        answered_questions[str(message.from_user.id)] = 0
        answered_questions[f"{message.from_user.username}_kafedra"] = ""

        total_answer = "<b>📑 Sizga quyidagi mezonlar belgilandi:</b> \n\n"
        await message.react([types.ReactionTypeEmoji(emoji='👍')])
        await message.answer(f"<b>Assalomu alaykum, <code>{message.from_user.full_name}</code>!</b>",reply_markup=reply_kb,parse_mode="html")
    else:
        await message.answer("Assalomu alaykum ustoz o'zingizga ovoz bera olmaysiz.")

@router.message(F.text == "➕ So'rovnomada qatnashish")
async def handle_message(message: Message):
    global total_answer

    answered_questions[message.from_user.username] = ""
    answered_questions[str(message.from_user.id)] = 0
    answered_questions[f"{message.from_user.username}_kafedra"] = ""

    total_answer = "<b>📑 Sizga quyidagi mezonlar belgilandi:</b> \n\n"
    
    if message.from_user.id not in TEACHERS_IDS:
        await message.answer("<b>Kafedralardan birini tanlang!</b>",parse_mode="html",reply_markup=reply_kb_2)
    else:
        await message.answer("Assalomu alaykum ustoz o'zingizga ovoz bera olmaysiz.")

@router.message(F.text.startswith("🏢"))
async def kofedra(message: Message):
    if message.from_user.id not in TEACHERS_IDS:
        global total_answer
        answered_questions[f"{message.from_user.username}_kafedra"] = str(message.text).replace("🏢","").strip()
        total_answer += f"<code>{answered_questions[f'{message.from_user.username}_kafedra']} kafedrasi. </code>\n"
        topic_name = message.text[2:].strip()
        reply_kb_3 = filter_teachers(topic_name)
        await message.answer(" <b>Ustozni tanlang!</b>",reply_markup=reply_kb_3,parse_mode="html")
    else:
        await message.answer("Assalomu alaykum ustoz o'zingizga ovoz bera olmaysiz.")

@router.message(F.text.startswith("👩‍🏫") | F.text.startswith("👨‍🏫"))
async def status(message: Message):
    if message.from_user.id not in TEACHERS_IDS:
        global total_answer


        answered_questions[message.from_user.username] = str(message.text).replace("👩‍🏫","").replace("👨‍🏫","").strip()

        total_answer += f"<code>{answered_questions[message.from_user.username]}</code> \n\n"
        
        await message.answer(f"<b>{queastions[answered_questions[str(message.from_user.id)]]}</b>",parse_mode="html",reply_markup=reply_kb_3)
        answered_questions[str(message.from_user.id)] += 1
    else:
        await message.answer("Assalomu alaykum ustoz o'zingizga ovoz bera olmaysiz.")

import aiohttp

@router.message(F.text.in_(["Yaxshi", "Past", "O'rtacha", "Juda yaxshi", "Yomon"]))
async def its_user_answer(message: Message):
    global total_answer
    
    
    if message.from_user.id not in TEACHERS_IDS:
      

        text = message.text
        user_id = str(message.from_user.id)
        username = message.from_user.username

        if answered_questions[user_id] <= 5:
            await message.react([types.ReactionTypeEmoji(emoji='👌')])
            teacher_name = answered_questions[username].strip()

            total_answer += f"{answered_questions[user_id]} - mezon: {text} \n"

            if 'user_scores' not in globals():
                global user_scores
                user_scores = {}

            if user_id not in user_scores:
                user_scores[user_id] = {
                    "juda_ham_qoniqaman": 0,
                    "ortacha_qoniqaman": 0,
                    "asosan_qoniqaman": 0,
                    "qoniqmayman": 0,
                    "umuman_qoniqaman": 0
                }

            if text == "Juda yaxshi":
                user_scores[user_id]["juda_ham_qoniqaman"] += 1
            elif text == "Yaxshi":
                user_scores[user_id]["ortacha_qoniqaman"] += 1
            elif text == "O'rtacha":
                user_scores[user_id]["asosan_qoniqaman"] += 1
            elif text == "Past":
                user_scores[user_id]["qoniqmayman"] += 1
            elif text == "Yomon":
                user_scores[user_id]["umuman_qoniqaman"] += 1  

            await message.answer(f"<b>{queastions[answered_questions[user_id]]}</b>", parse_mode="html", reply_markup=reply_kb_3)
            answered_questions[user_id] += 1

        elif answered_questions[user_id] == 6:
            answered_questions[user_id] += 1
            await message.react([types.ReactionTypeEmoji(emoji='⚡️')])

            teacher_name = answered_questions[username].strip()
            teacher_telegram_id = get_teacher_telegram_id(teacher_name)
            teacher_id = get_teacher_id(teacher_name)
            
            total_answer += f"{answered_questions[user_id]-1} - mezon: {text} \n"

            data = user_scores.get(user_id, {
                "juda_ham_qoniqaman": 0,
                "ortacha_qoniqaman": 0,
                "asosan_qoniqaman": 0,
                "qoniqmayman": 0,
                "umuman_qoniqaman": 0
            })

            edited_url = f"{url_edit_teacher}{teacher_id}/"

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(edited_url) as response:
                        current_data = await response.json()
                except Exception as e:
                    await message.answer(f"Xato: Server bilan bog'lanishda xato: {e}")
                    return

                for key in data:
                    data[key] += current_data.get(key, 0)

                try:
                    async with session.put(edited_url, json=data) as response:
                        if response.status != 200:
                            await message.answer(f"Xato: Ma'lumotlarni yangilashda xato. Kod: {response.status}")
                            return
                except Exception as e:
                    await message.answer(f"Xato: Server bilan bog'lanishda xato: {e}")
                    return

            await message.answer(total_answer, parse_mode="html")
            await message.answer(text="So'rovnomada ishtirokingiz uchun rahmat.", reply_markup=reply_kb)

            if teacher_telegram_id:
                text = await get_teacher_status(teacher_id)
                await bot.send_message(chat_id=teacher_telegram_id, text=text, parse_mode="html")
                asyncio.sleep(1)
                await bot.send_message(chat_id=teacher_telegram_id, text=total_answer, parse_mode="html")
       
    
    else:
        await message.answer("Assalomu alaykum ustoz o'zingizga ovoz bera olmaysiz.")

