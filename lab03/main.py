from aiogram import Dispatcher, Bot, executor, types
import dbManager
from datetime import datetime
import pytz
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import os
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

bot = Bot(os.getenv("BOT_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

scheduler = AsyncIOScheduler()

class States(StatesGroup):
    ADDING = State()
    EDITING = State()

def str_to_timestamp(s: str) -> float:
    try:
        return datetime.timestamp(datetime.strptime(s, "%Y-%m-%d %H:%M"))
    except:
        return 0

def timestamp_to_str(t: float) -> float:
    try:
        return datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M")
    except:
        return ""
    
async def task_reminder():
    MOSCOW_TIMEZONE = pytz.timezone('Europe/Moscow')  # Define Moscow timezone
    now = datetime.now(MOSCOW_TIMEZONE)
    current_time = datetime(now.year, now.month, now.day, now.hour, now.minute, now.second).timestamp()
    users = dbManager.getUsers()
    for user in users:
        tasks = dbManager.getTasksByUser(user)
        for task in tasks:
            if 0 < task.timestamp - current_time < 3600:
                await bot.send_message(user.telegram_id, f"Напоминание!\n{task.id}) {task.text}\n_______________\nПриоритет: {task.priority}\nКогда: {timestamp_to_str(task.timestamp)}", reply_markup=main_menu_markup())


tz = pytz.timezone('Europe/Moscow') 
scheduler.add_job(task_reminder, trigger='interval', minutes=15, seconds = 0, timezone=tz)
scheduler.start()

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    if not dbManager.getUserByTelegram(str(message.chat.id)):
        dbManager.addUser(telegram_id=str(message.chat.id))
    await message.answer(f"Hello", reply_markup=main_menu_markup())

@dp.message_handler(lambda message: message.text == "Добавить задачу")
async def add_task(message: types.Message, state = FSMContext):
    await state.set_state(States.ADDING)
    await message.answer("Введите задачу в формате:\nОписание | Время (YYYY-MM-DD HH:MM)", reply_markup=main_menu_markup())
    
@dp.message_handler(lambda message: "|" in message.text, state=States.ADDING)
async def save_new_task(message: types.Message, state: FSMContext):
    user_id = str(message.chat.id)
    parts = message.text.split("|")
    if len(parts) != 2:
        await message.answer("Неверный формат ввода.", reply_markup=main_menu_markup())
        return
    
    text, due_time = map(str.strip, parts)
    timestamp = str_to_timestamp(due_time)
    task = dbManager.addTask(text, dbManager.priorities.medium, timestamp)
    user = dbManager.getUserByTelegram(user_id)
    link = dbManager.addLink(task.id, user.id)
    if task:
        await message.answer("Выберите приоритет:", reply_markup=new_task_markup(task.id))
    else:
        await message.answer("Ошибка на стороне сервера", reply_markup=main_menu_markup())
    await state.finish()

@dp.message_handler(lambda message: message.text == "Список задач")
async def list_tasks(message: types.Message):
    user = dbManager.getUserByTelegram(str(message.chat.id))
    tasks = dbManager.getTasksByUser(user)
    tasks.sort(key=lambda c: {dbManager.priorities.low: 0, dbManager.priorities.medium: 1, dbManager.priorities.high: 2}[c.priority], reverse=True)
    if not tasks:
        await message.answer("У вас нет задач.", reply_markup=main_menu_markup())
    else:
        for task in tasks:
            await message.answer(f"{task.id}) {task.text}\n_______________\nПриоритет: {task.priority}\nКогда: {timestamp_to_str(task.timestamp)}", reply_markup=task_markup(task.id))

async def edit_task(message: types.Message, task_id: int, state: FSMContext):
    await state.set_state(States.EDITING)
    await state.set_data({"task_id": task_id})
    task = dbManager.getTask(int(task_id))
    await message.answer(f"Изменение {task.id}) {task.text}\n_______________\nПриоритет: {task.priority}\nКогда: {timestamp_to_str(task.timestamp)}\n_______________\nВведите изменения в формате(поле можете оставть пустым для сохранения предыдущего значения):\nОписание | Время (YYYY-MM-DD HH:MM)\nИли выберите новый приоритет:", reply_markup=new_task_markup(task_id))

@dp.message_handler(lambda message: "|" in message.text, state=States.EDITING)
async def save_edit_task(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    task_id = data["task_id"]
    parts = message.text.split("|")
    if len(parts) != 2:
        await message.answer("Неверный формат ввода.", reply_markup=main_menu_markup())
        return
    
    # task = dbManager.getTask()
    text, due_time = map(str.strip, parts)
    timestamp = str_to_timestamp(due_time)
    task = dbManager.editTask(task_id, text, "", timestamp)
    # task = dbManager.addTask(text, dbManager.priorities.medium, timestamp)
    
    if task:
        await message.answer("Задача изменена успешно", reply_markup=main_menu_markup())
    else:
        await message.answer("Ошибка на стороне сервера", reply_markup=main_menu_markup())
    await state.finish()

async def delete_task(message: types.Message, task_id: int, state: FSMContext):
    dbManager.deleteTask(task_id)
    await message.answer(f"Задача {task_id} удалена", reply_markup=main_menu_markup())

async def set_task_priority(message: types.Message, task_id: int, priority: str, state: FSMContext):
    dbManager.editTask(task_id, "", {"low": dbManager.priorities.low, "medium": dbManager.priorities.medium, "high": dbManager.priorities.high}[priority], 0)
    await message.answer(f"Приоритет задан", reply_markup=main_menu_markup())
    await state.finish()

@dp.callback_query_handler(state=States.EDITING)
async def edit_priority_buttons(callback: types.CallbackQuery, state: FSMContext):
    callback_type, callback_id = callback.data.split()
    if callback_type.split("/")[0] == "priority":
        await set_task_priority(callback.message, int(callback_id), callback_type.split("/")[1], state)
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

@dp.callback_query_handler()
async def under_buttons(callback: types.CallbackQuery, state: FSMContext):
    callback_type, callback_id = callback.data.split()
    if callback_type == "edit":
        await edit_task(callback.message, int(callback_id), state)
    elif callback_type == "delete":
        await delete_task(callback.message, int(callback_id), state)
    elif callback_type.split("/")[0] == "priority":
        await set_task_priority(callback.message, int(callback_id), callback_type.split("/")[1], state)
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

def main_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Список задач"))
    markup.add(types.KeyboardButton("Добавить задачу"))
    return markup

def task_markup(callback_task_id):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("Изменить задачу", callback_data="edit " + str(callback_task_id)))
    markup.row(types.InlineKeyboardButton("Удалить задачу", callback_data="delete " + str(callback_task_id)))
    return markup

def new_task_markup(callback_task_id):
    markup = types.InlineKeyboardMarkup()
    prefix = "priority"
    markup.row(types.InlineKeyboardButton("Низкий", callback_data=prefix + "/low " + str(callback_task_id)))
    markup.row(types.InlineKeyboardButton("Средний", callback_data=prefix + "/medium " + str(callback_task_id)))
    markup.row(types.InlineKeyboardButton("Высокий", callback_data=prefix + "/high " + str(callback_task_id)))
    return markup


if __name__ == "__main__":
    print("success")
    executor.start_polling(dp)