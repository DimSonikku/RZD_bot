import json
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import config
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from obrabotka import process_text

# Инициализация бота и диспетчера
bot = Bot(token=config.apiToken)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Определение состояний бота
class BotStates(StatesGroup):
    start = State()
    waitingForRequest = State()
    menu = State()
    aboutBot = State()


# Команда /start
@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    menuButton = KeyboardButton("Меню")
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(menuButton)

    await message.answer(text="Привет! Я чат-бот РЖД.\nЧто Вас интересует?", reply_markup=markup)
    await BotStates.menu.set()



@dp.message_handler(state=BotStates.menu)
async def inMenu(message: types.Message, state: FSMContext):
    inputButton = KeyboardButton("Ввести текст")
    aboutBotButton = KeyboardButton("О боте")
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(inputButton, aboutBotButton)

    if message.text == "Меню":
        await message.answer("Что вам угодно?", reply_markup=markup)
        await BotStates.start.set()



# Обработчик состояния BotStates.start
@dp.message_handler(state=BotStates.start)
async def handle_start(message: types.Message, state: FSMContext):
    inputButton = KeyboardButton("Ввести текст")
    aboutBotButton = KeyboardButton("О боте")
    goBackButton = KeyboardButton("Меню")

    if message.text == "О боте":
        markup = ReplyKeyboardMarkup(resize_keyboard=True).add(goBackButton)
        await BotStates.aboutBot.set()

    elif message.text == "Ввести текст" or message.text == "Повторить запрос":
        markup = ReplyKeyboardMarkup(resize_keyboard=True).add(goBackButton)
        await message.answer("Введите запрос", reply_markup=markup)
        await BotStates.waitingForRequest.set()

    elif message.text == "Меню":
        markup = ReplyKeyboardMarkup(resize_keyboard=True).add(inputButton, aboutBotButton)
        await message.answer("Что вам угодно?", reply_markup=markup)
        await BotStates.start.set()



@dp.message_handler(state=BotStates.waitingForRequest)
async def inputTextActivated(message: types.Message, state: FSMContext):
    goBackButton = KeyboardButton("Меню")
    againButton = KeyboardButton("Повторить запрос")

    if message.text == "Меню":
        # Вернуться в состояние "menu"
        markup = ReplyKeyboardMarkup(resize_keyboard=True).add(goBackButton)
        await message.answer("Возвращаемся в меню", reply_markup=markup)
        await BotStates.menu.set()

    else:
        markup = ReplyKeyboardMarkup(resize_keyboard=True).add(goBackButton, againButton)
        text = process_text(message.text, "Коллективный договор.pdf")
        MAX_MESSAGE_LENGTH = 4096

        # Разбиение сообщения на части и отправка
        for start in range(0, len(text), MAX_MESSAGE_LENGTH):
            part = text[start:start + MAX_MESSAGE_LENGTH]
            await bot.send_message(message.chat.id, part)
        await message.answer("Что дальше?", reply_markup=markup)
        await BotStates.start.set()




# Обработчик команды "О боте"
@dp.message_handler(state=BotStates.aboutBot)
async def about_bot_activated(message: types.Message, state: FSMContext):
    goBackButton = KeyboardButton("Меню")
    markup = ReplyKeyboardMarkup(resize_keyboard=True).add(goBackButton)
    
    await message.answer("Это бот для информации о РЖД.", reply_markup=markup)
    await BotStates.menu.set()



# Запуск бота
if __name__ == "__main__":
    try:
        executor.start_polling(dp, skip_updates=True)
    except ConnectionError as e:
        print('Ошибка соединения: ', e)
    except Exception as e:
        print("Непредвиденная ошибка: ", e)
    finally:
        print("Работа завершена.")
