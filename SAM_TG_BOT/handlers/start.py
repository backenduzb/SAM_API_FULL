from aiogram import Router, Bot, types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.reply_button import *
from utils.quest import queastions
from utils.teacher_id import get_teacher_telegram_id, get_teacher_id
from data.config import url_edit_teacher
from data.bot import bot
from utils.teacher_data import get_teacher_status
from utils.teacher import TEACHERS_IDS
import aiohttp
import asyncio
from datetime import datetime, timedelta
import time

router = Router()


class SurveyStates(StatesGroup):
    waiting_for_kafedra = State()
    waiting_for_teacher = State()
    answering_questions = State()

user_data = {}
last_vote_time = {}

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    if message.from_user.id in TEACHERS_IDS:
        await message.answer("Assalomu alaykum ustoz, o'zingizga ovoz bera olmaysiz.")
        return
    if user_id in last_vote_time:
        last_vote = last_vote_time[user_id]
        if datetime.now() - last_vote < timedelta(minutes=80):
            remaining_time = 80 - (datetime.now() - last_vote).seconds // 60
            await message.answer(
                f"Siz {remaining_time} daqiqadan keyin qayta ovoz bera olasiz",
                reply_markup=types.ReplyKeyboardRemove()
            )
            return
    
    await state.set_state(SurveyStates.waiting_for_kafedra)
    await message.react([types.ReactionTypeEmoji(emoji='👍')])
    await message.answer(
        f"<b>Assalomu alaykum, <code>{message.from_user.full_name}</code>!</b>",
        reply_markup=reply_kb,
        parse_mode="html"
    )

@router.message(F.text == "➕ So'rovnomada qatnashish" , SurveyStates.waiting_for_kafedra)
async def start_survey(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    
    if user_id in last_vote_time:
        last_vote = last_vote_time[user_id]
        if datetime.now() - last_vote < timedelta(minutes=80):
            remaining_time = 80 - (datetime.now() - last_vote).seconds // 60
            await message.answer(
                f"Siz {remaining_time} daqiqadan keyin qayta ovoz bera olasiz",
                reply_markup=reply_kb
            )
            return
    
    await message.answer(
        "<b>Kafedralardan birini tanlang!</b>",
        parse_mode="html",
        reply_markup=reply_kb_2
    )

@router.message(F.text.startswith("🏢"), SurveyStates.waiting_for_kafedra)
async def select_kafedra(message: Message, state: FSMContext):
    kafedra = message.text.replace("🏢", "").strip()
    await state.update_data(kafedra=kafedra)
    
    topic_name = message.text[2:].strip()
    reply_kb_3 = filter_teachers(topic_name)
    
    await state.set_state(SurveyStates.waiting_for_teacher)
    await message.answer(
        "<b>Ustozni tanlang!</b>",
        reply_markup=reply_kb_3,
        parse_mode="html"
    )

@router.message((F.text.startswith("👩‍🏫") | F.text.startswith("👨‍🏫")),SurveyStates.waiting_for_teacher)
async def select_teacher(message: Message, state: FSMContext):
    teacher_name = message.text.replace("👩‍🏫", "").replace("👨‍🏫", "").strip()
    await state.update_data(teacher_name=teacher_name)
    
    user_id = str(message.from_user.id)
    user_data[user_id] = {
        "current_question": 0,
        "scores": {
            "juda_ham_qoniqaman": 0,
            "ortacha_qoniqaman": 0,
            "asosan_qoniqaman": 0,
            "qoniqmayman": 0,
            "umuman_qoniqaman": 0
        },
        "answers": []
    }
    
    await state.set_state(SurveyStates.answering_questions)
    await message.answer(
        f"<b>{queastions[0]}</b>",
        parse_mode="html",
        reply_markup=reply_kb_3
    )

@router.message(
    F.text.in_(["Yaxshi", "Past", "O'rtacha", "Juda yaxshi", "Yomon"]),
    SurveyStates.answering_questions
)
async def process_answer(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    data = user_data.get(user_id)
    
    if not data or data["current_question"] >= len(queastions):
        await message.answer("Xatolik yuz berdi. /start bilan qayta boshlang.")
        await state.clear()
        return
    
    answer = message.text
    data["answers"].append(answer)
    
    if answer == "Juda yaxshi":
        data["scores"]["juda_ham_qoniqaman"] += 1
    elif answer == "Yaxshi":
        data["scores"]["ortacha_qoniqaman"] += 1
    elif answer == "O'rtacha":
        data["scores"]["asosan_qoniqaman"] += 1
    elif answer == "Past":
        data["scores"]["qoniqmayman"] += 1
    elif answer == "Yomon":
        data["scores"]["umuman_qoniqaman"] += 1
    
    data["current_question"] += 1
    
    if data["current_question"] < len(queastions):
        await message.react([types.ReactionTypeEmoji(emoji='👌')])
        await message.answer(
            f"<b>{queastions[data['current_question']]}</b>",
            parse_mode="html",
            reply_markup=reply_kb_3
        )
    else:
        await message.react([types.ReactionTypeEmoji(emoji='⚡')])
        
        state_data = await state.get_data()
        teacher_name = state_data["teacher_name"]
        teacher_id = get_teacher_id(teacher_name)
        teacher_telegram_id = get_teacher_telegram_id(teacher_name)
        
        edited_url = f"{url_edit_teacher}{teacher_id}/"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(edited_url) as response:
                    current_data = await response.json()
                
                for key in data["scores"]:
                    data["scores"][key] += current_data.get(key, 0)
                
                async with session.put(edited_url, json=data["scores"]) as response:
                    if response.status != 200:
                        await message.answer("Serverda xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")
                        return
                        
            except Exception as e:
                await message.answer(f"Xato: {e}")
                return
        
        kafedra = state_data["kafedra"]
        answers_text = "\n".join(
            f"{i+1} - mezon: {ans}"
            for i, ans in enumerate(data["answers"])
        )
        
        await message.answer(
            f"<b>So'rovnoma yakunlandi!\n\n"
            f"Kafedra: {kafedra}\n"
            f"Ustoz: {teacher_name}\n\n"
            f"Javoblar:\n{answers_text}</b>",
            parse_mode="html",
            reply_markup=reply_kb
        )
        
        if teacher_telegram_id:
            status_text = await get_teacher_status(teacher_id)
            await bot.send_message(
                chat_id=teacher_telegram_id,
                text=status_text,
                parse_mode="html"
            )
            await bot.send_message(
                chat_id=teacher_telegram_id,
                text=f"<b>📑 Sizga quyidagi mezonlar belgilandi:\n\nKafedra: {kafedra}\nUtoz: {teacher_name} \n\n{answers_text}</b>",
                parse_mode="html"
            )
        await state.clear()
        await state.set_state(SurveyStates.waiting_for_kafedra)
        last_vote_time[user_id] = datetime.now()